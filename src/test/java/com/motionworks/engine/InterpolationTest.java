package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.expr.Scope;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/** The "smooth" interpolation: auto-clamped Hermite through every key, seamless across loop seams. */
class InterpolationTest {
    private static final String JSON = """
            {`clips`: {
              `hold`: {`length`: 2.2, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `0.6`: [45,0,0], `1.4`: [45,0,0], `2.2`: [0,0,0]}, `lerp`: `smooth`}}}},
              `peak`: {`length`: 2, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `1`: [10,0,0], `2`: [0,0,0]}, `lerp`: `smooth`}}}},
              `rise`: {`length`: 2, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `0.3`: [1,0,0], `2`: [10,0,0]}, `lerp`: `smooth`}}}},
              `cycle`: {`length`: 1, `loop`: `loop`, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `0.25`: [10,0,0], `0.5`: [0,0,0], `0.75`: [-10,0,0], `1`: [0,0,0]}, `lerp`: `smooth`}}}},
              `oneshot`: {`length`: 1, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `0.25`: [10,0,0], `0.5`: [0,0,0], `0.75`: [-10,0,0], `1`: [0,0,0]}, `lerp`: `smooth`}}}}
            }}""";

    private final Map<String, AnimationClip> clips = TestClips.load(JSON);
    private final Scope scope = new Scope();
    private final float[] out = new float[3];

    private Channel ch(String id) {
        return clips.get(id).track("a").rotation();
    }

    private float at(String id, float t) {
        ch(id).sample(t, scope, out, 0);
        return out[0];
    }

    @Test
    void holdsStayExactlyOnTheAuthoredValue() {
        for (float t = 0.6f; t <= 1.4f; t += 0.01f) assertEquals(45f, at("hold", t), 1e-3f, "t=" + t);
        for (float t = 0f; t <= 2.2f; t += 0.01f) assertTrue(at("hold", t) <= 45f + 1e-3f, "overshoot at t=" + t);
    }

    @Test
    void peaksAreNeverExceeded() {
        assertEquals(10f, at("peak", 1f), 1e-3f);
        for (float t = 0f; t <= 2f; t += 0.01f) assertTrue(at("peak", t) <= 10f + 1e-3f, "overshoot at t=" + t);
    }

    @Test
    void segmentsBetweenRisingKeysStayMonotone() {
        float prev = -1f;
        for (float t = 0f; t <= 2f; t += 0.005f) {
            float v = at("rise", t);
            assertTrue(v >= prev - 1e-4f, "dips at t=" + t);
            prev = v;
        }
    }

    @Test
    void velocityIsContinuousThroughUnevenlySpacedKeys() {
        float left = (at("rise", 0.3f) - at("rise", 0.3f - 1e-3f)) / 1e-3f;
        float right = (at("rise", 0.3f + 1e-3f) - at("rise", 0.3f)) / 1e-3f;
        assertEquals(left, right, Math.abs(left) * 0.02f + 0.05f);
    }

    @Test
    void loopsWrapSmoothlyAndOneShotsSettle() {
        assertTrue(ch("cycle").isCyclic());
        assertFalse(ch("oneshot").isCyclic());
        float start = (at("cycle", 1e-3f) - at("cycle", 0f)) / 1e-3f;
        float end = (at("cycle", 1f) - at("cycle", 1f - 1e-3f)) / 1e-3f;
        assertTrue(start > 10f, "a cycle keeps moving through its seam: " + start);
        assertEquals(start, end, Math.abs(start) * 0.02f);
        assertEquals(0f, (at("oneshot", 1e-3f) - at("oneshot", 0f)) / 1e-3f, 1f, "a one-shot eases out of its first key");
    }
}
