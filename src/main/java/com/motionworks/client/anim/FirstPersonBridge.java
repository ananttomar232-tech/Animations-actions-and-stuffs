package com.motionworks.client.anim;

import com.motionworks.client.firstperson.FirstPersonAnimator;
import net.minecraft.client.Minecraft;

/** Forwards events of the local player's third-person animator to the first-person animator. */
public final class FirstPersonBridge {
    private FirstPersonBridge() {}

    static void onThirdPersonEvent(EntityAnimator a, String event) {
        if (a.entity == Minecraft.getInstance().player) FirstPersonAnimator.INSTANCE.fire(event, a.scope());
    }
}
