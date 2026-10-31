package com.motionworks.gametest;

import com.motionworks.MotionWorks;
import com.motionworks.common.WorldEventArgs;
import com.motionworks.mixin.common.ExplosionAccessor;
import com.motionworks.server.TriggerTrace;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestAssertException;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Skeleton;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

/**
 * In-game tests run by {@code ./gradlew runGameTestServer}: each drives a real vanilla code path on a
 * dedicated server and checks, through {@link TriggerTrace}, that the matching animation trigger is sent.
 * They also prove that the common mixins apply and that the server side loads without client classes.
 */
@GameTestHolder(MotionWorks.MOD_ID)
@PrefixGameTestTemplate(false)
public final class MotionWorksGameTests {
    private MotionWorksGameTests() {}

    private static final String TEMPLATE = "empty";

    /** Records every trigger sent while {@code action} runs. */
    private static List<TriggerTrace.Entry> traced(Runnable action) {
        List<TriggerTrace.Entry> seen = new ArrayList<>();
        Runnable stop = TriggerTrace.listen(seen::add);
        try {
            action.run();
        } finally {
            stop.run();
        }
        return seen;
    }

    private static void expect(List<TriggerTrace.Entry> seen, String what, Predicate<TriggerTrace.Entry> match) {
        if (seen.stream().noneMatch(match)) throw new GameTestAssertException("expected " + what + ", traced " + seen);
    }

    @GameTest(template = TEMPLATE)
    public static void explosionAccessorReadsTheBlastRadius(GameTestHelper helper) {
        Vec3 at = helper.absoluteVec(new Vec3(1.5, 1.5, 1.5));
        Explosion blast = new Explosion(helper.getLevel(), null, at.x, at.y, at.z, 3.5f, false, Explosion.BlockInteraction.KEEP);
        float radius = ((ExplosionAccessor) blast).motionworks$radius();
        if (radius != 3.5f) throw new GameTestAssertException("radius read as " + radius);
        helper.succeed();
    }

    @GameTest(template = TEMPLATE)
    public static void ambientSoundSendsVocalize(GameTestHelper helper) {
        Cow cow = helper.spawn(EntityType.COW, 1, 1, 1);
        List<TriggerTrace.Entry> seen = traced(cow::playAmbientSound);
        expect(seen, "vocalize from the cow (MobMixin)", e -> e.entityId() == cow.getId() && e.event().equals("vocalize"));
        helper.succeed();
    }

    @GameTest(template = TEMPLATE)
    public static void launchedArrowSendsShootArrow(GameTestHelper helper) {
        Skeleton skeleton = helper.spawn(EntityType.SKELETON, 1, 1, 1);
        Arrow arrow = new Arrow(helper.getLevel(), skeleton);
        List<TriggerTrace.Entry> seen = traced(() -> helper.getLevel().addFreshEntity(arrow));
        arrow.discard();
        expect(seen, "shoot:arrow from the skeleton", e -> e.entityId() == skeleton.getId() && e.key().equals("shoot:arrow"));
        helper.succeed();
    }

    @GameTest(template = TEMPLATE)
    public static void lightningSendsAPositionalThunderclap(GameTestHelper helper) {
        Vec3 at = helper.absoluteVec(new Vec3(1.5, 1, 1.5));
        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(helper.getLevel());
        if (bolt == null) throw new GameTestAssertException("could not create a lightning bolt");
        bolt.moveTo(at);
        bolt.setVisualOnly(true);
        List<TriggerTrace.Entry> seen = traced(() -> helper.getLevel().addFreshEntity(bolt));
        expect(seen, "thunderclap world event at the strike", e -> e.entityId() == -1 && e.event().equals("thunderclap") && near(e.arg(), at, 0f));
        helper.succeed();
    }

    @GameTest(template = TEMPLATE)
    public static void explosionSendsAftermathAndFlinch(GameTestHelper helper) {
        IronGolem golem = helper.spawn(EntityType.IRON_GOLEM, 0, 1, 0);
        Vec3 at = helper.absoluteVec(new Vec3(2.5, 1.5, 2.5));
        List<TriggerTrace.Entry> seen = traced(() -> helper.getLevel().explode(null, at.x, at.y, at.z, 2f, Level.ExplosionInteraction.NONE));
        expect(seen, "explosion world event carrying the blast power", e -> e.entityId() == -1 && e.event().equals("explosion") && near(e.arg(), at, 2f));
        expect(seen, "explosion_flinch for the golem in range", e -> e.entityId() == golem.getId() && e.event().equals("explosion_flinch"));
        helper.succeed();
    }

    @GameTest(template = TEMPLATE)
    public static void traceCommandIsRegistered(GameTestHelper helper) {
        var root = helper.getLevel().getServer().getCommands().getDispatcher().getRoot().getChild("motionworks");
        if (root == null || root.getChild("trace") == null || root.getChild("animate") == null || root.getChild("cinematic") == null) {
            throw new GameTestAssertException("/motionworks is missing a subcommand");
        }
        helper.succeed();
    }

    /** True when a world-event argument decodes to {@code at} (0.1 block precision) and, if given, the magnitude. */
    private static boolean near(String arg, Vec3 at, float magnitude) {
        double[] v = WorldEventArgs.decode(arg);
        return v != null && Math.abs(v[0] - at.x) <= 0.051 && Math.abs(v[1] - at.y) <= 0.051 && Math.abs(v[2] - at.z) <= 0.051
                && (magnitude == 0f || Math.abs(v[3] - magnitude) < 1e-6);
    }
}
