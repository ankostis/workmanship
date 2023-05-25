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
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

from ruamel.yaml import YAML

from . import TerminalError, textmenus

ESC_CHAR = chr(27)
BREAK_CHAR = chr(3)
RET_CHAR = "↳"  # chr(0x21B3)

# TODO: use `platformdirs` lib to locate user-prefs.
prefs_fpath = Path("~/.workmanship.yml").expanduser()
user_prefs: dict = None  # None is sentinel

selected_layout = ("d", "Dvorak")
beep_on_errors = False


def status_bar(win, txt=None, attr=curses.A_NORMAL, offset=0):
    maxy, maxx = win.getmaxyx()
    maxy -= 1 + offset
    if txt:
        win.addstr(maxy, 0, txt[: maxx - 1], attr)
    else:
        win.move(maxy, 0)
    win.clrtoeol()


def cps2wpm(cps):
    # from https://www.yorku.ca/mack/RN-TextEntrySpeed.html
    return cps / 5.0 * 60


class Stats(NamedTuple):
    cps: float
    wpm: float
    hits_ratio: float
    elapsed: float
    hits: int
    misses: int


def speed_stats(start_time, hits, misses):
    chars_typed = hits + misses
    if not chars_typed:
        return Stats(0, 0, 0, 0, 0, 0)

    elapsed = time.time() - start_time
    cps = hits / elapsed
    wpm = cps2wpm(cps)
    hits_ratio = hits / (hits + misses)

    return Stats(cps, wpm, hits_ratio, elapsed, hits, misses)


def speed_stats_msg(stats, nchars_to_type):
    cps, wpm, hits_ratio, elapsed, hits, misses = stats
    msg = (
        f"CPS {cps:.2f} WPM {wpm:.2f}"
        f" Hits: {100*hits_ratio:.2f}%"
        f" Misses: {misses}({100*(1-hits_ratio):.2f}%)"
        f" Completed {hits} of {nchars_to_type}({100 * hits / nchars_to_type:.1f}%)"
        f" Elapsed: {elapsed:.0f}sec"
    )

    return msg


def dump_stats(win, start_time, hits, misses, nchars_to_type):
    stats = speed_stats(start_time, hits, misses)
    msg = speed_stats_msg(stats, nchars_to_type)
    status_bar(win, msg, curses.A_REVERSE)

    return stats


def dump_lesson(win, lines, start_y):
    for y, row in enumerate(lines, start_y):
        # FIXME: breaks if terminal height too small
        win.addstr(y, 0, row[:-1])
        win.addstr(RET_CHAR)


def run_typing_lesson(win, title, text) -> tuple:
    text = text.strip()
    assert text

    lines = [f"{l.strip()}\n" for l in text.splitlines()]
    nchars_to_type = sum([len(l) for l in lines])

    win.erase()
    curses.noecho()
    curses.curs_set(False)

    win.addstr(0, 0, f"{title}:", curses.A_BOLD)

    start_y = 2
    dump_lesson(win, lines, start_y)

    status_bar(win, "Press any key to start (ESC to exit)", curses.A_ITALIC)
    if (c := win.get_wch()) == ESC_CHAR:
        return

    x = 0
    y = start_y
    ok = False
    hits = misses = 0
    start_time = time.time()
    pause_time = 0  # Used also as a flag if ESC has been pressed.
    stats = dump_stats(win, start_time, hits, misses, nchars_to_type)

    while True:
        c = win.get_wch()
        if y >= start_y + len(lines):
            ok = True
            return stats

        if c == ESC_CHAR:
            if pause_time:
                break  # User abandoned lesson by pressing ESC x2.
            else:
                pause_time = time.time()
                status_bar(
                    win,
                    "Press ESC to return to main menu, any other key to continue",
                    curses.A_ITALIC,
                    offset=1,
                )
        elif pause_time:  # User pressed any key after ESC
            status_bar(win, offset=1)
            start_time += time.time() - pause_time
            pause_time = 0
        else:
            row = lines[y - start_y]
            if c == chr(curses.KEY_RESIZE):  # Does it work?
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
                    y += 1
                    x = 0
                    if y >= start_y + len(lines):
                        status_bar(
                            win,
                            "Press any key to return to main menu",
                            curses.A_ITALIC,
                            offset=1,
                        )
                win.chgat(y, x, 1, curses.A_REVERSE)

        stats = dump_stats(win, start_time, hits, misses, nchars_to_type)
        win.move(y, x)


def toggle_beep_on_errors_cb(_):
    global beep_on_errors

    beep_on_errors = not beep_on_errors
    return (
        f"Toggled beep on errors, from {not beep_on_errors} -> {beep_on_errors}",
        curses.A_ITALIC,
    )


def select_layout_cb(_, layout):
    global selected_layout

    old_layout = selected_layout
    selected_layout = layout
    statusbar = (f"Switched layout from {old_layout} -> {layout}", curses.A_ITALIC)

    return statusbar


def lessons_menu(win, layouts, *, prompt_y=0, titles_y=2) -> bool:
    """Return true for parent loop to exit, false to continue."""

    def mark_selected(txt, flag):
        return (txt, curses.A_BOLD if flag else curses.A_NORMAL)

    menu = textmenus.Menu(
        (
            "b",
            mark_selected(f"Beep on errors", beep_on_errors),
            toggle_beep_on_errors_cb,
        ),
        *[
            (
                key,
                mark_selected(f"{title!r} layout", (key, title) == selected_layout),
                fnt.partial(select_layout_cb, layout=(key, title)),
            )
            for key, title in layouts
        ],
        (("s", "store prefs + scores"), store_user_prefs_cb),
        (("q", "Quit"), None),
        layouts[selected_layout],
    )

    menu.dump_rows(win, titles_y)

    win.addstr(
        prompt_y, 0, f"Type a lesson number or [{menu.letters}]? ", curses.A_ITALIC
    )
    win.clrtoeol()
    sel = win.getstr()
    if not sel or not isinstance(sel, bytes):
        return

    sel = sel.decode("utf-8").lower()

    if sel == "q" or all(i == ESC_CHAR for i in sel):
        return True
    if all(i == BREAK_CHAR for i in sel):
        # Emulate Ctrl+C.
        raise KeyboardInterrupt()

    if sel not in menu:
        status_bar(win, f"Invalid selection: {sel}", curses.A_BOLD)
    else:
        title, action = menu[sel]
        if callable(action):
            statusbar_args = action(title)
            status_bar(win, *(statusbar_args or ()))
        else:
            game_stats = run_typing_lesson(win, title, action)
            update_game_scores(sel, game_stats)
            win.erase()


def typing_tutorial(win, layouts):
    curses.set_escdelay(150)

    while True:
        curses.echo()
        curses.curs_set(2)
        try:
            if lessons_menu(win, layouts):
                break
        except TerminalError as ex:
            win.erase()
            win.addstr(0, 0, str(ex), curses.A_BOLD | curses.A_ITALIC)
            win.clrtoeol()
            win.getkey()
            win.erase()


def load_lessons(yaml_type="safe") -> dict:
    yaml = YAML(typ=yaml_type)  # default, if not specfied, is 'rt' (round-trip)
    with (pkg_resources.files(__package__) / "lessons.yml").open("rt") as f:
        return yaml.load(f)


def load_user_prefs(avail_layouts) -> dict:
    global user_prefs, beep_on_errors, selected_layout

    yaml = YAML(typ="rt")
    try:
        with open(prefs_fpath, "rt") as f:
            prefs = yaml.load(f)
    except FileNotFoundError:
        pass

    if not prefs:
        prefs = {}

    # TODO: use custocm YAML loader to convert yaml <-> prefs
    prefs["game_scores"] = defaultdict(list, prefs.get("game_scores") or {})
    beep_on_errors = prefs.get("beep_on_errors", False)
    layout = prefs.get("selected_layout")
    if layout:
        layout = tuple(layout)
        if layout in avail_layouts:
            selected_layout = layout

    user_prefs = prefs


def store_user_prefs(yaml_type="rt") -> dict:
    prefs = user_prefs

    prefs["beep_on_errors"] = beep_on_errors
    prefs["selected_layout"] = selected_layout
    prefs["game_scores"] = dict(prefs["game_scores"])

    tmp_fpath = prefs_fpath.with_suffix(".tmp")

    yaml = YAML(typ=yaml_type)
    with open(tmp_fpath, "wt") as f:
        yaml.dump(user_prefs, f)

    try:
        prefs_fpath.rename(prefs_fpath.with_suffix(".bak.yml"))
    except FileNotFoundError:
        pass
    try:
        tmp_fpath.rename(prefs_fpath)
    except FileNotFoundError:
        pass


def store_user_prefs_cb(_):
    store_user_prefs()
    return (
        f"User preferences stored in '{prefs_fpath}'.",
        curses.A_ITALIC,
    )


def update_game_scores(sel, stats: Stats | None):
    if stats:
        user_prefs["game_scores"][sel].append(stats._asdict())


def have_game_scores():
    return bool(user_prefs["game_scores"])


def main(*args):
    data = load_lessons()
    layouts = data["layouts"]
    load_user_prefs(layouts)
    try:
        curses.wrapper(typing_tutorial, layouts)
    except KeyboardInterrupt:
        if have_game_scores():
            raise SystemExit("Ctrl+C, exit without saving prefs")
    else:
        if have_game_scores():
            store_user_prefs()
