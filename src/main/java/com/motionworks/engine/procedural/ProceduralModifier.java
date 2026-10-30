package com.motionworks.engine.procedural;

import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.PoseBuffer;

/** Runs after all layers have been sampled and adjusts the pose procedurally. */
public interface ProceduralModifier {
    void apply(AnimationController controller, PoseBuffer pose, float dt);
}
