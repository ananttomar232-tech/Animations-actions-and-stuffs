#version 150

// MotionWorks living foliage. Identical to vanilla for untagged geometry; tagged vertices
// (vertex alpha < 255, written at bake time) are displaced by the shared wind field.

#moj_import <light.glsl>
#moj_import <fog.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform vec3 ChunkOffset;
uniform int FogShape;

uniform vec4 MwWind;
uniform float MwTime;
uniform vec3 MwCam;
uniform vec4 MwPush0;
uniform vec4 MwPush1;
uniform vec4 MwPush2;
uniform vec4 MwPush3;

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec4 normal;

// Spatial frequencies are whole multiples of 2*pi/256 so the field is seamless while the
// camera-relative origin (MwCam = camera mod 256) wraps.
const float K = 6.28318530718 / 256.0;

vec3 pushAway(vec3 p, vec4 pusher, float w) {
    if (pusher.w <= 0.0) return vec3(0.0);
    vec3 d = p - pusher.xyz;
    if (abs(d.y) > 2.5) return vec3(0.0);
    d.y = 0.0;
    float dist = length(d);
    float f = clamp(1.0 - dist / pusher.w, 0.0, 1.0);
    f *= f;
    vec3 dir = dist > 0.001 ? d / dist : vec3(0.0);
    return dir * f * 0.32 * w + vec3(0.0, -0.18 * f * w, 0.0);
}

vec3 field(vec3 world, float t, float s, vec2 dir, float gust) {
    vec3 n = vec3(
        sin(t * 2.3 + world.x * K * 31.0 + world.y * 0.81),
        sin(t * 1.9 + world.z * K * 27.0 + world.x * K * 15.0) * 0.5,
        cos(t * 2.1 + world.z * K * 29.0 + world.y * 0.9));
    float sway = sin(t * 1.1 + world.x * K * 11.0 + world.z * K * 7.0) * 0.5 + 0.5;
    return n * 0.03 * (0.35 + s) + vec3(dir.x, 0.0, dir.y) * (s * (0.3 + 0.7 * sway) + gust) * 0.05;
}

void main() {
    vec3 pos = Position + ChunkOffset;
    vec4 col = Color;
    float code = 254.0 - floor(Color.a * 255.0 + 0.5);
    if (code >= 0.0) {
        col.a = 1.0;
        float s = MwWind.z;
        if (s > 0.0001) {
            float profile = floor(code / 32.0 + 0.001);
            float weight = mod(code, 32.0) / 31.0;
            vec3 world = pos + MwCam;
            vec2 dir = MwWind.xy / s;
            float t = MwTime;
            float gust = MwWind.w * (0.55 + 0.45 * sin(t * 0.9 + world.x * K * 5.0 + world.z * K * 3.0));
            float wave = sin(t * 1.7 + world.x * K * 21.0 + world.z * K * 14.0) * 0.6
                       + sin(t * 3.1 + world.x * K * 40.0 - world.z * K * 30.0) * 0.3;
            float bend = (0.3 + 0.45 * wave) * s + gust * 0.7;
            vec3 off = vec3(0.0);
            if (profile < 0.5) {
                float h = weight * weight;
                off.xz = dir * bend * 0.2 * h
                       + vec2(sin(t * 4.7 + world.z * K * 60.0), cos(t * 5.3 + world.x * K * 60.0)) * 0.02 * s * h;
                off.y = -abs(bend) * 0.05 * h;
                off += pushAway(pos, MwPush0, h) + pushAway(pos, MwPush1, h) + pushAway(pos, MwPush2, h) + pushAway(pos, MwPush3, h);
            } else if (profile < 1.5) {
                off = field(world, t, s, dir, gust) * weight * 1.6;
            } else if (profile < 2.5) {
                float ang = sin(t * 2.2 + world.x * K * 21.0 + world.z * K * 16.0) * (0.04 + 0.12 * s) + gust * 0.1;
                off.xz = dir * ang * weight;
                off.y = -0.5 * ang * ang * weight;
            } else if (profile < 3.5) {
                float cur = sin(t * 0.8 + world.x * K * 18.0 + world.z * K * 11.0);
                off.xz = vec2(cur, cos(t * 0.65 + world.z * K * 16.0 + world.y * 0.4)) * 0.09 * weight;
            } else {
                off.y = sin(t * 1.3 + world.x * K * 25.0 + world.z * K * 20.0) * 0.012;
            }
            pos += off;
        }
    }
    gl_Position = ProjMat * ModelViewMat * vec4(pos, 1.0);

    vertexDistance = fog_distance(ModelViewMat, pos, FogShape);
    vertexColor = col * minecraft_sample_lightmap(Sampler2, UV2);
    texCoord0 = UV0;
    normal = ProjMat * ModelViewMat * vec4(Normal, 0.0);
}
