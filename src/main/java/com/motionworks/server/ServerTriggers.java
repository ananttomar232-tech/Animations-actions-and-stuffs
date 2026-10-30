package com.motionworks.server;

import com.motionworks.MotionWorks;
import com.motionworks.common.InteractionClassifier;
import com.motionworks.common.ItemCategories;
import com.motionworks.config.MWConfig;
import com.motionworks.network.AnimationEventPacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.EntityMountEvent;
import net.minecraftforge.event.entity.item.ItemTossEvent;
import net.minecraftforge.event.entity.living.AnimalTameEvent;
import net.minecraftforge.event.entity.living.BabyEntitySpawnEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.AdvancementEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.FillBucketEvent;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.player.PlayerXpEvent;
import net.minecraftforge.event.entity.player.TradeWithVillagerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Server-authoritative animation triggers. The acting player animates instantly from local
 * client hooks, so most events go to other trackers only; events the client cannot know about
 * (fishing results, trades, advancements, landing rolls) include the player as well.
 */
@Mod.EventBusSubscriber(modid = MotionWorks.MOD_ID)
public final class ServerTriggers {
    private ServerTriggers() {}

    static void send(Entity e, String event, String arg, float dir, boolean includeSelf) {
        send(e, event, arg, dir, 0f, includeSelf);
    }

    static void send(Entity e, String event, String arg, float dir, float height, boolean includeSelf) {
        if (!MWConfig.SERVER.broadcastTriggers.get()) return;
        MWNetwork.toTrackers(e, new AnimationEventPacket(e.getId(), event, arg == null ? "" : arg, dir, height), includeSelf);
    }

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock e) {
        if (e.getLevel().isClientSide || e.getHand() != InteractionHand.MAIN_HAND) return;
        String kind = InteractionClassifier.block(e.getLevel().getBlockState(e.getPos()), e.getItemStack(), e.getEntity().isShiftKeyDown());
        if (kind != null) {
            float dir = InteractionClassifier.relativeYaw(e.getEntity(), e.getPos().getX() + 0.5, e.getPos().getZ() + 0.5);
            send(e.getEntity(), "interact", kind, dir, (float) (e.getPos().getY() + 0.5 - e.getEntity().getEyeY()), false);
        }
    }

    @SubscribeEvent
    public static void onRightClickItem(PlayerInteractEvent.RightClickItem e) {
        if (e.getLevel().isClientSide) return;
        String cat = ItemCategories.of(e.getItemStack());
        if ("fishing_rod".equals(cat)) send(e.getEntity(), e.getEntity().fishing == null ? "fish_cast" : "fish_reel", "", 0f, false);
        else if ("throwable".equals(cat)) send(e.getEntity(), "throw", "", 0f, false);
        else if ("map".equals(cat) || "book".equals(cat) || "device".equals(cat)) send(e.getEntity(), "inspect_item", cat, 0f, false);
    }

    @SubscribeEvent
    public static void onEntityInteract(PlayerInteractEvent.EntityInteract e) {
        if (e.getLevel().isClientSide || e.getHand() != InteractionHand.MAIN_HAND) return;
        String kind = InteractionClassifier.entity(e.getTarget(), e.getItemStack());
        if (kind == null) return;
        send(e.getEntity(), "interact_entity", kind, InteractionClassifier.relativeYaw(e.getEntity(), e.getTarget().getX(), e.getTarget().getZ()), false);
        if (e.getTarget() instanceof LivingEntity target) {
            send(target, "interacted", kind, InteractionClassifier.relativeYaw(target, e.getEntity().getX(), e.getEntity().getZ()), true);
        }
    }

    @SubscribeEvent
    public static void onPlace(BlockEvent.EntityPlaceEvent e) {
        if (e.getEntity() instanceof Player p && !p.level().isClientSide) send(p, "place", ItemCategories.of(p.getMainHandItem()), 0f, true);
    }

    @SubscribeEvent
    public static void onBreak(BlockEvent.BreakEvent e) {
        if (!e.getPlayer().level().isClientSide) send(e.getPlayer(), "break_block", "", 0f, true);
    }

    @SubscribeEvent
    public static void onToss(ItemTossEvent e) {
        if (!e.getPlayer().level().isClientSide) send(e.getPlayer(), "drop", ItemCategories.of(e.getEntity().getItem()), 0f, true);
    }

    @SubscribeEvent
    public static void onPickup(PlayerEvent.ItemPickupEvent e) {
        if (!e.getEntity().level().isClientSide) send(e.getEntity(), "pickup", ItemCategories.of(e.getStack()), 0f, true);
    }

    @SubscribeEvent
    public static void onFished(ItemFishedEvent e) {
        send(e.getEntity(), "fish_catch", "", 0f, true);
    }

    @SubscribeEvent
    public static void onBucket(FillBucketEvent e) {
        if (!e.getLevel().isClientSide) send(e.getEntity(), "bucket", e.getEmptyBucket().isEmpty() ? "empty" : "fill", 0f, false);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onAttack(AttackEntityEvent e) {
        Player p = e.getEntity();
        if (p.level().isClientSide || e.isCanceled()) return;
        send(p, "attack", ItemCategories.of(p.getMainHandItem()), p.getAttackStrengthScale(0.5f), false);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHurt(LivingHurtEvent e) {
        if (e.isCanceled() || e.getEntity().level().isClientSide) return;
        Entity src = e.getSource().getEntity();
        if (src instanceof Mob mob && e.getSource().getDirectEntity() == mob) {
            send(mob, "melee_hit", "", 0f, true);
        }
    }

    @SubscribeEvent
    public static void onTarget(LivingChangeTargetEvent e) {
        if (e.getEntity().level().isClientSide || !(e.getEntity() instanceof Mob mob)) return;
        LivingEntity newTarget = e.getNewTarget();
        if (newTarget != null && mob.getTarget() != newTarget && newTarget instanceof Player) {
            send(mob, "notice", "player", InteractionClassifier.relativeYaw(mob, newTarget.getX(), newTarget.getZ()), true);
        }
    }

    @SubscribeEvent
    public static void onShield(ShieldBlockEvent e) {
        if (e.getEntity().level().isClientSide) return;
        Entity attacker = e.getDamageSource().getEntity();
        boolean breaks = attacker instanceof LivingEntity le && le.getMainHandItem().canDisableShield(e.getEntity().getUseItem(), e.getEntity(), le);
        send(e.getEntity(), breaks ? "guard_break" : "shield_block", "", 0f, true);
    }

    @SubscribeEvent
    public static void onTame(AnimalTameEvent e) {
        send(e.getAnimal(), "tamed", "", 0f, true);
        send(e.getTamer(), "celebrate", "tame", 0f, true);
    }

    @SubscribeEvent
    public static void onBaby(BabyEntitySpawnEvent e) {
        if (e.getParentA() != null) send(e.getParentA(), "proud", "", 0f, true);
        if (e.getParentB() != null) send(e.getParentB(), "proud", "", 0f, true);
    }

    @SubscribeEvent
    public static void onTrade(TradeWithVillagerEvent e) {
        send(e.getAbstractVillager(), "trade_complete", "", 0f, true);
        send(e.getEntity(), "trade", "", 0f, true);
    }

    @SubscribeEvent
    public static void onLevel(PlayerXpEvent.LevelChange e) {
        if (e.getLevels() > 0 && (e.getEntity().experienceLevel + e.getLevels()) % 5 == 0) send(e.getEntity(), "celebrate", "level", 0f, true);
    }

    @SubscribeEvent
    public static void onAdvancement(AdvancementEvent.AdvancementEarnEvent e) {
        var display = e.getAdvancement().getDisplay();
        if (display != null && display.shouldAnnounceChat()) send(e.getEntity(), "victory", display.getFrame().getName(), 0f, true);
    }

    @SubscribeEvent
    public static void onMount(EntityMountEvent e) {
        if (e.getLevel().isClientSide || !(e.getEntityMounting() instanceof LivingEntity rider)) return;
        if (e.getEntityBeingMounted() instanceof LivingEntity mount) send(mount, e.isMounting() ? "rider_on" : "rider_off", "", 0f, true);
        send(rider, e.isMounting() ? "mount_server" : "dismount_server", "", 0f, false);
    }

    @SubscribeEvent
    public static void onExplosion(ExplosionEvent.Detonate e) {
        if (e.getLevel().isClientSide) return;
        var pos = e.getExplosion().getPosition();
        for (Entity hit : e.getAffectedEntities()) {
            if (hit instanceof LivingEntity le && le.distanceToSqr(pos) < 12 * 12) {
                send(le, "explosion_flinch", "", InteractionClassifier.relativeYaw(le, pos.x, pos.z), true);
            }
        }
    }
}
