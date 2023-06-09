import itertools as itt
import random
from string import ascii_letters

import pytest

from workmanship import textmenus


@pytest.mark.parametrize(
    "item, exp",
    [
        ("a", {"1": (("a", 0), None)}),
        (("a", None), {"1": (("a", 0), None)}),
        (("1", "a", None), {"1": (("a", 0), None)}),
        (("2a", "a", None), {"2a": (("a", 0), None)}),
        ({("a"): None}, {"1": (("a", 0), None)}),
        ({("1", "a"): None}, {"1": (("a", 0), None)}),
        ({("2", "a"): None}, {"2": (("a", 0), None)}),
        ({("QB", "Quit"): None}, {"qb": (("Quit", 0), None)}),
        (1, ValueError("Invalid")),
        ((1, "dd"), ValueError("Invalid")),
        (("k", 12), {"1": (("k", 0), 12)}),
        ({(2, "a"): None}, ValueError("Invalid")),
        (1, ValueError("Invalid")),
        ((1, "dd"), ValueError("Invalid")),
        (("k", 12), {"1": (("k", 0), 12)}),
        ({(2, "a"): None}, ValueError("Invalid")),
        # with styles
        ((("a", 11), None), {"1": (("a", 11), None)}),
        (("1", ("a", 11), None), {"1": (("a", 11), None)}),
        (("2a", ("a", 11), None), {"2a": (("a", 11), None)}),
        ({("2", ("a", 22)): None}, {"2": (("a", 22), None)}),
        (("a", ("tt", "hh"), 4325), ValueError("Invalid")),
    ],
)
def test_menu(item, exp):
    if isinstance(exp, Exception):
        with pytest.raises(type(exp), match=str(exp)):
            textmenus.Menu(item)
    else:
        menu = textmenus.Menu(item)
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

    rows = textmenus.tabulate(texts, max_width, gutter)
    for r in rows:
        assert len(r) < max_width
