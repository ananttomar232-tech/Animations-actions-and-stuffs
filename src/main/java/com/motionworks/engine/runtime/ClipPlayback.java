package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.ClipEvent;
import com.motionworks.engine.clip.LoopMode;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.MathUtil;

/** One playing instance of a clip, with its own clock and fade envelope. */
public final class ClipPlayback {
    public final AnimationClip clip;
    public final Source source;
    final int[] binding;
    final boolean[] mask;

    float time;
    int loops;
    float age;
    float fadeInDuration;
    float fadeOutDuration;
    float fadeOutAge = -1f;
    float fadeFrom = 1f;
    boolean finished;
    boolean reverse;
    /** Seconds the selecting state condition has been false (state hysteresis). */
    float falseFor;
    float weight = 1f;
    int loopsAtReselect;
    private boolean started;

    public enum Source { STATE, EVENT, MANUAL }

    ClipPlayback(AnimationClip clip, Rig rig, Source source, float fadeIn, float startTime) {
        this.clip = clip;
        this.source = source;
        this.binding = rig.bind(clip);
        this.mask = rig.mask(clip);
        this.fadeInDuration = Math.max(0f, fadeIn);
        this.time = startTime;
    }

    public float time() {
        return time;
    }

    public float progress() {
        return clip.length() <= 0f ? 1f : MathUtil.clamp01(time / clip.length());
    }

    public float age() {
        return age;
    }

    public int loops() {
        return loops;
    }

    public boolean isStopping() {
        return fadeOutAge >= 0f;
    }

    public boolean isFinished() {
        return finished;
    }

    /** Begins fading out. Has no effect if already fading. */
    public void stop(float fadeOut) {
        if (fadeOutAge >= 0f) return;
        fadeFrom = fadeIn();
        fadeOutDuration = Math.max(0f, fadeOut);
        fadeOutAge = 0f;
        if (fadeOutDuration == 0f) finished = true;
    }

    private float fadeIn() {
        if (fadeInDuration <= 0f) return 1f;
        return MathUtil.hermiteBlend(MathUtil.clamp01(age / fadeInDuration));
    }

    /** Envelope weight from fades only. */
    public float envelope() {
        if (finished) return 0f;
        if (fadeOutAge >= 0f) {
            if (fadeOutDuration <= 0f) return 0f;
            return fadeFrom * (1f - MathUtil.hermiteBlend(MathUtil.clamp01(fadeOutAge / fadeOutDuration)));
        }
        return fadeIn();
    }

    void bindScope(Scope s, float dt) {
        s.animTime = time;
        s.animProgress = progress();
        s.animLoop = loops;
        s.deltaTime = dt;
    }

    /** Advances time by {@code dt} seconds and fires crossed events. */
    void advance(float dt, Scope scope, AnimationController controller, AnimationEventSink sink) {
        if (finished) return;
        age += dt;
        if (fadeOutAge >= 0f) {
            fadeOutAge += dt;
            if (fadeOutAge >= fadeOutDuration) {
                finished = true;
                return;
            }
        }
        bindScope(scope, dt);
        weight = MathUtil.clamp01(clip.weight().eval(scope));
        if (!started) {
            started = true;
            fireAt(time, controller, sink);
        }
        float length = clip.length();
        float before = time;
        float after;
        if (clip.timeDriver() != null) {
            after = clip.timeDriver().eval(scope);
            if (clip.loop() == LoopMode.LOOP && length > 0f) {
                int newLoops = (int) Math.floor(after / length);
                after -= newLoops * length;
                if (newLoops != loops && newLoops == loops + 1) {
                    fireRange(before, length, controller, sink);
                    before = 0f;
                }
                loops = newLoops;
            }
            if (after >= before) fireRange(before, after, controller, sink);
            time = clampForMode(after, length);
            return;
        }
        float rate = clip.speed().eval(scope) * controller.timeScale();
        float delta = dt * rate;
        if (delta <= 0f) return;
        switch (clip.loop()) {
            case LOOP -> {
                after = before + delta;
                if (length <= 0f) {
                    time = 0f;
                    return;
                }
                while (after >= length) {
                    fireRange(before, length, controller, sink);
                    after -= length;
                    before = 0f;
                    loops++;
                    // Events at exactly t=0 belong to the next cycle.
                    fireAt(0f, controller, sink);
                }
                fireRange(before, after, controller, sink);
                time = after;
            }
            case PING_PONG -> {
                if (length <= 0f) return;
                float t = reverse ? before - delta : before + delta;
                if (t >= length) {
                    t = length - (t - length);
                    reverse = true;
                    loops++;
                } else if (t <= 0f) {
                    t = -t;
                    reverse = false;
                    loops++;
                }
                if (!reverse) fireRange(before, t, controller, sink);
                time = MathUtil.clamp(t, 0f, length);
            }
            case HOLD -> {
                after = Math.min(length, before + delta);
                fireRange(before, after, controller, sink);
                time = after;
            }
            case ONCE -> {
                after = Math.min(length, before + delta);
                fireRange(before, after, controller, sink);
                time = after;
                float fadeOut = clip.blendOut();
                if (fadeOutAge < 0f && after >= length - fadeOut) {
                    stop(Math.max(0f, length - after));
                    if (fadeOutDuration == 0f) finished = true;
                }
                if (after >= length && fadeOutAge < 0f) finished = true;
            }
        }
    }

    private float clampForMode(float t, float length) {
        if (clip.loop() == LoopMode.LOOP) return t;
        return MathUtil.clamp(t, 0f, length);
    }

    private void fireAt(float t, AnimationController controller, AnimationEventSink sink) {
        for (ClipEvent e : clip.events()) {
            if (e.time() == t) sink.onEvent(controller, clip, e, envelope() * weight);
        }
    }

    /** Fires events with time in (from, to]. */
    private void fireRange(float from, float to, AnimationController controller, AnimationEventSink sink) {
        if (clip.events().isEmpty() || to <= from) return;
        for (ClipEvent e : clip.events()) {
            float et = e.time();
            if (et > from && et <= to) sink.onEvent(controller, clip, e, envelope() * weight);
        }
    }
}
