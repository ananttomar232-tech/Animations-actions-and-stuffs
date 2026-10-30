package com.motionworks.client.anim;

import com.motionworks.client.camera.CameraEffects;
import com.motionworks.client.particle.Effects;
import com.motionworks.client.particle.WeaponTrails;
import com.motionworks.common.CtxVars;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.ClipEvent;
import com.motionworks.engine.expr.StringIds;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.AnimationEventSink;
import com.motionworks.registry.MWSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.Map;

/**
 * Turns timed clip events into sounds, particles, camera shake and weapon trails. Events are
 * authored at exact keyframes (foot contact, blade impact) so effects line up with motion, and
 * faint instances (crossfading out) are skipped so nothing doubles up.
 */
public final class ClipEventDispatcher implements AnimationEventSink {
    public static final ClipEventDispatcher INSTANCE = new ClipEventDispatcher();
    private static final String[] SURFACE_SOUNDS = {"grass", "stone", "wood", "sand", "gravel", "snow", "metal", "wool", "mud", "water", "leaves"};

    private final Map<AnimationController, LivingEntity> owners = new IdentityHashMap<>();
    private final Map<String, Long> lastPlayed = new HashMap<>();

    private ClipEventDispatcher() {}

    @Override
    public void onEvent(AnimationController c, AnimationClip clip, ClipEvent e, float weight) {
        if (weight < 0.35f) return;
        LivingEntity entity = owner(c);
        if (entity == null) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        switch (e.type()) {
            case "footstep" -> footstep(c, entity, e);
            case "sound" -> sound(entity, e.get("sound", ""), e.getFloat("volume", 1f), e.getFloat("pitch", 1f), e.getFloat("var", 0.1f));
            case "whoosh" -> whoosh(entity, e.get("weight", "medium"));
            case "foley" -> foley(entity, c, e.get("kind", "cloth"), e.getFloat("volume", 0.5f));
            case "particle" -> particle(entity, e);
            case "shake" -> shake(entity, e.getFloat("amount", 0.2f), e.getFloat("radius", 12f));
            case "impact" -> {
                Vec3 at = point(entity, "front");
                Effects.impact(at, e.get("material", "dust"), e.getFloat("strength", 0.6f));
                if (entity == mc.player) CameraEffects.impactKick(e.getFloat("strength", 0.6f));
            }
            case "stomp" -> {
                float strength = e.getFloat("strength", 1f);
                Effects.shockwave(mc.level, point(entity, "feet"), strength);
                sound(entity, "motionworks:creature.heavy_step", 0.6f + strength * 0.4f, 0.8f, 0.1f);
                shake(entity, 0.12f * strength, 10f + 10f * strength);
            }
            case "trail" -> {
                if (MWConfig.CLIENT.weaponTrails.get()) {
                    if ("start".equals(e.get("state", "start"))) WeaponTrails.start(entity, e.get("hand", "main"), e.getFloat("width", 1f));
                    else WeaponTrails.stop(entity);
                }
            }
            case "breath" -> {
                if (c.scope().get(CtxVars.COLD) != 0f) Effects.burst("breath", point(entity, "mouth"), 2, 0.05, 0.02, look(entity).scale(0.04));
            }
            default -> { }
        }
    }

    public void register(AnimationController c, LivingEntity e) {
        owners.put(c, e);
    }

    private LivingEntity owner(AnimationController c) {
        LivingEntity e = owners.get(c);
        if (e != null && !e.isRemoved()) return e;
        AnimatorManager.forEach(a -> {
            if (a.controller() == c) owners.put(c, a.entity);
        });
        owners.values().removeIf(LivingEntity::isRemoved);
        return owners.get(c);
    }

    private void footstep(AnimationController c, LivingEntity entity, ClipEvent e) {
        float weight = e.getFloat("weight", 1f) * (0.6f + Math.min(1.5f, entity.getBbWidth() * entity.getBbHeight()));
        int surfaceId = (int) c.scope().get(CtxVars.SURFACE);
        String surface = "stone";
        for (String s : SURFACE_SOUNDS) if (StringIds.id(s) == surfaceId) surface = s;
        if (surfaceId == StringIds.id("dirt")) surface = "gravel";
        if (surfaceId == StringIds.id("moss")) surface = "leaves";
        if (surfaceId == StringIds.id("soul") || surfaceId == StringIds.id("nether")) surface = "stone";
        if (surfaceId == StringIds.id("air")) return;
        Vec3 foot = point(entity, "left".equals(e.get("foot", "")) ? "left_foot" : "right_foot");
        if (MWConfig.CLIENT.foleySounds.get() && !(entity.isSilent())) {
            float vol = 0.18f * weight * (c.scope().get(CtxVars.SNEAKING) != 0f ? 0.4f : 1f);
            playThrottled(entity, "motionworks:footstep." + surface, foot, vol, 0.9f + entity.getRandom().nextFloat() * 0.2f, 60);
            float armor = c.scope().get(CtxVars.ARMOR_WEIGHT);
            if (armor > 0.25f) playThrottled(entity, armor > 0.6f ? "motionworks:foley.plate" : "motionworks:foley.chain", foot, 0.08f + armor * 0.12f, 1f, 120);
        }
        Effects.footstep(surface, foot, weight);
    }

    private void whoosh(LivingEntity entity, String weight) {
        String name = switch (weight) {
            case "light" -> "motionworks:weapon.whoosh_light";
            case "heavy" -> "motionworks:weapon.whoosh_heavy";
            default -> "motionworks:weapon.whoosh_medium";
        };
        sound(entity, name, 0.55f, 1f, 0.12f);
    }

    private void foley(LivingEntity entity, AnimationController c, String kind, float volume) {
        if (!MWConfig.CLIENT.foleySounds.get()) return;
        String name = switch (kind) {
            case "armor" -> {
                float a = c.scope().get(CtxVars.ARMOR_WEIGHT);
                if (a <= 0.05f) yield "motionworks:foley.cloth";
                yield a > 0.6f ? "motionworks:foley.plate" : (a > 0.3f ? "motionworks:foley.chain" : "motionworks:foley.leather");
            }
            case "leather" -> "motionworks:foley.leather";
            default -> "motionworks:foley.cloth";
        };
        playThrottled(entity, name, entity.position(), volume * 0.4f, 1f, 150);
    }

    private void particle(LivingEntity entity, ClipEvent e) {
        Vec3 at = point(entity, e.get("at", "center"));
        Vec3 bias = "forward".equals(e.get("dir", "")) ? look(entity).scale(e.getFloat("speed", 0.1f)) : Vec3.ZERO;
        Effects.burst(e.get("particle", "dust_puff"), at, (int) e.getFloat("count", 3), e.getFloat("spread", 0.3f), e.getFloat("speed", 0.05f), bias);
    }

    private void shake(LivingEntity entity, float amount, float radius) {
        Minecraft mc = Minecraft.getInstance();
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        double d = cam.distanceTo(entity.position());
        if (d > radius) return;
        CameraEffects.addTrauma(amount * (float) (1.0 - d / radius));
    }

    private void sound(LivingEntity entity, String id, float volume, float pitch, float var) {
        if (id.isEmpty()) return;
        float p = pitch * (1f + (entity.getRandom().nextFloat() - 0.5f) * 2f * var);
        playThrottled(entity, id, entity.position(), volume * MWConfig.CLIENT.foleyVolume.get().floatValue(), p, 40);
    }

    private void playThrottled(LivingEntity entity, String id, Vec3 at, float volume, float pitch, long minMillis) {
        String key = entity.getId() + "|" + id;
        long now = net.minecraft.Util.getMillis();
        Long last = lastPlayed.get(key);
        if (last != null && now - last < minMillis) return;
        lastPlayed.put(key, now);
        if (lastPlayed.size() > 512) lastPlayed.clear();
        SoundEvent ev = resolve(id);
        if (ev == null) return;
        SoundSource src = entity instanceof Player ? SoundSource.PLAYERS : (entity instanceof net.minecraft.world.entity.monster.Enemy ? SoundSource.HOSTILE : SoundSource.NEUTRAL);
        entity.level().playLocalSound(at.x, at.y, at.z, ev, src, volume, pitch, false);
    }

    private static SoundEvent resolve(String id) {
        if (id.startsWith("motionworks:")) return MWSounds.get(id.substring(12));
        ResourceLocation loc = ResourceLocation.tryParse(id);
        return loc == null ? null : ForgeRegistries.SOUND_EVENTS.getValue(loc);
    }

    static Vec3 look(LivingEntity e) {
        float yaw = e.yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
    }

    /** Named attachment points in world space derived from the entity's bounds and facing. */
    static Vec3 point(LivingEntity e, String at) {
        Vec3 pos = e.position();
        Vec3 fwd = look(e);
        Vec3 side = new Vec3(-fwd.z, 0, fwd.x);
        float w = e.getBbWidth(), h = e.getBbHeight();
        return switch (at) {
            case "feet" -> pos.add(0, 0.05, 0);
            case "left_foot" -> pos.add(side.scale(w * 0.25)).add(0, 0.05, 0);
            case "right_foot" -> pos.add(side.scale(-w * 0.25)).add(0, 0.05, 0);
            case "head" -> pos.add(0, e.getEyeHeight(), 0);
            case "mouth" -> pos.add(0, e.getEyeHeight() - 0.1, 0).add(fwd.scale(w * 0.6));
            case "front" -> pos.add(0, h * 0.6, 0).add(fwd.scale(w * 0.5 + 0.6));
            case "back" -> pos.add(0, h * 0.6, 0).add(fwd.scale(-w * 0.5));
            default -> pos.add(0, h * 0.5, 0);
        };
    }
}
