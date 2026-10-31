package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.LayerSpec;
import com.motionworks.engine.runtime.PoseBuffer;
import com.motionworks.engine.runtime.Rig;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/** Spins (inspect flourishes, rolls, twirls) must blend in and out the short way round, never whirl back. */
class RotationBlendTest {
    private static final String JSON = """
            {`clips`: {
              `spin`: {`layer`: `gesture`, `priority`: 300, `length`: 1, `loop`: `hold`, `blend_in`: 0,
                       `trigger`: {`type`: `manual`}, `bones`: {`a`: {`rotation`: [730, 0, 0]}}},
              `still`: {`layer`: `gesture`, `priority`: 400, `length`: 1, `loop`: `hold`, `blend_in`: 1,
                        `trigger`: {`type`: `manual`}, `bones`: {`a`: {`rotation`: [0, 0, 0]}}},
              `twirl`: {`layer`: `additive`, `additive`: true, `length`: 1, `loop`: `hold`, `blend_in`: 0, `blend_out`: 1,
                        `trigger`: {`type`: `manual`}, `bones`: {`a`: {`rotation`: [700, 0, 0]}}}
            }}""";

    private final Map<String, AnimationClip> clips = TestClips.load(JSON);
    private final Rig rig = new Rig("test", List.of("a"), null, Map.of());

    private static float deg(float rad) {
        return (float) Math.toDegrees(rad);
    }

    private static void run(AnimationController c, float seconds) {
        for (float t = 0; t < seconds - 1e-4f; t += 1f / 60f) c.update(1f / 60f);
    }

    @Test
    void blendingAgainstVanillaTakesTheShortPath() {
        PoseBuffer p = new PoseBuffer(1);
        p.reset();
        p.blendOverride(0, 0, (float) Math.toRadians(731), 0, 0, 0.5f);
        assertEquals(5.5f, deg(p.resolve(0, 0, 0f, 0f)), 1e-3f, "half way from 0 to 731 degrees is 5.5, not 365.5");
    }

    @Test
    void crossfadingAwayFromASpinDoesNotUnwind() {
        AnimationController c = new AnimationController(rig, 1, LayerSpec.STANDARD, clips.values());
        assertTrue(c.play(clips.get("spin"), true));
        run(c, 0.5f);
        assertEquals(10f, Math.floorMod(Math.round(deg(c.pose().resolve(0, 0, 0f, 0f))), 360), 1e-3f);
        assertTrue(c.play(clips.get("still"), true));
        float worst = 0f;
        for (int i = 0; i < 60; i++) {
            c.update(1f / 60f);
            worst = Math.max(worst, Math.abs(com.motionworks.engine.math.MathUtil.wrapDegrees(deg(c.pose().resolve(0, 0, 0f, 0f)))));
        }
        assertTrue(worst <= 10.01f, "the crossfade from 730 to 0 degrees should stay within 10 degrees of rest, saw " + worst);
    }

    @Test
    void additiveSpinFadesOutTheShortWay() {
        AnimationController c = new AnimationController(rig, 1, LayerSpec.STANDARD, clips.values());
        assertTrue(c.play(clips.get("twirl"), true));
        run(c, 0.2f);
        assertTrue(c.stop(clips.get("twirl"), 1f));
        float worst = 0f;
        for (int i = 0; i < 70; i++) {
            c.update(1f / 60f);
            worst = Math.max(worst, Math.abs(deg(c.pose().resolve(0, 0, 0f, 0f))));
        }
        assertTrue(worst <= 20.01f, "700 degrees is -20: fading it out must stay within 20 degrees, saw " + worst);
    }
}
