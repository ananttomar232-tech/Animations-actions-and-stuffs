package com.motionworks.engine;

import com.google.gson.JsonParser;
import com.motionworks.engine.analysis.MotionSignature;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.Trigger;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.io.ClipJsonLoader;
import com.motionworks.engine.procedural.TwoBoneIK;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class LoaderAndSignatureTest {
    @Test
    void bedrockImportFlipsAxesAndReadsEvents() {
        String bedrock = """
                {"format_version": "1.8.0", "animations": {
                  "animation.test.wave": {
                    "loop": true, "animation_length": 1.0,
                    "bones": {"arm": {"rotation": {"0.0": [10, 20, 30], "1.0": [0, 0, 0]}, "position": [1, 2, 3]}},
                    "sound_effects": {"0.5": {"effect": "whoosh"}},
                    "motionworks": {"category": "emotes", "layer": "gesture"}
                  }}}""";
        List<AnimationClip> clips = ClipJsonLoader.load(JsonParser.parseString(bedrock).getAsJsonObject(), "bedrock");
        AnimationClip c = clips.get(0);
        assertEquals("test.wave", c.id());
        assertEquals("emotes", c.category());
        assertEquals("gesture", c.layer());
        assertEquals(1, c.events().size());
        assertEquals("whoosh", c.events().get(0).get("effect", ""));
        float[] out = new float[3];
        c.track("arm").rotation().sample(0f, new Scope(), out, 0);
        assertArrayEquals(new float[] {-10, -20, 30}, out, 1e-4f);
        c.track("arm").position().sample(0f, new Scope(), out, 0);
        assertArrayEquals(new float[] {-1, -2, 3}, out, 1e-4f);
        assertEquals(Trigger.Type.MANUAL, c.trigger().type());
    }

    @Test
    void signatureFlagsSpeedAmplitudeAndMirrorVariants() {
        Map<String, AnimationClip> clips = TestClips.load("""
                {`clips`: {
                  `wave`: {`length`: 1, `bones`: {`right_arm`: {`rotation`: {`0`: [0,0,0], `0.5`: [0,0,-120], `1`: [0,0,-90]}}}},
                  `wave_fast`: {`length`: 0.5, `bones`: {`right_arm`: {`rotation`: {`0`: [0,0,0], `0.25`: [0,0,-120], `0.5`: [0,0,-90]}}}},
                  `wave_big`: {`length`: 1, `bones`: {`right_arm`: {`rotation`: {`0`: [0,0,0], `0.5`: [0,0,-132], `1`: [0,0,-99]}}}},
                  `wave_left`: {`length`: 1, `bones`: {`left_arm`: {`rotation`: {`0`: [0,0,0], `0.5`: [0,0,120], `1`: [0,0,90]}}}},
                  `salute`: {`length`: 1, `bones`: {`right_arm`: {`rotation`: {`0`: [0,0,0], `0.3`: [-140,0,-30], `1`: [-140,0,-30]}}}}
                }}""");
        List<MotionSignature.Duplicate> dups = MotionSignature.findDuplicates(clips.values(), 0.995f);
        assertTrue(dups.stream().anyMatch(d -> pair(d, "wave", "wave_fast")), "speed variant");
        assertTrue(dups.stream().anyMatch(d -> pair(d, "wave", "wave_big")), "amplitude variant");
        assertTrue(dups.stream().anyMatch(d -> pair(d, "wave", "wave_left")), "mirror variant");
        assertFalse(dups.stream().anyMatch(d -> d.a().id().equals("salute") || d.b().id().equals("salute")), "distinct motion");
    }

    private static boolean pair(MotionSignature.Duplicate d, String a, String b) {
        return (d.a().id().equals(a) && d.b().id().equals(b)) || (d.a().id().equals(b) && d.b().id().equals(a));
    }

    @Test
    void twoBoneIkReachesTarget() {
        TwoBoneIK.Solution s = TwoBoneIK.solve(6f, 6f, 7f, 3f, true);
        assertTrue(s.reachable());
        float[] end = TwoBoneIK.forward(6f, 6f, s.rootAngle(), s.jointAngle());
        assertEquals(7f, end[0], 1e-3f);
        assertEquals(3f, end[1], 1e-3f);
        TwoBoneIK.Solution far = TwoBoneIK.solve(6f, 6f, 30f, 0f, false);
        assertFalse(far.reachable());
    }
}
