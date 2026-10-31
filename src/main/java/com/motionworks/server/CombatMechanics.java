package com.motionworks.server;

import com.motionworks.MotionWorks;
import com.motionworks.config.MWConfig;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Optional, server-authoritative combat mechanics that give the combat animations real
 * meaning: directional dodge with brief invulnerability, shield parry with stagger and a
 * counter-attack window, shield bash, and landing rolls. Every mechanic has a config switch.
 */
@Mod.EventBusSubscriber(modid = MotionWorks.MOD_ID)
public final class CombatMechanics {
    private static final Map<UUID, Long> DODGE_READY = new ConcurrentHashMap<>();
    private static final Map<UUID, Long> INVULNERABLE_UNTIL = new ConcurrentHashMap<>();
    private static final Map<UUID, Long> BLOCK_STARTED = new ConcurrentHashMap<>();
    private static final Map<UUID, Long> COUNTER_UNTIL = new ConcurrentHashMap<>();
    private static final Map<UUID, Long> BASH_READY = new ConcurrentHashMap<>();

    /** The longest any window above can legitimately reach ahead of the current game time, in ticks. */
    static final long MAX_WINDOW = 400;

    private CombatMechanics() {}

    /**
     * Whether a stored "until" time is still ahead of {@code now}. Times are game ticks of the world the player is
     * in; one that lies further ahead than any window could reach was recorded in another world (a singleplayer
     * session keeps these maps when the player switches worlds) and is dropped, so it cannot grant invulnerability,
     * a free parry or a cooldown in this one.
     */
    static boolean pending(Map<UUID, Long> map, UUID id, long now) {
        Long until = map.get(id);
        if (until == null) return false;
        if (until - now > MAX_WINDOW) {
            map.remove(id);
            return false;
        }
        return until > now;
    }

    /** Forgets every player's combat state: the server stopped, so game times from it mean nothing any more. */
    static void reset() {
        DODGE_READY.clear();
        INVULNERABLE_UNTIL.clear();
        BLOCK_STARTED.clear();
        COUNTER_UNTIL.clear();
        BASH_READY.clear();
    }

    static void forget(UUID id) {
        DODGE_READY.remove(id);
        INVULNERABLE_UNTIL.remove(id);
        BLOCK_STARTED.remove(id);
        COUNTER_UNTIL.remove(id);
        BASH_READY.remove(id);
    }

    @SubscribeEvent
    public static void onServerStopped(net.minecraftforge.event.server.ServerStoppedEvent e) {
        reset();
    }

    @SubscribeEvent
    public static void onLogout(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e) {
        forget(e.getEntity().getUUID());
    }

    public static void dodge(ServerPlayer p, float forward, float strafe) {
        if (!MWConfig.SERVER.dodge.get() || p.isPassenger() || !p.onGround() || p.isSpectator() || p.isSleeping()) return;
        long now = p.level().getGameTime();
        if (pending(DODGE_READY, p.getUUID(), now)) return;
        if (!p.isCreative() && p.getFoodData().getFoodLevel() <= 6) return;
        if (Math.abs(forward) < 0.1f && Math.abs(strafe) < 0.1f) forward = -1f;
        String dir;
        if (Math.abs(forward) >= Math.abs(strafe)) dir = forward > 0 ? "forward" : "back";
        else dir = strafe > 0 ? "left" : "right";
        float yaw = p.getYRot() * Mth.DEG_TO_RAD;
        Vec3 fwd = new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
        Vec3 left = new Vec3(Mth.cos(yaw), 0, Mth.sin(yaw));
        Vec3 impulse = fwd.scale(forward).add(left.scale(strafe)).normalize().scale(dir.equals("forward") ? 0.85 : 0.7);
        p.setDeltaMovement(impulse.x, 0.22, impulse.z);
        p.hurtMarked = true;
        p.causeFoodExhaustion(0.6f);
        DODGE_READY.put(p.getUUID(), now + MWConfig.SERVER.dodgeCooldownTicks.get());
        INVULNERABLE_UNTIL.put(p.getUUID(), now + MWConfig.SERVER.dodgeInvulnerabilityTicks.get());
        ServerTriggers.send(p, "dodge", dir, dir.equals("left") ? 1f : (dir.equals("right") ? -1f : 0f), true);
    }

    public static void bash(ServerPlayer p) {
        if (!MWConfig.SERVER.shieldBash.get() || !p.isBlocking()) return;
        long now = p.level().getGameTime();
        if (pending(BASH_READY, p.getUUID(), now)) return;
        BASH_READY.put(p.getUUID(), now + 40);
        Vec3 look = p.getLookAngle();
        AABB box = p.getBoundingBox().expandTowards(look.scale(2.5)).inflate(0.8);
        boolean hit = false;
        for (Entity e : p.level().getEntities(p, box, x -> x instanceof LivingEntity && x.isAlive())) {
            Vec3 to = e.position().subtract(p.position()).normalize();
            if (to.dot(new Vec3(look.x, 0, look.z).normalize()) < 0.4) continue;
            LivingEntity le = (LivingEntity) e;
            le.hurt(p.damageSources().playerAttack(p), 1.0f);
            le.knockback(0.9, -look.x, -look.z);
            le.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20, 1));
            ServerTriggers.send(le, "staggered", "bash", 0f, true);
            hit = true;
        }
        p.causeFoodExhaustion(0.3f);
        ServerTriggers.send(p, "shield_bash", hit ? "hit" : "miss", 0f, true);
    }

    @SubscribeEvent
    public static void onUseStart(LivingEntityUseItemEvent.Start e) {
        if (e.getEntity() instanceof Player p && !p.level().isClientSide && e.getItem().getItem() instanceof ShieldItem) {
            BLOCK_STARTED.put(p.getUUID(), p.level().getGameTime());
        }
    }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onAttacked(LivingAttackEvent e) {
        LivingEntity victim = e.getEntity();
        if (victim.level().isClientSide || !(victim instanceof Player p)) return;
        long now = p.level().getGameTime();
        if (pending(INVULNERABLE_UNTIL, p.getUUID(), now) && !e.getSource().is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            e.setCanceled(true);
            return;
        }
        if (!MWConfig.SERVER.parry.get() || !p.isBlocking()) return;
        Entity attacker = e.getSource().getDirectEntity();
        if (!(attacker instanceof LivingEntity la) || e.getSource().getEntity() != attacker) return;
        Long started = BLOCK_STARTED.get(p.getUUID());
        // A block that "started" in the future was recorded in another world: it is not a parry.
        if (started == null || started > now || now - started > MWConfig.SERVER.parryWindowTicks.get()) return;
        Vec3 to = la.position().subtract(p.position()).normalize();
        if (to.dot(p.getLookAngle()) < 0.3) return;
        e.setCanceled(true);
        la.knockback(0.6, p.getX() - la.getX(), p.getZ() - la.getZ());
        la.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 30, 2));
        la.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 30, 0));
        p.level().playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.0f, 1.4f);
        if (MWConfig.SERVER.counterAttacks.get()) COUNTER_UNTIL.put(p.getUUID(), now + 24);
        ServerTriggers.send(p, "parry", "", 0f, true);
        ServerTriggers.send(la, "parried", "", 0f, true);
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public static void onHurt(LivingHurtEvent e) {
        if (!(e.getSource().getEntity() instanceof Player p) || p.level().isClientSide) return;
        long now = p.level().getGameTime();
        Long until = COUNTER_UNTIL.remove(p.getUUID());
        if (until != null && until >= now && until - now <= MAX_WINDOW && e.getSource().getDirectEntity() == p) {
            e.setAmount(e.getAmount() * (1f + MWConfig.SERVER.counterDamageBonus.get().floatValue()));
            ServerTriggers.send(p, "counter", "", 0f, true);
        }
    }

    @SubscribeEvent
    public static void onFall(LivingFallEvent e) {
        if (!(e.getEntity() instanceof Player p) || p.level().isClientSide || !MWConfig.SERVER.rollOnLanding.get()) return;
        if (e.getDistance() >= 4f && e.getDistance() <= 12f && p.isSprinting()) {
            e.setDamageMultiplier(e.getDamageMultiplier() * 0.5f);
            ServerTriggers.send(p, "landing_roll", "", 0f, true);
        }
    }
}
