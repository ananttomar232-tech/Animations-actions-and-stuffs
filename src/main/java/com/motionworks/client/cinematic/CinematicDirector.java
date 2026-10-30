package com.motionworks.client.cinematic;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.motionworks.MotionWorks;
import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.client.camera.CameraEffects;
import com.motionworks.client.particle.Effects;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.math.MathUtil;
import com.motionworks.registry.MWSounds;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraftforge.registries.ForgeRegistries;

import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Stream;

/**
 * Plays authored cinematic sequences: drives the camera through shots (with cuts or blends),
 * fires timeline events (actor animation, sound, particles, dialogue, titles, fades, flashes,
 * slow motion, shake) and exposes overlay state. Sequences are always skippable unless an author
 * explicitly opts out, and by default end immediately if the player takes damage.
 */
public final class CinematicDirector implements ResourceManagerReloadListener {
    public static final CinematicDirector INSTANCE = new CinematicDirector();

    public record Shot(Vec3 position, float yaw, float pitch, float roll, float fov) {}

    private final Map<String, Sequence> library = new TreeMap<>();

    private Sequence active;
    private SequenceContext ctx;
    private float time;
    private int nextEvent;
    private long lastNanos;
    private float timeScale = 1f;
    private float timeScaleUntil = -1f;
    private Shot current;
    private ShotEvaluator.Placement blendFrom;
    private float lastHealth = -1f;

    // Overlay state
    float letterbox;
    boolean letterboxWanted;
    float fadeAlpha;
    float fadeFrom, fadeTo, fadeStart = -1f, fadeDuration;
    int fadeColor;
    Component title, subtitle;
    float titleStart = -1f, titleDuration;
    Component speaker, line;
    float lineStart = -1f, lineDuration;
    float flash;
    long titleCardUntil;

    private CinematicDirector() {}

    @Override
    public void onResourceManagerReload(ResourceManager manager) {
        library.clear();
        Map<ResourceLocation, Resource> files = manager.listResources("motionworks/cinematics", l -> l.getPath().endsWith(".json"));
        files.forEach((loc, res) -> {
            String id = loc.getNamespace() + ":" + loc.getPath().substring("motionworks/cinematics/".length()).replace(".json", "");
            try (Reader r = res.openAsReader()) {
                library.put(id, Sequence.parse(id, JsonParser.parseReader(r).getAsJsonObject()));
            } catch (Exception e) {
                MotionWorks.LOGGER.error("Bad cinematic {}: {}", loc, e.getMessage());
            }
        });
        loadUserSequences();
        MotionWorks.LOGGER.info("MotionWorks loaded {} cinematic sequences", library.size());
    }

    /** User-recorded sequences live in config/motionworks/cinematics. */
    public void loadUserSequences() {
        Path dir = userDir();
        if (!Files.isDirectory(dir)) return;
        try (Stream<Path> s = Files.list(dir)) {
            s.filter(p -> p.toString().endsWith(".json")).forEach(p -> {
                String id = "user:" + p.getFileName().toString().replace(".json", "");
                try (Reader r = Files.newBufferedReader(p)) {
                    library.put(id, Sequence.parse(id, JsonParser.parseReader(r).getAsJsonObject()));
                } catch (Exception e) {
                    MotionWorks.LOGGER.error("Bad user cinematic {}: {}", p, e.getMessage());
                }
            });
        } catch (Exception e) {
            MotionWorks.LOGGER.error("Could not list {}", dir, e);
        }
    }

    public static Path userDir() {
        return FMLPaths.CONFIGDIR.get().resolve("motionworks").resolve("cinematics");
    }

    public Map<String, Sequence> library() {
        return library;
    }

    public boolean isActive() {
        return active != null;
    }

    public Sequence active() {
        return active;
    }

    public float timeScale() {
        return active != null ? timeScale : 1f;
    }

    public boolean play(String id, Entity anchor) {
        Sequence s = library.get(id.contains(":") ? id : MotionWorks.MOD_ID + ":" + id);
        if (s == null) s = library.get(id);
        if (s == null) return false;
        return play(s, anchor);
    }

    public boolean play(Sequence s, Entity anchorOverride) {
        if (!MWConfig.CLIENT.cinematics.get()) return false;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return false;
        stop();
        ctx = new SequenceContext(mc.player);
        Entity anchor = anchorOverride != null ? anchorOverride : ctx.resolve(s.anchor);
        if (anchor == null) anchor = mc.player;
        ctx = new SequenceContext(anchor);
        active = s;
        time = 0f;
        nextEvent = 0;
        lastNanos = Util.getNanos();
        timeScale = 1f;
        timeScaleUntil = -1f;
        letterboxWanted = s.letterbox && MWConfig.CLIENT.letterbox.get();
        blendFrom = null;
        lastHealth = mc.player.getHealth();
        return true;
    }

    public void stop() {
        if (active == null) return;
        active = null;
        ctx = null;
        current = null;
        letterboxWanted = false;
        timeScale = 1f;
        lineStart = -1f;
        titleStart = -1f;
        fadeStart = -1f;
        fadeAlpha = 0f;
        AnimatorManager.setGlobalTimeScale(1f);
    }

    public void skip() {
        if (active != null && active.skippable) stop();
    }

    /** Short presentation without camera control: letterbox, title, sting. */
    public void titleCard(Component titleText, Component subtitleText, float seconds) {
        if (!MWConfig.CLIENT.cinematics.get()) return;
        title = titleText;
        subtitle = subtitleText;
        titleStart = 0f;
        titleDuration = seconds;
        titleCardUntil = Util.getMillis() + (long) (seconds * 1000);
        time = 0f;
        lastNanos = Util.getNanos();
        letterboxWanted = MWConfig.CLIENT.letterbox.get();
        playSound("motionworks:cinematic.sting", 1f, 1f);
    }

    public boolean isTitleCardActive() {
        return active == null && Util.getMillis() < titleCardUntil;
    }

    /** Per-frame update; also runs overlay animation when no sequence is active. */
    public void frame() {
        long now = Util.getNanos();
        float dt = MathUtil.clamp((now - lastNanos) / 1e9f, 0f, 0.1f);
        lastNanos = now;
        Minecraft mc = Minecraft.getInstance();
        if (mc.isPaused()) dt = 0f;
        if (isTitleCardActive()) time += dt;
        else if (active == null && titleCardUntil != 0) {
            titleCardUntil = 0;
            letterboxWanted = false;
            titleStart = -1f;
        }
        letterbox += ((letterboxWanted ? 1f : 0f) - letterbox) * MathUtil.approachFactor(0.18f, dt);
        flash = Math.max(0f, flash - dt * 3f);
        if (active == null) return;
        if (mc.player == null || mc.level == null) {
            stop();
            return;
        }
        if (active.cancelOnDamage && mc.player.getHealth() < lastHealth - 0.01f) {
            stop();
            return;
        }
        lastHealth = mc.player.getHealth();
        if (timeScaleUntil >= 0f && time >= timeScaleUntil) {
            timeScale = 1f;
            timeScaleUntil = -1f;
            AnimatorManager.setGlobalTimeScale(1f);
        }
        time += dt * timeScale;
        while (nextEvent < active.events.size() && active.events.get(nextEvent).time() <= time) {
            run(active.events.get(nextEvent++));
        }
        if (fadeStart >= 0f) {
            float u = fadeDuration <= 0f ? 1f : MathUtil.clamp01((time - fadeStart) / fadeDuration);
            fadeAlpha = MathUtil.lerp(fadeFrom, fadeTo, MathUtil.hermiteBlend(u));
            if (u >= 1f && fadeTo <= 0f) fadeStart = -1f;
        }
        if (time >= active.duration) stop();
    }

    float time() {
        return time;
    }

    /** Camera for this frame, or null when no sequence controls the camera. */
    public Shot currentCamera(float partial) {
        if (active == null || ctx == null || active.shots.isEmpty()) return null;
        Sequence.TimedShot ts = active.shotAt(time);
        if (ts == null) return null;
        float u = ts.duration() <= 0f ? 1f : MathUtil.clamp01((time - ts.start()) / ts.duration());
        ShotEvaluator.Placement p = ShotEvaluator.evaluate(ts.spec(), u, ctx, partial);
        if ("blend".equals(ts.transition()) && ts.blend() > 0f && time - ts.start() < ts.blend()) {
            Sequence.TimedShot prev = active.previous(ts);
            if (prev != null) {
                ShotEvaluator.Placement a = ShotEvaluator.evaluate(prev.spec(), 1f, ctx, partial);
                float k = MathUtil.hermiteBlend((time - ts.start()) / ts.blend());
                p = new ShotEvaluator.Placement(a.pos().lerp(p.pos(), k),
                        a.yaw() + MathUtil.wrapDegrees(p.yaw() - a.yaw()) * k,
                        MathUtil.lerp(a.pitch(), p.pitch(), k), MathUtil.lerp(a.roll(), p.roll(), k), MathUtil.lerp(a.fov(), p.fov(), k));
            }
        }
        current = new Shot(p.pos(), p.yaw(), p.pitch(), p.roll(), p.fov());
        return current;
    }

    public float roll() {
        return current != null && active != null ? current.roll() : 0f;
    }

    public float fov(float vanilla) {
        return current != null && active != null ? current.fov() : vanilla;
    }

    private void run(Sequence.TimedEvent e) {
        JsonObject o = e.spec();
        Minecraft mc = Minecraft.getInstance();
        switch (e.type()) {
            case "fade" -> {
                fadeFrom = ShotEvaluator.num(o, "from", fadeAlpha);
                fadeTo = ShotEvaluator.num(o, "to", 0f);
                fadeDuration = ShotEvaluator.num(o, "duration", 1f);
                fadeStart = time;
                fadeColor = o.has("color") ? (int) Long.parseLong(o.get("color").getAsString().replace("#", ""), 16) : 0;
            }
            case "title" -> {
                title = Component.translatable(ShotEvaluator.str(o, "title", ""));
                subtitle = Component.translatable(ShotEvaluator.str(o, "subtitle", ""));
                titleStart = time;
                titleDuration = ShotEvaluator.num(o, "duration", 3f);
            }
            case "dialogue" -> {
                speaker = Component.translatable(ShotEvaluator.str(o, "speaker", ""));
                line = Component.translatable(ShotEvaluator.str(o, "text", ""));
                lineStart = time;
                lineDuration = ShotEvaluator.num(o, "duration", 3f);
                Entity who = ctx.resolve(ShotEvaluator.str(o, "actor", "@anchor"));
                if (who instanceof LivingEntity le) {
                    EntityAnimator a = AnimatorManager.get(le);
                    a.fire("speak");
                }
            }
            case "sound" -> playSound(ShotEvaluator.str(o, "sound", ""), ShotEvaluator.num(o, "volume", 1f), ShotEvaluator.num(o, "pitch", 1f));
            case "animate" -> {
                Entity who = ctx.resolve(ShotEvaluator.str(o, "actor", "@anchor"));
                if (who instanceof LivingEntity le) {
                    EntityAnimator a = AnimatorManager.get(le);
                    if (o.has("clip")) {
                        AnimationClip clip = AnimationLibrary.INSTANCE.clips().get(o.get("clip").getAsString());
                        if (clip != null) a.play(clip);
                    }
                    if (o.has("event")) a.fire(o.get("event").getAsString());
                }
            }
            case "particles" -> {
                Entity who = ctx.resolve(ShotEvaluator.str(o, "actor", "@anchor"));
                Vec3 at = o.has("pos") ? ctx.local(ShotEvaluator.arr(o.getAsJsonArray("pos"))) : (who != null ? who.position().add(0, who.getBbHeight() * 0.5, 0) : ctx.origin());
                Effects.burst(ShotEvaluator.str(o, "particle", "mote"), at, (int) ShotEvaluator.num(o, "count", 12),
                        ShotEvaluator.num(o, "spread", 3f), ShotEvaluator.num(o, "speed", 0.02f), Vec3.ZERO);
            }
            case "flash" -> flash = Math.max(flash, ShotEvaluator.num(o, "strength", 1f));
            case "time_scale" -> {
                timeScale = ShotEvaluator.num(o, "value", 0.4f);
                timeScaleUntil = time + ShotEvaluator.num(o, "duration", 1.5f);
                AnimatorManager.setGlobalTimeScale(timeScale);
            }
            case "shake" -> CameraEffects.addTrauma(ShotEvaluator.num(o, "amount", 0.3f));
            case "letterbox" -> letterboxWanted = o.has("on") ? o.get("on").getAsBoolean() : !letterboxWanted;
            default -> MotionWorks.LOGGER.debug("Unknown cinematic event {}", e.type());
        }
        if (mc.player == null) stop();
    }

    void playSound(String id, float volume, float pitch) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || id.isEmpty()) return;
        SoundEvent ev = id.startsWith("motionworks:") ? MWSounds.get(id.substring(12)) : ForgeRegistries.SOUND_EVENTS.getValue(ResourceLocation.tryParse(id));
        if (ev == null) return;
        mc.level.playLocalSound(mc.player.getX(), mc.player.getEyeY(), mc.player.getZ(), ev, SoundSource.MASTER, volume, pitch, false);
    }
}
