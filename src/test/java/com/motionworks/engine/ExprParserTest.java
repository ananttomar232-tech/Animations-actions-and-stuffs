package com.motionworks.engine;

import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.expr.ExprParser;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.StringIds;
import com.motionworks.engine.expr.Vars;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ExprParserTest {
    private static float eval(String src, Scope s) {
        return ExprParser.parse(src).eval(s);
    }

    @Test
    void arithmeticAndPrecedence() {
        Scope s = new Scope();
        assertEquals(7f, eval("1 + 2 * 3", s), 1e-6);
        assertEquals(9f, eval("(1 + 2) * 3", s), 1e-6);
        assertEquals(-4f, eval("-2 * 2", s), 1e-6);
        assertEquals(1f, eval("7 % 3", s), 1e-6);
        assertEquals(0f, eval("5 / 0", s), 1e-6, "division by zero is defined as 0");
        assertEquals(1f, eval("2 > 1 && 3 >= 3", s), 1e-6);
        assertEquals(0f, eval("!(1 == 1)", s), 1e-6);
        assertEquals(5f, eval("1 < 2 ? 5 : 6", s), 1e-6);
        assertEquals(6f, eval("1 > 2 ? 5 : 1 > 0 ? 6 : 7", s), 1e-6);
    }

    @Test
    void constantsFold() {
        Expr e = ExprParser.parse("math.sin(90) * 10 + math.clamp(5, 0, 2)");
        assertTrue(e.isConstant());
        assertEquals(12f, e.eval(new Scope()), 1e-5);
    }

    @Test
    void variablesAndAliases() {
        Scope s = new Scope();
        s.set("q.ground_speed", 0.25f);
        assertEquals(0.25f, eval("query.ground_speed", s), 1e-6);
        assertEquals(2.5f, eval("q.ground_speed * 10", s), 1e-6);
        assertEquals(Vars.id("q.ground_speed"), Vars.id("QUERY.Ground_Speed"));
        s.animTime = 0.5f;
        assertEquals(0.5f, eval("q.anim_time", s), 1e-6);
    }

    @Test
    void stringComparisons() {
        Scope s = new Scope();
        s.setString(Vars.id("q.main_hand"), "sword");
        assertEquals(1f, eval("q.main_hand == 'sword'", s), 1e-6);
        assertEquals(0f, eval("q.main_hand == 'axe'", s), 1e-6);
        assertEquals(StringIds.id("SWORD"), StringIds.id("sword"));
    }

    @Test
    void deterministicRandom() {
        Scope a = new Scope();
        a.seed = 42;
        Scope b = new Scope();
        b.seed = 42;
        assertEquals(eval("math.random(0, 10)", a), eval("math.random(0, 10)", b), 0f);
        float v = eval("math.random(2, 3)", a);
        assertTrue(v >= 2f && v <= 3f);
        float n = eval("math.noise(q.anim_time * 3)", a);
        assertTrue(n >= -1f && n <= 1f);
    }

    @Test
    void helpers() {
        Scope s = new Scope();
        s.animTime = 0.25f;
        assertEquals(1f, eval("math.wave(q.anim_time, 1, 0)", s), 1e-5);
        assertEquals(1f, eval("math.pulse(0.5, 0, 1)", s), 1e-5);
        assertEquals(0f, eval("math.pulse(2, 0, 1)", s), 1e-5);
        assertEquals(170f, eval("math.lerprotate(170, -170, 0)", s), 1e-4);
        assertEquals(180f, eval("math.lerprotate(170, -170, 0.5)", s), 1e-4);
    }

    @Test
    void errorsAreReported() {
        assertThrows(IllegalArgumentException.class, () -> ExprParser.parse("1 +"));
        assertThrows(IllegalArgumentException.class, () -> ExprParser.parse("math.nope(1)"));
        assertThrows(IllegalArgumentException.class, () -> ExprParser.parse("math.clamp(1, 2)"));
    }
}
