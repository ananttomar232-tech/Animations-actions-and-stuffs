package com.motionworks.client.gui;

import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.client.environment.WindSystem;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import com.motionworks.config.MWConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** Animator inspector for the targeted entity (toggle with /mw debug). */
public final class DebugOverlay implements IGuiOverlay {
    public static final DebugOverlay INSTANCE = new DebugOverlay();

    private DebugOverlay() {}

    @Override
    public void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        if (!MWConfig.CLIENT.debugOverlay.get()) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return;
        Entity target = mc.hitResult instanceof EntityHitResult ehr ? ehr.getEntity() : mc.player;
        int y = 4;
        g.drawString(mc.font, String.format("MotionWorks  clips:%d  animators:%d  wind:%.2f", AnimationLibrary.INSTANCE.clips().size(),
                AnimatorManager.count(), WindSystem.strength()), 4, y, 0xFFE8C46A);
        y += 11;
        if (target instanceof LivingEntity le) {
            EntityAnimator a = AnimatorManager.find(le.getId());
            if (a != null && a.controller() != null) {
                g.drawString(mc.font, le.getName().getString() + "  rig:" + a.modelRig().rig.id + "  bones:" + a.modelRig().rig.size(), 4, y, 0xFFFFFFFF);
                y += 11;
                for (String line : a.controller().describe().split("\n")) {
                    if (line.isBlank()) continue;
                    g.drawString(mc.font, line, 4, y, 0xFFB8D8FF);
                    y += 10;
                }
            }
        }
        String fp = FirstPersonAnimator.INSTANCE.describe();
        if (!fp.isBlank()) {
            g.drawString(mc.font, "first person:", 4, y, 0xFFE8C46A);
            y += 10;
            for (String line : fp.split("\n")) {
                if (line.isBlank()) continue;
                g.drawString(mc.font, line, 4, y, 0xFFB8FFB8);
                y += 10;
            }
        }
    }
}
