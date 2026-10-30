package com.motionworks.engine;

import com.motionworks.engine.analysis.MotionSignature;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.Trigger;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.io.ClipJsonLoader;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.LayerSpec;
import com.motionworks.engine.runtime.Rig;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

/** Loads every shipped animation file with the runtime parser and checks the registry rules. */
class ShippedLibraryTest {
    private static final Path ROOT = Path.of("src/main/resources/assets/motionworks/motionworks/animations");

    static List<AnimationClip> loadAll() throws IOException {
        List<AnimationClip> all = new ArrayList<>();
        try (Stream<Path> files = Files.walk(ROOT)) {
            for (Path p : (Iterable<Path>) files.filter(f -> f.toString().endsWith(".json"))::iterator) {
                try (Reader r = Files.newBufferedReader(p)) {
                    all.addAll(ClipJsonLoader.load(r, p.toString()));
                }
            }
        }
        return all;
    }

    @Test
    void everyClipLoadsAndHasMetadata() throws IOException {
        List<AnimationClip> all = loadAll();
        assertFalse(all.isEmpty());
        Set<String> ids = new HashSet<>();
        for (AnimationClip c : all) {
            assertTrue(ids.add(c.id()), "duplicate id " + c.id());
            assertTrue(c.length() > 0f, c.id() + " has no duration");
            assertFalse(c.tracks().isEmpty(), c.id() + " has no tracks");
            assertNotNull(c.meta().get("status"), c.id());
            assertNotNull(c.meta().get("controller"), c.id());
            if (c.trigger().type() == Trigger.Type.EVENT) assertNotNull(c.trigger().event(), c.id());
        }
        System.out.println("Shipped clips: " + all.size());
    }

    @Test
    void noVariantsCountedAsUniqueAnimations() throws IOException {
        List<MotionSignature.Duplicate> dups = MotionSignature.findDuplicates(loadAll(), 0.995f);
        StringBuilder sb = new StringBuilder();
        for (MotionSignature.Duplicate d : dups.subList(0, Math.min(25, dups.size()))) {
            sb.append(d.a().id()).append(" ~ ").append(d.b().id()).append(" (").append(d.kind()).append(' ').append(d.score()).append(")\n");
        }
        assertTrue(dups.isEmpty(), dups.size() + " near-duplicate clips:\n" + sb);
    }

    @Test
    void everyClipEvaluatesOnAGenericRig() throws IOException {
        Map<String, List<AnimationClip>> byTarget = new HashMap<>();
        for (AnimationClip c : loadAll()) byTarget.computeIfAbsent(c.target(), k -> new ArrayList<>()).add(c);
        for (Map.Entry<String, List<AnimationClip>> e : byTarget.entrySet()) {
            Set<String> bones = new HashSet<>();
            for (AnimationClip c : e.getValue()) c.tracks().forEach(t -> bones.add(t.bone()));
            Rig rig = new Rig(e.getKey(), new ArrayList<>(bones), null, Map.of());
            AnimationController ctrl = new AnimationController(rig, 1, LayerSpec.STANDARD, e.getValue());
            Scope s = ctrl.scope();
            s.set("q.ground_speed", 0.2f);
            s.set("q.is_on_ground", 1f);
            s.set("q.limb_swing", 3f);
            s.set("q.limb_swing_amount", 0.8f);
            for (AnimationClip c : e.getValue()) {
                ctrl.play(c, true);
                ctrl.update(0.05f);
                ctrl.update(c.length() * 0.5f);
                for (float v : ctrl.pose().override) assertTrue(Float.isFinite(v), c.id() + " produced a non-finite value");
                for (float v : ctrl.pose().additive) assertTrue(Float.isFinite(v), c.id() + " produced a non-finite additive value");
            }
            for (String ev : List.of("attack", "hurt", "land", "jump", "interact", "swing")) ctrl.fire(ev);
            ctrl.update(0.1f);
        }
    }
}
