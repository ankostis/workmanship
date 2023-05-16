"""
An curses terminal app to practice typing into separate lessons.

Data and idea from `dvorak7min <https://github.com/yaychris/dvorak7min>`_
by Dan Wood <danwood@karelia.com>, available in the `original html format
<http://www.karelia.com/abcd/>`_.

Launch it with:

    python -m workmanship

Lesson texts configured with included ``src/workmanship/lessons.yml``,
currently for `*workman* layout <https://workmanlayout.org/>`_
converted hastily from dvorak (so gibberish grams & words).

"""
import curses
import importlib.resources as pkg_resources
import time
from pathlib import Path

from ruamel.yaml import YAML

import workmanship

KEY_CHAR = chr(27)
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
    if (c := win.getkey()) == KEY_CHAR:
        return

    ok = False
    hits = misses = 0
    start_time = time.time()
    dump_stats(win, start_time, total_len, hits, misses)

    while (c := win.getkey()) != KEY_CHAR:
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
    while (c := win.getkey()) != KEY_CHAR:
        pass

    return ok


def typing_tutorial(win, layouts):
    global beep_on_errors, selected_layout

    min_height = 6  # title, error, menu(x2), status-bar
    promp_y = 0
    err_y = 1
    titles_y = 2

    curses.set_escdelay(150)
    curses.initscr()
    maxy, maxx = win.getmaxyx()
    if maxy < min_height:
        raise SystemExit(f"Terminal height too small (< {min_height} rows)")

    while True:
        curses.echo()
        curses.curs_set(2)
        maxy, _ = win.getmaxyx()
        last_y = maxy - 4  # -1 win's last row, -1 status bar, -1 for last item

        titles = {l[0]: l for l in layouts}
        for j, (tkey, title) in enumerate(titles.items()):
            win.addstr(
                titles_y + j,
                0,
                f"{tkey}: {title} {'(selected)' if title == selected_layout else ''}",
            )
            win.clrtoeol()
        j += 1
        unfit_title = 0
        lessons = layouts[selected_layout]
        for i, title in enumerate(lessons):
            y = titles_y + j + i
            if y >= last_y:
                if not unfit_title:
                    unfit_title = i
            else:
                win.addstr(y, 0, f"{i+1}: {title}")
        if unfit_title:
            win.addstr(last_y, 0, f"{unfit_title}...{i}: {title}")

        win.addstr(
            promp_y,
            0,
            f"Type a lesson number or {'no-' if beep_on_errors else ''}[B]eep on errors"
            f", [Q]uit: ",
            curses.A_ITALIC,
        )
        win.clrtoeol()
        sel = win.getstr().decode("utf-8").lower()

        if sel == "q" or all(i == KEY_CHAR for i in sel):
            break

        if sel == "b":
            beep_on_errors = ~beep_on_errors
            win.addstr(
                err_y,
                0,
                f"Beep set to {'ON' if beep_on_errors else 'OFF'}",
                curses.A_BOLD,
            )
            win.clrtoeol()
        elif sel in titles:
            selected_layout = titles[sel]
        else:
            try:
                lesson = int(sel)

                title, text = list(lessons.items())[lesson - 1]
            except (ValueError, IndexError):
                win.addstr(err_y, 0, f"Invalid selection!", curses.A_BOLD)
            else:
                typing_lesson(win, title, text)
                win.clear()


def load_lessons(yaml_type="safe") -> dict:
    yaml = YAML(typ=yaml_type)  # default, if not specfied, is 'rt' (round-trip)
    with (pkg_resources.files(workmanship) / "lessons.yml").open("rt") as f:
        return yaml.load(f)


def main(*args):
    data = load_lessons()
    curses.wrapper(typing_tutorial, data["layouts"])
