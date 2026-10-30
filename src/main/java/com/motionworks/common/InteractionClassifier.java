package com.motionworks.common;

import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.AbstractGolem;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.npc.WanderingTrader;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.AbstractMinecart;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Classifies a block or entity interaction into a contextual animation argument, shared by the
 * client (instant local feedback) and the server (authoritative broadcast to others).
 */
public final class InteractionClassifier {
    private InteractionClassifier() {}

    /** @return the interaction kind, or null when the click is not a meaningful interaction */
    public static String block(BlockState state, ItemStack held, boolean sneaking) {
        Block b = state.getBlock();
        String item = ItemCategories.of(held);
        if (b instanceof CampfireBlock) {
            if (held.isEdible()) return "cook";
            if ("shovel".equals(item) && state.getValue(CampfireBlock.LIT)) return "douse";
            if (held.isEmpty()) return "campfire";
        }
        if (b instanceof FenceBlock && "lead".equals(item)) return "tie_lead";
        if (b instanceof BeehiveBlock && ("shears".equals(item) || "glass_bottle".equals(item))) return "harvest_hive";
        if ((b instanceof SweetBerryBushBlock || b instanceof CaveVinesBlock || b instanceof CaveVinesPlantBlock) && !"bone_meal".equals(item) && held.getItem() != net.minecraft.world.item.Items.BONE_MEAL) {
            return "pick_berries";
        }
        if (b instanceof PumpkinBlock && "shears".equals(item)) return "carve";
        if (b instanceof EndPortalFrameBlock && held.getItem() == net.minecraft.world.item.Items.ENDER_EYE) return "insert_eye";
        if ("honeycomb".equals(item)) return "wax";
        if ("firework".equals(item)) return "launch_firework";
        if ("vehicle".equals(item)) return "place_vehicle";
        if ("hanging".equals(item)) return "hang";
        if (held.isEmpty() && b instanceof FlowerBlock) return "smell_flower";
        if (held.isEmpty() && (b instanceof AmethystClusterBlock || b instanceof AmethystBlock)) return "amethyst";
        if (!sneaking || held.isEmpty()) {
            if (b == Blocks.IRON_DOOR) return "iron_door";
            if (b instanceof DoorBlock) return state.getValue(DoorBlock.OPEN) ? "door_close" : "door_open";
            if (b instanceof TrapDoorBlock) return state.getValue(TrapDoorBlock.OPEN) ? "trapdoor_close" : "trapdoor_open";
            if (b instanceof FenceGateBlock) return state.getValue(FenceGateBlock.OPEN) ? "gate_close" : "gate_open";
            if (b instanceof EnderChestBlock) return "ender_chest";
            if (b instanceof ChestBlock) return "chest";
            if (b instanceof BarrelBlock) return "barrel";
            if (b instanceof ShulkerBoxBlock) return "shulker";
            if (b instanceof CraftingTableBlock) return "crafting";
            if (b instanceof SmokerBlock || b instanceof BlastFurnaceBlock || b instanceof FurnaceBlock) return "furnace";
            if (b instanceof AnvilBlock) return "anvil";
            if (b instanceof EnchantmentTableBlock) return "enchanting";
            if (b instanceof LecternBlock) return "lectern";
            if (b instanceof BellBlock) return "bell";
            if (b instanceof LeverBlock) return state.getValue(LeverBlock.POWERED) ? "lever_off" : "lever_on";
            if (b instanceof ButtonBlock) return "button";
            if (b instanceof BedBlock) return "bed";
            if (b instanceof NoteBlock) return "note_block";
            if (b instanceof JukeboxBlock) return "jukebox";
            if (b instanceof BrewingStandBlock) return "brewing";
            if (b instanceof GrindstoneBlock || b instanceof StonecutterBlock) return "grindstone";
            if (b instanceof LoomBlock || b instanceof CartographyTableBlock || b instanceof SmithingTableBlock || b instanceof FletchingTableBlock) return "workstation";
            if (b instanceof CauldronBlock || b instanceof AbstractCauldronBlock) return "cauldron";
            if (b instanceof ComposterBlock) return "composter";
            if (b instanceof BeaconBlock) return "beacon";
            if (b instanceof RespawnAnchorBlock) return "respawn_anchor";
            if (b instanceof FlowerPotBlock) return "flower_pot";
            if (b instanceof CakeBlock) return "cake";
            if (b instanceof SignBlock) return "sign";
            if (b instanceof DispenserBlock || b instanceof HopperBlock) return "container";
            if (b instanceof RepeaterBlock || b instanceof ComparatorBlock || b instanceof DaylightDetectorBlock) return "tinker";
            if (b instanceof ChiseledBookShelfBlock) return "bookshelf";
            if (b instanceof DecoratedPotBlock) return "pot";
        }
        switch (item) {
            case "igniter" -> { return "ignite"; }
            case "bucket" -> { return "bucket"; }
            case "hoe" -> { if (state.is(BlockTags.DIRT)) return "till"; }
            case "axe" -> { if (state.is(BlockTags.LOGS)) return "strip"; }
            case "shovel" -> { if (state.is(BlockTags.DIRT)) return "flatten"; }
            case "brush" -> { return "brush"; }
            default -> { }
        }
        if (held.getItem() == net.minecraft.world.item.Items.BONE_MEAL && b instanceof BonemealableBlock) return "fertilize";
        return null;
    }

    public static String entity(Entity target, ItemStack held) {
        String item = ItemCategories.of(held);
        if (target instanceof WanderingTrader) return "trader";
        if (target instanceof AbstractVillager) return "villager";
        if (target instanceof net.minecraft.world.entity.animal.allay.Allay && !held.isEmpty()) return "give_item";
        if ("name_tag".equals(item)) return "name_tag";
        if ("saddle".equals(item)) return "saddle";
        if (target instanceof Sheep && "dye".equals(item)) return "dye";
        if (target instanceof Sheep && "shears".equals(item)) return "shear";
        if (target instanceof Cow && "bucket".equals(item)) return "milk";
        if ((target instanceof net.minecraft.world.entity.animal.AbstractFish || target instanceof net.minecraft.world.entity.animal.axolotl.Axolotl
                || target instanceof net.minecraft.world.entity.animal.frog.Tadpole) && "bucket".equals(item)) return "catch_fish";
        if (target instanceof net.minecraft.world.entity.TamableAnimal t && t.isTame() && held.isEmpty()) return "command_pet";
        if (target instanceof AbstractHorse && held.isEmpty()) return "mount";
        if (target instanceof Animal a && a.isFood(held)) {
            if (target instanceof AbstractHorse || target instanceof net.minecraft.world.entity.animal.camel.Camel) return "feed_horse";
            if (target instanceof net.minecraft.world.entity.animal.Parrot || target instanceof net.minecraft.world.entity.animal.Chicken) return "feed_bird";
            if (target instanceof net.minecraft.world.entity.TamableAnimal) return "feed_pet";
            return "feed";
        }
        if (target instanceof Animal && "lead".equals(item)) return "leash";
        if (target instanceof net.minecraft.world.entity.animal.Wolf || target instanceof net.minecraft.world.entity.animal.Fox) return "pet_dog";
        if (target instanceof net.minecraft.world.entity.animal.Cat || target instanceof net.minecraft.world.entity.animal.Ocelot) return "pet_cat";
        if (target instanceof AbstractHorse || target instanceof net.minecraft.world.entity.animal.camel.Camel) return "pet_horse";
        if (target instanceof Animal a2 && a2.getBbHeight() < 0.8f) return "pet_small";
        if (target instanceof Animal) return "pet_dog";
        if (target instanceof AbstractGolem) return "golem";
        if (target instanceof Player) return "greet";
        if (target instanceof ArmorStand) return "armor_stand";
        if (target instanceof ItemFrame) return "item_frame";
        if (target instanceof Boat || target instanceof AbstractMinecart) return "board";
        if (target instanceof LivingEntity) return "creature";
        return null;
    }

    /** Relative yaw (degrees, positive = right) from an entity's facing to a point. */
    public static float relativeYaw(LivingEntity e, double x, double z) {
        double dx = x - e.getX(), dz = z - e.getZ();
        float yawTo = (float) Math.toDegrees(Math.atan2(dz, dx)) - 90f;
        return net.minecraft.util.Mth.wrapDegrees(yawTo - e.yBodyRot);
    }
}
