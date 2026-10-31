#!/usr/bin/env python3
"""Writes data/motionworks/structures/empty.nbt, the GameTest template: a 3x3x3 box with a stone floor.

Structure templates are gzip-compressed NBT; this is a minimal writer for the tag types a template needs.
"""
import gzip
import os
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src/main/resources/data/motionworks/structures")
DATA_VERSION = 3465  # Minecraft 1.20.1

END, INT, STRING, LIST, COMPOUND = 0, 3, 8, 9, 10


def name(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def payload(tag, value):
    if tag == INT:
        return struct.pack(">i", value)
    if tag == STRING:
        return name(value)
    if tag == LIST:
        elem, items = value
        return struct.pack(">bi", elem if items else END, len(items)) + b"".join(payload(elem, v) for v in items)
    if tag == COMPOUND:
        return b"".join(struct.pack(">b", t) + name(k) + payload(t, v) for k, (t, v) in value.items()) + struct.pack(">b", END)
    raise ValueError(tag)


def ints(*v):
    return LIST, (INT, list(v))


def template(size, floor_block):
    w, h, d = size
    blocks = [{"pos": ints(x, 0, z), "state": (INT, 0)} for x in range(w) for z in range(d)]
    return {
        "DataVersion": (INT, DATA_VERSION),
        "size": ints(w, h, d),
        "palette": (LIST, (COMPOUND, [{"Name": (STRING, floor_block)}])),
        "blocks": (LIST, (COMPOUND, blocks)),
        "entities": (LIST, (COMPOUND, [])),
    }


def write(path, root):
    data = struct.pack(">b", COMPOUND) + name("") + payload(COMPOUND, root)
    with gzip.open(path, "wb") as fh:
        fh.write(data)


def main():
    os.makedirs(OUT, exist_ok=True)
    write(os.path.join(OUT, "empty.nbt"), template((3, 3, 3), "minecraft:stone"))
    print("wrote", os.path.relpath(os.path.join(OUT, "empty.nbt"), ROOT))


if __name__ == "__main__":
    main()
