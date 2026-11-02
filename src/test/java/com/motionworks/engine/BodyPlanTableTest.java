package com.motionworks.engine;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.motionworks.engine.io.BodyPlanTable;
import org.junit.jupiter.api.Test;

import java.io.Reader;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** The rules that animate entity types without a family (mobs from other mods), and the shipped rule file. */
class BodyPlanTableTest {
    private static final Path DATA = Path.of("src/main/resources/assets/motionworks/motionworks");

    private static BodyPlanTable shipped() throws Exception {
        BodyPlanTable t = new BodyPlanTable();
        try (Reader r = Files.newBufferedReader(DATA.resolve("body_plans.json"))) {
            t.load(r, "body_plans.json");
        }
        return t;
    }

    @Test
    void everyPlanBorrowsAFamilyThatExistsWithARigThatExists() throws Exception {
        JsonObject families;
        try (Reader r = Files.newBufferedReader(DATA.resolve("entities.json"))) {
            families = JsonParser.parseReader(r).getAsJsonObject();
        }
        BodyPlanTable t = shipped();
        assertTrue(t.plans().size() > 5);
        for (BodyPlanTable.Plan p : t.plans()) {
            if (p.like() == null) continue;
            assertTrue(families.has(p.like()), p.like() + " is not a family in entities.json");
            String rig = families.getAsJsonObject(p.like()).get("rig").getAsString();
            assertTrue(Files.exists(DATA.resolve("rigs/" + rig + ".json")), "rig " + rig + " of " + p.like());
        }
        // The last rule catches everything, so no entity type is left unclassified.
        assertEquals("any", t.plans().get(t.plans().size() - 1).shape());
        assertTrue(t.excluded().contains("minecraft:armor_stand"), "an armour stand is humanoid but must keep still");
    }

    @Test
    void firstMatchingPlanWinsAndEveryTraitMustHold() throws Exception {
        BodyPlanTable t = shipped();
        assertEquals("minecraft:skeleton", t.match("humanoid", List.of("undead", "skeleton", "hostile")).like());
        assertEquals("minecraft:zombie", t.match("humanoid", List.of("undead", "hostile")).like());
        assertEquals("minecraft:piglin", t.match("humanoid", List.of("piglin", "hostile")).like());
        assertEquals("minecraft:player", t.match("humanoid", List.of()).like());
        assertEquals("minecraft:polar_bear", t.match("quadruped", List.of("hostile")).like());
        assertEquals("minecraft:cow", t.match("quadruped", List.of("animal")).like());
        assertEquals("minecraft:cod", t.match("aquatic", List.of("fish", "water")).like());
        assertEquals("minecraft:dolphin", t.match("aquatic", List.of("water")).like());
        assertEquals("minecraft:phantom", t.match("winged", List.of("flying_mob", "hostile")).like());
        assertEquals("minecraft:parrot", t.match("winged", List.of("animal", "flying_animal")).like());
        assertNull(t.match("other", List.of("hostile")).like(), "an unknown body keeps vanilla animation");
    }

    @Test
    void shapesComeFromVanillaPartNames() {
        Set<String> humanoid = Set.of("head", "hat", "body", "right_arm", "left_arm", "right_leg", "left_leg");
        assertEquals("humanoid", BodyPlanTable.shapeOf(humanoid, false, false, false, false));
        Set<String> illager = Set.of("head", "hat", "nose", "body", "arms", "right_arm", "left_arm", "right_leg", "left_leg");
        assertEquals("illager", BodyPlanTable.shapeOf(illager, false, true, false, false), "illagers have both folded and separate arms");
        assertEquals("humanoid", BodyPlanTable.shapeOf(illager, false, false, false, false));
        Set<String> villager = Set.of("head", "hat", "hat_rim", "nose", "body", "jacket", "arms", "right_leg", "left_leg");
        assertEquals("villager", BodyPlanTable.shapeOf(villager, false, false, true, false));
        Set<String> horse = Set.of("body", "head_parts", "tail", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg",
                "right_hind_baby_leg", "left_hind_baby_leg", "right_front_baby_leg", "left_front_baby_leg");
        assertEquals("equine", BodyPlanTable.shapeOf(horse, true, false, false, false), "a horse's baby legs are not more legs");
        Set<String> cow = Set.of("head", "body", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg");
        assertEquals("quadruped", BodyPlanTable.shapeOf(cow, false, false, false, false));
        Set<String> spider = Set.of("head", "body0", "body1", "right_hind_leg", "left_hind_leg", "right_middle_hind_leg", "left_middle_hind_leg",
                "right_middle_front_leg", "left_middle_front_leg", "right_front_leg", "left_front_leg");
        assertEquals("arthropod", BodyPlanTable.shapeOf(spider, false, false, false, false));
        Set<String> chicken = Set.of("head", "beak", "red_thing", "body", "right_leg", "left_leg", "right_wing", "left_wing");
        assertEquals("winged", BodyPlanTable.shapeOf(chicken, false, false, false, false));
        Set<String> cod = Set.of("body", "head", "nose", "top_fin", "tail_fin");
        assertEquals("aquatic", BodyPlanTable.shapeOf(cod, false, false, false, true));
        assertEquals("other", BodyPlanTable.shapeOf(Set.of("cube"), false, false, false, false));
    }

    @Test
    void packsCanAddPlansButNotUnknownShapesOrTraits() {
        BodyPlanTable t = new BodyPlanTable();
        t.load(new StringReader("{\"exclude\":[\"mymod:statue\"],\"plans\":[{\"shape\":\"quadruped\",\"traits\":[\"water\"],\"like\":\"minecraft:turtle\"}]}"), "pack");
        assertEquals("minecraft:turtle", t.match("quadruped", List.of("water", "animal")).like());
        assertNull(t.match("quadruped", List.of("animal")));
        assertTrue(t.excluded().contains("mymod:statue"));
        assertThrows(IllegalArgumentException.class, () -> t.load(new StringReader("{\"plans\":[{\"shape\":\"blob\"}]}"), "bad"));
        assertThrows(IllegalArgumentException.class, () -> t.load(new StringReader("{\"plans\":[{\"shape\":\"any\",\"traits\":[\"shiny\"]}]}"), "bad"));
    }
}
