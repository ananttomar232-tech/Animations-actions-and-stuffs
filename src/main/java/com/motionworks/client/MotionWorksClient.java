package com.motionworks.client;

import com.motionworks.MotionWorks;
import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.client.cinematic.CinematicDirector;
import com.motionworks.client.cinematic.CinematicOverlay;
import com.motionworks.client.environment.FoliageShaders;
import com.motionworks.client.face.FaceLayer;
import com.motionworks.client.gui.DebugOverlay;
import com.motionworks.client.particle.MWParticle;
import com.motionworks.client.particle.ParticlePresets;
import com.motionworks.client.particle.TrailLayer;
import com.motionworks.client.rig.EquipmentLayer;
import com.motionworks.registry.MWParticles;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.world.entity.EntityType;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.client.event.RegisterClientCommandsEvent;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.ForgeRegistries;

/** Mod-bus client registration. */
public final class MotionWorksClient {
    private MotionWorksClient() {}

    public static void init(IEventBus modBus) {
        FoliageShaders.detectCompatibility();
        modBus.addListener(MotionWorksClient::reloadListeners);
        modBus.addListener(MotionWorksClient::keys);
        modBus.addListener(MotionWorksClient::overlays);
        modBus.addListener(MotionWorksClient::particles);
        modBus.addListener(MotionWorksClient::layers);
        modBus.addListener((ModelEvent.ModifyBakingResult e) -> FoliageShaders.onModifyBakingResult(e));
        MinecraftForge.EVENT_BUS.addListener((RegisterClientCommandsEvent e) -> ClientCommands.register(e.getDispatcher()));
    }

    private static void reloadListeners(RegisterClientReloadListenersEvent e) {
        e.registerReloadListener(AnimationLibrary.INSTANCE);
        e.registerReloadListener(CinematicDirector.INSTANCE);
    }

    private static void keys(RegisterKeyMappingsEvent e) {
        e.register(MWKeys.DODGE);
        e.register(MWKeys.BASH);
        e.register(MWKeys.EMOTES);
        e.register(MWKeys.INSPECT);
        e.register(MWKeys.SKIP_CINEMATIC);
    }

    private static void overlays(RegisterGuiOverlaysEvent e) {
        e.registerAboveAll("cinematic", CinematicOverlay.INSTANCE);
        e.registerAboveAll("debug", DebugOverlay.INSTANCE);
    }

    private static void particles(RegisterParticleProvidersEvent e) {
        for (String name : MWParticles.NAMES) {
            ParticlePresets.Preset preset = ParticlePresets.get(name);
            e.registerSpriteSet(MWParticles.BY_NAME.get(name).get(), sprites -> new MWParticle.Provider(preset, sprites));
        }
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static void layers(EntityRenderersEvent.AddLayers e) {
        for (String skin : e.getSkins()) {
            LivingEntityRenderer r = e.getSkin(skin);
            if (r == null) continue;
            r.addLayer(new TrailLayer(r));
            r.addLayer(new FaceLayer(r, FaceLayer.Kind.PLAYER));
            r.addLayer(new EquipmentLayer(r));
        }
        for (EntityType<?> type : ForgeRegistries.ENTITY_TYPES) {
            EntityRenderer<?> er;
            try {
                er = e.getRenderer((EntityType) type);
            } catch (RuntimeException ex) {
                continue;
            }
            if (!(er instanceof LivingEntityRenderer<?, ?> lr)) continue;
            EntityModel<?> model = lr.getModel();
            LivingEntityRenderer raw = lr;
            if (model instanceof ArmedModel) raw.addLayer(new TrailLayer(raw));
            FaceLayer.Kind kind = FaceLayer.kindFor(type);
            if (kind != null && model instanceof HeadedModel) raw.addLayer(new FaceLayer(raw, kind));
        }
        MotionWorks.LOGGER.debug("MotionWorks render layers attached");
    }
}
