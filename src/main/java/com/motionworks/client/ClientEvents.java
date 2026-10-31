package com.motionworks.client;

import com.motionworks.MotionWorks;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.client.camera.CameraEffects;
import com.motionworks.client.cinematic.BossIntros;
import com.motionworks.client.cinematic.CinematicDirector;
import com.motionworks.client.cinematic.CinematicOverlay;
import com.motionworks.client.environment.AmbientEffects;
import com.motionworks.client.environment.FoliageShaders;
import com.motionworks.client.environment.WindSystem;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import com.motionworks.client.gui.EmoteWheelScreen;
import com.motionworks.client.particle.WeaponTrails;
import com.motionworks.client.social.SocialDirector;
import com.motionworks.common.CtxVars;
import com.motionworks.common.InteractionClassifier;
import com.motionworks.common.ItemCategories;
import com.motionworks.config.MWConfig;
import com.motionworks.network.CombatActionPacket;
import com.motionworks.network.EmotePacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Game-bus client hooks: ticking, rendering stages, camera, HUD and local-player triggers. */
@Mod.EventBusSubscriber(modid = MotionWorks.MOD_ID, value = Dist.CLIENT)
public final class ClientEvents {
    private ClientEvents() {}

    public static void remoteAttack(EntityAnimator a, float strength) {
        a.onAttack(strength);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        AnimatorManager.clientTick();
        if (mc.level == null || mc.player == null) return;
        com.motionworks.client.rig.LibraryAudit.autoRun();
        com.motionworks.client.rig.PoseGallery.autoRun();
        FirstPersonAnimator.INSTANCE.tick();
        BossIntros.tick();
        SocialDirector.tick();
        AmbientEffects.tick();
        handleKeys(mc, mc.player);
        EntityAnimator self = AnimatorManager.find(mc.player.getId());
        if (self != null) {
            float fall = self.scope().get(CtxVars.LAST_FALL);
            if (self.scope().get(CtxVars.TIME_SINCE_LANDED) == 0.05f && fall > 1.2f) CameraEffects.landing(fall);
        }
    }

    private static void handleKeys(Minecraft mc, LocalPlayer p) {
        while (MWKeys.SKIP_CINEMATIC.consumeClick()) CinematicDirector.INSTANCE.skip();
        while (MWKeys.DODGE.consumeClick()) {
            float f = p.input.forwardImpulse, s = p.input.leftImpulse;
            MWNetwork.CHANNEL.sendToServer(new CombatActionPacket(CombatActionPacket.Action.DODGE, f, s));
        }
        while (MWKeys.BASH.consumeClick()) MWNetwork.CHANNEL.sendToServer(new CombatActionPacket(CombatActionPacket.Action.BASH, 0, 0));
        while (MWKeys.INSPECT.consumeClick()) {
            EntityAnimator a = AnimatorManager.get(p);
            a.fire("inspect", ItemCategories.of(p.getMainHandItem()), 0f);
            MWNetwork.CHANNEL.sendToServer(new EmotePacket("event:inspect"));
        }
        while (MWKeys.EMOTES.consumeClick()) {
            if (mc.screen == null) mc.setScreen(new EmoteWheelScreen());
        }
    }

    @SubscribeEvent
    public static void onRenderTick(TickEvent.RenderTickEvent e) {
        if (e.phase != TickEvent.Phase.START) return;
        CinematicDirector.INSTANCE.frame();
        CameraEffects.update();
    }

    @SubscribeEvent
    public static void onRenderStage(RenderLevelStageEvent e) {
        if (e.getStage() == RenderLevelStageEvent.Stage.AFTER_SKY) {
            WindSystem.update(e.getPartialTick());
            FoliageShaders.updateUniforms(e.getPartialTick());
            WeaponTrails.setViewMatrix(e.getPoseStack().last().pose());
        } else if (e.getStage() == RenderLevelStageEvent.Stage.AFTER_PARTICLES) {
            WeaponTrails.render(e.getPoseStack(), e.getCamera().getPosition());
        }
    }

    @SubscribeEvent
    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles e) {
        if (CinematicDirector.INSTANCE.isActive()) {
            e.setRoll(CinematicDirector.INSTANCE.roll() + CameraEffects.roll());
            e.setYaw(e.getYaw() + CameraEffects.yaw());
            e.setPitch(e.getPitch() + CameraEffects.pitch());
            return;
        }
        if (!MWConfig.CLIENT.cameraEffects.get()) return;
        FirstPersonAnimator fp = FirstPersonAnimator.INSTANCE;
        boolean firstPerson = Minecraft.getInstance().options.getCameraType().isFirstPerson();
        e.setYaw(e.getYaw() + CameraEffects.yaw() + (firstPerson ? fp.viewYaw() : 0f));
        e.setPitch(e.getPitch() + CameraEffects.pitch() + (firstPerson ? fp.viewPitch() : 0f));
        e.setRoll(e.getRoll() + CameraEffects.roll() + (firstPerson ? fp.viewRoll() : 0f));
    }

    @SubscribeEvent
    public static void onFov(ViewportEvent.ComputeFov e) {
        if (CinematicDirector.INSTANCE.isActive()) e.setFOV(CinematicDirector.INSTANCE.fov((float) e.getFOV()));
    }

    @SubscribeEvent
    public static void onHudOverlay(RenderGuiOverlayEvent.Pre e) {
        CinematicDirector d = CinematicDirector.INSTANCE;
        boolean hide = (d.isActive() && d.active().hideHud && MWConfig.CLIENT.hideHudInCinematics.get());
        if (hide && !e.getOverlay().id().getPath().equals("cinematic") && !e.getOverlay().id().getPath().equals("debug")) e.setCanceled(true);
    }

    @SubscribeEvent
    public static void onRenderHand(RenderHandEvent e) {
        if (CinematicDirector.INSTANCE.isActive()) e.setCanceled(true);
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut e) {
        AnimatorManager.clear();
        com.motionworks.client.rig.StowedEquipment.clear();
        CinematicDirector.INSTANCE.stop();
        FirstPersonAnimator.INSTANCE.reset();
    }

    // ---- local player triggers: animate instantly, the server relays to everyone else ----

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock e) {
        if (!e.getLevel().isClientSide || e.getHand() != InteractionHand.MAIN_HAND || e.getEntity() != Minecraft.getInstance().player) return;
        String kind = InteractionClassifier.block(e.getLevel().getBlockState(e.getPos()), e.getItemStack(), e.getEntity().isShiftKeyDown());
        if (kind == null) return;
        float dir = InteractionClassifier.relativeYaw(e.getEntity(), e.getPos().getX() + 0.5, e.getPos().getZ() + 0.5);
        AnimatorManager.get(e.getEntity()).fire("interact", kind, dir, (float) (e.getPos().getY() + 0.5 - e.getEntity().getEyeY()));
    }

    @SubscribeEvent
    public static void onRightClickItem(PlayerInteractEvent.RightClickItem e) {
        if (!e.getLevel().isClientSide || e.getEntity() != Minecraft.getInstance().player) return;
        String cat = ItemCategories.of(e.getItemStack());
        EntityAnimator a = AnimatorManager.get(e.getEntity());
        if ("fishing_rod".equals(cat)) a.fire(e.getEntity().fishing == null ? "fish_cast" : "fish_reel");
        else if ("throwable".equals(cat)) a.fire("throw");
        else if ("map".equals(cat) || "book".equals(cat) || "device".equals(cat)) a.fire("inspect_item", cat, 0f);
        else if ("glass_bottle".equals(cat)) a.fire("fill_bottle");
        else if ("firework".equals(cat) && e.getEntity().isFallFlying()) a.fire("boost");
    }

    private static String localMenu;

    /** Screens the server never hears about; relayed so other players see the owner busy. */
    @SubscribeEvent
    public static void onScreenOpen(net.minecraftforge.client.event.ScreenEvent.Opening e) {
        String kind = e.getNewScreen() instanceof net.minecraft.client.gui.screens.inventory.InventoryScreen ? "inventory"
                : e.getNewScreen() instanceof net.minecraft.client.gui.screens.ChatScreen ? "chat"
                : e.getNewScreen() instanceof net.minecraft.client.gui.screens.inventory.BookEditScreen ? "book_edit" : null;
        Minecraft mc = Minecraft.getInstance();
        if (kind == null || mc.player == null) return;
        localMenu = kind;
        AnimatorManager.get(mc.player).fire("menu_open", kind, 0f);
        MWNetwork.CHANNEL.sendToServer(new EmotePacket("event:menu_open:" + kind));
    }

    @SubscribeEvent
    public static void onScreenClose(net.minecraftforge.client.event.ScreenEvent.Closing e) {
        Minecraft mc = Minecraft.getInstance();
        if (localMenu == null || mc.player == null) return;
        AnimatorManager.get(mc.player).fire("menu_close", localMenu, 0f);
        MWNetwork.CHANNEL.sendToServer(new EmotePacket("event:menu_close:" + localMenu));
        localMenu = null;
    }

    @SubscribeEvent
    public static void onEntityInteract(PlayerInteractEvent.EntityInteract e) {
        if (!e.getLevel().isClientSide || e.getHand() != InteractionHand.MAIN_HAND || e.getEntity() != Minecraft.getInstance().player) return;
        String kind = InteractionClassifier.entity(e.getTarget(), e.getItemStack());
        if (kind != null) {
            AnimatorManager.get(e.getEntity()).fire("interact_entity", kind, InteractionClassifier.relativeYaw(e.getEntity(), e.getTarget().getX(), e.getTarget().getZ()));
        }
    }

    @SubscribeEvent
    public static void onAttack(AttackEntityEvent e) {
        if (!e.getEntity().level().isClientSide || e.getEntity() != Minecraft.getInstance().player) return;
        AnimatorManager.get(e.getEntity()).onAttack(e.getEntity().getAttackStrengthScale(0.5f));
    }
}
