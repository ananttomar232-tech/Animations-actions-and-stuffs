package com.motionworks.client.rig;

import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.runtime.ClipSampler;
import com.motionworks.engine.runtime.PoseBuffer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Checks the clip library against the models the game actually renders. For every entity family it takes the
 * model from the entity's real renderer, binds it exactly as rendering does, and poses every clip that family
 * plays. It reports clips that move nothing on that model (they still occupy their layer and block other
 * clips) and species clips naming bones the model lacks. For creatures that walk it also lists clips whose body
 * dips below the feet (lifted at runtime by {@link GroundContact}) and clips that lift the body off the ground,
 * for review, since jumps and hops lift on purpose.
 *
 * <p>Run with {@code /mw audit}, or automatically in a world with {@code -Dmotionworks.audit=<report file>}.
 */
public final class LibraryAudit {
    /** Model pixels a body may dip below the rest pose's lowest point before it is listed. */
    static final float SINK_LIMIT = 1f;
    static final float LIFT_REPORT = 8f;
    private static final int SAMPLES = 12;

    public record Result(int clips, int models, int issues, List<String> report) {}

    private LibraryAudit() {}

    public static Result run(Level level, Player viewer) {
        Minecraft mc = Minecraft.getInstance();
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        List<String> issues = new ArrayList<>(), lifts = new ArrayList<>(), corrected = new ArrayList<>(), notes = new ArrayList<>();
        int clipsChecked = 0, models = 0;
        for (Map.Entry<String, AnimationLibrary.EntityFamily> e : lib.families().entrySet()) {
            String id = e.getKey();
            Entity entity = id.equals("minecraft:player") ? viewer : create(level, id);
            if (!(entity instanceof LivingEntity living)) {
                notes.add("SKIP " + id + ": no living entity of this type");
                continue;
            }
            EntityRenderer<?> renderer = mc.getEntityRenderDispatcher().getRenderer(entity);
            if (!(renderer instanceof LivingEntityRenderer<?, ?> lr)) {
                notes.add("SKIP " + id + ": drawn by " + renderer.getClass().getSimpleName() + ", which has no part model");
                continue;
            }
            EntityModel<?> model = lr.getModel();
            RigProfile profile = lib.rig(e.getValue().rig());
            ModelRig mr = RigFactory.get(model, profile);
            Pose rest = Pose.capture(model, living, mr);
            models++;
            float restLowest = GroundContact.lowest(mr, null, 1f, true);
            boolean grounded = standsOnGround(living);
            Scope scope = new Scope();
            scope.setBool(com.motionworks.common.CtxVars.ON_GROUND, true);
            for (AnimationClip clip : lib.clips().forTargets(e.getValue().targets())) {
                clipsChecked++;
                coverage(clip, id, mr, issues);
                scaleDrift(clip, id, mr, issues);
                if (!grounded) continue;
                boolean free = "free".equals(clip.meta("ground", ""));
                float worstSink = 0f, worstLift = 0f, sinkAt = 0f, liftAt = 0f;
                for (int i = 0; i <= SAMPLES; i++) {
                    float t = clip.length() * i / SAMPLES;
                    rest.restore();
                    PoseBuffer pose = ClipSampler.sampleSolo(mr.rig, clip, t, scope);
                    PoseApplier.apply(mr, pose, 1f);
                    // Sinking is measured on the body alone (feet may sink); lifting on the whole model, feet included.
                    float body = GroundContact.lowest(mr, pose, 1f, false) - restLowest;
                    if (body > worstSink) {
                        worstSink = body;
                        sinkAt = t;
                    }
                    float whole = restLowest - GroundContact.lowest(mr, pose, 1f, true);
                    if (whole > worstLift) {
                        worstLift = whole;
                        liftAt = t;
                    }
                }
                // Ground contact lifts these at runtime; listed so authors can see which clips lean on it.
                if (worstSink > SINK_LIMIT) corrected.add(String.format("%s %s on %s: body %.1f px below the feet at %.2fs", free ? "FREE" : "LIFTED",
                        clip.id(), id, worstSink, sinkAt));
                if (worstLift > LIFT_REPORT) lifts.add(String.format("LIFT %s on %s: %.1f px off the ground at %.2fs", clip.id(), id, worstLift, liftAt));
            }
            rest.restore();
            PoseApplier.restore(mr);
        }
        List<String> plans = new ArrayList<>();
        clipsChecked += bodyPlans(level, issues, plans);
        List<String> report = new ArrayList<>();
        report.add(String.format("MotionWorks library audit: %d clip bindings on %d models, %d issues", clipsChecked, models, issues.size()));
        report.addAll(issues);
        report.add("-- bodies below the feet: LIFTED by ground contact at runtime, FREE where the clip goes underground on purpose:");
        report.addAll(corrected);
        report.add("-- lifts for review (jumps, hops, rears and flight lift on purpose):");
        report.addAll(lifts);
        report.add("-- entity types without a family (mobs from other mods), animated by body plan:");
        report.addAll(plans);
        report.add("-- notes:");
        report.addAll(notes);
        return new Result(clipsChecked, models, issues.size(), report);
    }

    /** Runs the audit and writes the report; returns the result, or null when there is no world to build entities in. */
    public static Result runAndWrite(java.nio.file.Path file) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return null;
        Result r = run(mc.level, mc.player);
        try {
            java.nio.file.Files.createDirectories(file.toAbsolutePath().getParent());
            java.nio.file.Files.write(file, r.report());
        } catch (java.io.IOException ex) {
            com.motionworks.MotionWorks.LOGGER.error("Could not write the library audit to {}", file, ex);
        }
        com.motionworks.MotionWorks.LOGGER.info("MotionWorks audit: {} clip bindings on {} models, {} issues, report {}", r.clips(), r.models(), r.issues(), file);
        return r;
    }

    private static boolean autoDone;

    /** With -Dmotionworks.audit=<file>, audits once, two seconds after the player is in a world. */
    public static void autoRun() {
        String target = System.getProperty("motionworks.audit");
        Minecraft mc = Minecraft.getInstance();
        if (autoDone || target == null || target.isEmpty() || mc.player == null || mc.player.tickCount < 40) return;
        autoDone = true;
        runAndWrite(java.nio.file.Path.of(target));
    }

    /** Ground contact only means something for creatures that walk: flyers and swimmers are skipped. */
    static boolean standsOnGround(Entity e) {
        return !(e instanceof net.minecraft.world.entity.FlyingMob || e instanceof net.minecraft.world.entity.animal.FlyingAnimal
                || e instanceof net.minecraft.world.entity.animal.WaterAnimal || e instanceof net.minecraft.world.entity.ambient.Bat
                || e instanceof net.minecraft.world.entity.monster.Vex || e instanceof net.minecraft.world.entity.animal.allay.Allay
                || e instanceof net.minecraft.world.entity.monster.Blaze || e instanceof net.minecraft.world.entity.boss.wither.WitherBoss
                || e instanceof net.minecraft.world.entity.monster.Guardian);
    }

    /**
     * Vanilla models whose body plan is known: the classifier must put each in its own family, or a mob from another
     * mod with the same body would be animated wrongly.
     */
    static final Map<String, String[]> EXPECTED_PLANS = Map.ofEntries(
            Map.entry("minecraft:player", new String[] {"humanoid", "minecraft:player"}),
            Map.entry("minecraft:zombie", new String[] {"humanoid", "minecraft:zombie"}),
            Map.entry("minecraft:skeleton", new String[] {"humanoid", "minecraft:skeleton"}),
            Map.entry("minecraft:piglin", new String[] {"humanoid", "minecraft:piglin"}),
            Map.entry("minecraft:villager", new String[] {"villager", "minecraft:villager"}),
            Map.entry("minecraft:vindicator", new String[] {"illager", "minecraft:vindicator"}),
            Map.entry("minecraft:horse", new String[] {"equine", "minecraft:horse"}),
            Map.entry("minecraft:cow", new String[] {"quadruped", "minecraft:cow"}),
            Map.entry("minecraft:spider", new String[] {"arthropod", "minecraft:spider"}),
            Map.entry("minecraft:cod", new String[] {"aquatic", "minecraft:cod"}),
            Map.entry("minecraft:dolphin", new String[] {"aquatic", "minecraft:dolphin"}),
            Map.entry("minecraft:phantom", new String[] {"winged", "minecraft:phantom"}),
            Map.entry("minecraft:parrot", new String[] {"winged", "minecraft:parrot"}));

    /**
     * Checks the body-plan classifier on the vanilla models above, then audits every living entity type that has no
     * family (in a modded game, the other mods' mobs): which plan it gets and how much of the borrowed clips its
     * model can play. Returns the clip bindings checked.
     */
    private static int bodyPlans(Level level, List<String> issues, List<String> plans) {
        Minecraft mc = Minecraft.getInstance();
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        int checked = 0;
        for (Map.Entry<String, String[]> e : new java.util.TreeMap<>(EXPECTED_PLANS).entrySet()) {
            LivingEntity living = living(level, e.getKey());
            EntityModel<?> model = living == null ? null : modelOf(living);
            if (model == null) {
                issues.add("PLAN " + e.getKey() + ": no model to classify");
                continue;
            }
            java.util.Set<String> parts = BodyPlans.partNames(RigFactory.get(model, lib.rig("generic")));
            String shape = BodyPlans.shapeOf(living, model, parts);
            var plan = lib.bodyPlans().match(shape, BodyPlans.traits(living));
            String like = plan == null ? null : plan.like();
            if (!shape.equals(e.getValue()[0]) || !e.getValue()[1].equals(like)) {
                issues.add("PLAN " + e.getKey() + ": classified as " + shape + " like " + like + ", expected " + e.getValue()[0] + " like "
                        + e.getValue()[1] + " (parts " + parts + ")");
            }
        }
        for (EntityType<?> type : ForgeRegistries.ENTITY_TYPES) {
            String id = String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(type));
            if (lib.family(id) != null || type == EntityType.PLAYER) continue;
            Entity entity;
            try {
                entity = type.create(level);
            } catch (RuntimeException ex) {
                // Another mod's entity may not survive being built on the client outside its own spawning code.
                plans.add("SKIP " + id + ": could not be created for the audit (" + ex + ")");
                continue;
            }
            if (!(entity instanceof LivingEntity living)) continue;
            EntityModel<?> model = modelOf(living);
            if (model == null) {
                plans.add("SKIP " + id + ": drawn by " + mc.getEntityRenderDispatcher().getRenderer(entity).getClass().getName()
                        + ", which is not a living-entity renderer, so no part model can be posed");
                continue;
            }
            BodyPlans.Resolved r = BodyPlans.resolve(living, id, model);
            ModelRig mr = RigFactory.get(model, r.profile());
            int clips = 0, bound = 0, wanted = 0;
            for (AnimationClip clip : lib.clips().forTargets(r.family().targets())) {
                clips++;
                checked++;
                for (BoneTrack t : clip.tracks()) {
                    if (t.bone().startsWith("mw_")) continue;
                    wanted++;
                    if (mr.rig.indexOf(t.bone()) >= 0) bound++;
                }
                scaleDrift(clip, id, mr, issues);
            }
            plans.add(String.format("%s: %s; %d clips, %d of %d bone tracks find a part (parts %s)", id, r.describe(), clips, bound, wanted,
                    BodyPlans.partNames(mr)));
        }
        return checked;
    }

    private static LivingEntity living(Level level, String id) {
        if (id.equals("minecraft:player")) return Minecraft.getInstance().player;
        return create(level, id) instanceof LivingEntity l ? l : null;
    }

    private static EntityModel<?> modelOf(LivingEntity e) {
        EntityRenderer<?> r = Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(e);
        return r instanceof LivingEntityRenderer<?, ?> lr ? lr.getModel() : null;
    }

    private static Entity create(Level level, String id) {
        EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(id));
        return type == null ? null : type.create(level);
    }

    /** Pixels a part's geometry may slide when it is scaled before it reads as coming apart. */
    static final float SCALE_DRIFT_LIMIT = 2f;

    /**
     * A part scales about its pivot. Some models place a part's boxes away from its pivot (a slime's body hangs
     * 17 px below its origin), so scaling slides the box away from the parts around it. A box that reaches its
     * pivot (a tongue, an arm) only stretches. Reports how far the face nearest the pivot moves.
     */
    private static void scaleDrift(AnimationClip clip, String entity, ModelRig mr, List<String> issues) {
        for (BoneTrack t : clip.tracks()) {
            if (t.scale() == null || t.bone().startsWith("mw_")) continue;
            int b = mr.rig.indexOf(t.bone());
            if (b < 2 || mr.parts[b] == null) continue;
            float[] face = nearestFace(mr.parts[b]);
            float worst = 0f;
            float[] v = new float[3], p = new float[3];
            for (int i = 0; i <= SAMPLES; i++) {
                float time = clip.length() * i / SAMPLES;
                t.scale().sample(time, new Scope(), v, 0);
                if (t.position() != null) t.position().sample(time, new Scope(), p, 0);
                // Where the nearest face lands: scaled about the pivot, then the pivot moved by any position track.
                float dx = face[0] * (v[0] - 1f) + p[0], dy = face[1] * (v[1] - 1f) + p[1], dz = face[2] * (v[2] - 1f) + p[2];
                worst = Math.max(worst, (float) Math.sqrt(dx * dx + dy * dy + dz * dz));
            }
            if (worst > SCALE_DRIFT_LIMIT) {
                issues.add(String.format("SCALE_DRIFT %s on %s: scaling %s moves its box %.1f px off its pivot", clip.id(), entity, t.bone(), worst));
            }
        }
    }

    /** Per axis, the signed position of the part's box face nearest its pivot (0 where a box reaches or spans it). */
    static float[] nearestFace(ModelPart part) {
        float[] out = new float[3];
        part.visit(new com.mojang.blaze3d.vertex.PoseStack(), (pose, path, index, cube) -> {
            if (!path.isEmpty()) return;
            float[] lo = {cube.minX, cube.minY, cube.minZ}, hi = {cube.maxX, cube.maxY, cube.maxZ};
            for (int a = 0; a < 3; a++) {
                float near = lo[a] * hi[a] <= 0f ? 0f : (Math.abs(lo[a]) < Math.abs(hi[a]) ? lo[a] : hi[a]);
                if (Math.abs(near) > Math.abs(out[a])) out[a] = near;
            }
        });
        return out;
    }

    private static void coverage(AnimationClip clip, String entity, ModelRig mr, List<String> issues) {
        List<String> missing = new ArrayList<>();
        int real = 0;
        boolean virtual = false;
        for (BoneTrack t : clip.tracks()) {
            if (t.bone().startsWith("mw_")) {
                virtual = true;
                continue;
            }
            real++;
            if (mr.rig.indexOf(t.bone()) < 0) missing.add(t.bone());
        }
        if (real > 0 && missing.size() == real && !virtual) {
            issues.add("DEAD " + clip.id() + " on " + entity + ": moves nothing on this model " + missing);
        } else if (!missing.isEmpty() && clip.target().equals(entity)) {
            issues.add("MISSING " + clip.id() + " on " + entity + ": the model has no " + missing);
        }
    }

    /** Vanilla's own standing pose for the model, captured so every sample starts from it. */
    record Pose(ModelPart[] parts, PartPose[] poses, float[] scales) {
        @SuppressWarnings({"unchecked", "rawtypes"})
        static Pose capture(EntityModel model, LivingEntity entity, ModelRig mr) {
            RigFactory.restore(model);
            model.setupAnim(entity, 0f, 0f, 0f, 0f, 0f);
            ModelPart[] parts = mr.parts;
            PartPose[] poses = new PartPose[parts.length];
            float[] scales = new float[parts.length * 3];
            for (int i = 0; i < parts.length; i++) {
                if (parts[i] == null) continue;
                poses[i] = parts[i].storePose();
                scales[i * 3] = parts[i].xScale;
                scales[i * 3 + 1] = parts[i].yScale;
                scales[i * 3 + 2] = parts[i].zScale;
            }
            return new Pose(parts, poses, scales);
        }

        void restore() {
            for (int i = 0; i < parts.length; i++) {
                if (parts[i] == null) continue;
                parts[i].loadPose(poses[i]);
                parts[i].xScale = scales[i * 3];
                parts[i].yScale = scales[i * 3 + 1];
                parts[i].zScale = scales[i * 3 + 2];
            }
        }
    }
}
