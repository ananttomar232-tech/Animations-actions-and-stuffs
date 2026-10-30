package com.motionworks.common;

import com.motionworks.engine.expr.Vars;

/**
 * Every context variable the samplers publish to animation expressions. Authored clips may
 * only rely on these names; {@code docs/CONTEXT_VARIABLES.md} documents units and meaning.
 */
public final class CtxVars {
    private CtxVars() {}

    // Movement
    public static final int GROUND_SPEED = Vars.id("q.ground_speed");
    public static final int FORWARD_SPEED = Vars.id("q.forward_speed");
    public static final int STRAFE_SPEED = Vars.id("q.strafe_speed");
    public static final int VERTICAL_SPEED = Vars.id("q.vertical_speed");
    public static final int ACCELERATION = Vars.id("q.acceleration");
    public static final int LIMB_SWING = Vars.id("q.limb_swing");
    public static final int LIMB_SWING_AMOUNT = Vars.id("q.limb_swing_amount");
    public static final int MOVING = Vars.id("q.moving");
    public static final int TURN_RATE = Vars.id("q.turn_rate");
    public static final int HEAD_YAW = Vars.id("q.head_yaw");
    public static final int HEAD_PITCH = Vars.id("q.head_pitch");
    public static final int ON_GROUND = Vars.id("q.is_on_ground");
    public static final int AIR_TIME = Vars.id("q.air_time");
    public static final int TIME_SINCE_LANDED = Vars.id("q.time_since_landed");
    public static final int LAST_FALL = Vars.id("q.last_fall");
    public static final int FALL_DISTANCE = Vars.id("q.fall_distance");
    public static final int IDLE_TIME = Vars.id("q.idle_time");
    public static final int MOVE_TIME = Vars.id("q.move_time");
    public static final int CLIMBING = Vars.id("q.is_climbing");
    public static final int TERRAIN_PITCH = Vars.id("q.terrain_pitch");

    // Stance / state
    public static final int SNEAKING = Vars.id("q.is_sneaking");
    public static final int SPRINTING = Vars.id("q.is_sprinting");
    public static final int CRAWLING = Vars.id("q.is_crawling");
    public static final int SWIMMING = Vars.id("q.is_swimming");
    public static final int IN_WATER = Vars.id("q.is_in_water");
    public static final int UNDERWATER = Vars.id("q.is_underwater");
    public static final int IN_LAVA = Vars.id("q.is_in_lava");
    public static final int FALL_FLYING = Vars.id("q.is_fall_flying");
    public static final int RIDING = Vars.id("q.is_riding");
    public static final int VEHICLE = Vars.id("q.vehicle");
    public static final int VEHICLE_SPEED = Vars.id("q.vehicle_speed");
    public static final int SLEEPING = Vars.id("q.is_sleeping");
    public static final int BABY = Vars.id("q.is_baby");
    public static final int AGE = Vars.id("q.age");
    public static final int SPIN_ATTACK = Vars.id("q.is_spin_attack");

    // Health & reactions
    public static final int HEALTH = Vars.id("q.health");
    public static final int HURT_TIME = Vars.id("q.hurt_time");
    public static final int RECENT_HURT = Vars.id("q.recent_hurt");
    public static final int HURT_DIR = Vars.id("q.hurt_dir");
    public static final int HURT_KIND = Vars.id("q.hurt_kind");
    public static final int HURT_AMOUNT = Vars.id("q.hurt_amount");
    public static final int DEAD = Vars.id("q.is_dead");
    public static final int DEATH_TIME = Vars.id("q.death_time");
    public static final int ON_FIRE = Vars.id("q.is_on_fire");
    public static final int FREEZING = Vars.id("q.freezing");
    public static final int IN_COMBAT = Vars.id("q.in_combat");
    public static final int EXERTION = Vars.id("q.exertion");
    public static final int HUNGER = Vars.id("q.hunger");

    // Items & actions
    public static final int MAIN_HAND = Vars.id("q.main_hand");
    public static final int OFF_HAND = Vars.id("q.off_hand");
    public static final int USING_ITEM = Vars.id("q.is_using_item");
    public static final int USE_ANIM = Vars.id("q.use_anim");
    public static final int USE_TIME = Vars.id("q.use_time");
    public static final int USE_HAND_OFF = Vars.id("q.use_offhand");
    public static final int SWING = Vars.id("q.swing_progress");
    public static final int SWINGING = Vars.id("q.is_swinging");
    public static final int MINING = Vars.id("q.is_mining");
    public static final int MINE_TARGET = Vars.id("q.mine_target");
    public static final int BLOCKING = Vars.id("q.is_blocking");
    public static final int CROSSBOW_CHARGED = Vars.id("q.crossbow_charged");
    public static final int ARMOR_WEIGHT = Vars.id("q.armor_weight");
    public static final int COMBO = Vars.id("q.combo");
    public static final int ATTACK_STRENGTH = Vars.id("q.attack_strength");
    public static final int AGGRESSIVE = Vars.id("q.is_aggressive");
    public static final int INTERACT_TARGET = Vars.id("q.interact_target");
    public static final int EVENT_ARG = Vars.id("q.event_arg");
    public static final int EVENT_DIR = Vars.id("q.event_dir");
    public static final int EVENT_HEIGHT = Vars.id("q.event_height");

    // Environment
    public static final int SURFACE = Vars.id("q.surface");
    public static final int RAINING = Vars.id("q.is_raining");
    public static final int THUNDERING = Vars.id("q.is_thundering");
    public static final int WIND = Vars.id("q.wind");
    public static final int DAYTIME = Vars.id("q.time_of_day");
    public static final int IS_NIGHT = Vars.id("q.is_night");
    public static final int LIGHT = Vars.id("q.light");
    public static final int NEAR_HOSTILE = Vars.id("q.near_hostile");
    public static final int HOSTILE_DISTANCE = Vars.id("q.hostile_distance");
    public static final int PLAYER_DISTANCE = Vars.id("q.player_distance");
    public static final int COLD = Vars.id("q.is_cold");
    public static final int DIMENSION = Vars.id("q.dimension");

    // Personality & social
    public static final int TRAIT_ENERGY = Vars.id("q.trait_energy");
    public static final int TRAIT_CURIOSITY = Vars.id("q.trait_curiosity");
    public static final int TRAIT_NERVOUS = Vars.id("q.trait_nervous");
    public static final int TRAIT_SOCIAL = Vars.id("q.trait_social");
    public static final int TRAIT_CONFIDENCE = Vars.id("q.trait_confidence");
    public static final int IN_CONVERSATION = Vars.id("q.in_conversation");
    public static final int SPEAKING = Vars.id("q.is_speaking");
    public static final int CONVERSATION_SIZE = Vars.id("q.conversation_size");
    public static final int MOOD = Vars.id("q.mood");

    // Ownership / taming / breeding
    public static final int TAME = Vars.id("q.is_tame");
    public static final int SITTING = Vars.id("q.is_sitting");
    public static final int ANGRY = Vars.id("q.is_angry");
    public static final int IN_LOVE = Vars.id("q.is_in_love");
    public static final int LEASHED = Vars.id("q.is_leashed");
    public static final int SADDLED = Vars.id("q.is_saddled");

    // Species-specific states (all 0/1 unless noted)
    public static final int EATING = Vars.id("q.is_eating");
    public static final int STANDING = Vars.id("q.is_standing");
    public static final int CHARGING = Vars.id("q.is_charging");
    public static final int SWELL = Vars.id("q.swell");
    public static final int POWERED = Vars.id("q.is_powered");
    public static final int SHAKING = Vars.id("q.is_shaking");
    public static final int INTERESTED = Vars.id("q.is_interested");
    public static final int LYING = Vars.id("q.is_lying");
    public static final int POUNCING = Vars.id("q.is_pouncing");
    public static final int CROUCHING = Vars.id("q.is_crouching");
    public static final int ROLLING = Vars.id("q.is_rolling");
    public static final int ON_BACK = Vars.id("q.is_on_back");
    public static final int SNEEZING = Vars.id("q.is_sneezing");
    public static final int GENE = Vars.id("q.gene");
    public static final int NECTAR = Vars.id("q.has_nectar");
    public static final int DANCING = Vars.id("q.is_dancing");
    public static final int FLYING = Vars.id("q.is_flying");
    public static final int PROFESSION = Vars.id("q.profession");
    public static final int VILLAGER_LEVEL = Vars.id("q.villager_level");
    public static final int TRADING = Vars.id("q.is_trading");
    public static final int UNHAPPY = Vars.id("q.is_unhappy");
    public static final int ADMIRING = Vars.id("q.is_admiring");
    public static final int CELEBRATING = Vars.id("q.is_celebrating");
    public static final int CASTING = Vars.id("q.is_casting");
    public static final int ARM_POSE = Vars.id("q.arm_pose");
    public static final int CREEPY = Vars.id("q.is_creepy");
    public static final int CARRYING = Vars.id("q.is_carrying");
    public static final int ATTACK_TICK = Vars.id("q.attack_tick");
    public static final int STUNNED = Vars.id("q.is_stunned");
    public static final int ROARING = Vars.id("q.is_roaring");
    public static final int EMERGING = Vars.id("q.is_emerging");
    public static final int DIGGING = Vars.id("q.is_digging");
    public static final int SNIFFING = Vars.id("q.is_sniffing");
    public static final int SQUISH = Vars.id("q.squish");
    public static final int SIZE = Vars.id("q.size");
    public static final int HAS_EGG = Vars.id("q.has_egg");
    public static final int LAYING_EGG = Vars.id("q.is_laying_egg");
    public static final int SUFFOCATING = Vars.id("q.is_suffocating");
    public static final int PHASE = Vars.id("q.phase");
    public static final int INVULNERABLE = Vars.id("q.invulnerable");
    public static final int ATTACKING = Vars.id("q.is_attacking");
    public static final int SCREAMING = Vars.id("q.is_screaming");
    public static final int RAMMING = Vars.id("q.is_ramming");
    public static final int HOLDING = Vars.id("q.is_holding");
    public static final int JUMP_PROGRESS = Vars.id("q.jump_progress");
    public static final int PLAYING_DEAD = Vars.id("q.is_playing_dead");
    public static final int SITTING_POSE = Vars.id("q.is_sitting_pose");

    // Viewer
    public static final int LOCAL_PLAYER = Vars.id("q.is_local_player");
    public static final int FIRST_PERSON = Vars.id("q.first_person");
    public static final int CINEMATIC = Vars.id("q.in_cinematic");
    public static final int DISTANCE_TO_CAMERA = Vars.id("q.camera_distance");
}
