package com.motionworks.client.cinematic;

import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.config.MWConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import net.minecraft.world.entity.monster.ElderGuardian;
import net.minecraft.world.entity.monster.warden.Warden;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Presents bosses the first time they are seen in a session. The default title-card mode never
 * takes the camera away from the player; the full cinematic is only used where it is safe
 * (creative, spectator or peaceful) and is always skippable.
 */
public final class BossIntros {
    private static final Set<UUID> SEEN = new HashSet<>();
    private static int cooldown;

    private BossIntros() {}

    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) {
            SEEN.clear();
            return;
        }
        MWConfig.BossIntroMode mode = MWConfig.CLIENT.bossIntros.get();
        if (mode == MWConfig.BossIntroMode.OFF || --cooldown > 0) return;
        cooldown = 10;
        for (Entity e : mc.level.entitiesForRendering()) {
            String key = bossKey(e);
            if (key == null || SEEN.contains(e.getUUID()) || !e.isAlive()) continue;
            if (e.distanceTo(mc.player) > (e instanceof EnderDragon ? 160 : 48) || !mc.player.hasLineOfSight(e) && !(e instanceof EnderDragon)) continue;
            SEEN.add(e.getUUID());
            boolean safe = mc.player.isCreative() || mc.player.isSpectator() || mc.level.getDifficulty() == Difficulty.PEACEFUL;
            if (e instanceof LivingEntity le) AnimatorManager.get(le).fire("boss_intro");
            if (mode == MWConfig.BossIntroMode.FULL_CINEMATIC && safe && CinematicDirector.INSTANCE.play("motionworks:boss_intro_" + key, e)) return;
            CinematicDirector.INSTANCE.titleCard(Component.translatable("motionworks.boss." + key + ".title"),
                    Component.translatable("motionworks.boss." + key + ".subtitle"), 3.6f);
            return;
        }
    }

    private static String bossKey(Entity e) {
        if (e instanceof WitherBoss) return "wither";
        if (e instanceof EnderDragon) return "ender_dragon";
        if (e instanceof Warden) return "warden";
        if (e instanceof ElderGuardian) return "elder_guardian";
        return null;
    }
}
