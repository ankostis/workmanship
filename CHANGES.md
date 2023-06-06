# CHANGES

- See also [TODOs](https://github.com/ankostis/workmanship/wiki/TODO).

## 6 Jun 2023, v0.3.0, user-preferences & scores, better data schema

- FEAT(terminal): polite handling of overflow of terminal size;
  - long lessons don;t crash the app anymore.
- FEAT(Prefs): store user Preferences & GameScores in `~/.workmanship.yml`;  
  - added `s` menu item to store them mid-game;
  - entering **Ctrl+C** skips storing Prefs.
- Feat: Mark visited lessons & selected items in menu.
- REFACT(data): Invert YAML Data schema to be layout-centric;
  - `lessons.yml` is now a list of layouts, each with its own title, words & ngrams.
  - updated `bin/convert_lessons_across_layouts.py` to produce the new schema.
- Feat(data): added COLEMAK-DH ISO/ANSI/EL layouts;
  - Workman(el) selected with greek chars.
- FIX: nchars  to type off-by-1 error ended game prematurely before last line.
- Feat: convertion script produces `lessons.yml` without human intervention;
  - all keys are now mapped.
- fix: read widechars from terminal when typing lessons.
- Doc(readme): improve whatis/ add lessons/similar sites
- feat: have title shown on the top of the lesson screen.

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
  