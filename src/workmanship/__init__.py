"""
An curses terminal app to practice typing into separate lessons.

Data and idea from `dvorak7min <https://github.com/yaychris/dvorak7min>`_
by Dan Wood <danwood@karelia.com>, available in the `original html format
<http://www.karelia.com/abcd/>`_.

Lesson texts configured with included ``src/workmanship/lessons.yml``,
currently for `*workman* layout <https://workmanlayout.org/>`_
converted hastily from dvorak (so gibberish grams & words).

"""
import curses
import functools as fnt
import importlib.resources as pkg_resources
import time
from importlib.metadata import PackageNotFoundError, version

from ruamel.yaml import YAML

from . import textmenus

try:
    __version__ = version("package-name")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
__title__ = "workmanship"
__summary__ = __doc__.splitlines()[0]
__license__ = "GPLv3"
__uri__ = "https://github.com/ankostis/workmanship"


ESC_CHAR = chr(27)
RET_CHAR = "↳"  # chr(0x21B3)

selected_layout = "dvorak"
beep_on_errors = False


def status_bar(win, txt=None, attr=curses.A_NORMAL, offset=0):
    maxy, _ = win.getmaxyx()
    maxy -= 1 + offset
    if txt:
        win.addstr(maxy, 0, txt, attr)
    else:
        win.move(maxy, 0)
    win.clrtoeol()


def cps2wpm(cps):
    # from https://www.yorku.ca/mack/RN-TextEntrySpeed.html
    return cps / 5.0 * 60


def speed_stats(start_time, hits, misses):
    chars_typed = hits + misses
    if not chars_typed:
        return 0, 0, 0, 0

    elapsed = time.time() - start_time
    cps = hits / elapsed
    wpm = cps2wpm(cps)
    hits_ratio = hits / (hits + misses)
    return cps, wpm, hits_ratio, elapsed


def speed_stats_msg(win, total_len, start_time, hits, misses):
    cps, wpm, hits_ratio, elapsed = speed_stats(start_time, hits, misses)
    stats = (
        f"CPS {cps:.2f} WPM {wpm:.2f}"
        f" Hits: {100*hits_ratio:.2f}%"
        f" Misses: {misses}({100*(1-hits_ratio):.2f}%)"
        f" Typed {hits} of {total_len}({100 * hits / total_len:.2f})"
        f" Elapsed: {elapsed:.0f}sec"
    )
    return stats


def dump_stats(win, total_len, start_time, hits, misses):
    stats = speed_stats_msg(win, total_len, start_time, hits, misses)
    status_bar(win, stats, curses.A_REVERSE)


def typing_lesson(win, title, text) -> str:
    text = text.strip()
    assert text
    total_len = len(text)

    lines = text.strip().splitlines()
    lines = [f"{l}\n" for l in lines]

    win.clear()
    curses.noecho()
    curses.curs_set(False)

    win.addstr(0, 0, f"{title}:", curses.A_BOLD)

    start_y = 2
    for y, row in enumerate(lines, start_y):
        # FIXME: breaks if terminal height too small
        win.addstr(y, 0, row[:-1])
        win.addstr(RET_CHAR)
    x = 0
    y = start_y

    status_bar(win, "Press any key to start (ESC to exit)", curses.A_ITALIC)
    if (c := win.getkey()) == ESC_CHAR:
        return

    ok = False
    hits = misses = 0
    start_time = time.time()
    dump_stats(win, start_time, total_len, hits, misses)

    while (c := win.getkey()) != ESC_CHAR:
        row = lines[y - start_y]
        if c == chr(curses.KEY_RESIZE):
            pass
        elif row[x] != c:
            misses += 1
            if beep_on_errors:
                curses.beep()
        else:
            hits += 1
            if x >= 0:
                win.chgat(y, x, 1, curses.A_NORMAL)
            x += 1
            if x >= len(row):
                if y >= len(lines):
                    ok = True
                    break
                y += 1
                x = 0
            win.chgat(y, x, 1, curses.A_REVERSE)

        dump_stats(win, total_len, start_time, hits, misses)
        win.move(y, x)

    status_bar(win, "Press ESC to return to main menu", curses.A_ITALIC, offset=1)
    dump_stats(win, total_len, start_time, hits, misses)
    while (c := win.getkey()) != ESC_CHAR:
        pass

    return ok


def toggle_beep_on_errors(_):
    global beep_on_errors

    beep_on_errors = not beep_on_errors
    return (
        f"Toggled beep on errors, from {not beep_on_errors} -> {beep_on_errors}",
        curses.A_ITALIC,
    )


def select_layout(_, layout):
    global selected_layout

    old_layout = selected_layout
    selected_layout = layout
    statusbar = (f"Switched layout from {old_layout} -> {layout}", curses.A_ITALIC)

    return statusbar


def typing_tutorial(win, layouts):
    min_height = 6  # title, error, menu(x2), status-bar
    promp_y = 0
    titles_y = 2

    curses.set_escdelay(150)
    curses.initscr()

    while True:
        curses.echo()
        curses.curs_set(2)
        maxy, maxx = win.getmaxyx()

        menu = textmenus.Menu(
            (
                "b",
                f"Beep on errors {'(enabled)' if beep_on_errors else '(disabled)'}",
                toggle_beep_on_errors,
            ),
            *[
                (
                    l[0].lower(),
                    f"{l.title()} layout{' (selected)' if l == selected_layout else ''}",
                    fnt.partial(select_layout, layout=l),
                )
                for l in layouts
            ],
            (("q", "Quit"), None),
            layouts[selected_layout],
        )

        # FIXME: use subpad to handle `maxy` overflows
        for y, row in enumerate(menu.rows(maxx), start=titles_y):
            win.addstr(y, 0, row)
            win.clrtoeol()

        win.addstr(
            promp_y, 0, f"Type a lesson number or [{menu.letters}]? ", curses.A_ITALIC
        )
        win.clrtoeol()
        sel = win.getstr().decode("utf-8").lower()

        if sel == "q" or all(i == ESC_CHAR for i in sel):
            break

        if sel not in menu:
            status_bar(win, f"Invalid selection: {sel}", curses.A_BOLD)
        else:
            title, action = menu[sel]
            if callable(action):
                statusbar_args = action(title)
                status_bar(win, *statusbar_args)

            else:
                typing_lesson(win, title, action)
                win.clear()


def load_lessons(yaml_type="safe") -> dict:
    yaml = YAML(typ=yaml_type)  # default, if not specfied, is 'rt' (round-trip)
    with (pkg_resources.files(__package__) / "lessons.yml").open("rt") as f:
        return yaml.load(f)


def main(*args):
    data = load_lessons()
    curses.wrapper(typing_tutorial, data["layouts"])
