package com.motionworks.client.gui;

import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.network.EmotePacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * Radial emote picker. Emotes are any clip whose meta has {@code "emote": "true"}; pages group
 * them by their {@code emote_group} (gestures, celebrations, expressions, dances).
 */
public final class EmoteWheelScreen extends Screen {
    private final List<AnimationClip> emotes = new ArrayList<>();
    private final List<String> groups = new ArrayList<>();
    private int page;
    private int hovered = -1;

    public EmoteWheelScreen() {
        super(Component.translatable("motionworks.emotes.title"));
        for (AnimationClip c : AnimationLibrary.INSTANCE.clips().all()) {
            if ("true".equals(c.meta("emote", "false"))) {
                emotes.add(c);
                String g = c.meta("emote_group", "gestures");
                if (!groups.contains(g)) groups.add(g);
            }
        }
    }

    private List<AnimationClip> pageClips() {
        if (groups.isEmpty()) return List.of();
        String g = groups.get(Math.floorMod(page, groups.size()));
        List<AnimationClip> l = new ArrayList<>();
        for (AnimationClip c : emotes) if (g.equals(c.meta("emote_group", "gestures"))) l.add(c);
        return l.subList(0, Math.min(12, l.size()));
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        renderBackground(g);
        int cx = width / 2, cy = height / 2;
        List<AnimationClip> clips = pageClips();
        double angle = Math.atan2(mouseY - cy, mouseX - cx);
        double dist = Math.hypot(mouseX - cx, mouseY - cy);
        hovered = -1;
        if (!clips.isEmpty() && dist > 30) {
            double slice = Math.PI * 2 / clips.size();
            hovered = (int) Math.floor(((angle + Math.PI / 2 + slice / 2) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) / slice);
        }
        for (int i = 0; i < clips.size(); i++) {
            double a = -Math.PI / 2 + i * Math.PI * 2 / clips.size();
            int x = cx + (int) (Math.cos(a) * 90), y = cy + (int) (Math.sin(a) * 90);
            boolean hot = i == hovered;
            String label = clips.get(i).name();
            int w = font.width(label) + 10;
            g.fill(x - w / 2, y - 8, x + w / 2, y + 8, hot ? 0xC0E8C46A : 0x90000000);
            g.drawCenteredString(font, label, x, y - 4, hot ? 0xFF1A1A1A : 0xFFFFFFFF);
        }
        String group = groups.isEmpty() ? "-" : groups.get(Math.floorMod(page, groups.size()));
        g.drawCenteredString(font, Component.translatable("motionworks.emotes.group." + group), cx, cy - 4, 0xFFE8C46A);
        g.drawCenteredString(font, Component.translatable("motionworks.emotes.hint"), cx, height - 20, 0xFFAAAAAA);
        super.render(g, mouseX, mouseY, partial);
    }

    @Override
    public boolean mouseScrolled(double x, double y, double delta) {
        page += delta > 0 ? -1 : 1;
        return true;
    }

    @Override
    public boolean mouseClicked(double x, double y, int button) {
        List<AnimationClip> clips = pageClips();
        if (button == 1) {
            page++;
            return true;
        }
        if (hovered >= 0 && hovered < clips.size()) {
            AnimationClip clip = clips.get(hovered);
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null) {
                AnimatorManager.get(mc.player).play(clip);
                AnimationClip fp = AnimationLibrary.INSTANCE.clips().get(clip.meta("first_person", ""));
                if (fp != null) FirstPersonAnimator.INSTANCE.play(fp);
                MWNetwork.CHANNEL.sendToServer(new EmotePacket(clip.id()));
            }
            onClose();
            return true;
        }
        return super.mouseClicked(x, y, button);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
