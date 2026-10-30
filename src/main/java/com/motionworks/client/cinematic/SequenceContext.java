package com.motionworks.client.cinematic;

import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

/**
 * The world binding of a playing sequence: an anchor entity and a frozen origin/yaw so that
 * relative coordinates in authored sequences work anywhere. Actor selectors:
 * {@code @self}, {@code @anchor}, {@code @target} (crosshair entity at start) and
 * {@code @nearest:<entity id>}.
 */
public final class SequenceContext {
    private final Entity anchor;
    private final Vec3 origin;
    private final float originYaw;
    private final Map<String, Entity> resolved = new HashMap<>();

    SequenceContext(Entity anchor) {
        this.anchor = anchor;
        this.origin = anchor.position();
        this.originYaw = anchor instanceof LivingEntity le ? le.yBodyRot : anchor.getYRot();
        Minecraft mc = Minecraft.getInstance();
        if (mc.hitResult instanceof EntityHitResult ehr) resolved.put("@target", ehr.getEntity());
    }

    public Entity anchor() {
        return anchor;
    }

    public Vec3 origin() {
        return origin;
    }

    public float originYaw() {
        return originYaw;
    }

    /** Converts anchor-local [right, up, forward] into world space. */
    public Vec3 local(Vec3 l) {
        return origin.add(ShotEvaluator.rotate(l, originYaw));
    }

    public Entity resolve(String selector) {
        if (selector == null) return anchor;
        Entity cached = resolved.get(selector);
        if (cached != null && !cached.isRemoved()) return cached;
        Minecraft mc = Minecraft.getInstance();
        Entity e = switch (selector) {
            case "@self" -> mc.player;
            case "@anchor" -> anchor;
            case "@target" -> null;
            default -> {
                if (selector.startsWith("@nearest:") && mc.level != null) {
                    String id = selector.substring(9);
                    yield mc.level.getEntities((Entity) null, new AABB(origin, origin).inflate(48),
                                    x -> id.equals(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(x.getType()))))
                            .stream().min(Comparator.comparingDouble(x -> x.distanceToSqr(origin))).orElse(null);
                }
                yield null;
            }
        };
        if (e != null) resolved.put(selector, e);
        return e;
    }
}
