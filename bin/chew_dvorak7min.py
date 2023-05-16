"""
Consume "dvorak" from ``lessons.yml`` and convert it into other layouts.

Original dvorak lessons extracted with ``$ strings dvorak7min``.
"""
import re

from ruamel.yaml import YAML

import workmanship

trans_chars = {
    "dvorak": (
        "[{]}",
        "'\",<.>pPyYfFgGcCrRlL/?=+",
        "oOeEuUiIdDhHtTnNsS-_",
        ";:qQjJkKxXbBmMwWvVzZ",
    ),
    "workman": (
        "-_=+",
        "qQdDrRwWbBjJfFuUpP;:[{]}",
        "sShHtTgGyYnNeEoOiI'\"",
        "zZxXmMcCvVkKlL,<.>/?",
    ),
}


def translate_lessons(trans: dict, lessons: dict) -> dict:
    def trans_title(t):
        m = re.match("^(.+): (.+)$", t)
        if m:
            return type(t)(f"{m.group(1).translate(trans)}: {m.group(2)}")
        return t

    def trans_words(w):
        return type(w)(w.translate(trans))

    return type(lessons)({trans_title(k): trans_words(v) for k, v in lessons.items()})


def make_chars_trans_table(inp_layout: str, out_layout: str) -> dict:
    inp_chars = trans_chars[inp_layout]
    out_chars = trans_chars[out_layout]
    for a, b in zip(inp_chars, out_chars, strict=True):
        assert len(a) == len(b), (a, b, len(a), len(b))

    return str.maketrans("".join(inp_chars), "".join(out_chars))


def append_layout(lessons, inp_layout: str, out_layout: str, out_fpath) -> dict:
    trans = make_chars_trans_table(inp_layout, out_layout)

    lessons = workmanship.load_lessons(yaml_type="rt")
    layouts = lessons["layouts"]

    new_layout = translate_lessons(trans, layouts[inp_layout])
    layouts[out_layout] = new_layout

    yaml = YAML()  # default, if not specfied, is 'rt' (round-trip)
    with open(out_fpath, "wt") as f:
        yaml.dump(lessons, f)


if __name__ == "__main__":
    append_layout(None, "dvorak", "workman", "lessons.yml")
