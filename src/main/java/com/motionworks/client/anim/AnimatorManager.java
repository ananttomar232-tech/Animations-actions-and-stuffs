package com.motionworks.client.anim;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.MotionWorks;
import com.motionworks.client.rig.ModelRig;
import com.motionworks.client.rig.PoseApplier;
import com.motionworks.client.rig.RigFactory;
import com.motionworks.config.MWConfig;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Owns every {@link EntityAnimator} on the client and connects them to ticking and rendering. */
public final class AnimatorManager {
    private static final Int2ObjectMap<EntityAnimator> ANIMATORS = new Int2ObjectOpenHashMap<>();
    private static ClientLevel level;
    private static boolean warned;
    private static float globalTimeScale = 1f;

    private AnimatorManager() {}

    public static EntityAnimator get(LivingEntity e) {
        EntityAnimator a = ANIMATORS.get(e.getId());
        if (a == null || a.entity != e) {
            a = new EntityAnimator(e);
            ANIMATORS.put(e.getId(), a);
        }
        return a;
    }

    /** Slow-motion presentation: scales every controller's clock (cinematics). */
    public static void setGlobalTimeScale(float s) {
        globalTimeScale = Math.max(0f, s);
    }

    public static float globalTimeScale() {
        return globalTimeScale;
    }

    public static EntityAnimator find(int entityId) {
        return ANIMATORS.get(entityId);
    }

    public static void forEach(Consumer<EntityAnimator> c) {
        ANIMATORS.values().forEach(c);
    }

    public static int count() {
        return ANIMATORS.size();
    }

    public static void clear() {
        ANIMATORS.clear();
        level = null;
    }

    public static void clientTick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            if (!ANIMATORS.isEmpty()) clear();
            return;
        }
        if (mc.level != level) {
            ANIMATORS.clear();
            level = mc.level;
        }
        if (mc.isPaused() || !MWConfig.CLIENT.enabled.get()) return;
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        double range = MWConfig.CLIENT.animationDistance.get();
        double rangeSq = range * range;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (!(e instanceof LivingEntity le)) continue;
            if (e.position().distanceToSqr(cam) > rangeSq && e != mc.player) continue;
            try {
                get(le).tick();
            } catch (RuntimeException ex) {
                if (!warned) {
                    warned = true;
                    MotionWorks.LOGGER.error("MotionWorks animator tick failed for {}", e, ex);
                }
            }
        }
        ANIMATORS.values().removeIf(a -> a.entity.isRemoved() && !a.entity.isDeadOrDying() || a.entity.level() != mc.level);
    }

    /**
     * Called right after vanilla setupAnim. Advances the entity's controller to the synced clock
     * and writes the pose onto the model and the pose stack.
     */
    public static void apply(LivingEntity entity, EntityModel<?> model, float partialTicks, PoseStack stack) {
        // The model is shared by every entity of this type: clear what the previous render wrote first.
        RigFactory.restore(model);
        if (!MWConfig.CLIENT.enabled.get() || entity.level() == null) return;
        Minecraft mc = Minecraft.getInstance();
        if (!MWConfig.CLIENT.playerAnimations.get() && entity instanceof net.minecraft.world.entity.player.Player) return;
        if (!MWConfig.CLIENT.mobAnimations.get() && !(entity instanceof net.minecraft.world.entity.player.Player)) return;
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        double range = MWConfig.CLIENT.animationDistance.get();
        if (entity.position().distanceToSqr(cam) > range * range) return;
        EntityAnimator a = ANIMATORS.get(entity.getId());
        if (a == null || a.entity != entity) return;
        try {
            if (!a.bind(model)) return;
            double clock = (entity.level().getGameTime() + partialTicks) / 20.0;
            a.sampleFrame(partialTicks);
            if (!a.advanceTo(clock)) return;
            ModelRig mr = a.modelRig();
            float strength = MWConfig.CLIENT.intensity.get().floatValue();
            PoseApplier.apply(mr, a.controller().pose(), strength);
            PoseApplier.applyRoot(mr, a.controller().pose(), stack, strength);
        } catch (RuntimeException ex) {
            if (!warned) {
                warned = true;
                MotionWorks.LOGGER.error("MotionWorks failed to animate {} with model {}", entity, model.getClass().getName(), ex);
            }
        }
    }

    /**
     * Fires a positional event on every live animator within range. dir is the source's yaw relative to each body,
     * the argument is "near" (under 16 blocks) or "far", so clips can listen to e.g. "thunderclap:near".
     */
    public static void fireNear(Vec3 at, double range, String event) {
        for (EntityAnimator a : ANIMATORS.values()) {
            LivingEntity e = a.entity;
            if (e.isRemoved() || e.position().distanceToSqr(at) > range * range) continue;
            float dir = com.motionworks.common.InteractionClassifier.relativeYaw(e, at.x, at.z);
            String proximity = e.position().distanceToSqr(at) < 16 * 16 ? "near" : "far";
            a.fire(event, proximity, dir, (float) (at.y - e.getEyeY()));
        }
    }

    public static void fire(int entityId, String event, String arg, float dir) {
        fire(entityId, event, arg, dir, 0f);
    }

    public static void fire(int entityId, String event, String arg, float dir, float height) {
        EntityAnimator a = ANIMATORS.get(entityId);
        if (a == null) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.level == null) return;
            Entity e = mc.level.getEntity(entityId);
            if (!(e instanceof LivingEntity le)) return;
            a = get(le);
        }
        a.fire(event, arg, dir, height);
    }
}
