import itertools as itt
import random
from string import ascii_letters

import pytest

import workmanship as wm


@pytest.mark.parametrize(
    "item, exp",
    [
        ("a", {"1": ("a", None)}),
        (("a", None), {"1": ("a", None)}),
        (("1", "a", None), {"1": ("a", None)}),
        (("2", "a", None), {"2": ("a", None)}),
        ({("a"): None}, {"1": ("a", None)}),
        ({("1", "a"): None}, {"1": ("a", None)}),
        ({("2", "a"): None}, {"2": ("a", None)}),
        ({("Q", "Quit"): None}, {"q": ("Quit", None)}),
        (1, ValueError("Invalid")),
        ((1, "dd"), ValueError("Invalid")),
        (("k", 12), {"1": ("k", 12)}),
        ({(2, "a"): None}, ValueError("Invalid")),
    ],
)
def test_menu(item, exp):
    if isinstance(exp, Exception):
        with pytest.raises(type(exp), match=str(exp)):
            wm.Menu(item)
    else:
        menu = wm.Menu(item)
        assert menu == exp


@pytest.mark.parametrize(
    "nitems, max_width, gutter",
    itt.product(
        (1, 3, 12, 13, 14, 23, 33, 64),
        (16, 32, 65, 80),
        (" ", "  ", ""),
    ),
)
def test_tabulate_smoke(nitems, max_width, gutter):
    rnd = random.Random(1)
    lengths = rnd.choices(range(5, 15), k=nitems)
    texts = ["".join(rnd.choices(ascii_letters, k=l)) for l in lengths]
    gutter = "  "

    rows = wm.tabulate(texts, max_width, gutter)
    for r in rows:
        assert len(r) < max_width
