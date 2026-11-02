package com.motionworks.client.anim;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.motionworks.MotionWorks;
import com.motionworks.client.rig.RigFactory;
import com.motionworks.client.rig.RigProfile;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.io.ClipJsonLoader;
import com.motionworks.engine.io.ClipLibrary;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;

import java.io.Reader;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Loads animation clips, rig profiles and entity family mappings from every resource pack
 * namespace:
 * <pre>
 *   assets/&lt;ns&gt;/motionworks/animations/**.json   clips (native or Bedrock/Blockbench format)
 *   assets/&lt;ns&gt;/motionworks/rigs/*.json          rig profiles
 *   assets/&lt;ns&gt;/motionworks/entities.json        entity type -&gt; rig + clip targets
 * </pre>
 * Resource packs can therefore add or override animations without code.
 */
public final class AnimationLibrary implements ResourceManagerReloadListener {
    public static final AnimationLibrary INSTANCE = new AnimationLibrary();

    public record EntityFamily(String rig, List<String> targets) {}

    private final ClipLibrary clips = new ClipLibrary();
    private final Map<String, RigProfile> rigs = new LinkedHashMap<>();
    private final Map<String, EntityFamily> families = new LinkedHashMap<>();
    private final com.motionworks.engine.io.BodyPlanTable bodyPlans = new com.motionworks.engine.io.BodyPlanTable();
    private int generation;
    private final List<String> errors = new ArrayList<>();

    private AnimationLibrary() {}

    public ClipLibrary clips() {
        return clips;
    }

    public RigProfile rig(String id) {
        RigProfile p = rigs.get(id);
        if (p == null) p = rigs.get("generic");
        if (p == null) p = new RigProfile("generic");
        return p;
    }

    public EntityFamily family(String entityTypeId) {
        return families.get(entityTypeId);
    }

    public Map<String, EntityFamily> families() {
        return families;
    }

    /** How entity types without a family (mobs from other mods) are animated; see {@code body_plans.json}. */
    public com.motionworks.engine.io.BodyPlanTable bodyPlans() {
        return bodyPlans;
    }

    /** Increments on each reload so animators can rebuild their controllers. */
    public int generation() {
        return generation;
    }

    public List<String> errors() {
        return errors;
    }

    @Override
    public void onResourceManagerReload(ResourceManager manager) {
        clips.clear();
        rigs.clear();
        families.clear();
        errors.clear();
        Map<ResourceLocation, Resource> rigFiles = new TreeMap<>(manager.listResources("motionworks/rigs", l -> l.getPath().endsWith(".json")));
        // Profiles may extend each other; resolve in dependency order by retrying.
        Map<String, JsonObject> pending = new LinkedHashMap<>();
        rigFiles.forEach((loc, res) -> {
            try (Reader r = res.openAsReader()) {
                String id = loc.getPath().substring(loc.getPath().lastIndexOf('/') + 1).replace(".json", "");
                pending.put(id, JsonParser.parseReader(r).getAsJsonObject());
            } catch (Exception e) {
                errors.add(loc + ": " + e.getMessage());
            }
        });
        for (int pass = 0; pass < 6 && !pending.isEmpty(); pass++) {
            pending.entrySet().removeIf(en -> {
                JsonObject o = en.getValue();
                if (o.has("extends") && !rigs.containsKey(o.get("extends").getAsString()) && pending.containsKey(o.get("extends").getAsString())) return false;
                rigs.put(en.getKey(), RigProfile.parse(en.getKey(), o, rigs));
                return true;
            });
        }
        for (String ns : manager.getNamespaces()) {
            for (Resource res : manager.getResourceStack(new ResourceLocation(ns, "motionworks/entities.json"))) {
                try (Reader r = res.openAsReader()) {
                    JsonObject o = JsonParser.parseReader(r).getAsJsonObject();
                    for (Map.Entry<String, JsonElement> e : o.entrySet()) {
                        if (e.getValue().isJsonNull()) {
                            // A pack can hand a type back to the body-plan rules (or test them on a vanilla mob).
                            families.remove(e.getKey());
                            continue;
                        }
                        JsonObject f = e.getValue().getAsJsonObject();
                        List<String> targets = new ArrayList<>();
                        f.getAsJsonArray("targets").forEach(t -> targets.add(t.getAsString()));
                        families.put(e.getKey(), new EntityFamily(f.get("rig").getAsString(), targets));
                    }
                } catch (Exception e) {
                    errors.add(ns + ":motionworks/entities.json: " + e.getMessage());
                }
            }
        }
        bodyPlans.clear();
        for (String ns : manager.getNamespaces()) {
            List<Resource> stack = new ArrayList<>(manager.getResourceStack(new ResourceLocation(ns, "motionworks/body_plans.json")));
            // Highest-priority pack first, so a resource pack's plans are tried before the mod's own.
            java.util.Collections.reverse(stack);
            for (Resource res : stack) {
                try (Reader r = res.openAsReader()) {
                    bodyPlans.load(r, ns + ":motionworks/body_plans.json (" + res.sourcePackId() + ")");
                } catch (Exception e) {
                    errors.add(ns + ":motionworks/body_plans.json: " + e.getMessage());
                }
            }
        }
        Map<ResourceLocation, Resource> animFiles = new TreeMap<>(manager.listResources("motionworks/animations", l -> l.getPath().endsWith(".json")));
        int files = 0;
        for (Map.Entry<ResourceLocation, Resource> e : animFiles.entrySet()) {
            try (Reader r = e.getValue().openAsReader()) {
                List<AnimationClip> list = ClipJsonLoader.load(r, e.getKey().toString());
                clips.addAll(list);
                files++;
            } catch (Exception ex) {
                errors.add(e.getKey() + ": " + ex.getMessage());
            }
        }
        generation++;
        RigFactory.clear();
        MotionWorks.LOGGER.info("MotionWorks loaded {} animation clips from {} files, {} rig profiles, {} entity families",
                clips.size(), files, rigs.size(), families.size());
        for (String err : errors) MotionWorks.LOGGER.error("MotionWorks animation data error: {}", err);
    }
}
