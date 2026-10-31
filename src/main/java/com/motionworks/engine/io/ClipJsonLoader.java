package com.motionworks.engine.io;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.clip.ClipEvent;
import com.motionworks.engine.clip.Interp;
import com.motionworks.engine.clip.Keyframe;
import com.motionworks.engine.clip.LoopMode;
import com.motionworks.engine.clip.Trigger;
import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.expr.ExprParser;
import com.motionworks.engine.math.Easing;

import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Loads clips from two formats:
 * <ul>
 *   <li><b>motionworks.v1</b> - the native format with full trigger/layer/registry metadata.</li>
 *   <li><b>Bedrock / Blockbench</b> animation files ({@code "animations": {"animation.x": ...}}), so
 *       animators can author in Blockbench and drop exports in. Bedrock axes are converted to
 *       ModelPart space and an optional {@code "motionworks"} block per animation supplies metadata.</li>
 * </ul>
 */
public final class ClipJsonLoader {
    private ClipJsonLoader() {}

    public static List<AnimationClip> load(Reader reader, String sourceName) {
        JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
        return load(root, sourceName);
    }

    public static List<AnimationClip> load(JsonObject root, String sourceName) {
        try {
            if (root.has("animations")) return loadBedrock(root.getAsJsonObject("animations"));
            return loadNative(root);
        } catch (RuntimeException e) {
            throw new IllegalArgumentException("Failed to load animations from " + sourceName + ": " + e.getMessage(), e);
        }
    }

    // ------------------------------------------------------------------ native

    private static List<AnimationClip> loadNative(JsonObject root) {
        JsonObject defaults = root.has("defaults") ? root.getAsJsonObject("defaults") : new JsonObject();
        JsonObject clips = root.getAsJsonObject("clips");
        List<AnimationClip> out = new ArrayList<>();
        for (Map.Entry<String, JsonElement> e : clips.entrySet()) {
            JsonObject merged = merge(defaults, e.getValue().getAsJsonObject());
            try {
                out.add(parseClip(e.getKey(), merged, false));
            } catch (RuntimeException ex) {
                throw new IllegalArgumentException("clip '" + e.getKey() + "': " + ex.getMessage(), ex);
            }
        }
        return out;
    }

    private static JsonObject merge(JsonObject defaults, JsonObject clip) {
        JsonObject m = new JsonObject();
        for (Map.Entry<String, JsonElement> d : defaults.entrySet()) m.add(d.getKey(), d.getValue());
        for (Map.Entry<String, JsonElement> c : clip.entrySet()) {
            if (c.getKey().equals("meta") && m.has("meta")) {
                JsonObject meta = m.getAsJsonObject("meta").deepCopy();
                for (Map.Entry<String, JsonElement> me : c.getValue().getAsJsonObject().entrySet()) meta.add(me.getKey(), me.getValue());
                m.add("meta", meta);
            } else {
                m.add(c.getKey(), c.getValue());
            }
        }
        return m;
    }

    static AnimationClip parseClip(String id, JsonObject o, boolean bedrockAxes) {
        String name = str(o, "name", humanize(id));
        String category = str(o, "category", "uncategorized");
        String target = str(o, "target", "any");
        String rig = str(o, "rig", "generic");
        float length = num(o, "length", -1f);
        LoopMode loop = LoopMode.parse(o.has("loop") ? prim(o.get("loop")) : null);
        String layer = str(o, "layer", "action");
        int priority = (int) num(o, "priority", 100);
        float blendIn = num(o, "blend_in", 0.15f);
        float blendOut = num(o, "blend_out", 0.2f);
        boolean additive = o.has("additive") && o.get("additive").getAsBoolean();
        Set<String> mask = null;
        if (o.has("mask")) {
            mask = new LinkedHashSet<>();
            for (JsonElement m : o.getAsJsonArray("mask")) mask.add(m.getAsString());
        }
        Expr speed = o.has("speed") ? ExprParser.parseValue(prim(o.get("speed"))) : Expr.ONE;
        Expr time = o.has("time") ? ExprParser.parseValue(prim(o.get("time"))) : null;
        Expr weight = o.has("weight") ? ExprParser.parseValue(prim(o.get("weight"))) : Expr.ONE;
        boolean interruptible = !o.has("interruptible") || o.get("interruptible").getAsBoolean();
        float interruptAfter = num(o, "interrupt_after", 0.6f);

        List<BoneTrack> tracks = new ArrayList<>();
        if (o.has("bones")) {
            for (Map.Entry<String, JsonElement> b : o.getAsJsonObject("bones").entrySet()) {
                JsonObject bone = b.getValue().getAsJsonObject();
                Channel rot = bone.has("rotation") ? parseChannel(ChannelTarget.ROTATION, bone.get("rotation"), bedrockAxes) : null;
                Channel pos = bone.has("position") ? parseChannel(ChannelTarget.POSITION, bone.get("position"), bedrockAxes) : null;
                Channel scl = bone.has("scale") ? parseChannel(ChannelTarget.SCALE, bone.get("scale"), bedrockAxes) : null;
                if (rot != null || pos != null || scl != null) tracks.add(new BoneTrack(b.getKey(), rot, pos, scl));
            }
        }
        if (length < 0f) {
            float max = 0f;
            for (BoneTrack t : tracks) {
                for (ChannelTarget ct : ChannelTarget.values()) {
                    Channel c = t.channel(ct);
                    if (c != null) max = Math.max(max, c.endTime());
                }
            }
            length = max;
        }
        if (loop == LoopMode.LOOP) {
            for (int i = 0; i < tracks.size(); i++) {
                BoneTrack t = tracks.get(i);
                tracks.set(i, new BoneTrack(t.bone(), cyclic(t.rotation(), length), cyclic(t.position(), length), cyclic(t.scale(), length)));
            }
        }

        List<ClipEvent> events = new ArrayList<>();
        if (o.has("events")) {
            for (JsonElement ev : o.getAsJsonArray("events")) {
                JsonObject eo = ev.getAsJsonObject();
                Map<String, String> data = new LinkedHashMap<>();
                for (Map.Entry<String, JsonElement> f : eo.entrySet()) {
                    if (f.getKey().equals("time") || f.getKey().equals("type")) continue;
                    data.put(f.getKey(), f.getValue().isJsonPrimitive() ? f.getValue().getAsString() : f.getValue().toString());
                }
                events.add(new ClipEvent(eo.get("time").getAsFloat(), eo.get("type").getAsString(), Collections.unmodifiableMap(data)));
            }
            events.sort((a, b) -> Float.compare(a.time(), b.time()));
        }

        Trigger trigger = o.has("trigger") ? parseTrigger(o.getAsJsonObject("trigger")) : Trigger.manual("Played explicitly");

        Map<String, String> meta = new LinkedHashMap<>();
        if (o.has("meta")) {
            for (Map.Entry<String, JsonElement> m : o.getAsJsonObject("meta").entrySet()) {
                meta.put(m.getKey(), m.getValue().isJsonPrimitive() ? m.getValue().getAsString() : m.getValue().toString());
            }
        }
        return new AnimationClip(id, name, category, target, rig, length, loop, layer, priority, blendIn, blendOut,
                additive, mask == null ? null : Collections.unmodifiableSet(mask), speed, time, weight, trigger,
                List.copyOf(tracks), List.copyOf(events), interruptible, interruptAfter, Collections.unmodifiableMap(meta));
    }

    private static Channel cyclic(Channel c, float length) {
        return c == null ? null : c.cyclicOver(length);
    }

    private static Trigger parseTrigger(JsonObject t) {
        Trigger.Type type = Trigger.Type.valueOf(str(t, "type", "manual").toUpperCase(Locale.ROOT));
        String event = str(t, "event", null);
        Expr when = t.has("when") ? ExprParser.parseValue(prim(t.get("when"))) : Expr.ONE;
        String group = str(t, "group", null);
        Expr weight = t.has("weight") ? ExprParser.parseValue(prim(t.get("weight"))) : Expr.ONE;
        Expr stopWhen = t.has("stop_when") ? ExprParser.parseValue(prim(t.get("stop_when"))) : null;
        if (type == Trigger.Type.EVENT && event == null) throw new IllegalArgumentException("event trigger without 'event'");
        return new Trigger(type, event, when, group, weight, num(t, "min_time", 0f), num(t, "exit_delay", 0.1f),
                num(t, "cooldown", 0f), num(t, "chance", 1f), stopWhen, str(t, "description", ""));
    }

    private static Channel parseChannel(ChannelTarget target, JsonElement el, boolean bedrockAxes) {
        Easing defaultEase = Easing.LINEAR;
        Interp defaultInterp = Interp.LINEAR;
        JsonElement keysEl = el;
        if (el.isJsonObject() && el.getAsJsonObject().has("keys")) {
            JsonObject wrapper = el.getAsJsonObject();
            if (wrapper.has("ease")) defaultEase = Easing.parse(wrapper.get("ease").getAsString());
            if (wrapper.has("lerp")) defaultInterp = Interp.parse(wrapper.get("lerp").getAsString());
            keysEl = wrapper.get("keys");
        }
        List<Keyframe> keys = new ArrayList<>();
        if (keysEl.isJsonArray() || keysEl.isJsonPrimitive()) {
            Expr[] v = vector(keysEl, target, bedrockAxes);
            keys.add(Keyframe.of(0f, v, defaultEase, defaultInterp));
        } else {
            for (Map.Entry<String, JsonElement> k : keysEl.getAsJsonObject().entrySet()) {
                float time = Float.parseFloat(k.getKey());
                JsonElement kv = k.getValue();
                if (kv.isJsonObject()) {
                    JsonObject ko = kv.getAsJsonObject();
                    Easing ease = defaultEase;
                    if (ko.has("ease")) ease = Easing.parse(ko.get("ease").getAsString());
                    else if (ko.has("e")) ease = Easing.parse(ko.get("e").getAsString());
                    else if (ko.has("easing")) ease = Easing.parse(ko.get("easing").getAsString());
                    Interp interp = defaultInterp;
                    if (ko.has("lerp")) interp = Interp.parse(ko.get("lerp").getAsString());
                    else if (ko.has("l")) interp = Interp.parse(ko.get("l").getAsString());
                    else if (ko.has("lerp_mode")) interp = Interp.parse(ko.get("lerp_mode").getAsString());
                    Expr[] pre;
                    Expr[] post;
                    if (ko.has("pre") || ko.has("post")) {
                        post = vector(ko.has("post") ? ko.get("post") : ko.get("pre"), target, bedrockAxes);
                        pre = ko.has("pre") ? vector(ko.get("pre"), target, bedrockAxes) : post;
                    } else {
                        JsonElement v = ko.has("value") ? ko.get("value") : ko.get("v");
                        pre = post = vector(v, target, bedrockAxes);
                    }
                    keys.add(new Keyframe(time, pre, post, ease, interp));
                } else {
                    keys.add(Keyframe.of(time, vector(kv, target, bedrockAxes), defaultEase, defaultInterp));
                }
            }
        }
        return new Channel(target, keys.toArray(new Keyframe[0]));
    }

    private static Expr[] vector(JsonElement el, ChannelTarget target, boolean bedrockAxes) {
        Expr[] v = new Expr[3];
        if (el.isJsonArray()) {
            JsonArray a = el.getAsJsonArray();
            for (int i = 0; i < 3; i++) v[i] = i < a.size() ? ExprParser.parseValue(prim(a.get(i))) : (target == ChannelTarget.SCALE ? Expr.ONE : Expr.ZERO);
        } else {
            Expr e = ExprParser.parseValue(prim(el));
            v[0] = v[1] = v[2] = e;
        }
        if (bedrockAxes && target != ChannelTarget.SCALE) {
            v[0] = negate(v[0]);
            v[1] = negate(v[1]);
        }
        return v;
    }

    private static Expr negate(Expr e) {
        if (e.isConstant()) return Expr.constant(-e.eval(null));
        return s -> -e.eval(s);
    }

    // ------------------------------------------------------------------ bedrock

    private static List<AnimationClip> loadBedrock(JsonObject animations) {
        List<AnimationClip> out = new ArrayList<>();
        for (Map.Entry<String, JsonElement> e : animations.entrySet()) {
            JsonObject a = e.getValue().getAsJsonObject();
            JsonObject o = a.has("motionworks") ? a.getAsJsonObject("motionworks").deepCopy() : new JsonObject();
            if (a.has("animation_length")) o.add("length", a.get("animation_length"));
            if (a.has("loop")) o.add("loop", a.get("loop"));
            if (a.has("bones")) o.add("bones", a.get("bones"));
            if (a.has("blend_weight")) o.add("weight", a.get("blend_weight"));
            if (a.has("anim_time_update")) o.add("time", a.get("anim_time_update"));
            JsonArray events = new JsonArray();
            addBedrockEvents(a, "sound_effects", "sound", "effect", events);
            addBedrockEvents(a, "particle_effects", "particle", "effect", events);
            addBedrockEvents(a, "timeline", "custom", "value", events);
            if (!events.isEmpty()) o.add("events", events);
            if (!o.has("category")) o.addProperty("category", "imported");
            String id = e.getKey().startsWith("animation.") ? e.getKey().substring(10) : e.getKey();
            out.add(parseClip(id, o, true));
        }
        return out;
    }

    private static void addBedrockEvents(JsonObject a, String key, String type, String field, JsonArray events) {
        if (!a.has(key)) return;
        for (Map.Entry<String, JsonElement> t : a.getAsJsonObject(key).entrySet()) {
            List<JsonElement> entries = new ArrayList<>();
            if (t.getValue().isJsonArray()) t.getValue().getAsJsonArray().forEach(entries::add);
            else entries.add(t.getValue());
            for (JsonElement entry : entries) {
                JsonObject ev = new JsonObject();
                ev.addProperty("time", Float.parseFloat(t.getKey()));
                ev.addProperty("type", type);
                if (entry.isJsonObject()) {
                    for (Map.Entry<String, JsonElement> f : entry.getAsJsonObject().entrySet()) ev.add(f.getKey(), f.getValue());
                } else {
                    ev.addProperty(field, entry.getAsString());
                }
                events.add(ev);
            }
        }
    }

    // ------------------------------------------------------------------ helpers

    private static Object prim(JsonElement e) {
        if (!e.isJsonPrimitive()) throw new IllegalArgumentException("Expected a number, boolean or expression string, got " + e);
        JsonPrimitive p = e.getAsJsonPrimitive();
        if (p.isNumber()) return p.getAsFloat();
        if (p.isBoolean()) return p.getAsBoolean();
        return p.getAsString();
    }

    private static String str(JsonObject o, String key, String fallback) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsString() : fallback;
    }

    private static float num(JsonObject o, String key, float fallback) {
        return o.has(key) ? o.get(key).getAsFloat() : fallback;
    }

    static String humanize(String id) {
        String last = id.substring(id.lastIndexOf('.') + 1).replace('_', ' ');
        return last.isEmpty() ? id : Character.toUpperCase(last.charAt(0)) + last.substring(1);
    }
}
