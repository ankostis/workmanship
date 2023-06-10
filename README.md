# Workmanship: configurable typing tutor for keyboard layouts

![gh-version](https://img.shields.io/github/v/release/ankostis/workmanship?label=GitHub%20release&include_prereleases&logo=github)
![pypi-version](https://img.shields.io/pypi/v/workmanship?label=PyPi%20release&logo=pypi)
![python-ver](https://img.shields.io/pypi/pyversions/workmanship?label=Python&logo=pypi)
![dev-status](https://img.shields.io/pypi/status/workmanship)
![codestyle](https://img.shields.io/badge/code%20style-black-black)
![License](https://img.shields.io/pypi/l/workmanship)

A curses terminal app to practice typing for your custom keyboard layouts
(eg. a Greek [*Colemak-DH*](https://colemakmods.github.io/mod-dh/)).

Totally ALPHA, meaningful training words and n-grams only for *dvorak*,
ie. [*workman*](https://workmanlayout.org/) & *colemak-ish* layouts
were translated from it.

## Usage

Install (prefferably in a *venv*) and launch it like this:

```bash
pip install workmanship
workmanship
```
![main menu](./docs/workmanship-menu.png)

### Customize layout lessons

Words & ngrams for the keyboard layouts are in `src/workmanship/lessons.yml` file.
The original *dvorak* lessons were extracted with `$ strings dvorak7min`
and were translated into *workman* layout by mapping the relocated keys between
these 2 layouts (see `bin/convert_lessons_across_layouts.py`) - hence
the gibberish ngrams & words in this layout.

As of v0.3.0, these layouts have been defined:

- Dvorak
- Workman (en, el)
- ColemakDH(en, el) for both ISO and ANSI keyboards
 
## History & similar apps or sites

Data and idea based on [dvorak7min](https://github.com/yaychris/dvorak7min)
by Dan Wood <danwood@karelia.com>, available in the [original html format](http://www.karelia.com/abcd/).

What started as a search for a personal training tutorial on *workman* layout,
ended up as a python *curses* excersize for multiple layouts with score statistics.

But it is, and will remain, an excersize in futility,
given the plethora of online typing tutors and games:

- Blogpost for [a tkinter tutor](https://hackernoon.com/make-your-own-typing-tutor-app-using-python-6i19734se).
- [keybr.com](https://www.keybr.com/): smart training at various layouts & styles.
- A [site with speed-tests](https://thetypingcat.com/typing-speed-test) for all layouts.
- [typing.io](https://typing.io/): training on various programming languages.
- [keyboard-design.com](https://www.keyboard-design.com/internet-letter-layout-db.html):
  a database of layouts ans their statistics.
- [Dreymar's Big Bag of Tricks](https://dreymar.colemak.org/ergo-mods.html#curl-dh):
  an insighgful collection of mods & software for *colemak* & *colemak-DH*.    
- [Colemak's Mods](https://colemakmods.github.io/mod-dh/)
  & [Ergonomic Mods](http://colemakmods.github.io/ergonomic-mods/)
- ...too many to count (but very few for *workman* layout).
