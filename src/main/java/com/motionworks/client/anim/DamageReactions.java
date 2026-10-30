package com.motionworks.client.anim;

import com.motionworks.client.camera.CameraEffects;
import com.motionworks.client.particle.Effects;
import net.minecraft.client.Minecraft;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/** Converts synced damage events into directional, type-aware hit reactions and impact effects. */
public final class DamageReactions {
    private DamageReactions() {}

    public static void onDamage(LivingEntity victim, DamageSource source) {
        String kind = kind(source);
        Vec3 from = source.getSourcePosition();
        Entity attacker = source.getEntity();
        if (from == null && attacker != null) from = attacker.position();
        float rel = 0f;
        if (from != null) {
            double dx = from.x - victim.getX();
            double dz = from.z - victim.getZ();
            float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90f;
            rel = Mth.wrapDegrees(yawTo - victim.yBodyRot);
        }
        float amount = Math.max(1f, victim.getMaxHealth() * 0.15f);
        EntityAnimator a = AnimatorManager.get(victim);
        a.onHurt(kind, rel, amount);
        if (victim == Minecraft.getInstance().player) CameraEffects.hurt(rel, amount);
        if ("melee".equals(kind)) {
            Vec3 at = victim.position().add(0, victim.getBbHeight() * 0.6, 0);
            if (from != null) at = at.add(from.subtract(victim.position()).normalize().scale(victim.getBbWidth() * 0.5));
            Effects.impact(at, victim.getArmorValue() > 6 ? "metal" : "dust", Math.min(1f, amount / 6f));
        }
    }

    static String kind(DamageSource s) {
        if (s.is(DamageTypes.FLY_INTO_WALL)) return "kinetic";
        if (s.is(DamageTypes.THORNS)) return "thorns";
        if (s.is(DamageTypes.SONIC_BOOM)) return "sonic";
        if (s.is(DamageTypes.STARVE)) return "starve";
        if (s.is(DamageTypes.IN_WALL) || s.is(DamageTypes.CRAMMING)) return "suffocate";
        if (s.is(DamageTypes.FALLING_BLOCK) || s.is(DamageTypes.FALLING_ANVIL) || s.is(DamageTypes.FALLING_STALACTITE) || s.is(DamageTypes.STALAGMITE)) return "crush";
        if (s.is(DamageTypes.DRAGON_BREATH)) return "breath";
        if (s.is(DamageTypes.WITHER) || s.is(DamageTypes.WITHER_SKULL)) return "wither";
        if (s.is(DamageTypes.STING)) return "sting";
        if (s.is(DamageTypeTags.IS_FALL)) return "fall";
        if (s.is(DamageTypeTags.IS_EXPLOSION)) return "explosion";
        if (s.is(DamageTypeTags.IS_FIRE)) return "fire";
        if (s.is(DamageTypeTags.IS_PROJECTILE)) return "projectile";
        if (s.is(DamageTypeTags.IS_DROWNING)) return "drown";
        if (s.is(DamageTypeTags.IS_FREEZING)) return "freeze";
        if (s.is(DamageTypeTags.IS_LIGHTNING)) return "lightning";
        if (s.is(DamageTypes.MAGIC) || s.is(DamageTypes.INDIRECT_MAGIC) || s.is(DamageTypes.WITHER)) return "magic";
        if (s.is(DamageTypes.CACTUS) || s.is(DamageTypes.SWEET_BERRY_BUSH)) return "prick";
        if (s.getDirectEntity() != null) return "melee";
        return "other";
    }
}
