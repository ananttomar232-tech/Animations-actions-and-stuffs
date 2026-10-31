package com.motionworks.common;

import org.junit.jupiter.api.Test;

import java.util.Locale;

import static org.junit.jupiter.api.Assertions.*;

class WorldEventArgsTest {
    @Test
    void positionRoundTripsWithDefaultMagnitude() {
        assertArrayEquals(new double[]{12.5, 64.0, -300.2, 1}, WorldEventArgs.decode(WorldEventArgs.encode(12.5, 64, -300.24)), 1e-9);
    }

    @Test
    void magnitudeRoundTrips() {
        assertArrayEquals(new double[]{0.0, -5.0, 7.0, 4.0}, WorldEventArgs.decode(WorldEventArgs.encode(0, -5, 7, 4f)), 1e-9);
    }

    @Test
    void encodingIgnoresTheDefaultLocale() {
        Locale saved = Locale.getDefault();
        try {
            Locale.setDefault(Locale.GERMANY);
            String arg = WorldEventArgs.encode(1.5, 2.5, 3.5, 6f);
            assertEquals("1.5,2.5,3.5,6.0", arg);
            assertNotNull(WorldEventArgs.decode(arg));
        } finally {
            Locale.setDefault(saved);
        }
    }

    @Test
    void malformedArgumentsAreRejected() {
        assertNull(WorldEventArgs.decode(""));
        assertNull(WorldEventArgs.decode("1,2"));
        assertNull(WorldEventArgs.decode("1,2,3,4,5"));
        assertNull(WorldEventArgs.decode("1,x,3"));
        assertNull(WorldEventArgs.decode("1,NaN,3"));
        assertNull(WorldEventArgs.decode("1,2,Infinity"));
    }
}
