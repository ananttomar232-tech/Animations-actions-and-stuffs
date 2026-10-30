package com.motionworks.client.cinematic;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** An authored cinematic: sequential camera shots plus timed events on a shared timeline. */
public final class Sequence {
    public record TimedShot(float start, float duration, JsonObject spec, String transition, float blend) {}

    public record TimedEvent(float time, String type, JsonObject spec) {}

    public final String id;
    public final String name;
    public final String anchor;
    public final boolean letterbox;
    public final boolean skippable;
    public final boolean hideHud;
    public final boolean cancelOnDamage;
    public final List<TimedShot> shots;
    public final List<TimedEvent> events;
    public final float duration;

    private Sequence(String id, String name, String anchor, boolean letterbox, boolean skippable, boolean hideHud, boolean cancelOnDamage,
                     List<TimedShot> shots, List<TimedEvent> events, float duration) {
        this.id = id;
        this.name = name;
        this.anchor = anchor;
        this.letterbox = letterbox;
        this.skippable = skippable;
        this.hideHud = hideHud;
        this.cancelOnDamage = cancelOnDamage;
        this.shots = shots;
        this.events = events;
        this.duration = duration;
    }

    public static Sequence parse(String id, JsonObject o) {
        List<TimedShot> shots = new ArrayList<>();
        float t = 0f;
        if (o.has("shots")) {
            for (JsonElement el : o.getAsJsonArray("shots")) {
                JsonObject s = el.getAsJsonObject();
                float d = s.has("duration") ? s.get("duration").getAsFloat() : 3f;
                String transition = "cut";
                float blend = 0f;
                if (s.has("transition")) {
                    JsonObject tr = s.getAsJsonObject("transition");
                    transition = tr.has("type") ? tr.get("type").getAsString() : "blend";
                    blend = tr.has("duration") ? tr.get("duration").getAsFloat() : 0.8f;
                }
                float start = s.has("at") ? s.get("at").getAsFloat() : t;
                shots.add(new TimedShot(start, d, s, transition, blend));
                t = start + d;
            }
        }
        List<TimedEvent> events = new ArrayList<>();
        if (o.has("events")) {
            for (JsonElement el : o.getAsJsonArray("events")) {
                JsonObject e = el.getAsJsonObject();
                events.add(new TimedEvent(e.get("time").getAsFloat(), e.get("type").getAsString(), e));
            }
        }
        events.sort((a, b) -> Float.compare(a.time(), b.time()));
        float duration = o.has("duration") ? o.get("duration").getAsFloat() : t;
        for (TimedEvent e : events) duration = Math.max(duration, e.time());
        return new Sequence(id,
                o.has("name") ? o.get("name").getAsString() : id,
                o.has("anchor") ? o.get("anchor").getAsString() : "@self",
                !o.has("letterbox") || o.get("letterbox").getAsBoolean(),
                !o.has("skippable") || o.get("skippable").getAsBoolean(),
                !o.has("hide_hud") || o.get("hide_hud").getAsBoolean(),
                !o.has("cancel_on_damage") || o.get("cancel_on_damage").getAsBoolean(),
                Collections.unmodifiableList(shots), Collections.unmodifiableList(events), duration);
    }

    TimedShot shotAt(float time) {
        TimedShot found = null;
        for (TimedShot s : shots) if (time >= s.start()) found = s;
        return found;
    }

    TimedShot previous(TimedShot s) {
        int i = shots.indexOf(s);
        return i > 0 ? shots.get(i - 1) : null;
    }
}
