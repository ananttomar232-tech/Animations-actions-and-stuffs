package com.motionworks.client.cinematic;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.motionworks.engine.math.Easing;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Evaluates one authored shot at normalised time into a camera placement. Shot vocabulary:
 * static, dolly, track, orbit, crane, pan, tilt, spline, pov, over_shoulder, low_angle,
 * high_angle, establishing, wide, close_up, extreme_close_up, reveal, push_in, pull_out.
 * Every shot also supports zoom (fov_from/fov_to), dutch roll (roll_from/roll_to) and
 * rule-of-thirds framing ({@code frame}: center, left_third, right_third, plus {@code headroom}).
 */
final class ShotEvaluator {
    private ShotEvaluator() {}

    record Placement(Vec3 pos, float yaw, float pitch, float roll, float fov) {}

    static Placement evaluate(JsonObject shot, float u, SequenceContext ctx, float partial) {
        Easing ease = shot.has("ease") ? Easing.parse(shot.get("ease").getAsString()) : Easing.IN_OUT_SINE;
        float t = ease.apply(MathUtil.clamp01(u));
        String type = shot.has("type") ? shot.get("type").getAsString() : "static";
        Vec3 pos;
        Vec3 look = null;
        Entity subject = shot.has("target") ? ctx.resolve(shot.get("target").getAsString()) : ctx.anchor();
        Vec3 subjectPoint = subject != null ? focus(subject, shot, partial) : ctx.origin();
        float subjectYaw = subject != null ? bodyYaw(subject, partial) : ctx.originYaw();
        switch (type) {
            case "dolly", "push_in", "pull_out" -> {
                Vec3 from = ctx.local(vec(shot, "from", type.equals("pull_out") ? new Vec3(0, 1.6, 2.5) : new Vec3(0, 1.6, 7)));
                Vec3 to = ctx.local(vec(shot, "to", type.equals("pull_out") ? new Vec3(0, 1.8, 8) : new Vec3(0, 1.6, 2.5)));
                pos = from.lerp(to, t);
                look = subjectPoint;
            }
            case "track" -> {
                Vec3 off = vec(shot, "offset", new Vec3(0, 1.0, 4));
                pos = subjectPoint.add(rotate(off, subjectYaw));
                look = subjectPoint;
            }
            case "orbit", "establishing" -> {
                boolean est = type.equals("establishing");
                float radius = num(shot, "radius", est ? 22f : 5f);
                float height = num(shot, "height", est ? 10f : 1.5f);
                float a0 = num(shot, "from_angle", est ? -35f : -60f);
                float a1 = num(shot, "to_angle", est ? 25f : 60f);
                float ang = (subjectYaw + Mth.lerp(t, a0, a1)) * Mth.DEG_TO_RAD;
                pos = subjectPoint.add(-Math.sin(ang) * radius, height, Math.cos(ang) * radius);
                look = subjectPoint;
            }
            case "crane" -> {
                float dist = num(shot, "distance", 6f);
                float h0 = num(shot, "from_height", 0.5f), h1 = num(shot, "to_height", 7f);
                float ang = (subjectYaw + num(shot, "angle", 20f)) * Mth.DEG_TO_RAD;
                float d = Mth.lerp(t, dist, dist * num(shot, "distance_scale", 1.3f));
                pos = subjectPoint.add(-Math.sin(ang) * d, Mth.lerp(t, h0, h1), Math.cos(ang) * d);
                look = subjectPoint;
            }
            case "pan", "tilt" -> {
                pos = ctx.local(vec(shot, "pos", new Vec3(0, 1.7, 0)));
                float yaw = type.equals("pan") ? Mth.lerp(t, num(shot, "from_yaw", -40f), num(shot, "to_yaw", 40f)) : num(shot, "yaw", 0f);
                float pitch = type.equals("tilt") ? Mth.lerp(t, num(shot, "from_pitch", 30f), num(shot, "to_pitch", -20f)) : num(shot, "pitch", 0f);
                return finish(shot, t, pos, ctx.originYaw() + yaw, pitch);
            }
            case "spline" -> {
                JsonArray pts = shot.getAsJsonArray("points");
                pos = spline(pts, t, ctx);
                if (shot.has("look_points")) look = spline(shot.getAsJsonArray("look_points"), t, ctx);
                else look = subjectPoint;
            }
            case "pov" -> {
                Entity actor = subject != null ? subject : ctx.anchor();
                Vec3 eye = actor.getEyePosition(partial);
                return finish(shot, t, eye, actor.getViewYRot(partial), actor.getViewXRot(partial));
            }
            case "over_shoulder" -> {
                Entity actor = subject;
                Entity other = shot.has("look_at") ? ctx.resolve(shot.get("look_at").getAsString()) : null;
                Vec3 eye = actor != null ? actor.getEyePosition(partial) : ctx.origin().add(0, 1.6, 0);
                Vec3 lookAt = other != null ? focus(other, shot, partial) : eye.add(rotate(new Vec3(0, 0, 6), subjectYaw));
                Vec3 dir = lookAt.subtract(eye).normalize();
                Vec3 right = new Vec3(-dir.z, 0, dir.x).normalize();
                float side = "left".equals(str(shot, "side", "right")) ? -1f : 1f;
                float dist = num(shot, "distance", 2.2f);
                pos = eye.subtract(dir.scale(dist)).add(right.scale(0.75 * side)).add(0, 0.25, 0);
                look = lookAt;
            }
            case "low_angle", "high_angle" -> {
                boolean low = type.equals("low_angle");
                float dist = num(shot, "distance", 4f);
                float ang = (subjectYaw + num(shot, "angle", 15f)) * Mth.DEG_TO_RAD;
                float h = low ? 0.2f : num(shot, "height", 6f);
                float drift = Mth.lerp(t, 0f, num(shot, "drift", 0.6f));
                pos = subjectPoint.add(-Math.sin(ang) * (dist + drift), h - (low ? subjectPoint.y - (subject != null ? subject.getY() : subjectPoint.y) : 0), Math.cos(ang) * (dist + drift));
                look = subjectPoint;
            }
            case "wide", "close_up", "extreme_close_up" -> {
                float height = subject != null ? subject.getBbHeight() : 1.8f;
                float frameFraction = switch (type) {
                    case "wide" -> 0.25f;
                    case "close_up" -> 1.6f;
                    default -> 4.0f;
                };
                float fov = num(shot, "fov_from", 70f);
                float visible = height / frameFraction;
                float dist = (float) (visible / (2 * Math.tan(Math.toRadians(fov) / 2)));
                float ang = (subjectYaw + num(shot, "angle", 10f) + t * num(shot, "drift_angle", 6f)) * Mth.DEG_TO_RAD;
                Vec3 target = type.equals("wide") ? subjectPoint : (subject != null ? subject.getEyePosition(partial) : subjectPoint);
                pos = target.add(-Math.sin(ang) * dist, 0.05, Math.cos(ang) * dist);
                look = target;
            }
            case "reveal" -> {
                float d0 = num(shot, "from_distance", 0.8f), d1 = num(shot, "to_distance", 9f);
                float ang = (subjectYaw + num(shot, "angle", 180f)) * Mth.DEG_TO_RAD;
                float d = Mth.lerp(t, d0, d1);
                pos = subjectPoint.add(-Math.sin(ang) * d, Mth.lerp(t, 0.3f, num(shot, "height", 2.5f)), Math.cos(ang) * d);
                look = subjectPoint;
            }
            default -> {
                pos = ctx.local(vec(shot, "pos", new Vec3(0, 1.7, 5)));
                look = subjectPoint;
            }
        }
        if (shot.has("look_at") && !type.equals("over_shoulder")) {
            Entity la = ctx.resolve(shot.get("look_at").getAsString());
            if (la != null) look = focus(la, shot, partial);
        }
        Vec3 d = look.subtract(pos);
        float yaw = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90f;
        float pitch = (float) -(Mth.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * Mth.RAD_TO_DEG);
        return finish(shot, t, pos, yaw, pitch);
    }

    /** Applies zoom, dutch roll and rule-of-thirds framing. */
    private static Placement finish(JsonObject shot, float t, Vec3 pos, float yaw, float pitch) {
        float fov = Mth.lerp(t, num(shot, "fov_from", 70f), num(shot, "fov_to", num(shot, "fov_from", 70f)));
        float roll = Mth.lerp(t, num(shot, "roll_from", num(shot, "roll", 0f)), num(shot, "roll_to", num(shot, "roll", 0f)));
        String frame = str(shot, "frame", "center");
        float hfov = fov * 1.5f;
        // Turning the camera by a sixth of the horizontal FOV places the subject on a thirds line.
        if (frame.equals("left_third")) yaw += hfov / 6f;
        else if (frame.equals("right_third")) yaw -= hfov / 6f;
        pitch += num(shot, "headroom", 0f);
        return new Placement(pos, yaw, Mth.clamp(pitch, -90f, 90f), roll, fov);
    }

    private static Vec3 focus(Entity e, JsonObject shot, float partial) {
        String part = str(shot, "focus", "chest");
        Vec3 p = e.getPosition(partial);
        return switch (part) {
            case "feet" -> p;
            case "eyes", "head" -> e.getEyePosition(partial);
            default -> p.add(0, e.getBbHeight() * 0.65, 0);
        };
    }

    private static float bodyYaw(Entity e, float partial) {
        if (e instanceof LivingEntity le) return Mth.rotLerp(partial, le.yBodyRotO, le.yBodyRot);
        return e.getViewYRot(partial);
    }

    static Vec3 rotate(Vec3 local, float yawDeg) {
        float r = yawDeg * Mth.DEG_TO_RAD;
        double cos = Math.cos(r), sin = Math.sin(r);
        // local: x = right, y = up, z = forward
        double fx = -sin, fz = cos;
        double rx = -cos, rz = -sin;
        return new Vec3(local.x * rx + local.z * fx, local.y, local.x * rz + local.z * fz);
    }

    private static Vec3 spline(JsonArray pts, float t, SequenceContext ctx) {
        int n = pts.size();
        if (n == 1) return ctx.local(arr(pts.get(0).getAsJsonArray()));
        float f = t * (n - 1);
        int i = Math.min(n - 2, (int) Math.floor(f));
        float u = f - i;
        Vec3 p0 = ctx.local(arr(pts.get(Math.max(0, i - 1)).getAsJsonArray()));
        Vec3 p1 = ctx.local(arr(pts.get(i).getAsJsonArray()));
        Vec3 p2 = ctx.local(arr(pts.get(i + 1).getAsJsonArray()));
        Vec3 p3 = ctx.local(arr(pts.get(Math.min(n - 1, i + 2)).getAsJsonArray()));
        return new Vec3(
                MathUtil.catmullRom((float) p0.x, (float) p1.x, (float) p2.x, (float) p3.x, u),
                MathUtil.catmullRom((float) p0.y, (float) p1.y, (float) p2.y, (float) p3.y, u),
                MathUtil.catmullRom((float) p0.z, (float) p1.z, (float) p2.z, (float) p3.z, u));
    }

    static Vec3 arr(JsonArray a) {
        return new Vec3(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble());
    }

    private static Vec3 vec(JsonObject o, String k, Vec3 fallback) {
        return o.has(k) ? arr(o.getAsJsonArray(k)) : fallback;
    }

    static float num(JsonObject o, String k, float fallback) {
        return o.has(k) ? o.get(k).getAsFloat() : fallback;
    }

    static String str(JsonObject o, String k, String fallback) {
        return o.has(k) ? o.get(k).getAsString() : fallback;
    }
}
