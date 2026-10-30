package com.motionworks.client.cinematic;

import com.motionworks.client.MWKeys;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

import java.util.List;

/** Letterbox bars, fades, flashes, title cards, dialogue subtitles and the skip hint. */
public final class CinematicOverlay implements IGuiOverlay {
    public static final CinematicOverlay INSTANCE = new CinematicOverlay();

    private CinematicOverlay() {}

    @Override
    public void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        CinematicDirector d = CinematicDirector.INSTANCE;
        Minecraft mc = Minecraft.getInstance();
        Font font = mc.font;
        float t = d.time();
        if (d.letterbox > 0.002f) {
            int bar = Math.round(height * 0.11f * d.letterbox);
            g.fill(0, 0, width, bar, 0xFF000000);
            g.fill(0, height - bar, width, height, 0xFF000000);
        }
        if (d.titleStart >= 0f) {
            float u = (t - d.titleStart) / Math.max(0.01f, d.titleDuration);
            if (u <= 1f) {
                float a = fadeEnvelope(u, 0.18f, 0.25f);
                int alpha = (int) (a * 255) << 24;
                if (alpha != 0 && d.title != null) {
                    g.pose().pushPose();
                    g.pose().translate(width / 2f, height * 0.40f, 0);
                    g.pose().scale(2.4f, 2.4f, 1f);
                    g.drawCenteredString(font, d.title, 0, 0, 0xF2E6C8 | alpha);
                    g.pose().popPose();
                    if (d.subtitle != null) g.drawCenteredString(font, d.subtitle, width / 2, (int) (height * 0.40f) + 30, 0xBFB8A8 | alpha);
                }
            }
        }
        if (d.lineStart >= 0f && d.line != null) {
            float u = (t - d.lineStart) / Math.max(0.01f, d.lineDuration);
            if (u <= 1f) {
                float a = fadeEnvelope(u, 0.08f, 0.12f);
                int alpha = (int) (a * 220) << 24;
                String full = d.line.getString();
                int chars = Math.min(full.length(), (int) ((t - d.lineStart) * 45f));
                Component shown = Component.literal(full.substring(0, chars));
                List<FormattedCharSequence> lines = font.split(shown, Math.min(width - 40, 360));
                int y = height - Math.round(height * 0.11f * d.letterbox) - 14 - lines.size() * 11;
                if (d.speaker != null && !d.speaker.getString().isEmpty()) {
                    g.drawCenteredString(font, d.speaker, width / 2, y - 12, 0xE8C46A | alpha);
                }
                for (FormattedCharSequence l : lines) {
                    g.drawCenteredString(font, l, width / 2, y, 0xFFFFFF | alpha);
                    y += 11;
                }
            }
        }
        if (d.fadeAlpha > 0.002f) {
            int a = (int) (MathUtil.clamp01(d.fadeAlpha) * 255) << 24;
            g.fill(0, 0, width, height, a | (d.fadeColor & 0xFFFFFF));
        }
        if (d.flash > 0.002f) {
            int a = (int) (MathUtil.clamp01(d.flash) * 200) << 24;
            g.fill(0, 0, width, height, a | 0xFFFFFF);
        }
        if (d.isActive() && d.active().skippable) {
            Component hint = Component.translatable("motionworks.cinematic.skip", MWKeys.SKIP_CINEMATIC.getTranslatedKeyMessage());
            g.drawString(font, hint, width - font.width(hint) - 6, height - 10 - Math.round(height * 0.11f * d.letterbox), 0x80FFFFFF);
        }
    }

    private static float fadeEnvelope(float u, float in, float out) {
        if (u < in) return u / in;
        if (u > 1f - out) return Math.max(0f, (1f - u) / out);
        return 1f;
    }
}
