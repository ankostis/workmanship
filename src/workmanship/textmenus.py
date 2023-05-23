import itertools as itt
import re
from collections import UserDict
from math import ceil
from typing import Any

from . import TerminalError


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(itt.islice(it, size)), ())


def tabulate(
    win,
    styled_texts: list[tuple[str, int]],
    starty,
    *,
    gutter="  ",
    bottom_clearance=2,  # +2 for emptyline + statusbar
):
    maxy, maxx = win.getmaxyx()
    ntexts = len(styled_texts)

    def calc_column_widths(item_lengths, ncols):
        nrows = ceil(ntexts / ncols)
        return nrows, [max(i) for i in chunk(item_lengths, nrows)]

    ## Find the maximum number of columns fitting in the terminal width.
    #
    #  We start with 1 column and keep adding columns while the total width
    # remain under terminals width
    lengths = [len(txt) for txt, _style in styled_texts]
    widths_per_ncols = []
    for ncols in itt.count(1):
        nrows, widths = calc_column_widths(lengths, ncols)
        total_width = sum(widths) + (ncols - 1) * len(gutter)
        if total_width >= maxx:
            break
        widths_per_ncols.append((ncols, nrows, widths))

    if not widths_per_ncols:
        raise TerminalError(
            f"Terminal width({maxx}) too small"
            f", must have more than x{total_width} columns."
        )

    ncols, nrows, widths = widths_per_ncols[-1]

    need_height = starty + nrows + bottom_clearance

    if need_height >= maxy:
        raise TerminalError(
            f"Terminal height({maxy}) too small"
            f", must have more than x{need_height} rows or more than  x{maxx} columns."
        )

    def dump_row(texts: list[tuple[str, int]], widths):
        gutter2 = ""
        for (txt, style), width in zip(texts, widths, strict=True):
            win.addstr(gutter2)
            win.addstr(f"{txt:{width}}", style)
            win.clrtoeol()
            gutter2 = gutter

    # TODO: use subpad to handle `maxy` overflows
    for y, row_texts in enumerate(
        itt.zip_longest(*chunk(styled_texts, nrows), fillvalue=("", 0)), start=starty
    ):
        win.move(y, 0)
        dump_row(row_texts, widths)


class Menu(UserDict[str, tuple[str, Any]]):  # {key: (title, value)}
    """
    A Menu is instanciated with a list of menu-items and one or more dicts.

    Menu-item syntax:

    ```txt
    title: str
    title: str, value
    (title: str, style: int), value
    key: str, title: str, value
    key: str, (title: str, style: int), value
    ``

    Menu-items constructed out of a dicts map dict-keys as menu-item *entries*
    (ie. `key`, `title`, `style`), and dict-values to menu-item values.
    """

    def __init__(self, *items, **kw) -> dict[str, tuple[str, Any]]:
        super().__init__()
        self.counter = 1

        def item2records(item) -> list[tuple[str | tuple[str, str], Any]]:
            match item:
                case dict():
                    return item.items()
                case key, title, value:
                    return [((key, title), value)]
                case entry, value:
                    return [(entry, value)]
                case _:
                    return [(item, None)]

        # Intermediate structure accepting menu titles w/ or w/o keys ("entries").
        item_records: list[tuple[str | tuple[str, str], Any]] = [
            (entry, value)
            for item in [*items, kw]
            for entry, value in item2records(item)
        ]

        for entry, v in item_records:
            self.__setitem__(entry, v)

    def __setitem__(self, entry, value=None):
        style = 0
        match entry:
            case str(key), str(title):
                pass
            case str(key), (str(title), int(style)):
                pass
            case str(title):
                key = str(self.counter)
                self.counter += 1
            case str(title), int(style):
                key = str(self.counter)
                self.counter += 1
            case _:
                raise ValueError(f"Invalid menu entry: {entry}")

        key = key.lower()  # Menu execution reads keyboards in lowercase.
        if key in self.data:
            raise AssertionError(f"Dupe key({key} - {title}) over {self.data[key]}")

        self.data[key] = ((title, style), value)

    @property
    def letters(self):
        return "".join([k for k in self.data if not re.match(r"^\d+$", k)])

    @property
    def labels(self) -> list[tuple[str, int]]:
        return [
            (f"{key} - {title}", style)
            for key, ((title, style), _) in self.data.items()
        ]

    def dump_rows(self, win, starty, gutter="  "):
        tabulate(win, self.labels, starty, gutter=gutter)
