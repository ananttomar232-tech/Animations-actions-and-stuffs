package com.motionworks.engine;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.io.ClipJsonLoader;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

final class TestClips {
    private TestClips() {}

    static Map<String, AnimationClip> load(String json) {
        JsonObject o = JsonParser.parseString(json.replace('`', '"')).getAsJsonObject();
        List<AnimationClip> clips = ClipJsonLoader.load(o, "test");
        return clips.stream().collect(Collectors.toMap(AnimationClip::id, Function.identity()));
    }
}
