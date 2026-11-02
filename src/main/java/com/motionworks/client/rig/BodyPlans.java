package com.motionworks.client.rig;

import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.engine.io.BodyPlanTable;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HorseModel;
import net.minecraft.client.model.IllagerModel;
import net.minecraft.client.model.VillagerModel;
import net.minecraft.world.entity.FlyingMob;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobType;
import net.minecraft.world.entity.animal.AbstractFish;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.FlyingAnimal;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.AbstractSkeleton;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.piglin.AbstractPiglin;
import net.minecraft.world.entity.npc.AbstractVillager;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Animates entity types MotionWorks has no family for, such as mobs from other mods: measures the model's body shape
 * from its part names and the entity's traits from its class, picks a plan from {@code body_plans.json}, and
 * borrows that vanilla family's clips. The borrowed rig profile is fitted to the model's proportions: the torso
 * pivots at the model's own hips and the body pivots are measured, not the vanilla ones.
 */
public final class BodyPlans {
    public record Resolved(String typeId, String shape, List<String> traits, String like, AnimationLibrary.EntityFamily family, RigProfile profile) {
        public String describe() {
            return "body plan " + shape + (traits.isEmpty() ? "" : " " + traits) + ", " + (like == null ? "keeps vanilla animation" : "animated like " + like);
        }
    }

    private static final Map<EntityModel<?>, Map<String, Resolved>> CACHE = new IdentityHashMap<>();
    private static final Map<String, Resolved> BY_TYPE = new LinkedHashMap<>();
    private static int generation = -1;

    private BodyPlans() {}

    /** The plan for an entity type without a family, rendered with this model. Cached per model and type. */
    public static synchronized Resolved resolve(LivingEntity entity, String typeId, EntityModel<?> model) {
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        if (generation != lib.generation()) {
            CACHE.clear();
            BY_TYPE.clear();
            generation = lib.generation();
        }
        Resolved r = CACHE.computeIfAbsent(model, m -> new LinkedHashMap<>()).computeIfAbsent(typeId, t -> build(entity, t, model));
        BY_TYPE.put(typeId, r);
        return r;
    }

    /** What was decided for an entity type in this session, or null if it has a family or was never drawn. */
    public static synchronized Resolved forType(String typeId) {
        return BY_TYPE.get(typeId);
    }

    private static Resolved build(LivingEntity entity, String typeId, EntityModel<?> model) {
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        ModelRig probe = RigFactory.get(model, lib.rig("generic"));
        Set<String> parts = partNames(probe);
        String shape = shapeOf(entity, model, parts);
        List<String> traits = traits(entity);
        BodyPlanTable table = lib.bodyPlans();
        BodyPlanTable.Plan plan = table.excluded().contains(typeId) ? null : table.match(shape, traits);
        String like = plan == null ? null : plan.like();
        AnimationLibrary.EntityFamily borrowed = like == null ? null : lib.family(like);
        if (borrowed == null) {
            // Nothing to borrow: the generic rig with only this type's own clips (a pack may still add some).
            return new Resolved(typeId, shape, traits, null, new AnimationLibrary.EntityFamily("generic", List.of(typeId)), lib.rig("generic"));
        }
        List<String> targets = new ArrayList<>();
        targets.add(typeId);
        for (String t : borrowed.targets()) if (!targets.contains(t)) targets.add(t);
        RigProfile profile = lib.rig(borrowed.rig()).fittedTo(hip(probe));
        return new Resolved(typeId, shape, traits, like, new AnimationLibrary.EntityFamily(borrowed.rig(), List.copyOf(targets)), profile);
    }

    static Set<String> partNames(ModelRig rig) {
        Set<String> names = new LinkedHashSet<>();
        for (int i = 2; i < rig.parts.length; i++) if (rig.parts[i] != null) names.add(rig.rig.bone(i));
        return names;
    }

    public static String shapeOf(LivingEntity e, EntityModel<?> model, Set<String> parts) {
        boolean horse = e instanceof AbstractHorse || model instanceof HorseModel<?>;
        boolean illager = e instanceof AbstractIllager || model instanceof IllagerModel<?>;
        boolean villager = e instanceof AbstractVillager || model instanceof VillagerModel<?>;
        return BodyPlanTable.shapeOf(parts, horse, illager, villager, e instanceof WaterAnimal);
    }

    public static List<String> traits(LivingEntity e) {
        List<String> t = new ArrayList<>();
        if (e.getMobType() == MobType.UNDEAD) t.add("undead");
        if (e.getMobType() == MobType.ARTHROPOD) t.add("arthropod");
        if (e instanceof AbstractSkeleton) t.add("skeleton");
        if (e instanceof AbstractPiglin) t.add("piglin");
        if (e instanceof AbstractIllager) t.add("illager");
        if (e instanceof AbstractVillager) t.add("villager");
        if (e instanceof AbstractHorse) t.add("horse");
        if (e instanceof Enemy) t.add("hostile");
        if (e instanceof Animal) t.add("animal");
        if (e instanceof AbstractFish) t.add("fish");
        if (e instanceof WaterAnimal) t.add("water");
        if (e instanceof FlyingMob) t.add("flying_mob");
        if (e instanceof FlyingAnimal) t.add("flying_animal");
        return t;
    }

    /** Where the legs join the body (the legs' own pivots), or null for a model without left and right legs. */
    static float[] hip(ModelRig rig) {
        int r = rig.rig.indexOf("right_leg"), l = rig.rig.indexOf("left_leg");
        if (r < 2 || l < 2 || rig.parts[r] == null || rig.parts[l] == null) return null;
        float[] rest = rig.rest;
        return new float[] {(rest[r * 9 + 3] + rest[l * 9 + 3]) / 2f, (rest[r * 9 + 4] + rest[l * 9 + 4]) / 2f, (rest[r * 9 + 5] + rest[l * 9 + 5]) / 2f};
    }
}
