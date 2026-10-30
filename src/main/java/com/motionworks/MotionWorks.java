package com.motionworks;

import com.motionworks.config.MWConfig;
import com.motionworks.network.MWNetwork;
import com.motionworks.registry.MWParticles;
import com.motionworks.registry.MWSounds;
import com.motionworks.server.ServerCommands;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** MotionWorks: cinematic animation and visual presentation overhaul. */
@Mod(MotionWorks.MOD_ID)
public final class MotionWorks {
    public static final String MOD_ID = "motionworks";
    public static final Logger LOGGER = LoggerFactory.getLogger("MotionWorks");

    public MotionWorks() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        MWSounds.register(bus);
        MWParticles.register(bus);
        ModLoadingContext.get().registerConfig(ModConfig.Type.CLIENT, MWConfig.CLIENT_SPEC);
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, MWConfig.SERVER_SPEC);
        bus.addListener(this::commonSetup);
        MinecraftForge.EVENT_BUS.addListener(ServerCommands::register);
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.motionworks.client.MotionWorksClient.init(bus));
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(MWNetwork::register);
    }
}
