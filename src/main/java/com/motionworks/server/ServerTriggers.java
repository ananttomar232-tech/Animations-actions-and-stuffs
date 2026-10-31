package com.motionworks.server;

import com.motionworks.MotionWorks;
import com.motionworks.common.InteractionClassifier;
import com.motionworks.common.ItemCategories;
import com.motionworks.common.WorldEventArgs;
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
        String a = arg == null ? "" : arg;
        TriggerTrace.entity(e, event, a);
        MWNetwork.toTrackers(e, new AnimationEventPacket(e.getId(), event, a, dir, height), includeSelf);
    }

    /** Positional world event (entity id -1, arg "x,y,z[,magnitude]"); clients fan it out to every nearby animated entity. */
    static void sendWorld(net.minecraft.server.level.ServerLevel level, net.minecraft.world.phys.Vec3 at, double range, String event, String arg) {
        TriggerTrace.world(level, at, event, arg);
        MWNetwork.toNearby(level, at, range, new AnimationEventPacket(-1, event, arg, 0f));
    }

    /** Server-thread task queue: lifecycle events are sent a tick later, once clients track the entity. */
    private record Delayed(int due, Runnable task) {}

    private static final java.util.List<Delayed> DELAYED = new java.util.ArrayList<>();

    static void later(net.minecraft.server.MinecraftServer server, int ticks, Runnable task) {
        if (DELAYED.size() < 4096) DELAYED.add(new Delayed(server.getTickCount() + ticks, task));
    }

    /** Nothing queued for, or remembered from, a stopped server may survive into the next one (singleplayer). */
    @SubscribeEvent
    public static void onServerStopped(net.minecraftforge.event.server.ServerStoppedEvent e) {
        DELAYED.clear();
        com.motionworks.network.EmotePacket.forget(null);
        TriggerTrace.clearTracing();
    }

    @SubscribeEvent
    public static void onPlayerLeft(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e) {
        com.motionworks.network.EmotePacket.forget(e.getEntity().getUUID());
    }

    @SubscribeEvent
    public static void onServerTick(net.minecraftforge.event.TickEvent.ServerTickEvent e) {
        if (e.phase != net.minecraftforge.event.TickEvent.Phase.END || DELAYED.isEmpty()) return;
        int now = e.getServer().getTickCount();
        java.util.List<Delayed> due = new java.util.ArrayList<>();
        DELAYED.removeIf(d -> d.due() <= now && due.add(d));
        for (Delayed d : due) d.task().run();
    }

    /** "spawn:<type>" (natural, spawner, spawn_egg, reinforcement, ...) for freshly created mobs. */
    @SubscribeEvent
    public static void onMobSpawn(net.minecraftforge.event.entity.living.MobSpawnEvent.FinalizeSpawn e) {
        Mob mob = e.getEntity();
        if (mob.level().isClientSide || mob.getServer() == null) return;
        String type = e.getSpawnType().name().toLowerCase(java.util.Locale.ROOT);
        later(mob.getServer(), 2, () -> { if (mob.isAlive()) send(mob, "spawn", type, 0f, true); });
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent e) {
        Player p = e.getEntity();
        if (p.getServer() != null) later(p.getServer(), 5, () -> send(p, "respawn", e.isEndConquered() ? "end" : "death", 0f, true));
    }

    @SubscribeEvent
    public static void onDimensionChange(PlayerEvent.PlayerChangedDimensionEvent e) {
        Player p = e.getEntity();
        String dim = e.getTo().location().getPath();
        if (p.getServer() != null) later(p.getServer(), 10, () -> { if (p.isAlive()) send(p, "dimension_enter", dim, 0f, true); });
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent e) {
        Player p = e.getEntity();
        if (p.getServer() != null) later(p.getServer(), 40, () -> { if (p.isAlive()) send(p, "join", "", 0f, true); });
    }

    /** Called from MobMixin when a mob plays its ambient sound (moo, bark, groan...). */
    public static void onAmbientSound(Mob mob) {
        if (mob.level().isClientSide || mob.isSilent()) return;
        send(mob, "vocalize", "", 0f, true);
    }

    /** The player who lands the killing blow on a boss gets "boss_slain:<boss>". */
    @SubscribeEvent
    public static void onBossDeath(net.minecraftforge.event.entity.living.LivingDeathEvent e) {
        LivingEntity dead = e.getEntity();
        if (dead.level().isClientSide || !(e.getSource().getEntity() instanceof Player killer)) return;
        String boss = dead instanceof net.minecraft.world.entity.boss.enderdragon.EnderDragon ? "ender_dragon"
                : dead instanceof net.minecraft.world.entity.boss.wither.WitherBoss ? "wither"
                : dead instanceof net.minecraft.world.entity.monster.warden.Warden ? "warden"
                : dead instanceof net.minecraft.world.entity.monster.ElderGuardian ? "elder_guardian" : null;
        if (boss != null && killer.getServer() != null) later(killer.getServer(), 10, () -> send(killer, "boss_slain", boss, 0f, true));
    }

    /** A totem of undying saves its holder: everyone nearby sees the revival. */
    @SubscribeEvent
    public static void onTotem(net.minecraftforge.event.entity.living.LivingUseTotemEvent e) {
        LivingEntity le = e.getEntity();
        if (!le.level().isClientSide) send(le, "totem", "", 0f, true);
    }

    /** Ender pearl arrival: the thrower lands at the destination ("teleport:pearl"). */
    @SubscribeEvent
    public static void onPearlTeleport(net.minecraftforge.event.entity.EntityTeleportEvent.EnderPearl e) {
        Player p = e.getPlayer();
        if (p.getServer() != null) later(p.getServer(), 1, () -> send(p, "teleport", "pearl", 0f, true));
    }

    /** Endermen and shulkers teleport without any client-visible cue; announce it so the vanish/arrive clips play. */
    @SubscribeEvent
    public static void onEnderTeleport(net.minecraftforge.event.entity.EntityTeleportEvent.EnderEntity e) {
        LivingEntity le = e.getEntityLiving();
        if (!le.level().isClientSide) send(le, "teleport", "", 0f, true);
    }

    /**
     * Ranged mobs never swing, so their attack clips key off the projectile they launch:
     * "shoot" with the projectile kind as argument (also exposed as "shoot:<kind>").
     */
    @SubscribeEvent
    public static void onEntityJoin(net.minecraftforge.event.entity.EntityJoinLevelEvent e) {
        if (e.getLevel().isClientSide || e.loadedFromDisk()) return;
        if (e.getEntity() instanceof net.minecraft.world.entity.LightningBolt bolt && e.getLevel() instanceof net.minecraft.server.level.ServerLevel level) {
            net.minecraft.world.phys.Vec3 at = bolt.position();
            sendWorld(level, at, 96, "thunderclap", WorldEventArgs.encode(at.x, at.y, at.z));
            return;
        }
        Entity owner = e.getEntity() instanceof net.minecraft.world.entity.projectile.Projectile proj ? proj.getOwner()
                : e.getEntity() instanceof net.minecraft.world.entity.projectile.EvokerFangs fangs ? fangs.getOwner() : null;
        if (owner instanceof Mob mob) send(mob, "shoot", projectileKind(e.getEntity()), 0f, true);
    }

    static String projectileKind(Entity p) {
        if (p instanceof net.minecraft.world.entity.projectile.LlamaSpit) return "spit";
        if (p instanceof net.minecraft.world.entity.projectile.ThrownTrident) return "trident";
        if (p instanceof net.minecraft.world.entity.projectile.AbstractArrow) return "arrow";
        if (p instanceof net.minecraft.world.entity.projectile.WitherSkull) return "skull";
        if (p instanceof net.minecraft.world.entity.projectile.DragonFireball) return "dragon_fireball";
        if (p instanceof net.minecraft.world.entity.projectile.AbstractHurtingProjectile) return "fireball";
        if (p instanceof net.minecraft.world.entity.projectile.Snowball) return "snowball";
        if (p instanceof net.minecraft.world.entity.projectile.ThrownPotion) return "potion";
        if (p instanceof net.minecraft.world.entity.projectile.ShulkerBullet) return "bullet";
        if (p instanceof net.minecraft.world.entity.projectile.EvokerFangs) return "fangs";
        return "other";
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
        else if ("glass_bottle".equals(cat)) send(e.getEntity(), "fill_bottle", "", 0f, false);
        else if ("firework".equals(cat) && e.getEntity().isFallFlying()) send(e.getEntity(), "boost", "", 0f, false);
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
        if (e.getPlayer().level().isClientSide) return;
        var st = e.getState();
        String mat = st.is(net.minecraft.tags.BlockTags.LOGS) || st.is(net.minecraft.tags.BlockTags.PLANKS) ? "wood"
                : st.is(net.minecraft.tags.BlockTags.CROPS) || st.getBlock() instanceof net.minecraft.world.level.block.BushBlock ? "plant"
                : st.is(net.minecraft.tags.BlockTags.MINEABLE_WITH_SHOVEL) ? "dirt"
                : st.is(net.minecraft.tags.BlockTags.MINEABLE_WITH_PICKAXE) ? "stone" : "other";
        send(e.getPlayer(), "break_block", mat, 0f, true);
    }

    @SubscribeEvent
    public static void onXp(PlayerXpEvent.PickupXp e) {
        if (!e.getEntity().level().isClientSide && e.getEntity().tickCount % 4 == 0) send(e.getEntity(), "xp_pickup", "", 0f, true);
    }

    @SubscribeEvent
    public static void onToolBreak(net.minecraftforge.event.entity.player.PlayerDestroyItemEvent e) {
        if (!e.getEntity().level().isClientSide) send(e.getEntity(), "tool_break", ItemCategories.of(e.getOriginal()), 0f, true);
    }

    @SubscribeEvent
    public static void onContainerOpen(net.minecraftforge.event.entity.player.PlayerContainerEvent.Open e) {
        if (!e.getEntity().level().isClientSide) send(e.getEntity(), "menu_open", menuKind(e.getContainer()), 0f, true);
    }

    @SubscribeEvent
    public static void onContainerClose(net.minecraftforge.event.entity.player.PlayerContainerEvent.Close e) {
        if (!e.getEntity().level().isClientSide) send(e.getEntity(), "menu_close", menuKind(e.getContainer()), 0f, true);
    }

    static String menuKind(net.minecraft.world.inventory.AbstractContainerMenu m) {
        if (m instanceof net.minecraft.world.inventory.ChestMenu c) return c.getRowCount() > 3 ? "large_chest" : "chest";
        if (m instanceof net.minecraft.world.inventory.ShulkerBoxMenu) return "shulker";
        if (m instanceof net.minecraft.world.inventory.CraftingMenu) return "crafting";
        if (m instanceof net.minecraft.world.inventory.SmokerMenu) return "smoker";
        if (m instanceof net.minecraft.world.inventory.BlastFurnaceMenu) return "blast_furnace";
        if (m instanceof net.minecraft.world.inventory.FurnaceMenu) return "furnace";
        if (m instanceof net.minecraft.world.inventory.AnvilMenu) return "anvil";
        if (m instanceof net.minecraft.world.inventory.EnchantmentMenu) return "enchanting";
        if (m instanceof net.minecraft.world.inventory.BrewingStandMenu) return "brewing";
        if (m instanceof net.minecraft.world.inventory.GrindstoneMenu) return "grindstone";
        if (m instanceof net.minecraft.world.inventory.StonecutterMenu) return "stonecutter";
        if (m instanceof net.minecraft.world.inventory.LoomMenu) return "loom";
        if (m instanceof net.minecraft.world.inventory.CartographyTableMenu) return "cartography";
        if (m instanceof net.minecraft.world.inventory.SmithingMenu) return "smithing";
        if (m instanceof net.minecraft.world.inventory.LecternMenu) return "lectern";
        if (m instanceof net.minecraft.world.inventory.BeaconMenu) return "beacon";
        if (m instanceof net.minecraft.world.inventory.MerchantMenu) return "merchant";
        if (m instanceof net.minecraft.world.inventory.HorseInventoryMenu) return "horse";
        if (m instanceof net.minecraft.world.inventory.DispenserMenu) return "dispenser";
        if (m instanceof net.minecraft.world.inventory.HopperMenu) return "hopper";
        return "other";
    }

    @SubscribeEvent
    public static void onToss(ItemTossEvent e) {
        if (e.getPlayer().level().isClientSide) return;
        send(e.getPlayer(), "drop", ItemCategories.of(e.getEntity().getItem()), 0f, true);
        if (e.getEntity().getItem().is(net.minecraft.world.item.Items.GOLD_INGOT)
                && !e.getPlayer().level().getEntitiesOfClass(net.minecraft.world.entity.monster.piglin.Piglin.class, e.getPlayer().getBoundingBox().inflate(6)).isEmpty()) {
            send(e.getPlayer(), "barter_toss", "", 0f, true);
        }
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
        if (attacker instanceof LivingEntity la) send(la, breaks ? "break_guard" : "deflected", "", 0f, true);
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
        if (e.getLevel().isClientSide || !(e.getLevel() instanceof net.minecraft.server.level.ServerLevel level)) return;
        var pos = e.getExplosion().getPosition();
        float power = ((com.motionworks.mixin.common.ExplosionAccessor) e.getExplosion()).motionworks$radius();
        // Aftermath effects for everyone in range, startles for creatures that only hear it.
        sendWorld(level, pos, 96, "explosion", WorldEventArgs.encode(pos.x, pos.y, pos.z, power));
        for (Entity hit : e.getAffectedEntities()) {
            if (hit instanceof LivingEntity le && le.distanceToSqr(pos) < 12 * 12) {
                send(le, "explosion_flinch", "", InteractionClassifier.relativeYaw(le, pos.x, pos.z), true);
            }
        }
    }
}
