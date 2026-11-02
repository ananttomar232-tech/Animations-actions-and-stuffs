package com.motionworks.engine.io;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.Reader;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * The rules ({@code motionworks/body_plans.json}) that decide how an entity type with no entry in
 * {@code entities.json}, typically a mob from another mod, is animated. Each rule names a body shape (measured from
 * the model's own parts), optional entity traits that must all hold, and the vanilla family whose rig and clips
 * the entity borrows. Rules are tried in order and the first match wins.
 */
public final class BodyPlanTable {
    /** Body shapes measured from a model. "any" in a rule matches every shape. */
    public static final List<String> SHAPES = List.of("humanoid", "illager", "villager", "equine", "quadruped", "arthropod", "winged", "aquatic", "other");

    /** Traits measured from an entity, which rules may require. */
    public static final List<String> TRAITS = List.of("undead", "skeleton", "piglin", "illager", "villager", "horse", "hostile", "animal", "fish",
            "water", "flying_mob", "flying_animal", "arthropod");

    /** like: the entity type id of the family to borrow, or null for none (the entity keeps vanilla animation). */
    public record Plan(String shape, List<String> traits, String like, String source) {}

    private final List<Plan> plans = new ArrayList<>();
    private final Set<String> excluded = new java.util.LinkedHashSet<>();

    public List<Plan> plans() {
        return plans;
    }

    /** Entity types that keep vanilla animation whatever their shape (an armour stand is a humanoid that must not move). */
    public Set<String> excluded() {
        return excluded;
    }

    public void clear() {
        plans.clear();
        excluded.clear();
    }

    /** Adds the rules of one file, after the rules already loaded. Throws on unknown shapes or traits. */
    public void load(Reader r, String source) {
        JsonObject o = JsonParser.parseReader(r).getAsJsonObject();
        if (o.has("exclude")) for (JsonElement e : o.getAsJsonArray("exclude")) excluded.add(e.getAsString());
        for (JsonElement e : o.getAsJsonArray("plans")) {
            JsonObject p = e.getAsJsonObject();
            String shape = p.get("shape").getAsString().toLowerCase(Locale.ROOT);
            if (!shape.equals("any") && !SHAPES.contains(shape)) throw new IllegalArgumentException("unknown body shape '" + shape + "' in " + source);
            List<String> traits = new ArrayList<>();
            if (p.has("traits")) {
                for (JsonElement t : p.getAsJsonArray("traits")) {
                    String trait = t.getAsString().toLowerCase(Locale.ROOT);
                    if (!TRAITS.contains(trait)) throw new IllegalArgumentException("unknown trait '" + trait + "' in " + source);
                    traits.add(trait);
                }
            }
            String like = p.has("like") && !p.get("like").isJsonNull() ? p.get("like").getAsString() : null;
            plans.add(new Plan(shape, List.copyOf(traits), like, source));
        }
    }

    /** The first rule whose shape and traits match, or null. */
    public Plan match(String shape, Collection<String> traits) {
        Set<String> have = Set.copyOf(traits);
        for (Plan p : plans) {
            if (!p.shape().equals("any") && !p.shape().equals(shape)) continue;
            if (have.containsAll(p.traits())) return p;
        }
        return null;
    }

    /**
     * The shape of a model from its part names (the names in its layer definition, which vanilla and most mods
     * share). {@code villagerLike} and {@code illagerLike} come from the model or entity class, since villagers and
     * illagers share one part layout.
     */
    public static String shapeOf(Set<String> parts, boolean horseLike, boolean illagerLike, boolean villagerLike, boolean water) {
        int legs = 0;
        // Horses also carry four baby legs, and players pants over their legs; neither is another leg.
        for (String n : parts) if (n.contains("leg") && !n.contains("pants") && !n.contains("baby")) legs++;
        if (legs >= 6) return "arthropod";
        boolean head = parts.contains("head");
        boolean twoLegs = parts.contains("right_leg") && parts.contains("left_leg");
        // Illager models carry both folded arms and separate ones, so the class decides before the arms do.
        if (head && twoLegs && parts.contains("arms")) {
            if (illagerLike) return "illager";
            if (villagerLike) return "villager";
        }
        if (head && twoLegs && (parts.contains("arms") || parts.contains("right_arm") && parts.contains("left_arm"))) return "humanoid";
        if (parts.containsAll(List.of("right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"))) {
            return horseLike ? "equine" : "quadruped";
        }
        boolean wings = parts.stream().anyMatch(n -> n.contains("wing"));
        if (water || parts.stream().anyMatch(n -> n.contains("fin"))) return "aquatic";
        if (wings) return "winged";
        return "other";
    }
}
