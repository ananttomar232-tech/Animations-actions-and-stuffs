package com.motionworks;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Conventions that unit tests cannot otherwise reach because the classes involved only load inside
 * a running client.
 */
class SourceConventionsTest {
    private static final Pattern SINGLETON = Pattern.compile("^ {4}(public |private )?static final \\w+ INSTANCE = new ");
    private static final Pattern STATIC_FIELD = Pattern.compile("^ {4}(public |private |protected )?static (final )?[\\w<>\\[\\], ?]+ [A-Z][A-Z0-9_]*\\s*[=;,]");

    /**
     * Statics initialise in declaration order, so a singleton constructed before another static field
     * sees that field as null (this crashed FirstPersonAnimator on the first client run).
     */
    @Test
    void singletonInstanceIsTheLastStaticField() throws IOException {
        List<String> offenders = new ArrayList<>();
        try (Stream<Path> files = Files.walk(Path.of("src/main/java"))) {
            for (Path f : (Iterable<Path>) files.filter(p -> p.toString().endsWith(".java"))::iterator) {
                List<String> lines = Files.readAllLines(f);
                for (int i = 0; i < lines.size(); i++) {
                    if (!SINGLETON.matcher(lines.get(i)).find()) continue;
                    for (int j = i + 1; j < lines.size(); j++) {
                        if (STATIC_FIELD.matcher(lines.get(j)).find()) offenders.add(f.getFileName() + ":" + (j + 1));
                    }
                }
            }
        }
        assertEquals(List.of(), offenders, "static fields declared after the INSTANCE singleton");
    }
}
