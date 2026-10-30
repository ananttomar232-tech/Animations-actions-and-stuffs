package com.motionworks.engine.expr;

import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Parser for the MotionWorks expression language, a deterministic subset of Bedrock Molang.
 *
 * <pre>
 *   ternary   := coalesce ('?' ternary ':' ternary)?
 *   coalesce  := or ('??' or)*
 *   or        := and ('||' and)*
 *   and       := equality ('&amp;&amp;' equality)*
 *   equality  := compare (('==' | '!=') compare)*
 *   compare   := additive (('&lt;' | '&lt;=' | '&gt;' | '&gt;=') additive)*
 *   additive  := mul (('+' | '-') mul)*
 *   mul       := unary (('*' | '/' | '%') unary)*
 *   unary     := ('-' | '!' | '+') unary | primary
 *   primary   := number | 'string' | ident | ident '(' args ')' | '(' ternary ')'
 * </pre>
 *
 * Trigonometric functions take degrees like Molang, so curves exported from Blockbench behave
 * identically. Sub-expressions made only of constants are folded at parse time.
 */
public final class ExprParser {
    private static final Map<String, Expr> CACHE = new ConcurrentHashMap<>();

    private final String src;
    private int pos;

    private ExprParser(String src) {
        this.src = src;
    }

    public static Expr parse(String source) {
        String key = source.trim();
        Expr cached = CACHE.get(key);
        if (cached != null) return cached;
        ExprParser p = new ExprParser(key);
        Expr e = p.parseTernary();
        p.skipWs();
        while (p.pos < p.src.length() && p.src.charAt(p.pos) == ';') {
            p.pos++;
            p.skipWs();
        }
        if (p.pos != p.src.length()) throw p.error("Unexpected '" + p.src.charAt(p.pos) + "'");
        CACHE.put(key, e);
        return e;
    }

    /** Accepts a JSON-ish value: a number literal or an expression string. */
    public static Expr parseValue(Object value) {
        if (value instanceof Number n) return Expr.constant(n.floatValue());
        if (value instanceof Boolean b) return b ? Expr.ONE : Expr.ZERO;
        if (value instanceof String s) return parse(s);
        throw new IllegalArgumentException("Unsupported expression value: " + value);
    }

    private IllegalArgumentException error(String msg) {
        return new IllegalArgumentException(msg + " at " + pos + " in expression: " + src);
    }

    private void skipWs() {
        while (pos < src.length() && Character.isWhitespace(src.charAt(pos))) pos++;
    }

    private boolean eat(String token) {
        skipWs();
        if (src.startsWith(token, pos)) {
            pos += token.length();
            return true;
        }
        return false;
    }

    private boolean peek(String token) {
        skipWs();
        return src.startsWith(token, pos);
    }

    private Expr parseTernary() {
        Expr cond = parseCoalesce();
        if (eat("?")) {
            Expr a = parseTernary();
            if (!eat(":")) throw error("Expected ':'");
            Expr b = parseTernary();
            return fold(new Ternary(cond, a, b), cond, a, b);
        }
        return cond;
    }

    private Expr parseCoalesce() {
        Expr left = parseOr();
        while (eat("??")) {
            Expr right = parseOr();
            Expr l = left;
            left = s -> {
                float v = l.eval(s);
                return Float.isNaN(v) ? right.eval(s) : v;
            };
        }
        return left;
    }

    private Expr parseOr() {
        Expr left = parseAnd();
        while (eat("||")) {
            Expr l = left, r = parseAnd();
            left = fold(s -> (l.eval(s) != 0f || r.eval(s) != 0f) ? 1f : 0f, l, r);
        }
        return left;
    }

    private Expr parseAnd() {
        Expr left = parseEquality();
        while (eat("&&")) {
            Expr l = left, r = parseEquality();
            left = fold(s -> (l.eval(s) != 0f && r.eval(s) != 0f) ? 1f : 0f, l, r);
        }
        return left;
    }

    private Expr parseEquality() {
        Expr left = parseCompare();
        while (true) {
            if (eat("==")) {
                Expr l = left, r = parseCompare();
                left = fold(s -> Math.abs(l.eval(s) - r.eval(s)) < 1e-5f ? 1f : 0f, l, r);
            } else if (eat("!=")) {
                Expr l = left, r = parseCompare();
                left = fold(s -> Math.abs(l.eval(s) - r.eval(s)) >= 1e-5f ? 1f : 0f, l, r);
            } else {
                return left;
            }
        }
    }

    private Expr parseCompare() {
        Expr left = parseAdditive();
        while (true) {
            if (eat("<=")) {
                Expr l = left, r = parseAdditive();
                left = fold(s -> l.eval(s) <= r.eval(s) ? 1f : 0f, l, r);
            } else if (eat(">=")) {
                Expr l = left, r = parseAdditive();
                left = fold(s -> l.eval(s) >= r.eval(s) ? 1f : 0f, l, r);
            } else if (eat("<")) {
                Expr l = left, r = parseAdditive();
                left = fold(s -> l.eval(s) < r.eval(s) ? 1f : 0f, l, r);
            } else if (eat(">")) {
                Expr l = left, r = parseAdditive();
                left = fold(s -> l.eval(s) > r.eval(s) ? 1f : 0f, l, r);
            } else {
                return left;
            }
        }
    }

    private Expr parseAdditive() {
        Expr left = parseMul();
        while (true) {
            if (eat("+")) {
                Expr l = left, r = parseMul();
                left = fold(s -> l.eval(s) + r.eval(s), l, r);
            } else if (peek("-") && !peek("->")) {
                pos++;
                Expr l = left, r = parseMul();
                left = fold(s -> l.eval(s) - r.eval(s), l, r);
            } else {
                return left;
            }
        }
    }

    private Expr parseMul() {
        Expr left = parseUnary();
        while (true) {
            if (eat("*")) {
                Expr l = left, r = parseUnary();
                left = fold(s -> l.eval(s) * r.eval(s), l, r);
            } else if (eat("/")) {
                Expr l = left, r = parseUnary();
                left = fold(s -> {
                    float d = r.eval(s);
                    return d == 0f ? 0f : l.eval(s) / d;
                }, l, r);
            } else if (eat("%")) {
                Expr l = left, r = parseUnary();
                left = fold(s -> {
                    float d = r.eval(s);
                    return d == 0f ? 0f : l.eval(s) % d;
                }, l, r);
            } else {
                return left;
            }
        }
    }

    private Expr parseUnary() {
        if (eat("-")) {
            Expr e = parseUnary();
            return fold(s -> -e.eval(s), e);
        }
        if (eat("+")) return parseUnary();
        if (peek("!") && !peek("!=")) {
            pos++;
            Expr e = parseUnary();
            return fold(s -> e.eval(s) == 0f ? 1f : 0f, e);
        }
        return parsePrimary();
    }

    private Expr parsePrimary() {
        skipWs();
        if (pos >= src.length()) throw error("Unexpected end");
        char c = src.charAt(pos);
        if (c == '(') {
            pos++;
            Expr e = parseTernary();
            if (!eat(")")) throw error("Expected ')'");
            return e;
        }
        if (c == '\'' || c == '"') {
            int end = src.indexOf(c, pos + 1);
            if (end < 0) throw error("Unterminated string");
            String str = src.substring(pos + 1, end);
            pos = end + 1;
            return Expr.constant(StringIds.id(str));
        }
        if (Character.isDigit(c) || c == '.') {
            int start = pos;
            while (pos < src.length() && (Character.isDigit(src.charAt(pos)) || src.charAt(pos) == '.')) pos++;
            if (pos < src.length() && (src.charAt(pos) == 'e' || src.charAt(pos) == 'E')) {
                pos++;
                if (pos < src.length() && (src.charAt(pos) == '-' || src.charAt(pos) == '+')) pos++;
                while (pos < src.length() && Character.isDigit(src.charAt(pos))) pos++;
            }
            if (pos < src.length() && (src.charAt(pos) == 'f' || src.charAt(pos) == 'F')) pos++;
            String num = src.substring(start, pos).replace("f", "").replace("F", "");
            return Expr.constant(Float.parseFloat(num));
        }
        if (Character.isLetter(c) || c == '_') {
            int start = pos;
            while (pos < src.length() && (Character.isLetterOrDigit(src.charAt(pos)) || src.charAt(pos) == '_' || src.charAt(pos) == '.')) pos++;
            String ident = src.substring(start, pos).toLowerCase(Locale.ROOT);
            if (eat("(")) {
                List<Expr> args = new ArrayList<>();
                if (!eat(")")) {
                    do {
                        args.add(parseTernary());
                    } while (eat(","));
                    if (!eat(")")) throw error("Expected ')' after arguments to " + ident);
                }
                return function(ident, args);
            }
            return identifier(ident);
        }
        throw error("Unexpected '" + c + "'");
    }

    private Expr identifier(String ident) {
        switch (ident) {
            case "true": return Expr.ONE;
            case "false": return Expr.ZERO;
            case "math.pi": return Expr.constant(MathUtil.PI);
            default: break;
        }
        // Query functions that Bedrock writes without parentheses map onto plain variables.
        int id = Vars.id(ident);
        return s -> s.get(id);
    }

    private Expr function(String name, List<Expr> a) {
        String n = name.startsWith("math.") ? name.substring(5) : name;
        Expr e = switch (n) {
            case "sin" -> arity(name, a, 1, s -> MathUtil.sinDeg(a.get(0).eval(s)));
            case "cos" -> arity(name, a, 1, s -> MathUtil.cosDeg(a.get(0).eval(s)));
            case "abs" -> arity(name, a, 1, s -> Math.abs(a.get(0).eval(s)));
            case "sign" -> arity(name, a, 1, s -> Math.signum(a.get(0).eval(s)));
            case "floor" -> arity(name, a, 1, s -> (float) Math.floor(a.get(0).eval(s)));
            case "ceil" -> arity(name, a, 1, s -> (float) Math.ceil(a.get(0).eval(s)));
            case "round" -> arity(name, a, 1, s -> (float) Math.round(a.get(0).eval(s)));
            case "trunc" -> arity(name, a, 1, s -> (float) (long) a.get(0).eval(s));
            case "sqrt" -> arity(name, a, 1, s -> (float) Math.sqrt(Math.max(0f, a.get(0).eval(s))));
            case "exp" -> arity(name, a, 1, s -> (float) Math.exp(a.get(0).eval(s)));
            case "ln" -> arity(name, a, 1, s -> (float) Math.log(Math.max(1e-9f, a.get(0).eval(s))));
            case "asin" -> arity(name, a, 1, s -> (float) Math.toDegrees(Math.asin(MathUtil.clamp(a.get(0).eval(s), -1f, 1f))));
            case "acos" -> arity(name, a, 1, s -> (float) Math.toDegrees(Math.acos(MathUtil.clamp(a.get(0).eval(s), -1f, 1f))));
            case "atan" -> arity(name, a, 1, s -> (float) Math.toDegrees(Math.atan(a.get(0).eval(s))));
            case "atan2" -> arity(name, a, 2, s -> (float) Math.toDegrees(Math.atan2(a.get(0).eval(s), a.get(1).eval(s))));
            case "pow" -> arity(name, a, 2, s -> (float) Math.pow(a.get(0).eval(s), a.get(1).eval(s)));
            case "mod" -> arity(name, a, 2, s -> {
                float d = a.get(1).eval(s);
                return d == 0f ? 0f : a.get(0).eval(s) % d;
            });
            case "min" -> arity(name, a, 2, s -> Math.min(a.get(0).eval(s), a.get(1).eval(s)));
            case "max" -> arity(name, a, 2, s -> Math.max(a.get(0).eval(s), a.get(1).eval(s)));
            case "clamp" -> arity(name, a, 3, s -> MathUtil.clamp(a.get(0).eval(s), a.get(1).eval(s), a.get(2).eval(s)));
            case "lerp" -> arity(name, a, 3, s -> MathUtil.lerp(a.get(0).eval(s), a.get(1).eval(s), a.get(2).eval(s)));
            case "lerprotate" -> arity(name, a, 3, s -> {
                float from = a.get(0).eval(s);
                float to = a.get(1).eval(s);
                return from + MathUtil.wrapDegrees(to - from) * a.get(2).eval(s);
            });
            case "hermite_blend" -> arity(name, a, 1, s -> MathUtil.hermiteBlend(MathUtil.clamp01(a.get(0).eval(s))));
            case "smoothstep" -> arity(name, a, 3, s -> MathUtil.smoothstep(a.get(0).eval(s), a.get(1).eval(s), a.get(2).eval(s)));
            case "wrap" -> arity(name, a, 1, s -> MathUtil.wrapDegrees(a.get(0).eval(s)));
            // Deterministic replacements for Molang's random functions.
            case "hash" -> arity(name, a, 1, s -> Hashing.unit(Hashing.combine(s.seed, Float.floatToIntBits(a.get(0).eval(s)))));
            case "noise" -> arity(name, a, 1, s -> Hashing.noise1(s.seed, a.get(0).eval(s)));
            case "random" -> arity(name, a, 2, s -> {
                float lo = a.get(0).eval(s), hi = a.get(1).eval(s);
                return lo + (hi - lo) * Hashing.unit(Hashing.combine(s.seed, (long) s.animLoop, Float.floatToIntBits(lo * 31 + hi)));
            });
            case "random_integer" -> arity(name, a, 2, s -> {
                float lo = a.get(0).eval(s), hi = a.get(1).eval(s);
                return (float) Math.floor(lo + (hi - lo + 1) * Hashing.unit(Hashing.combine(s.seed, (long) s.animLoop, Float.floatToIntBits(lo * 17 + hi))));
            });
            /* Periodic helpers used heavily by authored locomotion: a phase-shifted sine wave over a
               period in seconds and a pulse that rises then decays inside [start, start+len]. */
            case "wave" -> arity(name, a, 3, s -> {
                float period = a.get(1).eval(s);
                return period == 0f ? 0f : (float) Math.sin((a.get(0).eval(s) / period + a.get(2).eval(s)) * MathUtil.TAU);
            });
            case "pulse" -> arity(name, a, 3, s -> {
                float t = a.get(0).eval(s), start = a.get(1).eval(s), len = a.get(2).eval(s);
                if (t < start || t > start + len || len <= 0f) return 0f;
                return (float) Math.sin((t - start) / len * Math.PI);
            });
            default -> throw error("Unknown function " + name);
        };
        Expr[] args = a.toArray(new Expr[0]);
        boolean deterministicPure = !(n.equals("hash") || n.equals("noise") || n.equals("random") || n.equals("random_integer"));
        return deterministicPure ? fold(e, args) : e;
    }

    private Expr arity(String name, List<Expr> args, int expected, Expr body) {
        if (args.size() != expected) throw error(name + " expects " + expected + " argument(s), got " + args.size());
        return body;
    }

    /** Collapses an expression to a constant when every operand is constant. */
    private static Expr fold(Expr e, Expr... operands) {
        for (Expr o : operands) if (!o.isConstant()) return e;
        return Expr.constant(e.eval(new Scope()));
    }

    private record Ternary(Expr cond, Expr a, Expr b) implements Expr {
        @Override
        public float eval(Scope s) {
            return cond.eval(s) != 0f ? a.eval(s) : b.eval(s);
        }
    }
}
