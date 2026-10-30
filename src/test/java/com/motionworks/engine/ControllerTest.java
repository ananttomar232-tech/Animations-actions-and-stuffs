package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.ClipEvent;
import com.motionworks.engine.expr.Vars;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.LayerSpec;
import com.motionworks.engine.runtime.Rig;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class ControllerTest {
    private static final String JSON = """
            {`clips`: {
              `idle`: {`layer`: `base`, `priority`: 10, `loop`: true, `length`: 2, `blend_in`: 0.2,
                       `trigger`: {`type`: `state`, `when`: `1`, `group`: `idle`, `weight`: 3},
                       `bones`: {`arm`: {`rotation`: [10, 0, 0]}}},
              `idle_look`: {`layer`: `base`, `priority`: 10, `loop`: true, `length`: 2,
                       `trigger`: {`type`: `state`, `when`: `1`, `group`: `idle`, `weight`: 1},
                       `bones`: {`arm`: {`rotation`: [20, 0, 0]}}},
              `walk`: {`layer`: `base`, `priority`: 20, `loop`: true, `length`: 1, `blend_in`: 0.2,
                       `trigger`: {`type`: `state`, `when`: `q.speed > 0.1`, `exit_delay`: 0.1},
                       `bones`: {`leg`: {`rotation`: {`0`: [30,0,0], `0.5`: [-30,0,0], `1`: [30,0,0]}}},
                       `events`: [{`time`: 0.25, `type`: `footstep`}, {`time`: 0.75, `type`: `footstep`}]},
              `swing`: {`layer`: `action`, `priority`: 200, `length`: 0.5, `blend_in`: 0.05, `blend_out`: 0.1, `interrupt_after`: 0.6,
                       `trigger`: {`type`: `event`, `event`: `attack`},
                       `bones`: {`arm`: {`rotation`: {`0`: [-90,0,0], `0.5`: [60,0,0]}}}},
              `swing_heavy`: {`layer`: `action`, `priority`: 201, `length`: 0.8, `interrupt_after`: 0.6,
                       `trigger`: {`type`: `event`, `event`: `attack`, `when`: `q.heavy`},
                       `bones`: {`arm`: {`rotation`: [-120,0,0]}}},
              `death`: {`layer`: `action`, `priority`: 1000, `length`: 1, `loop`: `hold`,
                       `trigger`: {`type`: `state`, `when`: `q.dead`},
                       `bones`: {`body`: {`rotation`: [0,0,90]}}},
              `breathe`: {`layer`: `additive`, `additive`: true, `loop`: true, `length`: 3, `blend_in`: 0,
                       `trigger`: {`type`: `state`, `when`: `1`},
                       `bones`: {`body`: {`scale`: [1.0, 1.1, 1.0]}}},
              `wave`: {`layer`: `gesture`, `priority`: 300, `length`: 2, `loop`: true,
                       `trigger`: {`type`: `manual`, `stop_when`: `q.speed > 0.1`},
                       `bones`: {`arm`: {`rotation`: [0,0,-150]}}}
            }}""";

    private final Map<String, AnimationClip> clips = TestClips.load(JSON);
    private final Rig rig = new Rig("test", List.of("body", "arm", "leg"), null, Map.of("upper", Set.of("body", "arm")));

    private AnimationController controller(long seed) {
        return new AnimationController(rig, seed, LayerSpec.STANDARD, clips.values());
    }

    private static void run(AnimationController c, float seconds) {
        for (float t = 0; t < seconds; t += 1f / 60f) c.update(1f / 60f);
    }

    private float rot(AnimationController c, String bone, int axis) {
        return c.pose().resolve(rig.indexOf(bone), axis, 0f, 0f) * 180f / (float) Math.PI;
    }

    @Test
    void idlePoolIsDeterministicPerSeed() {
        AnimationController a = controller(7), b = controller(7);
        run(a, 0.5f);
        run(b, 0.5f);
        assertEquals(a.layer("base").current().clip.id(), b.layer("base").current().clip.id());
        assertTrue(a.layer("base").current().clip.id().startsWith("idle"));
    }

    @Test
    void higherPriorityStateTakesOverWithCrossfade() {
        AnimationController c = controller(1);
        run(c, 1f);
        c.scope().set("q.speed", 0.3f);
        c.update(1f / 60f);
        c.update(1f / 60f);
        c.update(1f / 60f);
        c.update(1f / 60f);
        assertEquals("walk", c.layer("base").current().clip.id());
        // Mid-crossfade the arm (idle only) has partial coverage and the leg is fading in.
        float leg = c.pose().overrideWeight[rig.indexOf("leg") * 3];
        assertTrue(leg > 0f && leg < 1f, "leg coverage mid-fade: " + leg);
        run(c, 0.5f);
        assertEquals(1f, c.pose().overrideWeight[rig.indexOf("leg") * 3], 1e-4f);
        assertEquals(0f, c.pose().overrideWeight[rig.indexOf("arm") * 3], 1e-4f, "idle arm faded out");
    }

    @Test
    void stateHysteresisAvoidsFlicker() {
        AnimationController c = controller(1);
        c.scope().set("q.speed", 0.3f);
        run(c, 0.5f);
        c.scope().set("q.speed", 0f);
        c.update(0.05f);
        assertEquals("walk", c.layer("base").current().clip.id(), "exit_delay keeps walk briefly");
        run(c, 0.3f);
        assertNotEquals("walk", c.layer("base").current().clip.id());
    }

    @Test
    void eventsSelectByConditionAndRespectInterruption() {
        AnimationController c = controller(3);
        run(c, 0.2f);
        assertTrue(c.fire("attack"));
        assertEquals("swing", c.layer("action").current().clip.id());
        c.update(0.1f);
        assertFalse(c.fire("attack"), "cannot re-trigger before interrupt_after");
        run(c, 0.25f);
        assertTrue(c.fire("attack"), "combo window after commit point");
        c.scope().set("q.heavy", 1f);
        run(c, 0.4f);
        assertTrue(c.fire("attack"));
        assertEquals("swing_heavy", c.layer("action").current().clip.id(), "the more specific variant is authored with higher priority");
    }

    @Test
    void deathPreemptsActions() {
        AnimationController c = controller(3);
        run(c, 0.2f);
        c.fire("attack");
        c.scope().set("q.dead", 1f);
        c.update(0.05f);
        c.update(0.05f);
        assertEquals("death", c.layer("action").current().clip.id());
        run(c, 1f);
        assertEquals(90f, rot(c, "body", 2), 1e-2f);
    }

    @Test
    void additiveLayerStacksOnOverride() {
        AnimationController c = controller(3);
        run(c, 0.5f);
        int body = rig.indexOf("body");
        float sy = c.pose().resolve(body, 7, 1f, 1f);
        assertEquals(1.1f, sy, 1e-3f);
    }

    @Test
    void loopEventsFireOncePerCycle() {
        AnimationController c = controller(3);
        List<ClipEvent> fired = new ArrayList<>();
        c.setEventSink((ctrl, clip, e, w) -> fired.add(e));
        c.scope().set("q.speed", 0.3f);
        run(c, 3.01f);
        // Walk starts on the first selection pass (~0s) and runs 3 cycles of 1 s with 2 steps each.
        assertTrue(fired.size() >= 5 && fired.size() <= 6, "footsteps fired: " + fired.size());
    }

    @Test
    void manualClipStopsWhenConditionHolds() {
        AnimationController c = controller(3);
        run(c, 0.2f);
        assertTrue(c.play(clips.get("wave"), false));
        run(c, 0.5f);
        assertEquals(-150f, rot(c, "arm", 2), 1e-2f);
        c.scope().set("q.speed", 0.5f);
        run(c, 0.6f);
        assertNull(c.layer("gesture").current());
    }

    @Test
    void timeScaleSlowsPlayback() {
        AnimationController c = controller(3);
        c.setTimeScale(0.25f);
        run(c, 1f);
        assertEquals(0.25f, c.time(), 0.01f);
        assertEquals(0, Vars.id("q.anim_time"));
    }
}
