"""
Consume ``$ strings dvorak7min`` output and convert it into *workman* layout.

(for constructing `data.yaml`)
"""

dvorak=(
    "[{]}",
    "'\",<.>pPyYfFgGcCrRlL/?=+",
    "oOeEuUiIdDhHtTnNsS-_",
    ";:qQjJkKxXbBmMwWvVzZ",
)
workman = (
    "-_=+",
    "qQdDrRwWbBjJfFuUpP;:[{]}",
    "sShHtTgGyYnNeEoOiI'\"",
    "zZxXmMcCvVkKlL,<.>/?"
)
for a,b in zip(dvorak, workman, strict=True):
    assert len(a) == len(b), (a,b, len(a), len(b))

trans = str.maketrans("".join(dvorak), "".join(workman))
with open("../../workmanship.git/data.txt", "rt") as f:
    dvo_chars = f.read()

wrk_chars = dvo_chars.translate(trans)

with open("../../workmanship.git/data.yml", "wt") as f:
    f.write(wrk_chars)
