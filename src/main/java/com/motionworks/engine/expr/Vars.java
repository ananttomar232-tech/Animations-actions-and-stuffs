package com.motionworks.engine.expr;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Global registry interning variable names to dense integer ids. Expressions are compiled
 * against ids so evaluation is an array lookup. Aliases follow Molang: {@code query.} and
 * {@code q.} are the same namespace, as are {@code variable.}/{@code v.} and {@code context.}/{@code c.}.
 */
public final class Vars {
    private static final Map<String, Integer> IDS = new ConcurrentHashMap<>();
    private static final List<String> NAMES = new ArrayList<>();

    /** Clip-local variables resolved by the evaluating scope rather than the entity context. */
    public static final int ANIM_TIME = id("q.anim_time");
    public static final int ANIM_PROGRESS = id("q.anim_progress");
    public static final int ANIM_LOOP = id("q.anim_loop");
    public static final int DELTA_TIME = id("q.delta_time");
    public static final int LOCAL_LIMIT = DELTA_TIME + 1;

    private Vars() {}

    public static String normalize(String name) {
        String n = name.trim().toLowerCase(Locale.ROOT);
        if (n.startsWith("query.")) n = "q." + n.substring(6);
        else if (n.startsWith("variable.")) n = "v." + n.substring(9);
        else if (n.startsWith("context.")) n = "c." + n.substring(8);
        else if (n.startsWith("temp.")) n = "t." + n.substring(5);
        return n;
    }

    public static synchronized int id(String name) {
        String n = normalize(name);
        Integer existing = IDS.get(n);
        if (existing != null) return existing;
        int id = NAMES.size();
        NAMES.add(n);
        IDS.put(n, id);
        return id;
    }

    public static int idIfPresent(String name) {
        Integer i = IDS.get(normalize(name));
        return i == null ? -1 : i;
    }

    public static synchronized String name(int id) {
        return id >= 0 && id < NAMES.size() ? NAMES.get(id) : "?" + id;
    }

    public static synchronized int count() {
        return NAMES.size();
    }

    public static synchronized List<String> names() {
        return List.copyOf(NAMES);
    }
}
