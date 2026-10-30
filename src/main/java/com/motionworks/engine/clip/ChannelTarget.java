package com.motionworks.engine.clip;

public enum ChannelTarget {
    /** Degrees in data, radians at runtime. Offset from the bone's rest rotation. */
    ROTATION(0),
    /** Model pixels, offset from the rest pivot. ModelPart space (y points down). */
    POSITION(3),
    /** Multiplier where 1 means unchanged. */
    SCALE(6);

    /** Index of this channel's first component inside a 9-float bone transform. */
    public final int offset;

    ChannelTarget(int offset) {
        this.offset = offset;
    }

    public int group() {
        return offset / 3;
    }
}
