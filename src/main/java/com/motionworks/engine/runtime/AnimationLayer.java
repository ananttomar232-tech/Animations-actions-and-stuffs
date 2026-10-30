package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.clip.LoopMode;
import com.motionworks.engine.clip.Trigger;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * A layer owns the clips assigned to it and decides which of them play.
 *
 * <p>In single mode the layer has one active "slot": state clips compete by priority (with
 * hysteresis, minimum durations and weighted idle pools), event clips interrupt according to the
 * interruption rules and manual clips are explicit requests. Changes crossfade.
 *
 * <p>In multi mode (used for additive layers) every state clip whose condition holds plays at
 * once and event clips overlap, which suits breathing, tail motion and hit flinches.
 */
public final class AnimationLayer {
    public final String name;
    public final boolean additive;
    public final boolean multi;
    private float weight = 1f;

    private final Rig rig;
    private final List<AnimationClip> stateClips = new ArrayList<>();
    private final Map<String, List<AnimationClip>> eventClips = new HashMap<>();
    private final List<ClipPlayback> playing = new ArrayList<>();
    private final Map<AnimationClip, Float> cooldownUntil = new IdentityHashMap<>();
    private final Set<AnimationClip> latched = Collections.newSetFromMap(new IdentityHashMap<>());
    private final long layerSeed;
    private ClipPlayback current;
    private long selections;
    private float clock;

    private final float[] sumV;
    private final float[] sumW;
    private final float[] tmp = new float[3];

    public AnimationLayer(String name, boolean additive, boolean multi, Rig rig) {
        this.name = name;
        this.additive = additive;
        this.multi = multi;
        this.rig = rig;
        this.layerSeed = Hashing.ofString(name);
        this.sumV = new float[rig.size() * 9];
        this.sumW = new float[rig.size() * 3];
    }

    public void addClip(AnimationClip clip) {
        Trigger t = clip.trigger();
        if (t.type() == Trigger.Type.STATE) {
            stateClips.add(clip);
            stateClips.sort(Comparator.comparingInt(AnimationClip::priority).reversed());
        } else if (t.type() == Trigger.Type.EVENT) {
            eventClips.computeIfAbsent(t.event(), k -> new ArrayList<>()).add(clip);
        }
    }

    public float weight() {
        return weight;
    }

    public void setWeight(float w) {
        weight = MathUtil.clamp01(w);
    }

    public ClipPlayback current() {
        return current;
    }

    public List<ClipPlayback> playing() {
        return Collections.unmodifiableList(playing);
    }

    public List<AnimationClip> stateClips() {
        return Collections.unmodifiableList(stateClips);
    }

    public Set<String> events() {
        return eventClips.keySet();
    }

    public boolean handles(String event) {
        return eventClips.containsKey(event);
    }

    // ------------------------------------------------------------------ selection

    void select(AnimationController c, float dt) {
        clock += dt;
        Scope s = c.scope();
        s.animTime = 0f;
        s.animProgress = 0f;
        if (multi) {
            selectMulti(c, s, dt);
            return;
        }
        if (current != null && (current.isFinished() || current.isStopping())) current = null;

        if (current != null && current.source != ClipPlayback.Source.STATE) {
            Trigger t = current.clip.trigger();
            if (t.stopWhen() != null && t.stopWhen().eval(s) != 0f) {
                current.stop(current.clip.blendOut());
                current = null;
            } else {
                AnimationClip preempt = bestState(s, current.clip.priority() + 1);
                if (preempt != null && (current.clip.interruptible() || preempt.priority() >= 1000)) {
                    start(c, preempt, ClipPlayback.Source.STATE, 0f);
                }
                return;
            }
        }

        // Clear latches for ONCE state clips whose conditions have gone false.
        if (!latched.isEmpty()) latched.removeIf(clip -> clip.trigger().when().eval(s) == 0f);

        AnimationClip top = bestState(s, Integer.MIN_VALUE);
        if (current != null) {
            AnimationClip cur = current.clip;
            boolean curTrue = !latched.contains(cur) && cur.trigger().when().eval(s) != 0f;
            if (curTrue) current.falseFor = 0f;
            else current.falseFor += dt;

            boolean onceDone = (cur.loop() == LoopMode.ONCE) && current.time() >= cur.length() - cur.blendOut() - 1e-4f;
            if (onceDone && curTrue) latched.add(cur);
            boolean minTimeMet = current.age() >= cur.trigger().minTime();
            if (top != null && top.priority() > cur.priority() && (minTimeMet || top.priority() >= 1000)) {
                start(c, pick(c, s, top), ClipPlayback.Source.STATE, 0f);
                return;
            }
            boolean exit = !curTrue && current.falseFor >= cur.trigger().exitDelay() && minTimeMet;
            if (exit || onceDone) {
                if (top != null) start(c, pick(c, s, top), ClipPlayback.Source.STATE, 0f);
                else {
                    current.stop(cur.blendOut());
                    current = null;
                }
                return;
            }
            if (cur.trigger().group() != null && poolExpired(current)) {
                AnimationClip next = pick(c, s, top != null && top.priority() == cur.priority() ? top : cur);
                if (next != cur) start(c, next, ClipPlayback.Source.STATE, 0f);
                else current.loopsAtReselect = current.loops();
            }
            return;
        }
        if (top != null) start(c, pick(c, s, top), ClipPlayback.Source.STATE, 0f);
    }

    private boolean poolExpired(ClipPlayback p) {
        AnimationClip clip = p.clip;
        if (clip.loop() != LoopMode.LOOP) return false;
        float hold = Math.max(clip.trigger().minTime(), clip.length() * 2f);
        return p.age() >= hold && p.loops() > p.loopsAtReselect;
    }

    private AnimationClip bestState(Scope s, int minPriority) {
        for (AnimationClip clip : stateClips) {
            if (clip.priority() < minPriority) return null;
            if (latched.contains(clip)) continue;
            if (onCooldown(clip)) continue;
            if (clip.trigger().when().eval(s) != 0f) return clip;
        }
        return null;
    }

    /** Weighted deterministic pick among true clips sharing priority and group with {@code anchor}. */
    private AnimationClip pick(AnimationController c, Scope s, AnimationClip anchor) {
        String group = anchor.trigger().group();
        if (group == null) return anchor;
        List<AnimationClip> pool = new ArrayList<>(4);
        float total = 0f;
        for (AnimationClip clip : stateClips) {
            if (clip.priority() != anchor.priority() || !group.equals(clip.trigger().group())) continue;
            if (latched.contains(clip) || onCooldown(clip) || clip.trigger().when().eval(s) == 0f) continue;
            float w = Math.max(0f, clip.trigger().weight().eval(s));
            if (w <= 0f) continue;
            pool.add(clip);
            total += w;
        }
        if (pool.isEmpty()) return anchor;
        float r = Hashing.unit(Hashing.combine(c.seed(), layerSeed, selections++ + c.selectionEpoch())) * total;
        for (AnimationClip clip : pool) {
            r -= Math.max(0f, clip.trigger().weight().eval(s));
            if (r <= 0f) return clip;
        }
        return pool.get(pool.size() - 1);
    }

    private void selectMulti(AnimationController c, Scope s, float dt) {
        for (AnimationClip clip : stateClips) {
            ClipPlayback p = find(clip);
            boolean want = clip.trigger().when().eval(s) != 0f;
            if (want) {
                if (p == null) startConcurrent(c, clip, ClipPlayback.Source.STATE);
                else p.falseFor = 0f;
            } else if (p != null && p.source == ClipPlayback.Source.STATE) {
                p.falseFor += dt;
                if (p.falseFor >= clip.trigger().exitDelay()) p.stop(clip.blendOut());
            }
        }
        for (ClipPlayback p : playing) {
            if (p.source != ClipPlayback.Source.STATE && !p.isStopping()) {
                Trigger t = p.clip.trigger();
                if (t.stopWhen() != null && t.stopWhen().eval(s) != 0f) p.stop(p.clip.blendOut());
            }
        }
    }

    private ClipPlayback find(AnimationClip clip) {
        for (ClipPlayback p : playing) if (p.clip == clip && !p.isStopping()) return p;
        return null;
    }

    private boolean onCooldown(AnimationClip clip) {
        Float until = cooldownUntil.get(clip);
        return until != null && clock < until;
    }

    // ------------------------------------------------------------------ events / manual

    /** Fires a gameplay event. Returns the clip that started or null. */
    AnimationClip fire(AnimationController c, String event) {
        List<AnimationClip> list = eventClips.get(event);
        if (list == null) return null;
        Scope s = c.scope();
        s.animTime = 0f;
        s.animProgress = 0f;
        long roll = c.nextEventRoll();
        int bestPriority = Integer.MIN_VALUE;
        List<AnimationClip> best = new ArrayList<>(2);
        for (AnimationClip clip : list) {
            Trigger t = clip.trigger();
            if (onCooldown(clip) || t.when().eval(s) == 0f) continue;
            if (t.chance() < 1f && Hashing.unit(Hashing.combine(roll, Hashing.ofString(clip.id()))) >= t.chance()) continue;
            if (clip.priority() > bestPriority) {
                best.clear();
                bestPriority = clip.priority();
            }
            if (clip.priority() == bestPriority) best.add(clip);
        }
        if (best.isEmpty()) return null;
        AnimationClip chosen = best.get(0);
        if (best.size() > 1) {
            float total = 0f;
            for (AnimationClip clip : best) total += Math.max(0.0001f, clip.trigger().weight().eval(s));
            float r = Hashing.unit(Hashing.combine(roll, layerSeed)) * total;
            for (AnimationClip clip : best) {
                r -= Math.max(0.0001f, clip.trigger().weight().eval(s));
                if (r <= 0f) {
                    chosen = clip;
                    break;
                }
            }
        }
        if (!multi && current != null && !canInterrupt(current, chosen)) return null;
        if (chosen.trigger().cooldown() > 0f) cooldownUntil.put(chosen, clock + chosen.trigger().cooldown());
        if (multi) startConcurrent(c, chosen, ClipPlayback.Source.EVENT);
        else start(c, chosen, ClipPlayback.Source.EVENT, 0f);
        return chosen;
    }

    static boolean canInterrupt(ClipPlayback cur, AnimationClip cand) {
        if (cur.isStopping() || cur.isFinished()) return true;
        int curP = cur.clip.priority();
        if (cur.source == ClipPlayback.Source.STATE) return cand.priority() >= curP || cur.clip.interruptible();
        if (cand.priority() > curP) return true;
        return cur.progress() >= cur.clip.interruptAfter() && (cand.priority() == curP || cur.clip.interruptible());
    }

    /** Plays a clip explicitly; {@code force} bypasses interruption rules. */
    boolean play(AnimationController c, AnimationClip clip, boolean force, float startTime) {
        if (multi) {
            startConcurrent(c, clip, ClipPlayback.Source.MANUAL);
            return true;
        }
        if (!force && current != null && !canInterrupt(current, clip)) return false;
        start(c, clip, ClipPlayback.Source.MANUAL, startTime);
        return true;
    }

    void stopAll(float fade) {
        for (ClipPlayback p : playing) p.stop(fade);
        current = null;
    }

    boolean stop(AnimationClip clip, float fade) {
        boolean any = false;
        for (ClipPlayback p : playing) {
            if (p.clip == clip && !p.isStopping()) {
                p.stop(fade);
                any = true;
            }
        }
        if (current != null && current.clip == clip) current = null;
        return any;
    }

    private void start(AnimationController c, AnimationClip clip, ClipPlayback.Source source, float startTime) {
        float fade = clip.blendIn();
        if (current != null) current.stop(Math.max(fade, 0.05f));
        ClipPlayback p = new ClipPlayback(clip, rig, source, current == null && !additive ? fade : fade, startTime);
        playing.add(p);
        current = p;
        c.notifyStarted(this, p);
    }

    private void startConcurrent(AnimationController c, AnimationClip clip, ClipPlayback.Source source) {
        ClipPlayback existing = find(clip);
        if (existing != null) existing.stop(Math.max(0.05f, clip.blendIn()));
        ClipPlayback p = new ClipPlayback(clip, rig, source, clip.blendIn(), 0f);
        playing.add(p);
        c.notifyStarted(this, p);
    }

    // ------------------------------------------------------------------ evaluation

    void advance(AnimationController c, float dt, AnimationEventSink sink) {
        for (int i = 0; i < playing.size(); i++) playing.get(i).advance(dt, c.scope(), c, sink);
        Iterator<ClipPlayback> it = playing.iterator();
        while (it.hasNext()) {
            ClipPlayback p = it.next();
            if (p.isFinished()) {
                it.remove();
                if (p == current) current = null;
            }
        }
        // Bound the number of simultaneously fading instances.
        while (playing.size() > 6) {
            ClipPlayback oldest = playing.remove(0);
            if (oldest == current) current = null;
        }
    }

    void sample(AnimationController c, PoseBuffer pose) {
        if (playing.isEmpty() || weight <= 0f) return;
        Scope s = c.scope();
        if (additive) {
            for (ClipPlayback p : playing) {
                float w = p.envelope() * p.weight * weight;
                if (w <= 0f) continue;
                p.bindScope(s, 0f);
                sampleAdditive(p, s, pose, w);
            }
            return;
        }
        Arrays.fill(sumV, 0f);
        Arrays.fill(sumW, 0f);
        for (ClipPlayback p : playing) {
            float w = p.envelope() * p.weight;
            if (w <= 0f) continue;
            p.bindScope(s, 0f);
            List<BoneTrack> tracks = p.clip.tracks();
            for (int i = 0; i < tracks.size(); i++) {
                int bone = p.binding[i];
                if (bone < 0 || (p.mask != null && !p.mask[bone])) continue;
                BoneTrack track = tracks.get(i);
                for (ChannelTarget target : ChannelTarget.values()) {
                    Channel ch = track.channel(target);
                    if (ch == null) continue;
                    ch.sample(p.time(), s, tmp, 0);
                    float k = target == ChannelTarget.ROTATION ? MathUtil.DEG_TO_RAD : 1f;
                    int o = bone * 9 + target.offset;
                    sumV[o] += tmp[0] * k * w;
                    sumV[o + 1] += tmp[1] * k * w;
                    sumV[o + 2] += tmp[2] * k * w;
                    sumW[bone * 3 + target.group()] += w;
                }
            }
        }
        for (int b = 0; b < rig.size(); b++) {
            for (int g = 0; g < 3; g++) {
                float w = sumW[b * 3 + g];
                if (w <= 0f) continue;
                int o = b * 9 + g * 3;
                pose.blendOverride(b, g, sumV[o] / w, sumV[o + 1] / w, sumV[o + 2] / w, Math.min(1f, w) * weight);
            }
        }
    }

    private void sampleAdditive(ClipPlayback p, Scope s, PoseBuffer pose, float w) {
        List<BoneTrack> tracks = p.clip.tracks();
        for (int i = 0; i < tracks.size(); i++) {
            int bone = p.binding[i];
            if (bone < 0 || (p.mask != null && !p.mask[bone])) continue;
            BoneTrack track = tracks.get(i);
            for (ChannelTarget target : ChannelTarget.values()) {
                Channel ch = track.channel(target);
                if (ch == null) continue;
                ch.sample(p.time(), s, tmp, 0);
                if (target == ChannelTarget.ROTATION) {
                    pose.addAdditive(bone, 0, tmp[0] * MathUtil.DEG_TO_RAD * w, tmp[1] * MathUtil.DEG_TO_RAD * w, tmp[2] * MathUtil.DEG_TO_RAD * w);
                } else if (target == ChannelTarget.POSITION) {
                    pose.addAdditive(bone, 1, tmp[0] * w, tmp[1] * w, tmp[2] * w);
                } else {
                    pose.addAdditive(bone, 2, (tmp[0] - 1f) * w, (tmp[1] - 1f) * w, (tmp[2] - 1f) * w);
                }
            }
        }
    }

    public Set<String> activeClipIds() {
        Set<String> ids = new HashSet<>();
        for (ClipPlayback p : playing) if (!p.isStopping()) ids.add(p.clip.id());
        return ids;
    }
}
