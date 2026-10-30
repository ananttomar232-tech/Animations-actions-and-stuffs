package com.motionworks.mixin.client;

import com.motionworks.client.camera.CameraEffects;
import com.motionworks.client.cinematic.CinematicDirector;
import net.minecraft.client.Camera;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Lets the cinematic director take over the camera, and adds landing dip to normal play. */
@Mixin(Camera.class)
public abstract class CameraMixin {
    @Shadow
    private boolean detached;

    @Shadow
    protected abstract void setPosition(Vec3 pos);

    @Shadow
    protected abstract void setRotation(float yaw, float pitch);

    @Shadow
    public abstract Vec3 getPosition();

    @Inject(method = "setup", at = @At("TAIL"))
    private void motionworks$setup(BlockGetter level, Entity entity, boolean detachedIn, boolean mirror, float partialTicks, CallbackInfo ci) {
        CinematicDirector.Shot shot = CinematicDirector.INSTANCE.currentCamera(partialTicks);
        if (shot != null) {
            this.detached = true;
            setPosition(shot.position());
            setRotation(shot.yaw(), shot.pitch());
            return;
        }
        float dy = CameraEffects.yOffset();
        if (dy != 0f && !detachedIn) setPosition(getPosition().add(0, dy, 0));
    }
}
