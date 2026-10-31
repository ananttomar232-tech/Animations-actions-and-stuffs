package com.motionworks.client.rig;

import com.google.gson.JsonParser;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.io.ClipJsonLoader;
import com.motionworks.engine.runtime.PoseBuffer;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

/**
 * Poses the real vanilla player model with every shipped player clip and checks that the limbs stay
 * attached to the torso: shoulders, neck and hips must sit where the torso's own transform puts them.
 */
class PlayerRigPoseTest {
    private static final Path ANIMATIONS = Path.of("src/main/resources/assets/motionworks/motionworks/animations");
    private static final Set<String> PLAYER_TARGETS = Set.of("@player", "@humanoid", "@living");

    record Joint(String part, float x, float y, float z) {}

    /** Rest-pose joint locations in the torso's frame (the torso pivot is the neck, y grows downward). */
    private static final List<Joint> JOINTS = List.of(new Joint("head", 0, 0, 0), new Joint("right_arm", -5, 2, 0), new Joint("left_arm", 5, 2, 0),
            new Joint("right_leg", -1.9f, 12, 0), new Joint("left_leg", 1.9f, 12, 0));

    static ModelRig playerRig() throws IOException {
        ModelPart root = LayerDefinition.create(PlayerModel.createMesh(CubeDeformation.NONE, false), 64, 64).bakeRoot();
        ModelPartIndex.index(new ModelLayerLocation(new ResourceLocation("minecraft", "player"), "main"), root);
        PlayerModel<?> model = new PlayerModel<>(root, false);
        try (Reader r = Files.newBufferedReader(Path.of("src/main/resources/assets/motionworks/motionworks/rigs/player.json"))) {
            return RigFactory.build(model, RigProfile.parse("player", JsonParser.parseReader(r).getAsJsonObject(), new HashMap<>()));
        }
    }

    static List<AnimationClip> playerClips() throws IOException {
        List<AnimationClip> out = new ArrayList<>();
        try (Stream<Path> files = Files.walk(ANIMATIONS)) {
            for (Path f : (Iterable<Path>) files.filter(x -> x.toString().endsWith(".json"))::iterator) {
                try (Reader r = Files.newBufferedReader(f)) {
                    for (AnimationClip c : ClipJsonLoader.load(r, f.toString())) if (PLAYER_TARGETS.contains(c.target())) out.add(c);
                }
            }
        }
        return out;
    }

    /** Largest distance in model pixels between a limb's pivot and the point on the torso it belongs to. */
    static float detachment(ModelRig mr) {
        ModelPart body = mr.part("body");
        Matrix4f m = new Matrix4f().translate(body.x, body.y, body.z).rotateZYX(body.zRot, body.yRot, body.xRot);
        float worst = 0;
        for (Joint j : JOINTS) {
            ModelPart p = mr.part(j.part());
            Vector3f expected = m.transformPosition(new Vector3f(j.x(), j.y(), j.z()));
            worst = Math.max(worst, expected.distance(p.x, p.y, p.z));
        }
        return worst;
    }

    /** One clip at full weight, sampled the way AnimationLayer does. */
    static PoseBuffer sample(ModelRig mr, AnimationClip clip, float t, Scope scope) {
        PoseBuffer pose = new PoseBuffer(mr.rig.size());
        pose.reset();
        float[] v = new float[3];
        for (BoneTrack track : clip.tracks()) {
            int bone = mr.rig.indexOf(track.bone());
            if (bone < 0) continue;
            for (ChannelTarget target : ChannelTarget.values()) {
                Channel ch = track.channel(target);
                if (ch == null) continue;
                ch.sample(t, scope, v, 0);
                float k = target == ChannelTarget.ROTATION ? MathUtil.DEG_TO_RAD : 1f;
                if (clip.additive()) {
                    float base = target == ChannelTarget.SCALE ? 1f : 0f;
                    pose.addAdditive(bone, target.group(), (v[0] - base) * k, (v[1] - base) * k, (v[2] - base) * k);
                } else {
                    pose.blendOverride(bone, target.group(), v[0] * k, v[1] * k, v[2] * k, 1f);
                }
            }
        }
        return pose;
    }

    /**
     * What vanilla's setupAnim does each frame for a standing player, limited to exactly the fields it
     * writes (read from HumanoidModel's bytecode): it never touches head/body x, z and zRot, leg x or any
     * scale, so whatever MotionWorks wrote there last frame is still present. PlayerModel then copies the
     * outer layers from their limbs.
     */
    static void vanillaFrame(ModelRig mr) {
        ModelPart head = mr.part("head"), body = mr.part("body");
        head.xRot = head.yRot = 0;
        head.y = 0;
        body.xRot = body.yRot = 0;
        body.y = 0;
        for (String side : new String[] {"right", "left"}) {
            float s = side.equals("right") ? -1 : 1;
            ModelPart arm = mr.part(side + "_arm"), leg = mr.part(side + "_leg");
            arm.x = 5 * s;
            arm.y = 2;
            arm.z = 0;
            arm.xRot = arm.yRot = arm.zRot = 0;
            leg.y = 12;
            leg.z = 0;
            leg.xRot = leg.yRot = leg.zRot = 0;
            mr.part(side + "_sleeve").copyFrom(arm);
            mr.part(side + "_pants").copyFrom(leg);
        }
        mr.part("hat").copyFrom(head);
        mr.part("jacket").copyFrom(body);
    }

    private static AnimationClip clip(List<AnimationClip> clips, String id) {
        return clips.stream().filter(c -> c.id().equals(id)).findFirst().orElseThrow();
    }

    @Test
    void eulerExtractionInvertsModelPartRotationOrder() {
        java.util.Random r = new java.util.Random(7);
        org.joml.Vector3f e = new org.joml.Vector3f();
        for (int i = 0; i < 200_000; i++) {
            float ex = (r.nextFloat() - 0.5f) * 7f, ey = (r.nextFloat() - 0.5f) * 7f, ez = (r.nextFloat() - 0.5f) * 7f;
            org.joml.Quaternionf q = new org.joml.Quaternionf().rotationZYX(ez, ey, ex);
            PoseApplier.eulerZYX(q, e);
            float dot = Math.abs(new org.joml.Quaternionf().rotationZYX(e.z, e.y, e.x).dot(q));
            assertTrue(dot > 0.9999f, "round trip failed for " + ex + "," + ey + "," + ez + ": " + dot);
        }
    }

    /** Regression: the head hung down into the chest when its turn and the torso's added up to 90 degrees. */
    @Test
    void turningTheTorsoCarriesTheHeadWithoutRollingIt() throws IOException {
        ModelRig mr = playerRig();
        AnimationClip c = clip(playerClips(), "player.idle.look_right");
        for (float t = 0f; t <= c.length(); t += 0.05f) {
            vanillaFrame(mr);
            PoseBuffer pose = sample(mr, c, t, new Scope());
            int head = mr.rig.indexOf("head"), body = mr.rig.indexOf("body");
            org.joml.Quaternionf local = new org.joml.Quaternionf().rotationZYX(pose.resolve(head, 2, 0f, 0f), pose.resolve(head, 1, 0f, 0f), pose.resolve(head, 0, 0f, 0f));
            org.joml.Quaternionf torso = new org.joml.Quaternionf().rotationZYX(pose.resolve(body, 2, 0f, 0f), pose.resolve(body, 1, 0f, 0f), pose.resolve(body, 0, 0f, 0f));
            PoseApplier.apply(mr, pose, 1f);
            ModelPart h = mr.part("head");
            org.joml.Quaternionf actual = new org.joml.Quaternionf().rotationZYX(h.zRot, h.yRot, h.xRot);
            org.joml.Quaternionf expected = new org.joml.Quaternionf(torso).mul(local);
            assertTrue(Math.abs(actual.dot(expected)) > 0.9999f, "head orientation wrong at t=" + t);
            // The head box hangs from its neck pivot upwards (model y points down): its top must stay above the neck.
            org.joml.Vector3f top = actual.transform(new org.joml.Vector3f(0f, -8f, 0f));
            assertTrue(top.y < -6f, "head turned upside down at t=" + t + ": top at " + top.y);
        }
    }

    @Test
    void groundContactLiftsBodiesButLetsFeetSink() throws IOException {
        ModelRig mr = playerRig();
        vanillaFrame(mr);
        float ground = GroundContact.lowest(mr, null, 1f, true);
        assertEquals(24f, ground, 0.01f, "a standing player's feet are 24 model pixels below the neck");

        PoseBuffer flip = new PoseBuffer(mr.rig.size());
        flip.reset();
        flip.blendOverride(mr.rig.indexOf("mw_root"), 0, (float) Math.PI, 0f, 0f, 1f);
        PoseApplier.apply(mr, flip, 1f);
        float lift = GroundContact.lift(mr, flip, 1f, ground);
        assertTrue(lift > 20f, "upside down about the feet, the head is deep in the ground: lift " + lift);
        assertEquals(ground, GroundContact.lowest(mr, flip, 1f, false) - lift, 0.01f, "after the lift the head rests on the ground");

        vanillaFrame(mr);
        PoseBuffer kneel = new PoseBuffer(mr.rig.size());
        kneel.reset();
        kneel.blendOverride(mr.rig.indexOf("mw_root"), 1, 0f, 6f, 0f, 1f);
        kneel.blendOverride(mr.rig.indexOf("right_leg"), 0, (float) Math.toRadians(-90), 0f, 0f, 1f);
        PoseApplier.apply(mr, kneel, 1f);
        assertEquals(0f, GroundContact.lift(mr, kneel, 1f, ground), 0.01f, "a kneel sinks only the feet, which is how it reads");
    }

    /** Regression: the torso drifted away from the legs on the first client run (stale coupled positions). */
    @Test
    void poseDoesNotAccumulateAcrossFrames() throws IOException {
        ModelRig mr = playerRig();
        List<AnimationClip> clips = playerClips();
        Scope scope = new Scope();
        for (String id : List.of("emote.bow", "emote.wave")) {
            AnimationClip c = clip(clips, id);
            for (int f = 0; f <= 60 * c.length(); f++) {
                vanillaFrame(mr);
                PoseApplier.apply(mr, sample(mr, c, f / 60f, scope), 1f);
                assertTrue(detachment(mr) < 3f, id + " tears the model at frame " + f + ": " + detachment(mr) + "px");
            }
        }
        // The clip has ended: an untouched pose must leave exactly what vanilla produced.
        PoseBuffer idle = new PoseBuffer(mr.rig.size());
        idle.reset();
        for (int f = 0; f < 3; f++) {
            vanillaFrame(mr);
            PoseApplier.apply(mr, idle, 1f);
        }
        for (String name : List.of("head", "body")) {
            ModelPart p = mr.part(name);
            assertArrayEquals(new float[] {0, 0, 0, 0, 0, 0}, new float[] {p.x, p.y, p.z, p.xRot, p.yRot, p.zRot}, 1e-4f, name + " kept a stale pose");
        }
        assertTrue(detachment(mr) < 1e-3f, "limbs detached after the clip ended");
    }

    @Test
    void everyPlayerClipKeepsTheLimbsAttached() throws IOException {
        ModelRig mr = playerRig();
        List<String> offenders = new ArrayList<>();
        Scope scope = new Scope();
        List<AnimationClip> clips = playerClips();
        for (AnimationClip clip : clips) {
            float worst = 0, at = 0;
            for (int i = 0; i <= 16; i++) {
                float t = clip.length() * i / 16f;
                vanillaFrame(mr);
                PoseApplier.apply(mr, sample(mr, clip, t, scope), 1f);
                float d = detachment(mr);
                if (d > worst) {
                    worst = d;
                    at = t;
                }
            }
            // Clips may deliberately shift a shoulder or hip a little (a reach, a lunge); tearing is far larger.
            if (worst > 3f) offenders.add(String.format("%s %.1fpx at %.2fs", clip.id(), worst, at));
        }
        assertTrue(clips.size() > 1000, "player clips loaded: " + clips.size());
        assertEquals(List.of(), offenders);
    }
}
