package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.procedural.ProceduralModifier;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiConsumer;

/**
 * Per-entity animation brain: a stack of layers over one rig, a scope of context variables,
 * procedural modifiers and an event sink. The host calls {@link #update(float)} once per frame
 * with the elapsed time and then reads {@link #pose()}.
 */
public final class AnimationController {
    private final Rig rig;
    private final Scope scope = new Scope();
    private final long seed;
    private final Map<String, AnimationLayer> layers = new LinkedHashMap<>();
    private final List<ProceduralModifier> modifiers = new ArrayList<>();
    private final PoseBuffer pose;
    private AnimationEventSink sink = AnimationEventSink.NONE;
    private BiConsumer<AnimationLayer, ClipPlayback> startListener;
    private float timeScale = 1f;
    private float selectAccumulator;
    private long eventCounter;
    private long selectionEpoch;
    private float time;

    /** Seconds between state re-selection passes; matches the 20 Hz game tick. */
    public static final float SELECT_INTERVAL = 0.05f;

    public AnimationController(Rig rig, long seed, List<LayerSpec> specs, Collection<AnimationClip> clips) {
        this.rig = rig;
        this.seed = seed;
        this.scope.seed = seed;
        this.pose = new PoseBuffer(rig.size());
        for (LayerSpec spec : specs) layers.put(spec.name(), new AnimationLayer(spec.name(), spec.additive(), spec.multi(), rig));
        for (AnimationClip clip : clips) {
            AnimationLayer layer = layers.computeIfAbsent(clip.layer(),
                    n -> new AnimationLayer(n, clip.additive(), clip.additive(), rig));
            layer.addClip(clip);
        }
        pose.reset();
    }

    public Rig rig() {
        return rig;
    }

    public Scope scope() {
        return scope;
    }

    public long seed() {
        return seed;
    }

    public PoseBuffer pose() {
        return pose;
    }

    public float time() {
        return time;
    }

    public float timeScale() {
        return timeScale;
    }

    public void setTimeScale(float s) {
        timeScale = Math.max(0f, s);
    }

    public void setEventSink(AnimationEventSink sink) {
        this.sink = sink == null ? AnimationEventSink.NONE : sink;
    }

    public void setStartListener(BiConsumer<AnimationLayer, ClipPlayback> listener) {
        this.startListener = listener;
    }

    public void addModifier(ProceduralModifier m) {
        modifiers.add(m);
    }

    public List<ProceduralModifier> modifiers() {
        return modifiers;
    }

    public AnimationLayer layer(String name) {
        return layers.get(name);
    }

    public Collection<AnimationLayer> layers() {
        return layers.values();
    }

    /**
     * Sets a value that varies the deterministic idle choices over time. Hosts feed the synced
     * world time divided into windows so that all clients pick the same variants.
     */
    public void setSelectionEpoch(long epoch) {
        selectionEpoch = epoch;
    }

    long selectionEpoch() {
        return selectionEpoch;
    }

    long nextEventRoll() {
        return Hashing.combine(seed, ++eventCounter, selectionEpoch);
    }

    void notifyStarted(AnimationLayer layer, ClipPlayback p) {
        if (startListener != null) startListener.accept(layer, p);
    }

    /** Fires a gameplay event on every layer that handles it. Returns true if any clip started. */
    public boolean fire(String event) {
        boolean any = false;
        for (AnimationLayer l : layers.values()) {
            if (l.handles(event) && l.fire(this, event) != null) any = true;
        }
        return any;
    }

    public boolean handles(String event) {
        for (AnimationLayer l : layers.values()) if (l.handles(event)) return true;
        return false;
    }

    /** Plays a clip on its declared layer. */
    public boolean play(AnimationClip clip, boolean force) {
        AnimationLayer l = layers.computeIfAbsent(clip.layer(), n -> new AnimationLayer(n, clip.additive(), clip.additive(), rig));
        return l.play(this, clip, force, 0f);
    }

    public boolean stop(AnimationClip clip, float fade) {
        AnimationLayer l = layers.get(clip.layer());
        return l != null && l.stop(clip, fade);
    }

    public void stopLayer(String name, float fade) {
        AnimationLayer l = layers.get(name);
        if (l != null) l.stopAll(fade);
    }

    /** Advances everything by {@code dt} real seconds and rebuilds the pose. */
    public void update(float dt) {
        if (dt < 0f) dt = 0f;
        if (dt > 0.25f) dt = 0.25f;
        float scaled = dt * timeScale;
        time += scaled;
        selectAccumulator += scaled;
        if (selectAccumulator >= SELECT_INTERVAL || time == scaled) {
            float step = Math.max(selectAccumulator, SELECT_INTERVAL);
            selectAccumulator = 0f;
            for (AnimationLayer l : layers.values()) l.select(this, step);
        }
        for (AnimationLayer l : layers.values()) l.advance(this, scaled, sink);
        pose.reset();
        for (AnimationLayer l : layers.values()) l.sample(this, pose);
        for (ProceduralModifier m : modifiers) m.apply(this, pose, scaled);
    }

    public String describe() {
        StringBuilder sb = new StringBuilder();
        for (AnimationLayer l : layers.values()) {
            if (l.playing().isEmpty()) continue;
            sb.append(l.name).append(':');
            for (ClipPlayback p : l.playing()) {
                sb.append(' ').append(p.clip.id());
                sb.append(String.format(java.util.Locale.ROOT, "(%.2f w%.2f)", p.time(), p.envelope() * p.weight));
            }
            sb.append('\n');
        }
        return sb.toString();
    }
}
