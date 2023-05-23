import itertools as itt
import re
from collections import UserDict
from math import ceil
from typing import Any

from . import TerminalError


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(itt.islice(it, size)), ())


def tabulate(texts, max_width, gutter="  "):
    ntexts = len(texts)

    def calc_column_widths(item_lengths, ncols):
        nrows = ceil(ntexts / ncols)
        return nrows, [max(i) for i in chunk(item_lengths, nrows)]

    ## Find the maximum number of columns fitting in the terminal width.
    #
    #  We start with 1 column and keep adding columns while the total width
    # remain under the given `max_width` limit
    lengths = [len(txt) for txt in texts]
    widths_per_ncols = []
    for ncols in itt.count(1):
        nrows, widths = calc_column_widths(lengths, ncols)
        total_width = sum(widths) + (ncols - 1) * len(gutter)
        if total_width >= max_width:
            break
        widths_per_ncols.append((ncols, nrows, widths))

    if not widths_per_ncols:
        raise TerminalError(
            f"Terminal width({max_width}) too small"
            f", must have more than x{total_width} columns."
        )

    ncols, nrows, widths = widths_per_ncols[-1]

    def join_row(texts, widths):
        return gutter.join(
            f"{txt:{width}}" for txt, width in zip(texts, widths, strict=True)
        )

    rows = [
        join_row(row_texts, widths)
        for row_texts in itt.zip_longest(*chunk(texts, nrows), fillvalue="")
    ]

    return rows


class Menu(UserDict[str, tuple[str, Any]]):  # {key: (title, value)}
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
        match entry:
            case (str(key), str(title)):
                pass
            case str(title):
                key = str(self.counter)
                self.counter += 1
            case _:
                raise ValueError(f"Invalid menu entry: {entry}")

        key = key.lower()  # Menu execution reads keyboards in lowercase.
        if key in self.data:
            raise AssertionError(f"Dupe key({key} - {title}) over {self.data[key]}")

        self.data[key] = (title, value)

    @property
    def letters(self):
        return "".join([k for k in self.data if not re.match(r"^\d+$", k)])

    def rows(self, max_width, gutter="  "):
        return tabulate(
            [f"{key} - {title}" for key, (title, _) in self.data.items()],
            max_width,
            gutter,
        )
