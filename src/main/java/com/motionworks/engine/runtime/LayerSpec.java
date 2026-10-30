package com.motionworks.engine.runtime;

import java.util.List;

/** Declares a controller layer. Layers evaluate in list order; later layers win. */
public record LayerSpec(String name, boolean additive, boolean multi) {
    /**
     * The standard stack every entity uses:
     * base (locomotion / full-body states), overlay (upper-body holds such as aiming or carrying),
     * action (one-shot full or masked actions), gesture (emotes and conversation gestures),
     * posture (additive personality and condition posture), additive (breathing, tails, ears),
     * reaction (additive hit flinches and impacts).
     */
    public static final List<LayerSpec> STANDARD = List.of(
            new LayerSpec("base", false, false),
            new LayerSpec("overlay", false, false),
            new LayerSpec("action", false, false),
            new LayerSpec("gesture", false, false),
            new LayerSpec("posture", true, true),
            new LayerSpec("additive", true, true),
            new LayerSpec("reaction", true, true));

    public static LayerSpec forUnknown(String name, boolean additive) {
        return new LayerSpec(name, additive, additive);
    }
}
