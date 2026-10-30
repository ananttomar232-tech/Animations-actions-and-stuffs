package com.motionworks.client;

import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.client.cinematic.CinematicDirector;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.network.AnimationEventPacket;
import com.motionworks.network.CinematicPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

/** Client-only packet handling, isolated so dedicated servers never load client classes. */
public final class ClientPacketHandlers {
    private ClientPacketHandlers() {}

    public static void animationEvent(AnimationEventPacket p) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        Entity e = mc.level.getEntity(p.entityId());
        if (!(e instanceof LivingEntity le)) return;
        EntityAnimator a = AnimatorManager.get(le);
        switch (p.event()) {
            case "play_clip" -> {
                AnimationClip clip = AnimationLibrary.INSTANCE.clips().get(p.arg());
                if (clip != null) a.play(clip);
            }
            case "attack" -> a.onAttack(p.dir());
            default -> a.fire(p.event(), p.arg(), p.dir(), p.height());
        }
        if (le == mc.player && "dodge".equals(p.event())) FirstPersonAnimator.INSTANCE.fire("dodge:" + p.arg(), a.scope());
    }

    public static void cinematic(CinematicPacket p) {
        Minecraft mc = Minecraft.getInstance();
        if (p.id().isEmpty()) {
            CinematicDirector.INSTANCE.stop();
            return;
        }
        Entity anchor = mc.level != null ? mc.level.getEntity(p.anchorId()) : null;
        CinematicDirector.INSTANCE.play(p.id(), anchor);
    }
}
