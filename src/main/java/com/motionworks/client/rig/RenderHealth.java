package com.motionworks.client.rig;

import com.motionworks.MotionWorks;
import com.motionworks.config.MWConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Watches the third-person hook in the running game and explains what stops it. For every entity type it counts,
 * over a rolling window, the frames where the renderer started ({@code RenderLivingEvent.Pre}), was cancelled by
 * another mod, reached the MotionWorks hook, and was posed; and the frames where another mod changed the parts
 * MotionWorks posed before the model was drawn (the pose is then written again) or while it was drawn (which
 * MotionWorks cannot undo). {@code /mw doctor} prints the report; a short warning goes to chat once per session
 * when the player or most mobs are blocked.
 */
public final class RenderHealth {
    /** Why a hooked frame was not posed. */
    public enum Skip { DISABLED, FAR, NO_ANIMATOR, NO_BONES, IDLE, ERROR }

    private static final long WINDOW_MS = 4000L;

    static final class Counts {
        int seen, cancelled, hooked, posed, changedBefore, changedDuring, bones, parts;
        final int[] skips = new int[Skip.values().length];

        void add(Counts o) {
            seen += o.seen;
            cancelled += o.cancelled;
            hooked += o.hooked;
            posed += o.posed;
            changedBefore += o.changedBefore;
            changedDuring += o.changedDuring;
            bones = Math.max(bones, o.bones);
            parts = Math.max(parts, o.parts);
            for (int i = 0; i < skips.length; i++) skips[i] += o.skips[i];
        }
    }

    private static Map<EntityType<?>, Counts> current = new LinkedHashMap<>();
    private static Map<EntityType<?>, Counts> last = new LinkedHashMap<>();
    private static long windowStart;
    private static boolean warned;
    private static int windows;

    /** The rig posed by the hook in this render call, checked before and after the model is drawn. */
    private static ModelRig pending;
    private static EntityModel<?> pendingModel;
    private static LivingEntity pendingEntity;

    private RenderHealth() {}

    private static Counts of(Entity e) {
        roll();
        return current.computeIfAbsent(e.getType(), t -> new Counts());
    }

    private static void roll() {
        long now = System.currentTimeMillis();
        if (now - windowStart < WINDOW_MS) return;
        if (windowStart != 0L) {
            last = current;
            current = new LinkedHashMap<>();
            windows++;
        }
        windowStart = now;
    }

    public static void reset() {
        current = new LinkedHashMap<>();
        last = new LinkedHashMap<>();
        windowStart = 0L;
        windows = 0;
        checked = 0;
        warned = false;
        loggedHealthy = false;
        loggedPlans.clear();
        pending = null;
        pendingModel = null;
        pendingEntity = null;
    }

    /** RenderLivingEvent.Pre, seen last and including cancelled events. */
    public static void preRender(LivingEntity e, boolean cancelled) {
        Counts c = of(e);
        c.seen++;
        if (cancelled) c.cancelled++;
    }

    /** The hook ran; nothing was posed (yet). */
    public static void hooked(LivingEntity e) {
        of(e).hooked++;
        pending = null;
    }

    public static void skipped(LivingEntity e, Skip why) {
        of(e).skips[why.ordinal()]++;
    }

    public static void posed(LivingEntity e, EntityModel<?> model, ModelRig mr) {
        Counts c = of(e);
        c.posed++;
        c.parts = mr.parts.length - 2;
        int bound = 0;
        for (int i = 2; i < mr.parts.length; i++) if (mr.parts[i] != null) bound++;
        c.bones = bound;
        pending = mr;
        pendingModel = model;
        pendingEntity = e;
    }

    /** Just before the body is drawn: puts back what another mod changed after the hook, if allowed. */
    public static void beforeDraw(LivingEntity e, EntityModel<?> model) {
        ModelRig mr = pending;
        if (mr == null || pendingEntity != e || pendingModel != model || !mr.hasOutput) return;
        if (changed(mr)) {
            of(e).changedBefore++;
            if (MWConfig.CLIENT.reassertPose.get()) rewrite(mr);
        }
    }

    /** Just after the body is drawn: a change here was made while drawing, which MotionWorks cannot undo. */
    public static void afterDraw(LivingEntity e, EntityModel<?> model) {
        ModelRig mr = pending;
        pending = null;
        if (mr == null || pendingEntity != e || pendingModel != model || !mr.hasOutput) return;
        if (changed(mr)) of(e).changedDuring++;
    }

    /** Whether a channel MotionWorks moved away from vanilla no longer holds what it wrote. */
    static boolean changed(ModelRig mr) {
        ModelPart[] parts = mr.parts;
        for (int b = 2; b < parts.length; b++) {
            ModelPart p = parts[b];
            if (p == null) continue;
            int o = b * 9;
            if (differs(p.xRot, mr, o) || differs(p.yRot, mr, o + 1) || differs(p.zRot, mr, o + 2) || differs(p.x, mr, o + 3)
                    || differs(p.y, mr, o + 4) || differs(p.z, mr, o + 5) || differs(p.xScale, mr, o + 6) || differs(p.yScale, mr, o + 7)
                    || differs(p.zScale, mr, o + 8)) return true;
        }
        return false;
    }

    private static boolean differs(float now, ModelRig mr, int o) {
        float w = mr.written[o];
        return w != mr.replaced[o] && Math.abs(now - w) > 1e-4f;
    }

    private static void rewrite(ModelRig mr) {
        ModelPart[] parts = mr.parts;
        for (int b = 2; b < parts.length; b++) {
            ModelPart p = parts[b];
            if (p == null) continue;
            int o = b * 9;
            p.xRot = mr.written[o];
            p.yRot = mr.written[o + 1];
            p.zRot = mr.written[o + 2];
            p.x = mr.written[o + 3];
            p.y = mr.written[o + 4];
            p.z = mr.written[o + 5];
            p.xScale = mr.written[o + 6];
            p.yScale = mr.written[o + 7];
            p.zScale = mr.written[o + 8];
        }
    }

    /** One finding per line, worst first. Empty when nothing is wrong. */
    public static List<String> problems() {
        roll();
        List<String> out = new ArrayList<>();
        MWConfig.Client cfg = MWConfig.CLIENT;
        if (!cfg.enabled.get()) out.add("Animation is switched off: set animation.enabled = true in config/motionworks-client.toml");
        if (!cfg.playerAnimations.get()) out.add("Player animation is switched off (animation.playerAnimations)");
        if (!cfg.mobAnimations.get()) out.add("Mob animation is switched off (animation.mobAnimations)");
        if (cfg.intensity.get() < 0.05) out.add("animation.intensity is " + cfg.intensity.get() + ": poses are blended back to vanilla");
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null) {
            EntityRenderer<?> r = mc.getEntityRenderDispatcher().getRenderer(mc.player);
            if (!(r instanceof LivingEntityRenderer<?, ?>)) {
                out.add("Your player is drawn by " + r.getClass().getName() + " (" + owner(r.getClass()) + "), not Minecraft's living-entity renderer,"
                        + " so no animation mod that hooks it can pose you");
            }
        }
        for (Map.Entry<EntityType<?>, Counts> e : snapshot().entrySet()) {
            Counts c = e.getValue();
            String name = String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(e.getKey()));
            if (c.seen >= 10 && c.cancelled * 2 >= c.seen) {
                out.add(name + ": another mod cancels its normal rendering (" + pct(c.cancelled, c.seen) + " of frames) and draws it itself" + suspects());
            } else if (c.seen - c.cancelled >= 10 && c.hooked * 2 < c.seen - c.cancelled) {
                out.add(name + ": the render hook ran on " + pct(c.hooked, c.seen - c.cancelled) + " of frames; another mod replaces "
                        + "Minecraft's entity rendering code" + suspects());
            }
            if (c.posed >= 10 && c.changedDuring * 2 >= c.posed) {
                out.add(name + ": another mod re-poses its model while drawing it (" + pct(c.changedDuring, c.posed)
                        + " of frames), which hides MotionWorks' pose" + suspects());
            }
            if (c.hooked >= 10 && c.skips[Skip.NO_BONES.ordinal()] * 2 >= c.hooked) {
                out.add(name + ": its model has no parts MotionWorks can find (a mod replaced the model)" + suspects());
            }
            if (c.hooked >= 10 && c.skips[Skip.ERROR.ordinal()] > 0) out.add(name + ": animation failed with an error (see latest.log)");
        }
        return out;
    }

    /** Full report for /mw doctor: per-type counts over the last window, then the findings. */
    public static List<String> report() {
        List<String> lines = new ArrayList<>();
        Map<EntityType<?>, Counts> snap = snapshot();
        Counts total = new Counts();
        for (Counts c : snap.values()) total.add(c);
        lines.add("Last " + (WINDOW_MS / 1000) + " s: " + snap.size() + " entity types drawn, " + total.seen + " renders, " + total.cancelled
                + " cancelled by other mods, " + total.hooked + " reached the MotionWorks hook, " + total.posed + " posed");
        snap.entrySet().stream().sorted((a, b) -> Integer.compare(b.getValue().seen, a.getValue().seen)).limit(12).forEach(e -> {
            Counts c = e.getValue();
            StringBuilder s = new StringBuilder(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(e.getKey())));
            s.append(": drawn ").append(c.seen).append(", hooked ").append(c.hooked).append(", posed ").append(c.posed);
            if (c.cancelled > 0) s.append(", cancelled ").append(c.cancelled);
            if (c.changedBefore > 0) s.append(", re-posed by another mod before drawing ").append(c.changedBefore);
            if (c.changedDuring > 0) s.append(", while drawing ").append(c.changedDuring);
            if (c.parts > 0) s.append(", bones ").append(c.bones).append('/').append(c.parts);
            BodyPlans.Resolved plan = BodyPlans.forType(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(e.getKey())));
            if (plan != null) s.append(", ").append(plan.describe());
            for (Skip k : Skip.values()) {
                int n = c.skips[k.ordinal()];
                if (n > 0) s.append(", ").append(k.name().toLowerCase(java.util.Locale.ROOT)).append(' ').append(n);
            }
            lines.add(s.toString());
        });
        List<String> known = knownMods();
        if (!known.isEmpty()) lines.add("Installed mods that also change entity animation: " + String.join(", ", known));
        List<String> p = problems();
        if (p.isEmpty()) lines.add("No problems found: third-person animation is reaching the models.");
        else lines.addAll(p);
        return lines;
    }

    private static Map<EntityType<?>, Counts> snapshot() {
        return windows > 0 ? last : current;
    }

    /**
     * Checks each completed window until something is wrong, then warns in chat and the log once per world. (The
     * player is only drawn in third person, so a problem with it can show up long after joining.)
     */
    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        roll();
        if (mc.player == null || windows < 2 || windows == checked) return;
        checked = windows;
        logPlans();
        if (warned) return;
        List<String> p = problems();
        if (p.isEmpty()) {
            if (!loggedHealthy) MotionWorks.LOGGER.info("MotionWorks render check: third-person hook healthy ({} entity types drawn)", last.size());
            loggedHealthy = true;
            return;
        }
        warned = true;
        for (String s : p) MotionWorks.LOGGER.warn("MotionWorks render check: {}", s);
        mc.player.displayClientMessage(Component.translatable("motionworks.doctor.warning", p.get(0)), false);
    }

    /** Logs, once per type, how each entity type without a family is being animated (mobs from other mods). */
    private static void logPlans() {
        for (Map.Entry<EntityType<?>, Counts> e : last.entrySet()) {
            String id = String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(e.getKey()));
            BodyPlans.Resolved plan = BodyPlans.forType(id);
            if (plan == null || e.getValue().seen == 0 || !loggedPlans.add(id)) continue;
            MotionWorks.LOGGER.info("MotionWorks body plan: {}: {}, posed {} of {} frames", id, plan.describe(), e.getValue().posed, e.getValue().seen);
        }
    }

    private static final java.util.Set<String> loggedPlans = new java.util.HashSet<>();
    private static int checked;
    private static boolean loggedHealthy;

    private static String pct(int a, int b) {
        return b <= 0 ? "0%" : Math.round(100f * a / b) + "%";
    }

    /** Mods known to draw or pose entities themselves, by mod id, with what each one does. */
    static final Map<String, String> KNOWN = Map.ofEntries(
            Map.entry("epicfight", "Epic Fight (draws players and many mobs with its own skeleton)"),
            Map.entry("entity_model_features", "Entity Model Features (animates custom entity models, e.g. Fresh Animations)"),
            Map.entry("optifine", "OptiFine (custom entity models)"),
            Map.entry("notenoughanimations", "Not Enough Animations"),
            Map.entry("playeranimator", "playerAnimator (Better Combat, Emotecraft)"),
            Map.entry("bettercombat", "Better Combat"),
            Map.entry("emotecraft", "Emotecraft"),
            Map.entry("firstperson", "First-person Model"),
            Map.entry("figura", "Figura (player avatars)"),
            Map.entry("cpm", "Customizable Player Models"),
            Map.entry("yes_steve_model", "Yes Steve Model"),
            Map.entry("geckolib", "GeckoLib (only its own entities)"),
            Map.entry("azurelib", "AzureLib (only its own entities)"));

    static List<String> knownMods() {
        List<String> out = new ArrayList<>();
        ModList mods = ModList.get();
        if (mods == null) return out;
        for (Map.Entry<String, String> e : KNOWN.entrySet()) if (mods.isLoaded(e.getKey())) out.add(e.getValue());
        out.sort(String::compareTo);
        return out;
    }

    /** What a player can do about a mod that takes over rendering, where there is a setting for it. */
    static final Map<String, String> REMEDIES = Map.of(
            "epicfight", "Epic Fight draws you with its own skeleton unless its 'Player Vanilla Model' option is ON and you are in Mining mode"
                    + " (its Toggle Battle/Mining Mode key); the mobs it gives combat animations to are always drawn by Epic Fight",
            "entity_model_features", "Entity Model Features animates mobs that a resource pack (such as Fresh Animations) gives custom models;"
                    + " disable that pack, or its models for the mobs you want MotionWorks to animate");

    private static String suspects() {
        List<String> k = knownMods();
        k.removeIf(s -> s.contains("only its own"));
        if (k.isEmpty()) return "";
        StringBuilder sb = new StringBuilder(" (installed and known to do this: ").append(String.join(", ", k)).append(')');
        ModList mods = ModList.get();
        if (mods != null) REMEDIES.forEach((id, fix) -> {
            if (mods.isLoaded(id)) sb.append(". ").append(fix);
        });
        return sb.toString();
    }

    /** The mod a class comes from, from its module or jar name. */
    static String owner(Class<?> c) {
        Module m = c.getModule();
        if (m != null && m.isNamed()) return m.getName();
        try {
            var src = c.getProtectionDomain().getCodeSource();
            if (src != null && src.getLocation() != null) {
                String path = src.getLocation().getPath();
                return path.substring(path.lastIndexOf('/') + 1);
            }
        } catch (SecurityException ignored) {
            // fall through
        }
        return "unknown mod";
    }
}
