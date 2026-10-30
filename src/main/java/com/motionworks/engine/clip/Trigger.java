package com.motionworks.engine.clip;

import com.motionworks.engine.expr.Expr;

/**
 * Describes when a clip plays.
 * <ul>
 *   <li>{@link Type#STATE}: continuously evaluated; the highest-priority true clip on a layer is active.
 *       Clips sharing a {@code group} and priority form a weighted pool (idle variations).</li>
 *   <li>{@link Type#EVENT}: fired by a named gameplay event (attack, hurt, interact:door...).</li>
 *   <li>{@link Type#MANUAL}: only played explicitly (emotes, cinematics, commands).</li>
 * </ul>
 * {@code stopWhen} lets event/manual clips end early, e.g. an emote cancelled by walking away.
 */
public record Trigger(Type type, String event, Expr when, String group, Expr weight, float minTime,
                      float exitDelay, float cooldown, float chance, Expr stopWhen, String description) {
    public enum Type { STATE, EVENT, MANUAL }

    public static Trigger manual(String description) {
        return new Trigger(Type.MANUAL, null, Expr.ONE, null, Expr.ONE, 0f, 0f, 0f, 1f, null, description);
    }
}
