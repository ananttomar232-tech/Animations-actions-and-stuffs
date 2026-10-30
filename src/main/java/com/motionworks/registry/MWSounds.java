package com.motionworks.registry;

import com.motionworks.MotionWorks;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.LinkedHashMap;
import java.util.Map;

/** Original MotionWorks sound events. Files and variations are declared in sounds.json. */
public final class MWSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, MotionWorks.MOD_ID);
    private static final Map<String, RegistryObject<SoundEvent>> BY_NAME = new LinkedHashMap<>();

    public static final String[] NAMES = {
            "footstep.grass", "footstep.stone", "footstep.wood", "footstep.sand", "footstep.gravel", "footstep.snow",
            "footstep.metal", "footstep.wool", "footstep.mud", "footstep.water", "footstep.leaves",
            "foley.cloth", "foley.leather", "foley.chain", "foley.plate",
            "weapon.whoosh_light", "weapon.whoosh_medium", "weapon.whoosh_heavy", "weapon.draw_blade", "weapon.sheathe_blade",
            "weapon.draw_haft", "weapon.bow_creak", "weapon.crossbow_crank", "weapon.shield_raise", "weapon.shield_bash", "weapon.parry",
            "impact.flesh", "impact.metal", "impact.wood", "impact.stone",
            "body.land_soft", "body.land_hard", "body.roll", "body.fall", "body.dodge",
            "creature.heavy_step", "creature.wing_flap", "creature.sniff",
            "water.splash_small", "water.splash_big", "water.bubbles", "water.surface",
            "interact.handle", "interact.page", "interact.lever_clunk", "interact.rummage", "interact.tool_tap",
            "ambient.wind_gust", "ambient.leaves_rustle", "ambient.chain_jingle", "ambient.banner_flap", "ambient.thunder_rumble",
            "cinematic.boom", "cinematic.riser", "cinematic.sting", "cinematic.whoosh", "cinematic.drone",
            "emote.clap", "emote.snap", "emote.whistle"
    };

    static {
        for (String n : NAMES) {
            BY_NAME.put(n, SOUNDS.register(n, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(MotionWorks.MOD_ID, n))));
        }
    }

    private MWSounds() {}

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }

    /** Returns the sound for a short name (e.g. "footstep.snow") or null. */
    public static SoundEvent get(String name) {
        RegistryObject<SoundEvent> r = BY_NAME.get(name);
        return r != null && r.isPresent() ? r.get() : null;
    }
}
