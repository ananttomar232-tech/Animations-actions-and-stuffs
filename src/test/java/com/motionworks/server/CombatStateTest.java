package com.motionworks.server;

import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

/** Combat windows are game ticks of one world; times from another world must not grant anything. */
class CombatStateTest {
    private final UUID player = UUID.randomUUID();

    @Test
    void liveWindowsArePendingUntilTheyExpire() {
        Map<UUID, Long> until = new HashMap<>();
        until.put(player, 1006L);
        assertTrue(CombatMechanics.pending(until, player, 1000L));
        assertFalse(CombatMechanics.pending(until, player, 1006L));
        assertFalse(CombatMechanics.pending(until, player, 2000L));
    }

    @Test
    void aTimeFromAnotherWorldIsDroppedNotHonoured() {
        // Dodged at tick 500000 in one world, then joined a new world at tick 1000 in the same session.
        Map<UUID, Long> until = new HashMap<>();
        until.put(player, 500_006L);
        assertFalse(CombatMechanics.pending(until, player, 1000L), "would have meant invulnerability for ~7 hours");
        assertFalse(until.containsKey(player), "the stale entry is removed");
    }

    @Test
    void noRecordMeansNothingPending() {
        assertFalse(CombatMechanics.pending(new HashMap<>(), player, 1000L));
    }
}
