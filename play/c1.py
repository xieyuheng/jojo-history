'''
- the challenge 1 -
  write a module called 's1.py'
  to implement a function called 'get_current_module'
  that can pass the following assertion
'''

import s1
import sys

m1 = s1.get_current_module()
m2 = sys.modules[__name__]

assert m1 == m2
