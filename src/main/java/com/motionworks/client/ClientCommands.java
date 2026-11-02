package com.motionworks.client;

import com.motionworks.MotionWorks;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.suggestion.SuggestionProvider;
import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.cinematic.CameraRecorder;
import com.motionworks.client.cinematic.CinematicDirector;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.network.EmotePacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.client.Minecraft;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.fml.loading.FMLPaths;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

/**
 * Client-side tooling: {@code /mw play|list|stats|export|audit|doctor|debug|emote}, {@code /mw cinematic ...}
 * and the {@code /mw cam ...} camera recorder.
 */
public final class ClientCommands {
    private static final SuggestionProvider<CommandSourceStack> CLIPS = (c, b) ->
            SharedSuggestionProvider.suggest(AnimationLibrary.INSTANCE.clips().all().stream().map(AnimationClip::id), b);
    private static final SuggestionProvider<CommandSourceStack> CINEMATICS = (c, b) ->
            SharedSuggestionProvider.suggest(CinematicDirector.INSTANCE.library().keySet(), b);

    private ClientCommands() {}

    public static void register(CommandDispatcher<CommandSourceStack> d) {
        d.register(Commands.literal("mw")
                .then(Commands.literal("play").then(Commands.argument("clip", StringArgumentType.greedyString()).suggests(CLIPS)
                        .executes(c -> play(StringArgumentType.getString(c, "clip")))))
                .then(Commands.literal("emote").then(Commands.argument("clip", StringArgumentType.greedyString()).suggests(CLIPS)
                        .executes(c -> {
                            int r = play(StringArgumentType.getString(c, "clip"));
                            MWNetwork.CHANNEL.sendToServer(new EmotePacket(StringArgumentType.getString(c, "clip")));
                            return r;
                        })))
                .then(Commands.literal("stats").executes(c -> stats()))
                .then(Commands.literal("list").executes(c -> list("")).then(Commands.argument("filter", StringArgumentType.greedyString())
                        .executes(c -> list(StringArgumentType.getString(c, "filter")))))
                .then(Commands.literal("export").executes(c -> export()))
                .then(Commands.literal("audit").executes(c -> audit()))
                .then(Commands.literal("doctor").executes(c -> doctor()))
                .then(Commands.literal("debug").executes(c -> {
                    MWConfig.CLIENT.debugOverlay.set(!MWConfig.CLIENT.debugOverlay.get());
                    return 1;
                }))
                .then(Commands.literal("cinematic")
                        .then(Commands.literal("play").then(Commands.argument("id", StringArgumentType.greedyString()).suggests(CINEMATICS)
                                .executes(c -> say(CinematicDirector.INSTANCE.play(StringArgumentType.getString(c, "id"), null)
                                        ? "motionworks.cinematic.playing" : "motionworks.cinematic.unknown", StringArgumentType.getString(c, "id")))))
                        .then(Commands.literal("stop").executes(c -> {
                            CinematicDirector.INSTANCE.stop();
                            return 1;
                        }))
                        .then(Commands.literal("list").executes(c -> say("motionworks.cinematic.list", String.join(", ", CinematicDirector.INSTANCE.library().keySet())))))
                .then(Commands.literal("cam")
                        .then(Commands.literal("add").executes(c -> say("motionworks.cam.added", String.valueOf(CameraRecorder.add(2f))))
                                .then(Commands.argument("seconds", FloatArgumentType.floatArg(0.1f, 60f))
                                        .executes(c -> say("motionworks.cam.added", String.valueOf(CameraRecorder.add(FloatArgumentType.getFloat(c, "seconds")))))))
                        .then(Commands.literal("clear").executes(c -> {
                            CameraRecorder.clear();
                            return say("motionworks.cam.cleared", "");
                        }))
                        .then(Commands.literal("preview").executes(c -> say(CameraRecorder.preview() ? "motionworks.cam.preview" : "motionworks.cam.need_two", "")))
                        .then(Commands.literal("save").then(Commands.argument("name", StringArgumentType.word()).executes(c -> {
                            try {
                                Path p = CameraRecorder.save(StringArgumentType.getString(c, "name"));
                                return say("motionworks.cam.saved", p.toString());
                            } catch (Exception e) {
                                return say("motionworks.cam.failed", e.getMessage());
                            }
                        })))));
    }

    private static int say(String key, String arg) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null) mc.player.displayClientMessage(Component.translatable(key, arg), false);
        return 1;
    }

    private static int play(String id) {
        Minecraft mc = Minecraft.getInstance();
        AnimationClip clip = AnimationLibrary.INSTANCE.clips().get(id);
        if (clip == null || mc.player == null) return say("motionworks.play.unknown", id);
        LivingEntity target = mc.player;
        if (mc.hitResult instanceof EntityHitResult ehr && ehr.getEntity() instanceof LivingEntity le) target = le;
        if ("@first_person".equals(clip.target())) {
            FirstPersonAnimator.INSTANCE.play(clip);
            return say("motionworks.play.ok", id);
        }
        boolean ok = AnimatorManager.get(target).play(clip);
        return say(ok ? "motionworks.play.ok" : "motionworks.play.not_bound", id);
    }

    /** Why third-person animation is or is not showing in this game: hook, other mods, config. Also written to the log. */
    private static int doctor() {
        for (String line : com.motionworks.client.rig.RenderHealth.report()) {
            say("motionworks.doctor.line", line);
            MotionWorks.LOGGER.info("MotionWorks doctor: {}", line);
        }
        return 1;
    }

    private static int stats() {
        var lib = AnimationLibrary.INSTANCE.clips();
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, Integer> e : lib.countByCategory().entrySet()) sb.append(e.getKey()).append('=').append(e.getValue()).append("  ");
        say("motionworks.stats", lib.size() + " clips: " + sb);
        if (!AnimationLibrary.INSTANCE.errors().isEmpty()) say("motionworks.stats.errors", String.valueOf(AnimationLibrary.INSTANCE.errors().size()));
        return 1;
    }

    private static int list(String filter) {
        StringBuilder sb = new StringBuilder();
        int n = 0;
        for (AnimationClip c : AnimationLibrary.INSTANCE.clips().all()) {
            if (!filter.isEmpty() && !c.id().contains(filter)) continue;
            if (n++ < 40) sb.append(c.id()).append(", ");
        }
        return say("motionworks.list", n + ": " + sb);
    }

    /** Writes the live registry (every loaded clip with its metadata) for auditing. */
    private static int audit() {
        Path p = FMLPaths.GAMEDIR.get().resolve("motionworks_audit.txt");
        com.motionworks.client.rig.LibraryAudit.Result r = com.motionworks.client.rig.LibraryAudit.runAndWrite(p);
        if (r == null) return 0;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null) mc.player.displayClientMessage(Component.translatable("motionworks.audit.done", r.clips(), r.models(), r.issues(), p.toString()), false);
        return 1;
    }

    private static int export() {
        JsonArray arr = new JsonArray();
        for (AnimationClip c : AnimationLibrary.INSTANCE.clips().all()) {
            JsonObject o = new JsonObject();
            o.addProperty("id", c.id());
            o.addProperty("name", c.name());
            o.addProperty("category", c.category());
            o.addProperty("target", c.target());
            o.addProperty("trigger", c.trigger().type().name().toLowerCase() + (c.trigger().event() != null ? ":" + c.trigger().event() : ""));
            o.addProperty("duration", c.length());
            o.addProperty("priority", c.priority());
            o.addProperty("layer", c.layer());
            o.addProperty("rig", c.rig());
            o.addProperty("keyframes", c.keyCount());
            arr.add(o);
        }
        try {
            Path p = FMLPaths.GAMEDIR.get().resolve("motionworks_registry_export.json");
            Files.writeString(p, new GsonBuilder().setPrettyPrinting().create().toJson(arr));
            return say("motionworks.export", p.toString());
        } catch (Exception e) {
            return say("motionworks.cam.failed", e.getMessage());
        }
    }
}
