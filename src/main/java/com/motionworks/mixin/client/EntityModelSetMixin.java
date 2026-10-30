package com.motionworks.mixin.client;

import com.motionworks.client.rig.ModelPartIndex;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Records the layer-definition name of every baked part so rigs can be discovered by name. */
@Mixin(EntityModelSet.class)
public abstract class EntityModelSetMixin {
    @Inject(method = "bakeLayer", at = @At("RETURN"))
    private void motionworks$indexParts(ModelLayerLocation layer, CallbackInfoReturnable<ModelPart> cir) {
        ModelPartIndex.index(layer, cir.getReturnValue());
    }
}
