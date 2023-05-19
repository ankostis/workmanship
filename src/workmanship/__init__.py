"""
An curses terminal app to practice typing into separate lessons.

Data and idea from `dvorak7min <https://github.com/yaychris/dvorak7min>`_
by Dan Wood <danwood@karelia.com>, available in the `original html format
<http://www.karelia.com/abcd/>`_.

Lesson texts configured with included ``src/workmanship/lessons.yml``,
currently for `*workman* layout <https://workmanlayout.org/>`_
converted hastily from dvorak (so gibberish grams & words).

"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("package-name")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
__title__ = "workmanship"
__summary__ = __doc__.splitlines()[0]
__license__ = "GPLv3"
__uri__ = "https://github.com/ankostis/workmanship"


class TerminalError(Exception):
    pass
