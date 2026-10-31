package com.motionworks.client.anim;

import com.motionworks.client.rig.ModelRig;
import com.motionworks.client.rig.RigFactory;
import com.motionworks.client.rig.RigProfile;
import com.motionworks.common.CtxVars;
import com.motionworks.common.ItemCategories;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.expr.ExprParser;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.StringIds;
import com.motionworks.engine.expr.Vars;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.procedural.ExpressionDriver;
import com.motionworks.engine.procedural.LifeNoise;
import com.motionworks.engine.procedural.SpringBone;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.LayerSpec;
import net.minecraft.client.model.EntityModel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Deque;
import java.util.List;

/** Client-side animation state for one living entity. */
public final class EntityAnimator {
    private static final int PREV_MAIN_HAND = Vars.id("q.prev_main_hand");

    public final LivingEntity entity;
    final String typeId;
    final long seed;
    final ContextSampler.History history = new ContextSampler.History();
    private final Scope staging = new Scope();
    private final Deque<String> pending = new ArrayDeque<>();

    private AnimationController controller;
    private ModelRig modelRig;
    private EntityModel<?> boundModel;
    private int generation = -1;
    private double lastClock = Double.NaN;
    private boolean sampled;

    // Edge-detection memory
    private boolean wasOnGround = true, wasSwinging, wasUsing, wasSneaking, wasSprinting, wasMoving, wasInWater,
            wasUnderwater, wasRiding, wasSleeping, wasFlying, wasAggressive, wasDead, wasClimbing, wasBlocking, wasInCombat, wasCharged;
    private String lastOff = "";
    private final net.minecraft.world.item.Item[] lastArmor = new net.minecraft.world.item.Item[4];
    private boolean armorKnown;
    private String lastMain = "";
    private int lastHurtTime;
    private int combo;
    private float sinceAttack = 9f;
    private float sinceHurtEvent = 9f;

    EntityAnimator(LivingEntity entity) {
        this.entity = entity;
        this.typeId = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(entity.getType()).toString();
        this.seed = entity.getUUID().getMostSignificantBits() * 31 + entity.getUUID().getLeastSignificantBits();
    }

    public AnimationController controller() {
        return controller;
    }

    public ModelRig modelRig() {
        return modelRig;
    }

    public Scope scope() {
        return controller != null ? controller.scope() : staging;
    }

    AnimationLibrary.EntityFamily family() {
        AnimationLibrary.EntityFamily f = AnimationLibrary.INSTANCE.family(typeId);
        if (f != null) return f;
        if (entity instanceof Player) f = AnimationLibrary.INSTANCE.family("minecraft:player");
        return f != null ? f : new AnimationLibrary.EntityFamily("generic", List.of(typeId, "@living"));
    }

    /** Binds (or rebinds) a controller to the model that is about to render. */
    boolean bind(EntityModel<?> model) {
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        if (controller != null && model == boundModel && generation == lib.generation()) return true;
        AnimationLibrary.EntityFamily fam = family();
        RigProfile profile = lib.rig(fam.rig());
        ModelRig mr = RigFactory.get(model, profile);
        Collection<AnimationClip> clips = lib.clips().forTargets(fam.targets());
        Scope previous = controller != null ? controller.scope() : staging;
        AnimationController c = new AnimationController(mr.rig, seed, LayerSpec.STANDARD, clips);
        System.arraycopy(previous.values, 0, grow(c.scope(), previous.values.length), 0, previous.values.length);
        addProcedurals(c, mr);
        c.setEventSink(ClipEventDispatcher.INSTANCE);
        ClipEventDispatcher.INSTANCE.register(c, entity);
        controller = c;
        modelRig = mr;
        boundModel = model;
        generation = lib.generation();
        while (!pending.isEmpty()) controller.fire(pending.poll());
        return true;
    }

    private static float[] grow(Scope s, int min) {
        if (s.values.length < min) s.set(min - 1, 0f);
        return s.values;
    }

    private void addProcedurals(AnimationController c, ModelRig mr) {
        RigProfile p = mr.profile;
        for (RigProfile.Spring s : p.springs) {
            com.motionworks.engine.expr.Expr[] t = new com.motionworks.engine.expr.Expr[3];
            for (int i = 0; i < 3; i++) t[i] = s.targets()[i] == null ? null : ExprParser.parse(s.targets()[i]);
            c.addModifier(new SpringBone(mr.rig.indexOf(s.bone()), t, s.stiffness(), s.damping(), s.limit()));
        }
        int salt = 0;
        for (RigProfile.Noise n : p.noise) {
            c.addModifier(new LifeNoise(mr.rig.indexOf(n.bone()), n.amplitude(), n.frequency(), ExprParser.parse(n.scale()), salt++));
        }
        for (RigProfile.Driver d : p.drivers) {
            com.motionworks.engine.expr.Expr[] e = new com.motionworks.engine.expr.Expr[3];
            for (int i = 0; i < 3; i++) e[i] = d.exprs()[i] == null ? null : ExprParser.parse(d.exprs()[i]);
            c.addModifier(new ExpressionDriver(mr.rig.indexOf(d.bone()), d.group(), e, d.halfLife()));
        }
    }

    /** Client tick: sample context and turn state changes into animation events. */
    void tick() {
        Scope s = scope();
        ContextSampler.sample(entity, s, history, 0.05f);
        sampled = true;
        if (controller != null) controller.setSelectionEpoch(entity.level().getGameTime() / 100L);
        sinceAttack += 0.05f;
        sinceHurtEvent += 0.05f;
        if (sinceAttack > 1.2f) combo = 0;
        s.set(CtxVars.COMBO, combo);

        boolean onGround = s.get(CtxVars.ON_GROUND) != 0f;
        if (onGround && !wasOnGround) fire("land");
        if (!onGround && wasOnGround && s.get(CtxVars.VERTICAL_SPEED) > 0.08f && !entity.isPassenger()) fire("jump");
        wasOnGround = onGround;

        boolean swinging = entity.swinging;
        if (swinging && !wasSwinging) {
            fire("swing");
            if (!(entity instanceof Player)) fire("attack");
        }
        wasSwinging = swinging;

        boolean using = entity.isUsingItem();
        if (using && !wasUsing) fire("use_start");
        if (!using && wasUsing) fire(entity.getUseItemRemainingTicks() <= 1 ? "use_finish" : "use_stop");
        wasUsing = using;

        boolean blocking = entity.isBlocking();
        if (blocking && !wasBlocking) fire("guard_up");
        if (!blocking && wasBlocking) fire("guard_down");
        wasBlocking = blocking;

        String main = ItemCategories.of(entity.getMainHandItem());
        boolean mainChanged = !main.equals(lastMain);
        if (mainChanged) {
            s.set(PREV_MAIN_HAND, StringIds.id(lastMain));
            if (!lastMain.isEmpty()) fire("item_switch");
            lastMain = main;
        }

        String off = ItemCategories.of(entity.getOffhandItem());
        if (!off.equals(lastOff)) {
            // Main and off hand changing in the same tick is the swap-hands key.
            if (!lastOff.isEmpty() && mainChanged) fire("offhand_switch");
            lastOff = off;
        }
        int slot = 0;
        for (net.minecraft.world.entity.EquipmentSlot es : new net.minecraft.world.entity.EquipmentSlot[] {
                net.minecraft.world.entity.EquipmentSlot.HEAD, net.minecraft.world.entity.EquipmentSlot.CHEST,
                net.minecraft.world.entity.EquipmentSlot.LEGS, net.minecraft.world.entity.EquipmentSlot.FEET}) {
            net.minecraft.world.item.Item now = entity.getItemBySlot(es).getItem();
            if (armorKnown && now != lastArmor[slot]) {
                String name = es == net.minecraft.world.entity.EquipmentSlot.HEAD ? "head" : es == net.minecraft.world.entity.EquipmentSlot.CHEST ? "chest"
                        : es == net.minecraft.world.entity.EquipmentSlot.LEGS ? "legs" : "feet";
                fire(now == net.minecraft.world.item.Items.AIR ? "armor_off:" + name : "armor_on:" + name);
            }
            lastArmor[slot++] = now;
        }
        armorKnown = true;
        boolean inCombat = s.get(CtxVars.IN_COMBAT) != 0f;
        edge(inCombat, wasInCombat, "combat_enter", "combat_exit");
        wasInCombat = inCombat;
        boolean charged = s.get(CtxVars.CROSSBOW_CHARGED) != 0f;
        if (wasCharged && !charged && !entity.isUsingItem()) fire("crossbow_fire");
        wasCharged = charged;
        edge(s.get(CtxVars.SNEAKING) != 0f, wasSneaking, "sneak_start", "sneak_stop");
        wasSneaking = s.get(CtxVars.SNEAKING) != 0f;
        edge(s.get(CtxVars.SPRINTING) != 0f, wasSprinting, "sprint_start", "sprint_stop");
        wasSprinting = s.get(CtxVars.SPRINTING) != 0f;
        boolean moving = s.get(CtxVars.GROUND_SPEED) > (wasMoving ? 0.01f : 0.03f);
        edge(moving, wasMoving, "start_moving", "stop_moving");
        wasMoving = moving;
        boolean inWater = entity.isInWater();
        edge(inWater, wasInWater, "enter_water", "exit_water");
        wasInWater = inWater;
        boolean under = entity.isUnderWater();
        edge(under, wasUnderwater, "submerge", "surface");
        wasUnderwater = under;
        boolean riding = entity.isPassenger();
        edge(riding, wasRiding, "mount", "dismount");
        wasRiding = riding;
        // Sampled state, so species that "sleep" outside a bed (resting bats, sleeping foxes) also fire sleep/wake.
        boolean sleeping = s.get(CtxVars.SLEEPING) != 0f;
        edge(sleeping, wasSleeping, "sleep", "wake");
        wasSleeping = sleeping;
        boolean flying = entity.isFallFlying();
        edge(flying, wasFlying, "glide_start", "glide_stop");
        wasFlying = flying;
        boolean creativeFlight = entity instanceof Player && s.get(CtxVars.FLYING) != 0f;
        edge(creativeFlight, wasCreativeFlying, "fly_start", "fly_stop");
        wasCreativeFlying = creativeFlight;
        boolean spin = entity.isAutoSpinAttack();
        edge(spin, wasSpinning, "riptide_start", "riptide_stop");
        wasSpinning = spin;
        boolean climbing = s.get(CtxVars.CLIMBING) != 0f;
        edge(climbing, wasClimbing, "climb_start", "climb_stop");
        wasClimbing = climbing;
        stateEdge(CtxVars.SITTING, s.get(CtxVars.SITTING) != 0f, "sit_down", "stand_up");
        stateEdge(CtxVars.LYING, s.get(CtxVars.LYING) != 0f, "lie_down", "get_up");
        stateEdge(CtxVars.EATING, s.get(CtxVars.EATING) != 0f, "eat_start", "eat_stop");
        stateEdge(CtxVars.ANGRY, s.get(CtxVars.ANGRY) != 0f, "anger", "calm");
        stateEdge(CtxVars.STANDING, s.get(CtxVars.STANDING) != 0f, "rear_up", "rear_down");
        stateEdge(CtxVars.ADMIRING, s.get(CtxVars.ADMIRING) != 0f, "admire_start", "admire_stop");
        stateEdge(CtxVars.TRADING, s.get(CtxVars.TRADING) != 0f, "trade_open", "trade_close");
        stateEdge(CtxVars.NEAR_HOSTILE, s.get(CtxVars.NEAR_HOSTILE) != 0f, "danger_near", "danger_clear");
        stateEdge(CtxVars.RAINING, s.get(CtxVars.RAINING) != 0f, "rain_start", "rain_stop");
        stateEdge(CtxVars.IS_NIGHT, s.get(CtxVars.IS_NIGHT) != 0f, "nightfall", "daybreak");
        stateEdge(CtxVars.HEALTH, s.get(CtxVars.HEALTH) < 0.3f, "wounded", "recovered");
        stateEdge(CtxVars.LIGHT, s.get(CtxVars.LIGHT) < 4f, "enter_dark", "exit_dark");
        stateEdge(CtxVars.HUNGER, s.get(CtxVars.HUNGER) > 0.7f, "hungry", "sated");
        stateEdge(CtxVars.AT_LEDGE, s.get(CtxVars.AT_LEDGE) != 0f, "ledge_reached", "ledge_left");
        stateEdge(CtxVars.BABY, s.get(CtxVars.BABY) != 0f, "baby", "grow_up");
        stateEdge(CtxVars.PLAYING_DEAD, s.get(CtxVars.PLAYING_DEAD) != 0f, "play_dead", "revive");
        stateEdge(CtxVars.DIGGING, s.get(CtxVars.DIGGING) != 0f, "dig_start", "dig_end");
        stateEdge(CtxVars.LAYING_EGG, s.get(CtxVars.LAYING_EGG) != 0f, "lay_start", "lay_end");
        stateEdge(CtxVars.STUNNED, s.get(CtxVars.STUNNED) != 0f, "stunned", "unstunned");
        stateEdge(CtxVars.CHARGING, s.get(CtxVars.CHARGING) != 0f, "charge_start", "charge_stop");
        boolean aggressive = entity instanceof Mob m && m.isAggressive();
        if (aggressive && !wasAggressive) fire("aggro");
        wasAggressive = aggressive;
        boolean dead = entity.isDeadOrDying();
        if (dead && !wasDead) fire("death");
        wasDead = dead;

        // Fallback hurt detection when the damage-event hook did not run (e.g. other mods).
        if (entity.hurtTime > lastHurtTime && entity.hurtTime >= entity.hurtDuration - 1 && sinceHurtEvent > 0.3f) {
            ContextSampler.noteHurt(history);
            fire("hurt");
        }
        lastHurtTime = entity.hurtTime;
    }

    private boolean wasCreativeFlying, wasSpinning;
    /** Last observed value per tracked state; the first observation only primes it, so nothing fires on spawn-in. */
    private final java.util.Map<Integer, Boolean> stateEdges = new java.util.HashMap<>();

    private void stateEdge(int key, boolean now, String on, String off) {
        Boolean before = stateEdges.put(key, now);
        if (before == null || before == now) return;
        fire(now ? on : off);
    }

    private void edge(boolean now, boolean before, String on, String off) {
        if (now && !before) fire(on);
        else if (!now && before) fire(off);
    }

    /** Called by the damage hook with the reconstructed damage context. */
    public void onHurt(String kind, float relativeYaw, float amount) {
        Scope s = scope();
        s.setString(CtxVars.HURT_KIND, kind);
        s.set(CtxVars.HURT_DIR, relativeYaw);
        s.set(CtxVars.HURT_AMOUNT, amount);
        ContextSampler.noteHurt(history);
        sinceHurtEvent = 0f;
        fire("hurt");
        if (Math.abs(relativeYaw) > 135f) fire("hurt_back");
        else if (relativeYaw > 45f) fire("hurt_right");
        else if (relativeYaw < -45f) fire("hurt_left");
        else fire("hurt_front");
    }

    /** Local or server-confirmed melee hit by this entity. */
    public void onAttack(float strength) {
        Scope s = scope();
        s.set(CtxVars.ATTACK_STRENGTH, strength);
        s.set(CtxVars.COMBO, combo);
        ContextSampler.noteCombat(history);
        fire("attack");
        combo = (combo + 1) % 3;
        sinceAttack = 0f;
    }

    public void fire(String event) {
        if (!MWConfig.CLIENT.enabled.get()) return;
        if (controller == null) {
            if (pending.size() < 8) pending.add(event);
            return;
        }
        controller.fire(event);
        FirstPersonBridge.onThirdPersonEvent(this, event);
    }

    public void fire(String event, String arg, float dir) {
        fire(event, arg, dir, 0f);
    }

    public void fire(String event, String arg, float dir, float height) {
        Scope s = scope();
        if ("menu_open".equals(event)) s.setString(CtxVars.MENU, arg);
        if ("menu_close".equals(event)) s.setString(CtxVars.MENU, "none");
        s.setString(CtxVars.EVENT_ARG, arg);
        s.set(CtxVars.EVENT_DIR, dir);
        s.set(CtxVars.EVENT_HEIGHT, height);
        fire(event);
        // Contextual variants are also exposed as their own event, e.g. "interact:door_open".
        if (!arg.isEmpty()) fire(event + ":" + arg);
    }

    public boolean play(AnimationClip clip) {
        return controller != null && controller.play(clip, true);
    }

    /** Per-frame inputs that must be interpolated with the render partial tick (gait phase). */
    void sampleFrame(float partialTicks) {
        if (controller == null) return;
        Scope s = scope();
        float position = entity.walkAnimation.position(partialTicks);
        if (entity.isBaby()) position *= 3f;
        s.set(CtxVars.LIMB_SWING, position);
        s.set(CtxVars.LIMB_SWING_AMOUNT, Math.min(1f, entity.walkAnimation.speed(partialTicks)));
    }

    /** Advances to the given synced clock (seconds) and returns false if nothing should apply. */
    boolean advanceTo(double clock) {
        if (controller == null || !sampled) return false;
        if (Double.isNaN(lastClock)) lastClock = clock;
        float dt = (float) (clock - lastClock);
        lastClock = clock;
        if (dt > 0f) controller.update(Math.min(dt, 0.25f) * AnimatorManager.globalTimeScale());
        return true;
    }

    /**
     * Ground contact applies to a creature standing, crouching or sitting on the ground, unless a playing clip goes
     * underground on purpose (meta "ground": "free", e.g. a sniffer digging or a zombie rising from the earth).
     */
    boolean standsOnGround() {
        LivingEntity e = entity;
        if (!e.onGround() || e.isPassenger() || e.isSleeping() || e.deathTime > 0 || e.isInWater()) return false;
        net.minecraft.world.entity.Pose p = e.getPose();
        if (p != net.minecraft.world.entity.Pose.STANDING && p != net.minecraft.world.entity.Pose.CROUCHING && p != net.minecraft.world.entity.Pose.SITTING) {
            return false;
        }
        if (controller == null) return true;
        for (com.motionworks.engine.runtime.AnimationLayer l : controller.layers()) {
            for (com.motionworks.engine.runtime.ClipPlayback pb : l.playing()) {
                if ("free".equals(pb.clip.meta("ground", ""))) return false;
            }
        }
        return true;
    }

    long seed() {
        return Hashing.mix(seed);
    }

    List<String> activeClips() {
        List<String> ids = new ArrayList<>();
        if (controller != null) controller.layers().forEach(l -> ids.addAll(l.activeClipIds()));
        return ids;
    }
}
