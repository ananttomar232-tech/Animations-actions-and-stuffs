package com.motionworks.common;

import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BookItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.BrushItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.CompassItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.EggItem;
import net.minecraft.world.item.ElytraItem;
import net.minecraft.world.item.EnderpearlItem;
import net.minecraft.world.item.ExperienceBottleItem;
import net.minecraft.world.item.FireworkRocketItem;
import net.minecraft.world.item.FishingRodItem;
import net.minecraft.world.item.FlintAndSteelItem;
import net.minecraft.world.item.HoeItem;
import net.minecraft.world.item.InstrumentItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.LeadItem;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.item.MilkBucketItem;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.PotionItem;
import net.minecraft.world.item.ShearsItem;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.ShovelItem;
import net.minecraft.world.item.SnowballItem;
import net.minecraft.world.item.SpyglassItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.ThrowablePotionItem;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.item.WritableBookItem;
import net.minecraft.world.item.WrittenBookItem;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.TorchBlock;

/**
 * Maps any item stack to a coarse handling category. Animations select by category, so modded
 * swords, axes and bows inherit the right motion automatically.
 */
public final class ItemCategories {
    private ItemCategories() {}

    public static String of(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return "empty";
        Item item = stack.getItem();
        if (item instanceof SwordItem) return "sword";
        if (item instanceof AxeItem) return "axe";
        if (item instanceof PickaxeItem) return "pickaxe";
        if (item instanceof ShovelItem) return "shovel";
        if (item instanceof HoeItem) return "hoe";
        if (item instanceof TridentItem) return "trident";
        if (item instanceof CrossbowItem) return "crossbow";
        if (item instanceof BowItem) return "bow";
        if (item instanceof ShieldItem) return "shield";
        if (item instanceof FishingRodItem) return "fishing_rod";
        if (item instanceof ShearsItem) return "shears";
        if (item instanceof FlintAndSteelItem || item == Items.FIRE_CHARGE) return "igniter";
        if (item instanceof BucketItem || item instanceof MilkBucketItem) return "bucket";
        if (item instanceof SpyglassItem) return "spyglass";
        if (item instanceof InstrumentItem) return "horn";
        if (item instanceof BrushItem) return "brush";
        if (item instanceof MapItem || item == Items.MAP) return "map";
        if (item instanceof BookItem || item instanceof WritableBookItem || item instanceof WrittenBookItem || item == Items.ENCHANTED_BOOK) return "book";
        if (item instanceof EnderpearlItem || item == Items.ENDER_EYE) return "pearl";
        if (item instanceof ThrowablePotionItem) return "splash_potion";
        if (item instanceof SnowballItem || item instanceof EggItem || item instanceof ExperienceBottleItem) return "throwable";
        if (item instanceof PotionItem) return "potion";
        if (item instanceof net.minecraft.world.item.HoneyBottleItem) return "honey";
        if (item == Items.GOLDEN_APPLE || item == Items.ENCHANTED_GOLDEN_APPLE || item == Items.GOLDEN_CARROT) return "golden_food";
        if (item instanceof net.minecraft.world.item.BowlFoodItem || item instanceof net.minecraft.world.item.SuspiciousStewItem) return "bowl_food";
        if (stack.isEdible()) {
            var food = stack.getFoodProperties(null);
            return food != null && food.isMeat() ? "meat" : "food";
        }
        if (item instanceof net.minecraft.world.item.NameTagItem) return "name_tag";
        if (item instanceof net.minecraft.world.item.SaddleItem) return "saddle";
        if (item instanceof net.minecraft.world.item.FoodOnAStickItem<?>) return "steering_stick";
        if (item instanceof net.minecraft.world.item.DyeItem) return "dye";
        if (item instanceof net.minecraft.world.item.RecordItem) return "record";
        if (item instanceof net.minecraft.world.item.HoneycombItem) return "honeycomb";
        if (item instanceof net.minecraft.world.item.BottleItem) return "glass_bottle";
        if (item instanceof net.minecraft.world.item.HangingEntityItem || item instanceof net.minecraft.world.item.ItemFrameItem) return "hanging";
        if (item instanceof net.minecraft.world.item.BoatItem || item instanceof net.minecraft.world.item.MinecartItem) return "vehicle";
        if (item instanceof CompassItem || item == Items.CLOCK || item == Items.RECOVERY_COMPASS) return "device";
        if (item instanceof LeadItem) return "lead";
        if (item instanceof ElytraItem) return "elytra";
        if (item instanceof ArmorItem) return "armor";
        if (item instanceof FireworkRocketItem) return "firework";
        if (item == Items.TOTEM_OF_UNDYING) return "totem";
        if (item instanceof BlockItem bi) {
            if (bi.getBlock() instanceof TorchBlock) return "torch";
            if (bi.getBlock() instanceof net.minecraft.world.level.block.CropBlock || bi.getBlock() instanceof net.minecraft.world.level.block.StemBlock) return "seed";
            if (bi.getBlock() instanceof net.minecraft.world.level.block.BushBlock) return "plant";
            if (bi.getBlock() instanceof LanternBlock) return "lantern";
            return "block";
        }
        if (stack.isDamageableItem()) return "tool";
        return "item";
    }

    /** True for categories that read as weapons for draw/sheathe and combat stance purposes. */
    public static boolean isWeapon(String category) {
        return switch (category) {
            case "sword", "axe", "trident", "bow", "crossbow" -> true;
            default -> false;
        };
    }
}
