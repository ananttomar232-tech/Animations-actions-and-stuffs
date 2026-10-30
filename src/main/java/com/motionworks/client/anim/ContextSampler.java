package com.motionworks.client.anim;

import com.motionworks.client.environment.WindSystem;
import com.motionworks.common.CtxVars;
import com.motionworks.common.ItemCategories;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.StringIds;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.animal.Cat;
import net.minecraft.world.entity.animal.Fox;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.animal.Panda;
import net.minecraft.world.entity.animal.Parrot;
import net.minecraft.world.entity.animal.PolarBear;
import net.minecraft.world.entity.animal.Rabbit;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.animal.Turtle;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.entity.animal.allay.Allay;
import net.minecraft.world.entity.animal.axolotl.Axolotl;
import net.minecraft.world.entity.animal.camel.Camel;
import net.minecraft.world.entity.animal.goat.Goat;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.animal.sniffer.Sniffer;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Blaze;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.EnderMan;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.Ghast;
import net.minecraft.world.entity.monster.Guardian;
import net.minecraft.world.entity.monster.Ravager;
import net.minecraft.world.entity.monster.Slime;
import net.minecraft.world.entity.monster.SpellcasterIllager;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.entity.monster.Strider;
import net.minecraft.world.entity.monster.Vex;
import net.minecraft.world.entity.monster.Zoglin;
import net.minecraft.world.entity.monster.hoglin.Hoglin;
import net.minecraft.world.entity.monster.piglin.Piglin;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.entity.vehicle.AbstractMinecart;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Publishes an entity's state into its controller scope once per client tick. Everything here is
 * derived from data vanilla already synchronises, so every client computes the same values.
 */
public final class ContextSampler {
    private static final Map<SoundType, String> SURFACES = new IdentityHashMap<>();

    static {
        SURFACES.put(SoundType.GRASS, "grass");
        SURFACES.put(SoundType.ROOTED_DIRT, "dirt");
        SURFACES.put(SoundType.GRAVEL, "gravel");
        SURFACES.put(SoundType.SAND, "sand");
        SURFACES.put(SoundType.SNOW, "snow");
        SURFACES.put(SoundType.POWDER_SNOW, "snow");
        SURFACES.put(SoundType.WOOD, "wood");
        SURFACES.put(SoundType.BAMBOO_WOOD, "wood");
        SURFACES.put(SoundType.CHERRY_WOOD, "wood");
        SURFACES.put(SoundType.NETHER_WOOD, "wood");
        SURFACES.put(SoundType.LADDER, "wood");
        SURFACES.put(SoundType.SCAFFOLDING, "wood");
        SURFACES.put(SoundType.STONE, "stone");
        SURFACES.put(SoundType.DEEPSLATE, "stone");
        SURFACES.put(SoundType.DEEPSLATE_BRICKS, "stone");
        SURFACES.put(SoundType.POLISHED_DEEPSLATE, "stone");
        SURFACES.put(SoundType.TUFF, "stone");
        SURFACES.put(SoundType.CALCITE, "stone");
        SURFACES.put(SoundType.BASALT, "stone");
        SURFACES.put(SoundType.NETHER_BRICKS, "stone");
        SURFACES.put(SoundType.NETHERRACK, "nether");
        SURFACES.put(SoundType.SOUL_SAND, "soul");
        SURFACES.put(SoundType.SOUL_SOIL, "soul");
        SURFACES.put(SoundType.METAL, "metal");
        SURFACES.put(SoundType.COPPER, "metal");
        SURFACES.put(SoundType.ANVIL, "metal");
        SURFACES.put(SoundType.CHAIN, "metal");
        SURFACES.put(SoundType.LANTERN, "metal");
        SURFACES.put(SoundType.NETHERITE_BLOCK, "metal");
        SURFACES.put(SoundType.WOOL, "wool");
        SURFACES.put(SoundType.GLASS, "glass");
        SURFACES.put(SoundType.AMETHYST, "glass");
        SURFACES.put(SoundType.MUD, "mud");
        SURFACES.put(SoundType.PACKED_MUD, "mud");
        SURFACES.put(SoundType.MUD_BRICKS, "stone");
        SURFACES.put(SoundType.MOSS, "moss");
        SURFACES.put(SoundType.MOSS_CARPET, "moss");
        SURFACES.put(SoundType.AZALEA_LEAVES, "leaves");
        SURFACES.put(SoundType.CHERRY_LEAVES, "leaves");
        SURFACES.put(SoundType.HONEY_BLOCK, "slime");
        SURFACES.put(SoundType.SLIME_BLOCK, "slime");
        SURFACES.put(SoundType.CORAL_BLOCK, "stone");
    }

    private ContextSampler() {}

    /** Per-entity history needed for derived variables. */
    static final class History {
        Vec3 lastPos;
        float lastBodyYaw;
        float lastSpeed;
        boolean wasOnGround = true;
        float airTime;
        float sinceLanded = 10f;
        float lastFall;
        float peakY;
        float idleTime;
        float moveTime;
        float exertion;
        float sinceHurt = 99f;
        float sinceCombat = 99f;
        int hostileCheck;
        float hostileDistance = 99f;
        float playerDistance = 99f;
        float terrainPitch;
        float[] traits;
        int envCheck;
        boolean nearFire;
        boolean skyExposed = true;
    }

    static void sample(LivingEntity e, Scope s, History h, float dt) {
        Level level = e.level();
        Vec3 pos = e.position();
        if (h.lastPos == null) {
            h.lastPos = pos;
            h.lastBodyYaw = e.yBodyRot;
            h.peakY = (float) pos.y;
        }
        double dx = pos.x - h.lastPos.x;
        double dz = pos.z - h.lastPos.z;
        double dy = pos.y - h.lastPos.y;
        h.lastPos = pos;
        float ground = (float) Math.sqrt(dx * dx + dz * dz);
        if (e.isPassenger()) ground = 0f;
        float yawRad = e.yBodyRot * MathUtil.DEG_TO_RAD;
        float forward = (float) (-dx * Math.sin(yawRad) + dz * Math.cos(yawRad));
        float strafe = (float) (dx * Math.cos(yawRad) + dz * Math.sin(yawRad));
        float accel = (ground - h.lastSpeed) / Math.max(dt, 1e-3f);
        h.lastSpeed = ground;
        float turn = Mth.wrapDegrees(e.yBodyRot - h.lastBodyYaw);
        h.lastBodyYaw = e.yBodyRot;

        s.set(CtxVars.GROUND_SPEED, ground);
        s.set(CtxVars.FORWARD_SPEED, forward);
        s.set(CtxVars.STRAFE_SPEED, strafe);
        s.set(CtxVars.VERTICAL_SPEED, (float) dy);
        s.set(CtxVars.ACCELERATION, accel);
        s.set(CtxVars.TURN_RATE, turn);
        s.set(CtxVars.HEAD_YAW, Mth.wrapDegrees(e.yHeadRot - e.yBodyRot));
        s.set(CtxVars.HEAD_PITCH, e.getXRot());
        boolean moving = ground > 0.015f;
        s.setBool(CtxVars.MOVING, moving);

        boolean onGround = e.onGround();
        if (onGround) {
            if (!h.wasOnGround) {
                h.lastFall = Math.max(0f, h.peakY - (float) pos.y);
                h.sinceLanded = 0f;
            }
            h.airTime = 0f;
            h.peakY = (float) pos.y;
            h.sinceLanded += dt;
        } else {
            h.airTime += dt;
            h.peakY = Math.max(h.peakY, (float) pos.y);
        }
        h.wasOnGround = onGround;
        s.setBool(CtxVars.ON_GROUND, onGround);
        s.set(CtxVars.AIR_TIME, h.airTime);
        s.set(CtxVars.TIME_SINCE_LANDED, h.sinceLanded);
        s.set(CtxVars.LAST_FALL, h.lastFall);
        s.set(CtxVars.FALL_DISTANCE, onGround ? 0f : Math.max(0f, h.peakY - (float) pos.y));
        s.setBool(CtxVars.CLIMBING, e.onClimbable() && !onGround);

        if (moving) {
            h.moveTime += dt;
            h.idleTime = 0f;
        } else {
            h.idleTime += dt;
            h.moveTime = 0f;
        }
        s.set(CtxVars.IDLE_TIME, h.idleTime);
        s.set(CtxVars.MOVE_TIME, h.moveTime);

        boolean sprinting = e.isSprinting();
        float exertTarget = sprinting ? 1f : (e.isSwimming() ? 0.8f : (moving ? 0.25f : 0f));
        if (h.sinceCombat < 3f) exertTarget = Math.max(exertTarget, 0.7f);
        h.exertion += (exertTarget - h.exertion) * MathUtil.approachFactor(exertTarget > h.exertion ? 4f : 10f, dt);
        s.set(CtxVars.EXERTION, h.exertion);

        s.setBool(CtxVars.SNEAKING, e.isCrouching());
        s.setBool(CtxVars.SPRINTING, sprinting);
        s.setBool(CtxVars.CRAWLING, e.hasPose(Pose.SWIMMING) && !e.isInWater());
        s.setBool(CtxVars.SWIMMING, e.isSwimming() || (e.isInWater() && !onGround));
        s.setBool(CtxVars.IN_WATER, e.isInWater());
        s.setBool(CtxVars.UNDERWATER, e.isUnderWater());
        s.setBool(CtxVars.IN_LAVA, e.isInLava());
        s.setBool(CtxVars.FALL_FLYING, e.isFallFlying());
        s.setBool(CtxVars.SPIN_ATTACK, e.isAutoSpinAttack());
        Entity vehicle = e.getVehicle();
        s.setBool(CtxVars.RIDING, vehicle != null);
        s.setString(CtxVars.VEHICLE, vehicleKind(vehicle));
        if (vehicle != null) {
            Vec3 v = vehicle.getDeltaMovement();
            s.set(CtxVars.VEHICLE_SPEED, (float) Math.sqrt(v.x * v.x + v.z * v.z));
        } else {
            s.set(CtxVars.VEHICLE_SPEED, 0f);
        }
        s.setBool(CtxVars.SLEEPING, e.isSleeping());
        s.setBool(CtxVars.BABY, e.isBaby());
        s.set(CtxVars.AGE, e.tickCount / 20f);

        float health = e.getMaxHealth() > 0f ? e.getHealth() / e.getMaxHealth() : 1f;
        s.set(CtxVars.HEALTH, MathUtil.clamp01(health));
        s.set(CtxVars.HURT_TIME, e.hurtTime);
        h.sinceHurt += dt;
        h.sinceCombat += dt;
        s.set(CtxVars.RECENT_HURT, h.sinceHurt);
        s.set(CtxVars.IN_COMBAT, h.sinceCombat < 6f ? 1f : 0f);
        s.setBool(CtxVars.DEAD, e.isDeadOrDying());
        s.set(CtxVars.DEATH_TIME, e.deathTime);
        s.setBool(CtxVars.ON_FIRE, e.isOnFire());
        s.set(CtxVars.FREEZING, MathUtil.clamp01(e.getTicksFrozen() / 140f));
        if (e instanceof Player p) {
            s.set(CtxVars.HUNGER, 1f - p.getFoodData().getFoodLevel() / 20f);
            s.setBool(CtxVars.FISHING, p.fishing != null);
        }

        ItemStack main = e.getMainHandItem();
        ItemStack off = e.getOffhandItem();
        s.setString(CtxVars.MAIN_HAND, ItemCategories.of(main));
        s.setString(CtxVars.OFF_HAND, ItemCategories.of(off));
        boolean using = e.isUsingItem();
        s.setBool(CtxVars.USING_ITEM, using);
        if (using) {
            ItemStack use = e.getUseItem();
            s.setString(CtxVars.USE_ANIM, use.getUseAnimation().name().toLowerCase(Locale.ROOT));
            s.set(CtxVars.USE_TIME, e.getTicksUsingItem() / 20f);
            s.set(CtxVars.LAST_USE_TIME, e.getTicksUsingItem() / 20f);
            s.setBool(CtxVars.USE_HAND_OFF, e.getUsedItemHand() == net.minecraft.world.InteractionHand.OFF_HAND);
        } else {
            s.setString(CtxVars.USE_ANIM, "none");
            s.set(CtxVars.USE_TIME, 0f);
            s.setBool(CtxVars.USE_HAND_OFF, false);
        }
        s.setBool(CtxVars.BLOCKING, e.isBlocking());
        s.setBool(CtxVars.CROSSBOW_CHARGED, main.getItem() instanceof CrossbowItem && CrossbowItem.isCharged(main));
        s.set(CtxVars.SWING, e.getAttackAnim(1f));
        s.setBool(CtxVars.SWINGING, e.swinging);
        boolean mining = MiningTracker.isMining(e);
        s.setBool(CtxVars.MINING, mining);
        s.setString(CtxVars.MINE_TARGET, mining ? MiningTracker.target(e) : "none");
        s.set(CtxVars.ARMOR_WEIGHT, MathUtil.clamp01(e.getArmorValue() / 20f));
        s.setBool(CtxVars.AGGRESSIVE, e instanceof Mob m && m.isAggressive());

        // Environment
        BlockPos below = BlockPos.containing(pos.x, pos.y - 0.2, pos.z);
        BlockState onState = level.getBlockState(below);
        String surface = e.isInWater() ? "water" : SURFACES.getOrDefault(onState.getSoundType(), onState.isAir() ? "air" : "stone");
        s.setString(CtxVars.SURFACE, surface);
        BlockPos at = e.blockPosition();
        s.setBool(CtxVars.RAINING, level.isRainingAt(at.above()));
        s.setBool(CtxVars.THUNDERING, level.isThundering());
        s.set(CtxVars.WIND, WindSystem.strengthAt(e));
        float dayTime = (level.getDayTime() % 24000L) / 24000f;
        s.set(CtxVars.DAYTIME, dayTime);
        s.setBool(CtxVars.IS_NIGHT, dayTime > 0.54f && dayTime < 0.96f);
        s.set(CtxVars.LIGHT, level.getMaxLocalRawBrightness(at));
        s.setBool(CtxVars.COLD, level.getBiome(at).value().coldEnoughToSnow(at));
        s.setString(CtxVars.DIMENSION, level.dimension().location().getPath());
        s.setString(CtxVars.FEET_BLOCK, feetBlock(level.getBlockState(at)));
        s.set(CtxVars.FLUID_DEPTH, (float) e.getFluidHeight(net.minecraft.tags.FluidTags.WATER));
        s.set(CtxVars.TEMPERATURE, level.getBiome(at).value().getBaseTemperature());
        s.set(CtxVars.ALTITUDE, (float) pos.y);
        if (--h.envCheck <= 0) {
            h.envCheck = 10;
            h.nearFire = nearFire(level, at);
            h.skyExposed = level.canSeeSky(at.above());
        }
        s.setBool(CtxVars.NEAR_FIRE, h.nearFire);
        s.setBool(CtxVars.SKY_EXPOSED, h.skyExposed);
        s.setBool(CtxVars.HAS_RIDER, e.isVehicle());
        s.setBool(CtxVars.LEVITATING, e.hasEffect(MobEffects.LEVITATION));
        s.setBool(CtxVars.SLOW_FALLING, e.hasEffect(MobEffects.SLOW_FALLING));
        s.setBool(CtxVars.POISONED, e.hasEffect(MobEffects.POISON));
        s.setBool(CtxVars.WITHERING, e.hasEffect(MobEffects.WITHER));
        s.setBool(CtxVars.BLINDED, e.hasEffect(MobEffects.BLINDNESS) || e.hasEffect(MobEffects.DARKNESS));
        s.setBool(CtxVars.NAUSEOUS, e.hasEffect(MobEffects.CONFUSION));
        s.setBool(CtxVars.INVISIBLE, e.isInvisible());
        if (e instanceof net.minecraft.world.entity.player.Player p) s.setBool(CtxVars.FLYING, p.getAbilities().flying);
        h.terrainPitch += (terrainPitch(level, e) - h.terrainPitch) * MathUtil.approachFactor(0.15f, dt);
        s.set(CtxVars.TERRAIN_PITCH, h.terrainPitch);

        if (--h.hostileCheck <= 0) {
            h.hostileCheck = 10;
            h.hostileDistance = nearestDistance(e, true);
            h.playerDistance = nearestDistance(e, false);
        }
        s.set(CtxVars.HOSTILE_DISTANCE, h.hostileDistance);
        s.setBool(CtxVars.NEAR_HOSTILE, h.hostileDistance < 10f);
        s.set(CtxVars.PLAYER_DISTANCE, h.playerDistance);

        if (h.traits == null) h.traits = traits(e);
        s.set(CtxVars.TRAIT_ENERGY, h.traits[0]);
        s.set(CtxVars.TRAIT_CURIOSITY, h.traits[1]);
        s.set(CtxVars.TRAIT_NERVOUS, h.traits[2]);
        s.set(CtxVars.TRAIT_SOCIAL, h.traits[3]);
        s.set(CtxVars.TRAIT_CONFIDENCE, h.traits[4]);
        s.set(CtxVars.MOOD, mood(s));

        Minecraft mc = Minecraft.getInstance();
        boolean local = e == mc.player;
        s.setBool(CtxVars.LOCAL_PLAYER, local);
        s.setBool(CtxVars.FIRST_PERSON, local && mc.options.getCameraType().isFirstPerson());
        s.set(CtxVars.DISTANCE_TO_CAMERA, (float) mc.gameRenderer.getMainCamera().getPosition().distanceTo(pos));

        species(e, s);
    }

    static void noteHurt(History h) {
        h.sinceHurt = 0f;
        h.sinceCombat = 0f;
    }

    static void noteCombat(History h) {
        h.sinceCombat = 0f;
    }

    /** Deterministic personality from the entity UUID; identical on every client. */
    static float[] traits(LivingEntity e) {
        long seed = e.getUUID().getMostSignificantBits() ^ e.getUUID().getLeastSignificantBits();
        float[] t = new float[5];
        for (int i = 0; i < 5; i++) {
            // Average two samples so traits cluster around the middle like real temperament.
            t[i] = (Hashing.unit(Hashing.combine(seed, i)) + Hashing.unit(Hashing.combine(seed, i + 17))) * 0.5f;
        }
        return t;
    }

    /** -1 (distressed) .. 1 (content), from health, threat, weather and personality. */
    private static float mood(Scope s) {
        float m = 0.3f;
        m -= (1f - s.get(CtxVars.HEALTH)) * 0.8f;
        m -= s.get(CtxVars.NEAR_HOSTILE) * (0.3f + s.get(CtxVars.TRAIT_NERVOUS) * 0.5f);
        m -= s.get(CtxVars.RAINING) * 0.15f;
        m += (s.get(CtxVars.TRAIT_CONFIDENCE) - 0.5f) * 0.4f;
        m -= s.get(CtxVars.FREEZING) * 0.5f;
        return MathUtil.clamp(m, -1f, 1f);
    }

    private static float terrainPitch(Level level, LivingEntity e) {
        float width = e.getBbWidth();
        if (width < 0.8f || !e.onGround()) return 0f;
        double yaw = e.yBodyRot * MathUtil.DEG_TO_RAD;
        double fx = -Math.sin(yaw) * width * 0.6, fz = Math.cos(yaw) * width * 0.6;
        double front = groundHeight(level, e.getX() + fx, e.getY(), e.getZ() + fz);
        double back = groundHeight(level, e.getX() - fx, e.getY(), e.getZ() - fz);
        return (float) Math.toDegrees(Math.atan2(front - back, width * 1.2));
    }

    private static double groundHeight(Level level, double x, double y, double z) {
        BlockPos p = BlockPos.containing(x, y + 0.5, z);
        for (int i = 0; i < 3; i++) {
            BlockState st = level.getBlockState(p);
            if (!st.getCollisionShape(level, p).isEmpty()) {
                return p.getY() + st.getCollisionShape(level, p).max(net.minecraft.core.Direction.Axis.Y);
            }
            p = p.below();
        }
        return y;
    }

    private static float nearestDistance(LivingEntity e, boolean hostile) {
        AABB box = e.getBoundingBox().inflate(16);
        double best = 99;
        List<? extends Entity> list = hostile
                ? e.level().getEntitiesOfClass(Mob.class, box, m -> m instanceof Enemy && m.isAlive() && m != e)
                : e.level().getEntitiesOfClass(Player.class, box, p -> p != e && !p.isSpectator());
        for (Entity o : list) best = Math.min(best, o.distanceTo(e));
        return (float) best;
    }

    private static String vehicleKind(Entity v) {
        if (v == null) return "none";
        if (v instanceof Boat) return "boat";
        if (v instanceof AbstractMinecart) return "minecart";
        if (v instanceof Camel) return "camel";
        if (v instanceof AbstractHorse) return "horse";
        if (v instanceof Strider) return "strider";
        if (v instanceof net.minecraft.world.entity.animal.Pig) return "pig";
        if (v instanceof LivingEntity) return "creature";
        return "other";
    }

    /** Blocks the entity is standing inside that change how it moves. */
    private static String feetBlock(BlockState st) {
        net.minecraft.world.level.block.Block b = st.getBlock();
        if (b == Blocks.COBWEB) return "cobweb";
        if (b == Blocks.POWDER_SNOW) return "powder_snow";
        if (b == Blocks.SWEET_BERRY_BUSH) return "berry_bush";
        if (b == Blocks.HONEY_BLOCK) return "honey";
        if (b == Blocks.SCAFFOLDING) return "scaffolding";
        if (b == Blocks.BUBBLE_COLUMN) return "bubble_column";
        if (b == Blocks.SNOW) return "snow";
        if (b == Blocks.SOUL_SAND || b == Blocks.SOUL_SOIL) return "soul_sand";
        if (b == Blocks.MUD) return "mud";
        if (st.is(net.minecraft.tags.BlockTags.FLOWERS) || st.is(net.minecraft.tags.BlockTags.REPLACEABLE_BY_TREES)) return "foliage";
        return st.isAir() ? "air" : "other";
    }

    private static boolean nearFire(Level level, BlockPos at) {
        for (BlockPos p : BlockPos.betweenClosed(at.offset(-2, -1, -2), at.offset(2, 1, 2))) {
            BlockState st = level.getBlockState(p);
            if (st.is(net.minecraft.tags.BlockTags.CAMPFIRES) || st.is(net.minecraft.tags.BlockTags.FIRE) || st.is(Blocks.LAVA) || st.is(Blocks.MAGMA_BLOCK)) return true;
        }
        return false;
    }

    /** Stable names for the dragon's phase ids (EnderDragonPhase.toString() embeds the id, unsuitable for matching). */
    private static final String[] DRAGON_PHASES = {"holding_pattern", "strafe_player", "landing_approach", "landing", "takeoff", "sitting_flaming",
            "sitting_scanning", "sitting_attacking", "charging_player", "dying", "hovering"};

    static String dragonPhase(int id) {
        return id >= 0 && id < DRAGON_PHASES.length ? DRAGON_PHASES[id] : "unknown";
    }

    private static boolean started(AnimationState a) {
        return a.isStarted();
    }

    private static void species(LivingEntity e, Scope s) {
        if (e instanceof TamableAnimal t) {
            s.setBool(CtxVars.TAME, t.isTame());
            s.setBool(CtxVars.SITTING, t.isInSittingPose());
        }
        if (e instanceof NeutralMob n) s.setBool(CtxVars.ANGRY, n.isAngry());
        if (e instanceof net.minecraft.world.entity.ambient.Bat bat) s.setBool(CtxVars.SLEEPING, bat.isResting());
        if (e instanceof Animal a) s.setBool(CtxVars.IN_LOVE, a.isInLove());
        if (e instanceof Mob m) s.setBool(CtxVars.LEASHED, m.isLeashed());

        if (e instanceof Wolf w) {
            s.setBool(CtxVars.SHAKING, w.getWetShade(1f) < 0.99f);
            s.setBool(CtxVars.INTERESTED, w.isInterested());
        } else if (e instanceof Cat c) {
            s.setBool(CtxVars.LYING, c.isLying());
            s.setBool(CtxVars.SITTING_POSE, c.isInSittingPose());
        } else if (e instanceof Fox f) {
            s.setBool(CtxVars.SITTING, f.isSitting());
            s.setBool(CtxVars.SLEEPING, f.isSleeping());
            s.setBool(CtxVars.POUNCING, f.isPouncing());
            s.setBool(CtxVars.CROUCHING, f.isCrouching());
            s.setBool(CtxVars.INTERESTED, f.isInterested());
        } else if (e instanceof Panda p) {
            s.setBool(CtxVars.ROLLING, p.isRolling());
            s.setBool(CtxVars.SITTING, p.isSitting());
            s.setBool(CtxVars.ON_BACK, p.isOnBack());
            s.setBool(CtxVars.SNEEZING, p.isSneezing());
            s.setBool(CtxVars.EATING, p.isEating());
            s.setString(CtxVars.GENE, p.getMainGene().getSerializedName());
        } else if (e instanceof Bee b) {
            s.setBool(CtxVars.NECTAR, b.hasNectar());
            s.setBool(CtxVars.FLYING, b.isFlying());
        } else if (e instanceof Parrot p) {
            s.setBool(CtxVars.DANCING, p.isPartyParrot());
            s.setBool(CtxVars.FLYING, p.isFlying());
        } else if (e instanceof Sheep sh) {
            s.setBool(CtxVars.EATING, sh.getHeadEatPositionScale(1f) > 0.01f);
        } else if (e instanceof PolarBear pb) {
            s.setBool(CtxVars.STANDING, pb.isStanding());
        } else if (e instanceof Turtle t) {
            s.setBool(CtxVars.HAS_EGG, t.hasEgg());
            s.setBool(CtxVars.LAYING_EGG, t.isLayingEgg());
        } else if (e instanceof Rabbit r) {
            s.set(CtxVars.JUMP_PROGRESS, r.getJumpCompletion(1f));
        } else if (e instanceof Goat g) {
            s.setBool(CtxVars.SCREAMING, g.isScreamingGoat());
            s.setBool(CtxVars.RAMMING, g.getRammingXHeadRot() > 0.1f);
        } else if (e instanceof Camel c) {
            s.setBool(CtxVars.SITTING, c.isCamelVisuallySitting());
            s.setBool(CtxVars.CHARGING, c.isDashing());
            s.setBool(CtxVars.SADDLED, c.isSaddled());
        } else if (e instanceof AbstractHorse hz) {
            s.setBool(CtxVars.EATING, hz.isEating());
            s.setBool(CtxVars.STANDING, hz.isStanding());
            s.setBool(CtxVars.SADDLED, hz.isSaddled());
        } else if (e instanceof Sniffer sn) {
            s.setBool(CtxVars.SNIFFING, sn.isSearching());
            s.setBool(CtxVars.DIGGING, started(sn.diggingAnimationState));
        } else if (e instanceof Axolotl ax) {
            s.setBool(CtxVars.PLAYING_DEAD, ax.isPlayingDead());
        } else if (e instanceof Allay al) {
            s.setBool(CtxVars.DANCING, al.isDancing());
            s.setBool(CtxVars.HOLDING, al.hasItemInHand());
        } else if (e instanceof IronGolem ig) {
            s.set(CtxVars.ATTACK_TICK, ig.getAttackAnimationTick());
            s.setBool(CtxVars.HOLDING, ig.getOfferFlowerTick() > 0);
        } else if (e instanceof Creeper cr) {
            s.set(CtxVars.SWELL, cr.getSwelling(1f));
            s.setBool(CtxVars.POWERED, cr.isPowered());
            s.setBool(CtxVars.CHARGING, cr.getSwellDir() > 0);
        } else if (e instanceof EnderMan en) {
            s.setBool(CtxVars.CREEPY, en.isCreepy());
            s.setBool(CtxVars.CARRYING, en.getCarriedBlock() != null);
        } else if (e instanceof Ghast g) {
            s.setBool(CtxVars.CHARGING, g.isCharging());
        } else if (e instanceof Blaze b) {
            s.setBool(CtxVars.CHARGING, b.isOnFire());
        } else if (e instanceof Slime sl) {
            s.set(CtxVars.SQUISH, sl.squish);
            s.set(CtxVars.SIZE, sl.getSize());
        } else if (e instanceof Guardian gu) {
            s.setBool(CtxVars.ATTACKING, gu.hasActiveAttackTarget());
        } else if (e instanceof Ravager rv) {
            s.set(CtxVars.ATTACK_TICK, rv.getAttackTick());
            s.setBool(CtxVars.STUNNED, rv.getStunnedTick() > 0);
            s.setBool(CtxVars.ROARING, rv.getRoarTick() > 0);
        } else if (e instanceof Strider st) {
            s.setBool(CtxVars.SUFFOCATING, st.isSuffocating());
            s.setBool(CtxVars.SADDLED, st.isSaddled());
        } else if (e instanceof Warden wd) {
            s.setBool(CtxVars.EMERGING, started(wd.emergeAnimationState));
            s.setBool(CtxVars.DIGGING, started(wd.diggingAnimationState));
            s.setBool(CtxVars.ROARING, started(wd.roarAnimationState));
            s.setBool(CtxVars.SNIFFING, started(wd.sniffAnimationState));
            s.setBool(CtxVars.CHARGING, started(wd.sonicBoomAnimationState));
            s.setBool(CtxVars.ATTACKING, started(wd.attackAnimationState));
            s.set(CtxVars.ATTACK_TICK, wd.getClientAngerLevel() / 80f);
        } else if (e instanceof Piglin pg) {
            s.setBool(CtxVars.DANCING, pg.isDancing());
            s.setString(CtxVars.ARM_POSE, pg.getArmPose().name().toLowerCase(Locale.ROOT));
            s.setBool(CtxVars.ADMIRING, pg.getArmPose() == net.minecraft.world.entity.monster.piglin.PiglinArmPose.ADMIRING_ITEM);
        } else if (e instanceof Spider sp) {
            s.setBool(CtxVars.CLIMBING, sp.isClimbing());
        } else if (e instanceof Hoglin ho) {
            s.set(CtxVars.ATTACK_TICK, ho.getAttackAnimationRemainingTicks());
        } else if (e instanceof Zoglin zo) {
            s.set(CtxVars.ATTACK_TICK, zo.getAttackAnimationRemainingTicks());
        } else if (e instanceof WitherBoss wb) {
            s.setBool(CtxVars.INVULNERABLE, wb.getInvulnerableTicks() > 0);
            s.setBool(CtxVars.POWERED, wb.isPowered());
        } else if (e instanceof EnderDragon dr) {
            s.setString(CtxVars.PHASE, dragonPhase(dr.getPhaseManager().getCurrentPhase().getPhase().getId()));
        } else if (e instanceof Vex vx) {
            s.setBool(CtxVars.CHARGING, vx.isCharging());
        }
        if (e instanceof AbstractIllager il) {
            s.setString(CtxVars.ARM_POSE, il.getArmPose().name().toLowerCase(Locale.ROOT));
            if (il instanceof SpellcasterIllager sc) s.setBool(CtxVars.CASTING, sc.isCastingSpell());
        }
        if (e instanceof Raider r) s.setBool(CtxVars.CELEBRATING, r.isCelebrating());
        if (e instanceof AbstractVillager av) {
            s.setBool(CtxVars.TRADING, av.isTrading());
            if (av instanceof Villager v) {
                s.setString(CtxVars.PROFESSION, v.getVillagerData().getProfession().name());
                s.set(CtxVars.VILLAGER_LEVEL, v.getVillagerData().getLevel());
                s.setBool(CtxVars.UNHAPPY, v.getUnhappyCounter() > 0);
            } else {
                s.setString(CtxVars.PROFESSION, "trader");
            }
        }
    }

    static int stringId(String s) {
        return StringIds.id(s);
    }
}
