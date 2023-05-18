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
