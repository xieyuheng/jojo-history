import inspect
import sys

get_current_module = lambda: sys.modules[inspect.stack()[1].frame.f_globals['__name__']]
