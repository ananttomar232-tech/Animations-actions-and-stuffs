package com.motionworks.client.rig;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Data-driven description of how a family of models should be animated: named bone groups for
 * masks, follower parts that mirror a leader (hat follows head), virtual parent couplings that
 * give flat vanilla models a spine, the whole-body pivot and procedural secondary motion.
 */
public final class RigProfile {
    public record Coupling(String parent, float[] pivot, boolean moveParent, List<String> children) {}

    public record Spring(String bone, String[] targets, float stiffness, float damping, float limit) {}

    public record Noise(String bone, float amplitude, float frequency, String scale) {}

    public record Driver(String bone, int group, String[] exprs, float halfLife) {}

    public final String id;
    public final Map<String, List<String>> groups = new LinkedHashMap<>();
    public final Map<String, String> followers = new LinkedHashMap<>();
    public final List<Coupling> couplings = new ArrayList<>();
    public final List<Spring> springs = new ArrayList<>();
    public final List<Noise> noise = new ArrayList<>();
    public final List<Driver> drivers = new ArrayList<>();
    /** Pivots of the virtual bones in model pixels; null means measured from the model's own geometry. */
    public float[] center;
    public float[] ground;

    public RigProfile(String id) {
        this.id = id;
    }

    public static RigProfile parse(String id, JsonObject o, Map<String, RigProfile> existing) {
        RigProfile p = new RigProfile(id);
        if (o.has("extends")) {
            RigProfile base = existing.get(o.get("extends").getAsString());
            if (base != null) p.inherit(base);
        }
        if (o.has("groups")) {
            for (Map.Entry<String, JsonElement> g : o.getAsJsonObject("groups").entrySet()) p.groups.put(g.getKey(), strings(g.getValue().getAsJsonArray()));
        }
        if (o.has("followers")) {
            for (Map.Entry<String, JsonElement> f : o.getAsJsonObject("followers").entrySet()) p.followers.put(f.getKey(), f.getValue().getAsString());
        }
        if (o.has("couplings")) {
            p.couplings.clear();
            for (JsonElement c : o.getAsJsonArray("couplings")) {
                JsonObject co = c.getAsJsonObject();
                p.couplings.add(new Coupling(co.get("parent").getAsString(), co.has("pivot") ? vec(co.getAsJsonArray("pivot")) : null,
                        co.has("move_parent") && co.get("move_parent").getAsBoolean(), strings(co.getAsJsonArray("children"))));
            }
        }
        if (o.has("springs")) {
            for (JsonElement s : o.getAsJsonArray("springs")) {
                JsonObject so = s.getAsJsonObject();
                JsonArray t = so.getAsJsonArray("targets");
                String[] targets = new String[3];
                for (int i = 0; i < 3 && i < t.size(); i++) targets[i] = t.get(i).isJsonNull() ? null : t.get(i).getAsString();
                p.springs.add(new Spring(so.get("bone").getAsString(), targets, so.get("stiffness").getAsFloat(),
                        so.get("damping").getAsFloat(), so.has("limit") ? so.get("limit").getAsFloat() : 45f));
            }
        }
        if (o.has("life_noise")) {
            for (JsonElement s : o.getAsJsonArray("life_noise")) {
                JsonObject so = s.getAsJsonObject();
                p.noise.add(new Noise(so.get("bone").getAsString(), so.get("amplitude").getAsFloat(), so.get("frequency").getAsFloat(),
                        so.has("scale") ? so.get("scale").getAsString() : "1"));
            }
        }
        if (o.has("drivers")) {
            for (JsonElement s : o.getAsJsonArray("drivers")) {
                JsonObject so = s.getAsJsonObject();
                JsonArray t = so.getAsJsonArray("exprs");
                String[] exprs = new String[3];
                for (int i = 0; i < 3 && i < t.size(); i++) exprs[i] = t.get(i).isJsonNull() ? null : t.get(i).getAsString();
                int group = "position".equals(so.has("group") ? so.get("group").getAsString() : "rotation") ? 1 : 0;
                p.drivers.add(new Driver(so.get("bone").getAsString(), group, exprs, so.has("half_life") ? so.get("half_life").getAsFloat() : 0.1f));
            }
        }
        if (o.has("center")) p.center = vec(o.getAsJsonArray("center"));
        if (o.has("ground")) p.ground = vec(o.getAsJsonArray("ground"));
        return p;
    }

    /**
     * A copy for a model of other proportions (a mob from another mod borrowing this profile): couplings pivot at the
     * given hip instead of the vanilla one, and the centre and ground pivots are measured from the model.
     */
    public RigProfile fittedTo(float[] hip) {
        RigProfile p = new RigProfile(id + "~fit");
        p.inherit(this);
        p.couplings.clear();
        for (Coupling c : couplings) p.couplings.add(new Coupling(c.parent(), c.pivot() == null || hip == null ? c.pivot() : hip.clone(), c.moveParent(), c.children()));
        p.center = null;
        p.ground = null;
        return p;
    }

    private void inherit(RigProfile b) {
        groups.putAll(b.groups);
        followers.putAll(b.followers);
        couplings.addAll(b.couplings);
        springs.addAll(b.springs);
        noise.addAll(b.noise);
        drivers.addAll(b.drivers);
        center = b.center == null ? null : b.center.clone();
        ground = b.ground == null ? null : b.ground.clone();
    }

    private static List<String> strings(JsonArray a) {
        List<String> l = new ArrayList<>();
        for (JsonElement e : a) l.add(e.getAsString());
        return l;
    }

    private static float[] vec(JsonArray a) {
        return new float[] {a.get(0).getAsFloat(), a.get(1).getAsFloat(), a.get(2).getAsFloat()};
    }
}
