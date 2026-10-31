package com.motionworks.server;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Consumer;

/**
 * Observers of every animation trigger the server sends. {@code /motionworks trace on} prints them to
 * the player's chat so pack authors can see which event names fire, with which argument, and bind
 * clips to them; the in-game tests subscribe to assert that vanilla code paths reach the triggers.
 */
public final class TriggerTrace {
    private TriggerTrace() {}

    /** One sent trigger; entityId is -1 for positional world events. */
    public record Entry(int entityId, String entity, String event, String arg, Vec3 pos) {
        /** The name a clip trigger matches: "event" or "event:arg". */
        public String key() {
            return arg.isEmpty() ? event : event + ":" + arg;
        }
    }

    public static final double CHAT_RANGE = 48;
    private static final List<Consumer<Entry>> LISTENERS = new CopyOnWriteArrayList<>();
    private static final Set<UUID> TRACING = new HashSet<>();

    /** Subscribes until the returned handle is run. */
    public static Runnable listen(Consumer<Entry> listener) {
        LISTENERS.add(listener);
        return () -> LISTENERS.remove(listener);
    }

    public static void setTracing(ServerPlayer player, boolean on) {
        if (on) TRACING.add(player.getUUID());
        else TRACING.remove(player.getUUID());
    }

    static void clearTracing() {
        TRACING.clear();
    }

    static void entity(Entity e, String event, String arg) {
        if (LISTENERS.isEmpty() && TRACING.isEmpty() || !(e.level() instanceof ServerLevel level)) return;
        publish(level, new Entry(e.getId(), BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()) + " #" + e.getId(), event, arg, e.position()));
    }

    static void world(ServerLevel level, Vec3 at, String event, String arg) {
        if (LISTENERS.isEmpty() && TRACING.isEmpty()) return;
        publish(level, new Entry(-1, "world", event, arg, at));
    }

    private static void publish(ServerLevel level, Entry entry) {
        for (Consumer<Entry> l : LISTENERS) l.accept(entry);
        if (TRACING.isEmpty()) return;
        for (ServerPlayer p : level.players()) {
            if (TRACING.contains(p.getUUID()) && p.distanceToSqr(entry.pos()) < CHAT_RANGE * CHAT_RANGE) {
                p.sendSystemMessage(Component.translatable("motionworks.trace.entry", entry.entity(), entry.key()).withStyle(ChatFormatting.GRAY));
            }
        }
    }
}
