"""
Consume "dvorak" from ``lessons.yml`` and convert it into other layouts.

Original dvorak lessons extracted with ``$ strings dvorak7min``.
"""
import re

from ruamel.yaml import YAML

from workmanship import lessons as ls

trans_chars = {
    "Dvorak": [
        "7&8*9(0)[{]}",
        "'\",<.>pPyYfFgGcCrRlL/?=+",
        "aAoOeEuUiIdDhHtTnNsS-_",
        ";:qQjJkKxXbBmMwWvVzZ",
    ],
    "Workman": [
        "7&8*9(0)-_=+",
        "qQdDrRwWbBjJfFuUpP;:[{]}",
        "aAsShHtTgGyYnNeEoOiI'\"",
        "zZxXmMcCvVkKlL,<.>/?",
    ],
    "Workman(EL)": [
        "7&8*9(0)-_=+",
        ";:δΔρΡςΣβΒξΞφΦθΘπΠ;:[{]}",
        "αΑσΣηΗτΤγΓυΥνΝεΕοΟιΙ'\"",
        "ζΖχΧμΜψΨωΩκΚλΛ,<.>/?",
    ],
    "ColemakDH(ISO)": [
        "-_7&8*9(0)=+",
        "qQwWfFpPbBjJlLuUyY;:[{]}",
        "aArRsStTgGmMnNeEiIoO'\"",
        "zZxXcCdDvVkKhH,<.>/?",
    ],
    "ColemakDH(ISO,EL)": [
        "-_7&8*9(0)=+",
        ";:ςΣφΦπΠβΒξΞλΛθΘυΥ;:[{]}",
        "αΑρΡσΣτΤγΓμΜνΝεΕιΙοΟ'\"",
        "ζΖχΧψΨδΔωΩκΚηΗ,<.>/?",
    ],
    "ColemakDH(ANSI)": [
        "-_7&8*9(0)=+",
        "qQwWfFpPbBjJlLuUyY;:[{]}",
        "aArRsStTgGmMnNeEiIoO'\"",
        "xXcCdDvVzZkKhH,<.>/?",
    ],
    "ColemakDH(ANSI,EL)": [
        "-_7&8*9(0)=+",
        ";:ςΣφΦπΠβΒξΞλΛθΘυΥ;:[{]}",
        "αΑρΡσΣτΤγΓμΜνΝεΕιΙοΟ'\"",
        "χΧψΨδΔωΩζΖκΚηΗ,<.>/?",
    ],
}


def translate_lessons(trans: dict, lessons: dict) -> dict:
    def trans_title(t):
        m = re.match("^(.+): (.+)$", t)
        if m:
            return type(t)(
                f"{m.group(1).lower().translate(trans).upper()}: {m.group(2)}"
            )
        return t

    def trans_words(w):
        return type(w)(w.translate(trans))

    return type(lessons)({trans_title(k): trans_words(v) for k, v in lessons.items()})


def make_chars_trans_table(inp_layout: str, out_layout: str) -> dict:
    inp_chars = trans_chars[inp_layout]
    out_chars = trans_chars[out_layout]
    for a, b in zip(inp_chars, out_chars, strict=True):
        assert len(a) == len(b), (inp_layout, out_layout, a, b, len(a), len(b))

    return str.maketrans("".join(inp_chars), "".join(out_chars))


def convert_layouts(conversions: list[tuple[str, str]], out_fpath) -> dict:
    data = ls.load_lessons(yaml_type="rt")
    layouts = data["layouts"]

    for inp_layout, (out_layout, out_key) in conversions:
        trans = make_chars_trans_table(inp_layout, out_layout)
        lessons = translate_lessons(trans, layouts[inp_layout]["lessons"])
        layouts[out_layout] = {
            "key": out_key,
            "lessons": lessons,
        }

    yaml = YAML()  # default, if not specfied, is 'rt' (round-trip)
    with open(out_fpath, "wt") as f:
        yaml.dump(data, f)


if __name__ == "__main__":
    conversions = [
        ("Dvorak", ("Workman", "w")),
        ("Dvorak", ("Workman(EL)", "ς")),
        ("Dvorak", ("ColemakDH(ISO)", "cdh")),
        ("Dvorak", ("ColemakDH(ISO,EL)", "ψδη")),
        ("Dvorak", ("ColemakDH(ANSI)", "cdha")),
        ("Dvorak", ("ColemakDH(ANSI,EL)", "ψδηα")),
    ]
    convert_layouts(conversions, "lessons.yml")
