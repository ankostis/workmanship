# Workmanship: configurable typing tutor for keyboard layouts

![gh-version](https://img.shields.io/github/v/release/ankostis/workmanship?label=GitHub%20release&include_prereleases&logo=github)
![pypi-version](https://img.shields.io/pypi/v/workmanship?label=PyPi%20release&logo=pypi)
![python-ver](https://img.shields.io/pypi/pyversions/workmanship?label=Python&logo=pypi)
![dev-status](https://img.shields.io/pypi/status/workmanship)
![codestyle](https://img.shields.io/badge/code%20style-black-black)
![License](https://img.shields.io/pypi/l/workmanship)

A curses terminal app to practice typing for various keyboard layouts.

Totally ALPHA, decent training texts only for *dvorak*,
[*workman* layout](https://workmanlayout.org/) was translated from it.

## Usage

Install (prefferably in a *venv*) and launch it like this:

```bash
pip install workmanship
python -m workmanship
```

### Data for layout lessons

Words & ngrams for the keyboard layouts are in `src/workmanship/lessons.yml` file.
The original *dvorak* lessons were extracted with `$ strings dvorak7min`
and were translated into *workman* layout by mapping the relocated keys between
these 2 layouts (see `bin/convert_lessons_across_layouts.py`) - hence
the gibberish ngrams & words in this layout.
 
## History 

Data and idea based on [dvorak7min](https://github.com/yaychris/dvorak7min)
by Dan Wood <danwood@karelia.com>, available in the [original html format](http://www.karelia.com/abcd/).

What started as a search for a personal training tutorial on *workman* layout,
ended up as a python-curses experiment for multiple layouts.

## Similar apps

- Blogpost for [a tkinter tutor](https://hackernoon.com/make-your-own-typing-tutor-app-using-python-6i19734se).
- Excellent site for [training at various layouts & styles](https://www.keybr.com/).
- A [site with speed-tests](https://thetypingcat.com/typing-speed-test) for all layouts.
- ...too many to count (but very few for *workman* layout).
