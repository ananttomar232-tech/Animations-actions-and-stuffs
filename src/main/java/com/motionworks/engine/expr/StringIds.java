package com.motionworks.engine.expr;

import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Interns categorical string values (item categories, surfaces, professions...) to small exact
 * floats so expressions such as {@code q.main_hand == 'sword'} compile to numeric comparisons.
 * Id 0 is reserved for "none"/empty.
 */
public final class StringIds {
    private static final Map<String, Integer> IDS = new ConcurrentHashMap<>();
    private static int next = 1;

    static {
        IDS.put("", 0);
        IDS.put("none", 0);
    }

    private StringIds() {}

    public static synchronized int id(String value) {
        if (value == null) return 0;
        String v = value.toLowerCase(Locale.ROOT);
        Integer i = IDS.get(v);
        if (i != null) return i;
        int id = next++;
        IDS.put(v, id);
        return id;
    }
}
