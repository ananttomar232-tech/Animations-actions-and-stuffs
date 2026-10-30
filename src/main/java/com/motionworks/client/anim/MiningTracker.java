package com.motionworks.client.anim;

import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.MapColor;

/** Tracks who is mining what, from vanilla block-destruction progress packets. */
public final class MiningTracker {
    private record Mining(BlockPos pos, long time) {}

    private static final Int2ObjectMap<Mining> MINING = new Int2ObjectOpenHashMap<>();

    private MiningTracker() {}

    public static void onProgress(int breakerId, BlockPos pos, int progress) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        if (progress >= 0 && progress < 10) MINING.put(breakerId, new Mining(pos.immutable(), mc.level.getGameTime()));
        else MINING.remove(breakerId);
    }

    public static boolean isMining(LivingEntity e) {
        Minecraft mc = Minecraft.getInstance();
        if (e == mc.player) return mc.gameMode != null && mc.gameMode.isDestroying();
        Mining m = MINING.get(e.getId());
        if (m == null || mc.level == null) return false;
        if (mc.level.getGameTime() - m.time > 20) {
            MINING.remove(e.getId());
            return false;
        }
        return true;
    }

    /** Coarse material of the block being mined: stone, wood, dirt, plant, metal or other. */
    public static String target(LivingEntity e) {
        Minecraft mc = Minecraft.getInstance();
        BlockPos pos = null;
        if (e == mc.player && mc.hitResult instanceof net.minecraft.world.phys.BlockHitResult bhr) pos = bhr.getBlockPos();
        else {
            Mining m = MINING.get(e.getId());
            if (m != null) pos = m.pos;
        }
        if (pos == null || mc.level == null) return "none";
        BlockState st = mc.level.getBlockState(pos);
        MapColor c = st.getMapColor(mc.level, pos);
        if (st.is(net.minecraft.tags.BlockTags.LOGS) || st.is(net.minecraft.tags.BlockTags.PLANKS) || c == MapColor.WOOD) return "wood";
        if (st.is(net.minecraft.tags.BlockTags.MINEABLE_WITH_SHOVEL)) return "dirt";
        if (st.is(net.minecraft.tags.BlockTags.MINEABLE_WITH_HOE) || st.is(net.minecraft.tags.BlockTags.LEAVES)) return "plant";
        if (c == MapColor.METAL) return "metal";
        if (st.is(net.minecraft.tags.BlockTags.MINEABLE_WITH_PICKAXE)) return "stone";
        return "other";
    }
}
