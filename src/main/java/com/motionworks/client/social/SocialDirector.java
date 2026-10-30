package com.motionworks.client.social;

import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.common.CtxVars;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.Hashing;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Forms conversations between idle villagers (and players standing still near them). Groups are
 * formed from relative positions only when members are close, facing roughly toward each other
 * and have line of sight, so gestures never play toward empty space. Speaking turns rotate
 * deterministically from world time, so every client sees the same person talking.
 */
public final class SocialDirector {
    private static int cooldown;

    private SocialDirector() {}

    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !MWConfig.CLIENT.conversations.get() || --cooldown > 0) return;
        cooldown = 5;
        List<LivingEntity> candidates = new ArrayList<>();
        for (var e : mc.level.entitiesForRendering()) {
            if (!(e instanceof AbstractVillager || e instanceof Player) || !(e instanceof LivingEntity le)) continue;
            if (le.distanceToSqr(mc.gameRenderer.getMainCamera().getPosition()) > 48 * 48) continue;
            EntityAnimator a = AnimatorManager.find(le.getId());
            if (a == null) continue;
            Scope s = a.scope();
            s.set(CtxVars.IN_CONVERSATION, 0f);
            s.set(CtxVars.SPEAKING, 0f);
            s.set(CtxVars.CONVERSATION_SIZE, 0f);
            boolean idle = s.get(CtxVars.GROUND_SPEED) < 0.02f && s.get(CtxVars.SLEEPING) == 0f && s.get(CtxVars.TRADING) == 0f
                    && s.get(CtxVars.NEAR_HOSTILE) == 0f && !le.isPassenger();
            if (idle) candidates.add(le);
        }
        candidates.sort(Comparator.comparing(LivingEntity::getUUID));
        boolean[] used = new boolean[candidates.size()];
        long epoch = mc.level.getGameTime() / 70L;
        for (int i = 0; i < candidates.size(); i++) {
            if (used[i]) continue;
            LivingEntity a = candidates.get(i);
            List<LivingEntity> group = new ArrayList<>();
            group.add(a);
            for (int j = i + 1; j < candidates.size() && group.size() < 4; j++) {
                if (used[j]) continue;
                LivingEntity b = candidates.get(j);
                if (inRange(a, b) && a.hasLineOfSight(b)) {
                    group.add(b);
                    used[j] = true;
                }
            }
            if (group.size() < 2 || group.stream().allMatch(e -> e instanceof Player)) continue;
            used[i] = true;
            long seed = Hashing.combine(group.get(0).getUUID().getLeastSignificantBits(), epoch);
            int speaker = (int) Math.floorMod(Hashing.mix(seed), (long) group.size());
            for (int k = 0; k < group.size(); k++) {
                LivingEntity m = group.get(k);
                EntityAnimator an = AnimatorManager.find(m.getId());
                if (an == null) continue;
                Scope s = an.scope();
                s.set(CtxVars.IN_CONVERSATION, 1f);
                s.set(CtxVars.CONVERSATION_SIZE, group.size());
                boolean speaking = k == speaker && !(m instanceof Player);
                if (speaking && s.get(CtxVars.SPEAKING) == 0f) an.fire("speak");
                s.set(CtxVars.SPEAKING, speaking ? 1f : 0f);
                if (!(m instanceof Player)) faceGroup(m, group);
            }
        }
    }

    private static boolean inRange(LivingEntity a, LivingEntity b) {
        double d = a.distanceTo(b);
        return d > 0.9 && d < 3.6 && Math.abs(a.getY() - b.getY()) < 1.2;
    }

    /** Turns the head (and gradually the body) toward the group centre or current speaker. */
    private static void faceGroup(LivingEntity m, List<LivingEntity> group) {
        double cx = 0, cz = 0;
        for (LivingEntity o : group) {
            if (o == m) continue;
            cx += o.getX();
            cz += o.getZ();
        }
        cx /= group.size() - 1;
        cz /= group.size() - 1;
        float yaw = (float) (Math.toDegrees(Math.atan2(cz - m.getZ(), cx - m.getX())) - 90.0);
        float diff = net.minecraft.util.Mth.wrapDegrees(yaw - m.yBodyRot);
        m.yBodyRot += diff * 0.15f;
        m.yHeadRot = m.yBodyRot + net.minecraft.util.Mth.clamp(net.minecraft.util.Mth.wrapDegrees(yaw - m.yBodyRot), -50f, 50f);
    }
}
