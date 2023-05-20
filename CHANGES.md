# CHANGES

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
  