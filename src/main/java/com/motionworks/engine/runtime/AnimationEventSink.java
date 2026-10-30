package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.ClipEvent;

@FunctionalInterface
public interface AnimationEventSink {
    AnimationEventSink NONE = (c, clip, e, w) -> {};

    /** @param weight blend weight of the instance that fired, so callers can scale or skip faint events */
    void onEvent(AnimationController controller, AnimationClip clip, ClipEvent event, float weight);
}
