package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.expr.Scope;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

/** Every shipped clip, sampled like playback: see {@link MotionReview} for what is measured. */
class MotionQualityTest {
    /** Deliberately faster than one frame's worth of motion, with the reason. */
    private static final Map<String, String> FAST_ON_PURPOSE = Map.of(
            "frog.tongue_lash", "a whip strike that extends the tongue as fast as vanilla's own tongue animation",
            "elder_guardian.spike_bristle", "spikes popping out are meant to read as instant");

    @Test
    void noShippedClipGlitches() throws IOException {
        List<String> found = new ArrayList<>();
        for (AnimationClip c : ShippedLibraryTest.loadAll()) {
            List<MotionReview.Finding> f = new ArrayList<>(MotionReview.review(c, new Scope(), "zero"));
            f.addAll(MotionReview.review(c, MotionReview.realistic(), "realistic"));
            f.addAll(MotionReview.review(c, MotionReview.random(c.id().hashCode()), "random"));
            for (MotionReview.Finding x : f) {
                if (x.kind().equals("frame_jump") && FAST_ON_PURPOSE.containsKey(x.clip())) continue;
                found.add(String.format("%s %s %s %.2f", x.clip(), x.kind(), x.detail(), x.amount()));
            }
        }
        assertEquals(List.of(), found.stream().distinct().toList());
    }
}
