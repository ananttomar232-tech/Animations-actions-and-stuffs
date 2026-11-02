package com.motionworks.client.rig;

import com.google.gson.JsonParser;
import com.motionworks.engine.io.BodyPlanTable;
import com.motionworks.engine.runtime.PoseBuffer;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Rigs for models MotionWorks was not written for, and detecting other mods that change its poses. */
class AdaptiveRigTest {
    /** A humanoid from "another mod": short legs (hips 8 px below the neck instead of 12) and a long torso. */
    static ModelRig shortLeggedHumanoid(RigProfile profile) {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("head", CubeListBuilder.create().addBox(-4f, -8f, -4f, 8f, 8f, 8f), PartPose.ZERO);
        root.addOrReplaceChild("body", CubeListBuilder.create().addBox(-4f, 0f, -2f, 8f, 8f, 4f), PartPose.ZERO);
        root.addOrReplaceChild("right_arm", CubeListBuilder.create().addBox(-3f, -2f, -2f, 4f, 10f, 4f), PartPose.offset(-5f, 2f, 0f));
        root.addOrReplaceChild("left_arm", CubeListBuilder.create().addBox(-1f, -2f, -2f, 4f, 10f, 4f), PartPose.offset(5f, 2f, 0f));
        root.addOrReplaceChild("right_leg", CubeListBuilder.create().addBox(-2f, 0f, -2f, 4f, 16f, 4f), PartPose.offset(-2f, 8f, 0f));
        root.addOrReplaceChild("left_leg", CubeListBuilder.create().addBox(-2f, 0f, -2f, 4f, 16f, 4f), PartPose.offset(2f, 8f, 0f));
        ModelPart baked = LayerDefinition.create(mesh, 64, 64).bakeRoot();
        ModelPartIndex.index(new ModelLayerLocation(new ResourceLocation("othermod", "golem"), "main"), baked);
        HierarchicalModel<Entity> model = new HierarchicalModel<>() {
            @Override
            public ModelPart root() {
                return baked;
            }

            @Override
            public void setupAnim(Entity e, float a, float b, float c, float d, float f) {}
        };
        return RigFactory.build(model, profile);
    }

    static RigProfile profile(String id) throws IOException {
        try (Reader r = Files.newBufferedReader(Path.of("src/main/resources/assets/motionworks/motionworks/rigs/" + id + ".json"))) {
            return RigProfile.parse(id, JsonParser.parseReader(r).getAsJsonObject(), new HashMap<>());
        }
    }

    @Test
    void anotherModsHumanoidIsClassifiedAndItsHipsAreFound() throws IOException {
        ModelRig probe = shortLeggedHumanoid(new RigProfile("generic"));
        Set<String> parts = BodyPlans.partNames(probe);
        assertEquals("humanoid", BodyPlanTable.shapeOf(parts, false, false, false, false));
        assertArrayEquals(new float[] {0f, 8f, 0f}, BodyPlans.hip(probe), 1e-5f);
        assertArrayEquals(new float[] {0f, 12f, 0f}, BodyPlans.hip(PlayerRigPoseTest.playerRig()), 0.01f, "vanilla hips are where the player rig pivots");
    }

    @Test
    void aFittedRigTurnsTheTorsoAboutTheModelsOwnHips() throws IOException {
        RigProfile player = profile("player");
        assertArrayEquals(new float[] {0f, 12f, 0f}, player.couplings.get(0).pivot(), "vanilla proportions");
        RigProfile fitted = player.fittedTo(new float[] {0f, 8f, 0f});
        assertArrayEquals(new float[] {0f, 8f, 0f}, fitted.couplings.get(0).pivot());
        assertNull(fitted.center, "the body centre is measured on the model");
        assertNull(fitted.ground);
        assertArrayEquals(new float[] {0f, 12f, 0f}, player.couplings.get(0).pivot(), "fitting does not change the shared profile");

        ModelRig mr = shortLeggedHumanoid(fitted);
        assertEquals(24f, mr.ground[1], 0.01f, "measured ground is under the 16 px legs");
        int body = mr.rig.indexOf("body"), head = mr.rig.indexOf("head");
        float restDistance = distance(mr.parts[head], 0f, 8f, 0f);
        PoseBuffer bend = new PoseBuffer(mr.rig.size());
        bend.reset();
        bend.blendOverride(body, 0, (float) Math.toRadians(60), 0f, 0f, 1f);
        PoseApplier.apply(mr, bend, 1f);
        assertTrue(Math.abs(mr.parts[head].z) > 3f, "bending forward carries the head forward: z " + mr.parts[head].z);
        assertEquals(restDistance, distance(mr.parts[head], 0f, 8f, 0f), 0.01f, "the head swings rigidly about the model's hips");
    }

    @Test
    void anotherModChangingThePoseIsDetectedButItsOwnChannelsAreNot() throws IOException {
        ModelRig mr = PlayerRigPoseTest.playerRig();
        PlayerRigPoseTest.vanillaFrame(mr);
        int arm = mr.rig.indexOf("right_arm");
        PoseBuffer raise = new PoseBuffer(mr.rig.size());
        raise.reset();
        raise.blendOverride(arm, 0, (float) Math.toRadians(-120), 0f, 0f, 1f);
        PoseApplier.apply(mr, raise, 1f);
        assertFalse(RenderHealth.changed(mr), "nothing else has touched the model");

        ModelPart leg = mr.parts[mr.rig.indexOf("left_leg")];
        leg.xRot += 0.4f;
        assertFalse(RenderHealth.changed(mr), "a channel MotionWorks left alone belongs to whoever sets it");

        mr.parts[arm].xRot = 0f;
        assertTrue(RenderHealth.changed(mr), "another mod put the raised arm back down");
    }

    private static float distance(ModelPart p, float x, float y, float z) {
        float dx = p.x - x, dy = p.y - y, dz = p.z - z;
        return (float) Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
}
