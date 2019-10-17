import sys
p = '/usr/people/ryanf/Desktop/scripts'
if p not in sys.path: sys.path.insert(0,p)
import move2Piv
reload(move2Piv)