package com.motionworks.engine.clip;

/** All channels of a single bone within a clip. Any channel may be null. */
public record BoneTrack(String bone, Channel rotation, Channel position, Channel scale) {
    public Channel channel(ChannelTarget t) {
        return switch (t) {
            case ROTATION -> rotation;
            case POSITION -> position;
            case SCALE -> scale;
        };
    }

    public int keyCount() {
        int n = 0;
        if (rotation != null) n += rotation.keyCount();
        if (position != null) n += position.keyCount();
        if (scale != null) n += scale.keyCount();
        return n;
    }
}
