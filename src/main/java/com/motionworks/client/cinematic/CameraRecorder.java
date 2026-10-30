package com.motionworks.client.cinematic;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.world.phys.Vec3;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Machinima tool: capture camera keyframes while flying around, preview them as a spline shot
 * and save them as a reusable sequence (config/motionworks/cinematics/&lt;name&gt;.json).
 */
public final class CameraRecorder {
    private record Key(Vec3 pos, Vec3 look, float duration) {}

    private static final List<Key> KEYS = new ArrayList<>();

    private CameraRecorder() {}

    public static int add(float duration) {
        Camera cam = Minecraft.getInstance().gameRenderer.getMainCamera();
        Vec3 look = cam.getPosition().add(new Vec3(cam.getLookVector()).scale(8));
        KEYS.add(new Key(cam.getPosition(), look, duration));
        return KEYS.size();
    }

    public static void clear() {
        KEYS.clear();
    }

    public static int size() {
        return KEYS.size();
    }

    public static JsonObject toJson(String name) {
        JsonObject root = new JsonObject();
        root.addProperty("name", name);
        root.addProperty("anchor", "@self");
        root.addProperty("absolute", true);
        JsonArray shots = new JsonArray();
        JsonObject shot = new JsonObject();
        shot.addProperty("type", "spline");
        float total = 0f;
        for (int i = 1; i < KEYS.size(); i++) total += KEYS.get(i).duration;
        shot.addProperty("duration", Math.max(1f, total));
        shot.addProperty("ease", "in_out_sine");
        Minecraft mc = Minecraft.getInstance();
        Vec3 origin = mc.player.position();
        float yaw = mc.player.yBodyRot;
        JsonArray pts = new JsonArray();
        JsonArray looks = new JsonArray();
        for (Key k : KEYS) {
            pts.add(local(k.pos.subtract(origin), yaw));
            looks.add(local(k.look.subtract(origin), yaw));
        }
        shot.add("points", pts);
        shot.add("look_points", looks);
        shots.add(shot);
        root.add("shots", shots);
        return root;
    }

    /** Inverse of SequenceContext.local: world offset to [right, up, forward]. */
    private static JsonArray local(Vec3 d, float yawDeg) {
        double r = Math.toRadians(yawDeg);
        double fx = -Math.sin(r), fz = Math.cos(r);
        double rx = -Math.cos(r), rz = -Math.sin(r);
        JsonArray a = new JsonArray();
        a.add(Math.round((d.x * rx + d.z * rz) * 100) / 100.0);
        a.add(Math.round(d.y * 100) / 100.0);
        a.add(Math.round((d.x * fx + d.z * fz) * 100) / 100.0);
        return a;
    }

    public static boolean preview() {
        if (KEYS.size() < 2) return false;
        return CinematicDirector.INSTANCE.play(Sequence.parse("recorder:preview", toJson("preview")), Minecraft.getInstance().player);
    }

    public static Path save(String name) throws IOException {
        Path dir = CinematicDirector.userDir();
        Files.createDirectories(dir);
        Path file = dir.resolve(name.replaceAll("[^a-zA-Z0-9_\\-]", "_") + ".json");
        Files.writeString(file, new GsonBuilder().setPrettyPrinting().create().toJson(toJson(name)));
        CinematicDirector.INSTANCE.loadUserSequences();
        return file;
    }
}
