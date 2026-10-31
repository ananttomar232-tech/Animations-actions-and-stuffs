package com.motionworks.client.firstperson;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.expr.ExprParser;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.Vars;
import com.motionworks.engine.math.MathUtil;
import com.motionworks.engine.procedural.SpringBone;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.AnimationLayer;
import com.motionworks.engine.runtime.ClipPlayback;
import com.motionworks.engine.runtime.LayerSpec;
import com.motionworks.engine.runtime.PoseBuffer;
import com.motionworks.engine.runtime.Rig;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.HumanoidArm;
import org.joml.Quaternionf;

import java.util.List;
import java.util.Map;

/**
 * First-person animation: a dedicated controller over a virtual rig of the main hand, off hand,
 * the items they hold and the view. It receives exactly the same gameplay events as the local
 * player's third-person animator, with the same deterministic seed, so both views pick matching
 * variants (the same combo swing, the same draw style).
 *
 * <p>Clips are authored for the main hand on the right; left-handed players get the mirrored
 * transform automatically.
 */
public final class FirstPersonAnimator {
    public static final List<String> BONES = List.of("mw_root", "mw_center", "fp_main", "fp_off", "fp_main_item", "fp_off_item", "fp_view");
    private static final int MAIN = 2, OFF = 3, MAIN_ITEM = 4, OFF_ITEM = 5, VIEW = 6;
    private static final int LOOK_YAW = Vars.id("q.look_yaw_delta");
    private static final int LOOK_PITCH = Vars.id("q.look_pitch_delta");
    private static final int EQUIP = Vars.id("q.equip_progress");
    // Last static field: the constructor reads BONES, and statics initialise in declaration order.
    public static final FirstPersonAnimator INSTANCE = new FirstPersonAnimator();

    private final Rig rig = new Rig("first_person", BONES, null, Map.of(
            "hands", List.of("fp_main", "fp_off"), "items", List.of("fp_main_item", "fp_off_item"), "main", List.of("fp_main", "fp_main_item"),
            "off", List.of("fp_off", "fp_off_item")));
    private AnimationController controller;
    private int generation = -1;
    private long lastNanos;
    private float lastYaw, lastPitch;
    private boolean renderingFirstPersonItem;
    private final Quaternionf q = new Quaternionf();

    private FirstPersonAnimator() {}

    private AnimationController controller() {
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        if (controller == null || generation != lib.generation()) {
            LocalPlayer p = Minecraft.getInstance().player;
            long seed = p == null ? 0 : p.getUUID().getMostSignificantBits() * 31 + p.getUUID().getLeastSignificantBits();
            controller = new AnimationController(rig, seed, LayerSpec.STANDARD, lib.clips().forTargets(List.of("@first_person")));
            // Inertial weapon sway: the hands lag behind view rotation and settle with a little overshoot.
            controller.addModifier(new SpringBone(MAIN, new com.motionworks.engine.expr.Expr[] {
                    ExprParser.parse("math.clamp(q.look_pitch_delta * 0.6, -12, 12)"),
                    ExprParser.parse("math.clamp(q.look_yaw_delta * 0.5, -14, 14)"),
                    ExprParser.parse("math.clamp(q.look_yaw_delta * -0.25, -6, 6)")}, 110f, 0.6f, 15f));
            controller.addModifier(new SpringBone(OFF, new com.motionworks.engine.expr.Expr[] {
                    ExprParser.parse("math.clamp(q.look_pitch_delta * 0.6, -12, 12)"),
                    ExprParser.parse("math.clamp(q.look_yaw_delta * 0.5, -14, 14)"),
                    ExprParser.parse("math.clamp(q.look_yaw_delta * 0.25, -6, 6)")}, 110f, 0.6f, 15f));
            generation = lib.generation();
        }
        return controller;
    }

    /** Client tick: mirror the third-person context and measure view rotation speed. */
    public void tick() {
        LocalPlayer p = Minecraft.getInstance().player;
        if (p == null) return;
        AnimationController c = controller();
        EntityAnimator a = AnimatorManager.find(p.getId());
        Scope s = c.scope();
        if (a != null) {
            Scope src = a.scope();
            if (s.values.length < src.values.length) s.set(src.values.length - 1, 0f);
            System.arraycopy(src.values, 0, s.values, 0, src.values.length);
        }
        float dy = MathUtil.wrapDegrees(p.getYRot() - lastYaw);
        float dp = p.getXRot() - lastPitch;
        lastYaw = p.getYRot();
        lastPitch = p.getXRot();
        s.set(LOOK_YAW, MWConfig.CLIENT.weaponSway.get() ? dy : 0f);
        s.set(LOOK_PITCH, MWConfig.CLIENT.weaponSway.get() ? dp : 0f);
    }

    public void fire(String event, Scope thirdPerson) {
        if (!MWConfig.CLIENT.firstPerson.get()) return;
        AnimationController c = controller();
        Scope s = c.scope();
        if (s.values.length < thirdPerson.values.length) s.set(thirdPerson.values.length - 1, 0f);
        System.arraycopy(thirdPerson.values, 0, s.values, 0, thirdPerson.values.length);
        c.fire(event);
    }

    public boolean play(com.motionworks.engine.clip.AnimationClip clip) {
        return controller().play(clip, true);
    }

    /** Advances once per frame. */
    public void frame(float equipProgress) {
        long now = Util.getNanos();
        float dt = lastNanos == 0 ? 0f : (now - lastNanos) / 1e9f;
        lastNanos = now;
        AnimationController c = controller();
        c.scope().set(EQUIP, equipProgress);
        if (Minecraft.getInstance().isPaused()) dt = 0f;
        c.update(Math.min(dt, 0.1f));
    }

    /** True while an action clip that replaces vanilla's swing is playing. */
    public boolean overridesVanillaSwing() {
        if (controller == null || !MWConfig.CLIENT.firstPerson.get()) return false;
        AnimationLayer action = controller.layer("action");
        if (action == null) return false;
        ClipPlayback cur = action.current();
        return cur != null && !cur.isStopping() && "true".equals(cur.clip.meta("replaces_vanilla_swing", "false"));
    }

    /** Applies the hand bone to the pose stack before vanilla renders the arm and item. */
    public void applyHand(boolean mainHand, HumanoidArm side, PoseStack stack) {
        if (controller == null || !MWConfig.CLIENT.firstPerson.get()) return;
        apply(controller.pose(), mainHand ? MAIN : OFF, side == HumanoidArm.LEFT, stack, side == HumanoidArm.RIGHT ? 0.56f : -0.56f, -0.52f, -0.72f);
    }

    public void applyItem(boolean mainHand, HumanoidArm side, PoseStack stack) {
        if (controller == null || !MWConfig.CLIENT.firstPerson.get()) return;
        apply(controller.pose(), mainHand ? MAIN_ITEM : OFF_ITEM, side == HumanoidArm.LEFT, stack, 0f, 0f, 0f);
    }

    private void apply(PoseBuffer pose, int bone, boolean mirror, PoseStack stack, float px, float py, float pz) {
        if (!pose.isTouched(bone)) return;
        float k = MWConfig.CLIENT.firstPersonIntensity.get().floatValue();
        float rx = pose.resolve(bone, 0, 0f, 0f) * k;
        float ry = pose.resolve(bone, 1, 0f, 0f) * k;
        float rz = pose.resolve(bone, 2, 0f, 0f) * k;
        float tx = pose.resolve(bone, 3, 0f, 0f) * k / 16f;
        float ty = pose.resolve(bone, 4, 0f, 0f) * k / 16f;
        float tz = pose.resolve(bone, 5, 0f, 0f) * k / 16f;
        float s = 1f + (pose.resolve(bone, 7, 1f, 1f) - 1f) * k;
        if (mirror) {
            tx = -tx;
            ry = -ry;
            rz = -rz;
        }
        // Authored in ModelPart convention (y down); first-person space is y up.
        stack.translate(tx, -ty, tz);
        stack.translate(px, py, pz);
        stack.mulPose(q.rotationZYX(rz, ry, rx));
        if (s != 1f) stack.scale(s, s, s);
        stack.translate(-px, -py, -pz);
    }

    /** View offsets (degrees) authored on fp_view for camera bob, recoil and landing. */
    public float viewPitch() {
        return view(0);
    }

    public float viewYaw() {
        return view(1);
    }

    public float viewRoll() {
        return view(2);
    }

    private float view(int axis) {
        if (controller == null || !MWConfig.CLIENT.firstPerson.get()) return 0f;
        return controller.pose().resolve(VIEW, axis, 0f, 0f) * MathUtil.RAD_TO_DEG * MWConfig.CLIENT.firstPersonIntensity.get().floatValue();
    }

    public void setRenderingFirstPersonItem(boolean b) {
        renderingFirstPersonItem = b;
    }

    public boolean isRenderingFirstPersonItem() {
        return renderingFirstPersonItem;
    }

    public String describe() {
        return controller == null ? "" : controller.describe();
    }

    public void reset() {
        controller = null;
        generation = -1;
    }
}
