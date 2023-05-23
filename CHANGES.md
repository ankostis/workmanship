# CHANGES

- See also [TODOs](https://github.com/ankostis/workmanship/wiki/TODO).

## 23 May 2023: v0.2.1

- FIX: was skipping last typing row of lessons.
- fix: was clearing screen w/ menu replies.
- FEAT: Pause lesson when ESC pressed, any key to continue, 
  without accumulating time.
- FEAT: Workman Greek(EL) layout (converted from dvorak).
- feat: read widechar while typing lessons run (to support other encodings).
- break: layouts dict in yaml MUST now specify their selection-key,
  like `key, title (so stopped deducing key from the 1t title-char).
- feat(preproc): include also `aA` key in the conversion maps.

## 20 May 2023: v0.1.0

- Fix: handle terminal resizing; menu notifies when term too small 
  (stopped not crashing).
  - BUG: long lessons still don't fit when terminal too small.
- FEAT: +Menu class to tabulate items and associate callables as item-values.
- refact: exract code out of package as own modules.
- TEST: Pytest setup, yet only for Menu.

## 16 May 2023: v0.0.0

- 15 May 2023: started to parse strings out of `dvorac7min` executable for fun,
  convert them into a `yaml` file readand use it by a rudimentary *curses* program.
  