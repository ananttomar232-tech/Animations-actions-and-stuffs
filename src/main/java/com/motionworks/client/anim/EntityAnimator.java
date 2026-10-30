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
        boolean sleeping = entity.isSleeping();
        edge(sleeping, wasSleeping, "sleep", "wake");
        wasSleeping = sleeping;
        boolean flying = entity.isFallFlying();
        edge(flying, wasFlying, "glide_start", "glide_stop");
        wasFlying = flying;
        boolean climbing = s.get(CtxVars.CLIMBING) != 0f;
        edge(climbing, wasClimbing, "climb_start", "climb_stop");
        wasClimbing = climbing;
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

    /** Advances to the given synced clock (seconds) and returns false if nothing should apply. */
    boolean advanceTo(double clock) {
        if (controller == null || !sampled) return false;
        if (Double.isNaN(lastClock)) lastClock = clock;
        float dt = (float) (clock - lastClock);
        lastClock = clock;
        if (dt > 0f) controller.update(Math.min(dt, 0.25f) * AnimatorManager.globalTimeScale());
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
