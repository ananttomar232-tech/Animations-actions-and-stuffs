package com.motionworks.server;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.motionworks.network.AnimationEventPacket;
import com.motionworks.network.CinematicPacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.RegisterCommandsEvent;

/**
 * {@code /motionworks cinematic <players> <id> [anchor]}, {@code /motionworks cinematic <players> stop}
 * and {@code /motionworks animate <entities> <clip>} for map makers and servers, and
 * {@code /motionworks trace on|off}, which prints every animation trigger the server sends near you.
 */
public final class ServerCommands {
    private ServerCommands() {}

    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("motionworks").requires(s -> s.hasPermission(2))
                .then(Commands.literal("cinematic")
                        .then(Commands.argument("players", EntityArgument.players())
                                .then(Commands.literal("stop").executes(c -> {
                                    for (ServerPlayer p : EntityArgument.getPlayers(c, "players")) MWNetwork.toPlayer(p, new CinematicPacket("", -1));
                                    return 1;
                                }))
                                .then(Commands.argument("id", StringArgumentType.string())
                                        .executes(c -> cinematic(c.getSource(), EntityArgument.getPlayers(c, "players"), StringArgumentType.getString(c, "id"), null))
                                        .then(Commands.argument("anchor", EntityArgument.entity())
                                                .executes(c -> cinematic(c.getSource(), EntityArgument.getPlayers(c, "players"),
                                                        StringArgumentType.getString(c, "id"), EntityArgument.getEntity(c, "anchor")))))))
                .then(Commands.literal("trace")
                        .then(Commands.literal("on").executes(c -> trace(c.getSource(), true)))
                        .then(Commands.literal("off").executes(c -> trace(c.getSource(), false))))
                .then(Commands.literal("animate")
                        .then(Commands.argument("targets", EntityArgument.entities())
                                .then(Commands.argument("clip", StringArgumentType.greedyString()).executes(c -> {
                                    String clip = StringArgumentType.getString(c, "clip");
                                    int n = 0;
                                    for (Entity e : EntityArgument.getEntities(c, "targets")) {
                                        MWNetwork.toTrackers(e, new AnimationEventPacket(e.getId(), "play_clip", clip, 0f), true);
                                        n++;
                                    }
                                    int count = n;
                                    c.getSource().sendSuccess(() -> Component.translatable("motionworks.command.animate", clip, count), false);
                                    return n;
                                })))));
    }

    private static int trace(CommandSourceStack src, boolean on) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        TriggerTrace.setTracing(src.getPlayerOrException(), on);
        src.sendSuccess(() -> Component.translatable(on ? "motionworks.trace.on" : "motionworks.trace.off", (int) TriggerTrace.CHAT_RANGE), false);
        return 1;
    }

    private static int cinematic(CommandSourceStack src, java.util.Collection<ServerPlayer> players, String id, Entity anchor) {
        for (ServerPlayer p : players) MWNetwork.toPlayer(p, new CinematicPacket(id, anchor == null ? p.getId() : anchor.getId()));
        src.sendSuccess(() -> Component.translatable("motionworks.command.cinematic", id, players.size()), true);
        return players.size();
    }
}
