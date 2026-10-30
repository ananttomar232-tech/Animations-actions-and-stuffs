package com.motionworks.engine.procedural;

/**
 * Analytic two-bone inverse kinematics in a plane (law of cosines). Used for reaching hands in
 * first person and for rigs with two-segment limbs (custom models). Returns the root and joint
 * angles in radians for a chain of lengths {@code l1}, {@code l2} reaching a target at distance
 * {@code (tx, ty)} from the root, with the joint bending toward positive angles when
 * {@code bendPositive} is true.
 */
public final class TwoBoneIK {
    private TwoBoneIK() {}

    public record Solution(float rootAngle, float jointAngle, boolean reachable) {}

    public static Solution solve(float l1, float l2, float tx, float ty, boolean bendPositive) {
        float d = (float) Math.sqrt(tx * tx + ty * ty);
        boolean reachable = d <= l1 + l2 && d >= Math.abs(l1 - l2);
        float dc = Math.max(Math.abs(l1 - l2) + 1e-4f, Math.min(l1 + l2 - 1e-4f, d));
        float cosJoint = (l1 * l1 + l2 * l2 - dc * dc) / (2f * l1 * l2);
        float joint = (float) Math.PI - (float) Math.acos(Math.max(-1f, Math.min(1f, cosJoint)));
        float cosRoot = (l1 * l1 + dc * dc - l2 * l2) / (2f * l1 * dc);
        float rootOffset = (float) Math.acos(Math.max(-1f, Math.min(1f, cosRoot)));
        float base = (float) Math.atan2(ty, tx);
        if (bendPositive) return new Solution(base - rootOffset, joint, reachable);
        return new Solution(base + rootOffset, -joint, reachable);
    }

    /** Forward kinematics for verification: end effector position for the given angles. */
    public static float[] forward(float l1, float l2, float rootAngle, float jointAngle) {
        float x1 = l1 * (float) Math.cos(rootAngle);
        float y1 = l1 * (float) Math.sin(rootAngle);
        float a2 = rootAngle + jointAngle;
        return new float[] {x1 + l2 * (float) Math.cos(a2), y1 + l2 * (float) Math.sin(a2)};
    }
}
