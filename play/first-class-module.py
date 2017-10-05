import types
import sys

m1 = types.ModuleType('module1')

setattr(m1, 'x', 1)

sys.modules['module1'] = m1

from module1 import x
