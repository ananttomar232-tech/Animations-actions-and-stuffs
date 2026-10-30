package com.motionworks.engine.expr;

/** A compiled expression. Booleans are represented as 0 / 1. */
public interface Expr {
    float eval(Scope s);

    default boolean isConstant() {
        return false;
    }

    static Expr constant(float v) {
        return new Const(v);
    }

    Expr ZERO = new Const(0f);
    Expr ONE = new Const(1f);

    final class Const implements Expr {
        public final float value;

        public Const(float value) {
            this.value = value;
        }

        @Override
        public float eval(Scope s) {
            return value;
        }

        @Override
        public boolean isConstant() {
            return true;
        }

        @Override
        public String toString() {
            return Float.toString(value);
        }
    }
}
