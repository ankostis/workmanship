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

from ruamel.yaml import YAML

from . import TerminalError, textmenus

ESC_CHAR = chr(27)
RET_CHAR = "↳"  # chr(0x21B3)


selected_layout = ("d", "dvorak")
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


def run_typing_lesson(win, title, text) -> str:
    text = text.strip()
    assert text
    total_len = len(text)

    lines = text.strip().splitlines()
    lines = [f"{l}\n" for l in lines]

    win.erase()
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
    if (c := win.get_wch()) == ESC_CHAR:
        return

    ok = False
    hits = misses = 0
    start_time = time.time()
    pause_time = 0  # Used also as a flag if ESC has been pressed.
    dump_stats(win, start_time, total_len, hits, misses)

    while True:
        c = win.get_wch()

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
                    if y > len(lines):
                        ok = True
                        break
                    y += 1
                    x = 0
                win.chgat(y, x, 1, curses.A_REVERSE)

        dump_stats(win, total_len, start_time, hits, misses)
        win.move(y, x)

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


def lessons_menu(win, layouts, *, prompt_y=0, titles_y=2) -> bool:
    def mark_selected(k, t):
        return (
            f"{t.title()!r} layout{' (selected)' if (k, t) == selected_layout else ''}"
        )

    menu = textmenus.Menu(
        (
            "b",
            f"Beep on errors {'(enabled)' if beep_on_errors else '(disabled)'}",
            toggle_beep_on_errors,
        ),
        *[
            (
                key,
                mark_selected(key, title),
                fnt.partial(select_layout, layout=(key, title)),
            )
            for key, title in layouts
        ],
        (("q", "Quit"), None),
        layouts[selected_layout],
    )

    # FIXME: use subpad to handle `maxy` overflows
    maxy, maxx = win.getmaxyx()
    menu_rows = menu.rows(maxx)
    need_height = titles_y + len(menu_rows) + 2  # +2 for emptyline + statusbar
    if need_height >= maxy:
        raise TerminalError(
            f"Terminal height({maxy}) too small"
            f", must have more than x{need_height} rows or more than  x{maxx} columns."
        )
    for y, row in enumerate(menu_rows, start=titles_y):
        win.addstr(y, 0, row)
        win.clrtoeol()

    win.addstr(
        prompt_y, 0, f"Type a lesson number or [{menu.letters}]? ", curses.A_ITALIC
    )
    win.clrtoeol()
    sel = win.getstr().decode("utf-8").lower()
    if not sel:
        return

    if sel == "q" or all(i == ESC_CHAR for i in sel):
        return True

    if sel not in menu:
        status_bar(win, f"Invalid selection: {sel}", curses.A_BOLD)
    else:
        title, action = menu[sel]
        if callable(action):
            statusbar_args = action(title)
            status_bar(win, *statusbar_args)
        else:
            run_typing_lesson(win, title, action)
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
            win.addstr(0, 0, str(ex), curses.A_BOLD)  # | curses.A_ITALIC)
            win.getkey()


def load_lessons(yaml_type="safe") -> dict:
    yaml = YAML(typ=yaml_type)  # default, if not specfied, is 'rt' (round-trip)
    with (pkg_resources.files(__package__) / "lessons.yml").open("rt") as f:
        return yaml.load(f)


def main(*args):
    data = load_lessons()
    curses.wrapper(typing_tutorial, data["layouts"])
