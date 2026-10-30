package com.motionworks.config;

import net.minecraftforge.common.ForgeConfigSpec;
import org.apache.commons.lang3.tuple.Pair;

/** All user-facing switches. Client options are per-player; server options govern gameplay. */
public final class MWConfig {
    public static final Client CLIENT;
    public static final ForgeConfigSpec CLIENT_SPEC;
    public static final Server SERVER;
    public static final ForgeConfigSpec SERVER_SPEC;

    static {
        Pair<Client, ForgeConfigSpec> c = new ForgeConfigSpec.Builder().configure(Client::new);
        CLIENT = c.getLeft();
        CLIENT_SPEC = c.getRight();
        Pair<Server, ForgeConfigSpec> s = new ForgeConfigSpec.Builder().configure(Server::new);
        SERVER = s.getLeft();
        SERVER_SPEC = s.getRight();
    }

    private MWConfig() {}

    public enum BossIntroMode { OFF, TITLE_CARD, FULL_CINEMATIC }

    public static final class Client {
        public final ForgeConfigSpec.BooleanValue enabled;
        public final ForgeConfigSpec.BooleanValue playerAnimations;
        public final ForgeConfigSpec.BooleanValue mobAnimations;
        public final ForgeConfigSpec.DoubleValue intensity;
        public final ForgeConfigSpec.IntValue animationDistance;

        public final ForgeConfigSpec.BooleanValue firstPerson;
        public final ForgeConfigSpec.DoubleValue firstPersonIntensity;
        public final ForgeConfigSpec.BooleanValue weaponSway;

        public final ForgeConfigSpec.BooleanValue cameraEffects;
        public final ForgeConfigSpec.DoubleValue cameraShake;
        public final ForgeConfigSpec.BooleanValue landingDip;
        public final ForgeConfigSpec.BooleanValue damageTilt;

        public final ForgeConfigSpec.BooleanValue cinematics;
        public final ForgeConfigSpec.EnumValue<BossIntroMode> bossIntros;
        public final ForgeConfigSpec.BooleanValue letterbox;
        public final ForgeConfigSpec.BooleanValue hideHudInCinematics;

        public final ForgeConfigSpec.BooleanValue foliageWind;
        public final ForgeConfigSpec.DoubleValue windStrength;
        public final ForgeConfigSpec.BooleanValue bannerWind;
        public final ForgeConfigSpec.BooleanValue weatherEffects;
        public final ForgeConfigSpec.BooleanValue ambientParticles;

        public final ForgeConfigSpec.IntValue maxParticlesPerSecond;
        public final ForgeConfigSpec.BooleanValue footstepParticles;
        public final ForgeConfigSpec.BooleanValue weaponTrails;
        public final ForgeConfigSpec.BooleanValue impactParticles;

        public final ForgeConfigSpec.BooleanValue foleySounds;
        public final ForgeConfigSpec.DoubleValue foleyVolume;

        public final ForgeConfigSpec.BooleanValue villagerFaces;
        public final ForgeConfigSpec.BooleanValue illagerFaces;
        public final ForgeConfigSpec.BooleanValue playerFaces;
        public final ForgeConfigSpec.IntValue playerEyeRow;

        public final ForgeConfigSpec.BooleanValue personality;
        public final ForgeConfigSpec.BooleanValue conversations;
        public final ForgeConfigSpec.BooleanValue equipmentDisplay;
        public final ForgeConfigSpec.BooleanValue debugOverlay;

        Client(ForgeConfigSpec.Builder b) {
            b.push("animation");
            enabled = b.comment("Master switch for all MotionWorks animation").define("enabled", true);
            playerAnimations = b.comment("Animate players").define("playerAnimations", true);
            mobAnimations = b.comment("Animate mobs, animals and NPCs").define("mobAnimations", true);
            intensity = b.comment("Global animation strength (0 = vanilla, 1 = authored)").defineInRange("intensity", 1.0, 0.0, 1.5);
            animationDistance = b.comment("Entities further than this many blocks keep vanilla animation").defineInRange("animationDistance", 64, 8, 256);
            b.pop();

            b.push("firstPerson");
            firstPerson = b.comment("Animated first-person hands and items").define("enabled", true);
            firstPersonIntensity = b.defineInRange("intensity", 1.0, 0.0, 1.5);
            weaponSway = b.comment("Inertial sway of held items when turning and moving").define("weaponSway", true);
            b.pop();

            b.push("camera");
            cameraEffects = b.comment("Camera effects such as impact shake and landing dip").define("enabled", true);
            cameraShake = b.defineInRange("shakeStrength", 1.0, 0.0, 2.0);
            landingDip = b.define("landingDip", true);
            damageTilt = b.define("damageTilt", true);
            b.pop();

            b.push("cinematics");
            cinematics = b.comment("Allow cinematic sequences (always skippable)").define("enabled", true);
            bossIntros = b.comment("OFF, TITLE_CARD (letterbox + title, never takes the camera) or FULL_CINEMATIC (only outside survival danger)")
                    .defineEnum("bossIntros", BossIntroMode.TITLE_CARD);
            letterbox = b.define("letterbox", true);
            hideHudInCinematics = b.define("hideHud", true);
            b.pop();

            b.push("environment");
            foliageWind = b.comment("Wind-driven grass, leaves, crops and hanging lanterns (core shader; disabled automatically with shader packs)").define("foliageWind", true);
            windStrength = b.defineInRange("windStrength", 1.0, 0.0, 2.0);
            bannerWind = b.define("bannerWind", true);
            weatherEffects = b.comment("Wind-blown rain, snow drift, leaf fall, storm atmosphere").define("weatherEffects", true);
            ambientParticles = b.comment("Dust motes, fireflies, pollen, embers").define("ambientParticles", true);
            b.pop();

            b.push("particles");
            maxParticlesPerSecond = b.defineInRange("maxPerSecond", 400, 0, 5000);
            footstepParticles = b.define("footsteps", true);
            weaponTrails = b.define("weaponTrails", true);
            impactParticles = b.define("impacts", true);
            b.pop();

            b.push("sound");
            foleySounds = b.comment("Animation-synchronised foley (cloth, armour, weapon handling, surface layers)").define("foley", true);
            foleyVolume = b.defineInRange("foleyVolume", 0.8, 0.0, 2.0);
            b.pop();

            b.push("faces");
            villagerFaces = b.comment("Blinking, eye tracking and expressions for villagers").define("villagers", true);
            illagerFaces = b.define("illagers", true);
            playerFaces = b.comment("Overlay face rig for players (works best with default-style skins)").define("players", true);
            playerEyeRow = b.comment("Row of the eyes on the 8x8 face (Steve/Alex = 4)").defineInRange("playerEyeRow", 4, 0, 7);
            b.pop();

            b.push("acting");
            personality = b.comment("Per-character personality profiles influencing idles and posture").define("personality", true);
            conversations = b.comment("Nearby idle villagers and players face each other and converse").define("conversations", true);
            equipmentDisplay = b.comment("Show stowed weapons, shields and quivers on the body").define("equipmentDisplay", true);
            debugOverlay = b.comment("Show the active clips of the targeted entity").define("debugOverlay", false);
            b.pop();
        }
    }

    public static final class Server {
        public final ForgeConfigSpec.BooleanValue broadcastTriggers;
        public final ForgeConfigSpec.BooleanValue dodge;
        public final ForgeConfigSpec.IntValue dodgeCooldownTicks;
        public final ForgeConfigSpec.IntValue dodgeInvulnerabilityTicks;
        public final ForgeConfigSpec.BooleanValue parry;
        public final ForgeConfigSpec.IntValue parryWindowTicks;
        public final ForgeConfigSpec.BooleanValue shieldBash;
        public final ForgeConfigSpec.BooleanValue counterAttacks;
        public final ForgeConfigSpec.DoubleValue counterDamageBonus;
        public final ForgeConfigSpec.BooleanValue emotes;
        public final ForgeConfigSpec.BooleanValue rollOnLanding;

        Server(ForgeConfigSpec.Builder b) {
            b.push("sync");
            broadcastTriggers = b.comment("Send interaction/combat animation triggers to nearby players").define("broadcastTriggers", true);
            b.pop();
            b.push("combat");
            dodge = b.comment("Dodge key performs a directional roll/step with brief invulnerability").define("dodge", true);
            dodgeCooldownTicks = b.defineInRange("dodgeCooldownTicks", 24, 5, 200);
            dodgeInvulnerabilityTicks = b.defineInRange("dodgeInvulnerabilityTicks", 6, 0, 20);
            parry = b.comment("Raising a shield just before a melee hit parries it and staggers the attacker").define("parry", true);
            parryWindowTicks = b.defineInRange("parryWindowTicks", 5, 1, 20);
            shieldBash = b.define("shieldBash", true);
            counterAttacks = b.comment("An attack shortly after a parry deals bonus damage").define("counterAttacks", true);
            counterDamageBonus = b.defineInRange("counterDamageBonus", 0.25, 0.0, 2.0);
            rollOnLanding = b.comment("Sprinting players who land from 4-12 blocks roll and take reduced fall damage").define("rollOnLanding", true);
            b.pop();
            b.push("social");
            emotes = b.define("emotes", true);
            b.pop();
        }
    }
}
