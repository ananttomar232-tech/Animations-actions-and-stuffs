package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.expr.Scope;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ChannelTest {
    private static final String JSON = """
            {`clips`: {
              `lin`: {`length`: 1, `bones`: {`a`: {`rotation`: {`0`: [0,0,0], `1`: [10,20,30]}}}},
              `step`: {`length`: 1, `bones`: {`a`: {`rotation`: {`0`: [0,0,0], `0.5`: {`v`: [5,5,5], `l`: `step`}, `1`: [9,9,9]}}}},
              `ease`: {`length`: 1, `bones`: {`a`: {`rotation`: {`0`: [0,0,0], `1`: {`v`: [10,0,0], `e`: `in_quad`}}}}},
              `smooth`: {`length`: 2, `bones`: {`a`: {`rotation`: {`keys`: {`0`: [0,0,0], `1`: [10,0,0], `2`: [0,0,0]}, `lerp`: `smooth`}}}},
              `prepost`: {`length`: 1, `bones`: {`a`: {`rotation`: {`0`: [0,0,0], `0.5`: {`pre`: [10,0,0], `post`: [-10,0,0]}, `1`: [0,0,0]}}}},
              `expr`: {`length`: 1, `bones`: {`a`: {`rotation`: [`math.sin(q.anim_time * 360) * 10`, 0, 0]}}}
            }}""";

    private final Map<String, AnimationClip> clips = TestClips.load(JSON);

    private float[] sample(String id, float t) {
        Channel ch = clips.get(id).track("a").rotation();
        float[] out = new float[3];
        Scope s = new Scope();
        s.animTime = t;
        ch.sample(t, s, out, 0);
        return out;
    }

    @Test
    void linear() {
        float[] v = sample("lin", 0.5f);
        assertArrayEquals(new float[] {5, 10, 15}, v, 1e-4f);
        assertArrayEquals(new float[] {10, 20, 30}, sample("lin", 3f), 1e-4f);
        assertArrayEquals(new float[] {0, 0, 0}, sample("lin", -1f), 1e-4f);
    }

    @Test
    void step() {
        assertEquals(0f, sample("step", 0.49f)[0], 1e-4f);
        assertEquals(0f, sample("step", 0.5f - 1e-4f)[0], 1e-4f);
        assertEquals(5.8f, sample("step", 0.6f)[0], 1e-4f, "after the step key the next segment is linear");
    }

    @Test
    void easing() {
        assertEquals(2.5f, sample("ease", 0.5f)[0], 1e-4f);
    }

    @Test
    void smoothPassesThroughKeys() {
        assertEquals(10f, sample("smooth", 1f)[0], 1e-4f);
        float mid = sample("smooth", 0.5f)[0];
        assertTrue(mid > 5f, "catmull-rom bulges above the linear midpoint: " + mid);
    }

    @Test
    void preAndPostValues() {
        assertEquals(5f, sample("prepost", 0.25f)[0], 1e-4f);
        assertEquals(-5f, sample("prepost", 0.75f)[0], 1e-4f);
    }

    @Test
    void expressionValues() {
        assertEquals(10f, sample("expr", 0.25f)[0], 1e-3f);
        assertEquals(-10f, sample("expr", 0.75f)[0], 1e-3f);
    }
}
