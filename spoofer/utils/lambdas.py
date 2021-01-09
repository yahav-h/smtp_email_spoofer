from time import time
from platform import platform
from os import system
from uuid import NAMESPACE_X500, uuid5

__WIN__ = 'win'
__CLS__ = 'cls'
__CLR__ = 'clear'
stamp = lambda: time().__str__()[:10]
isWin = lambda: True if platform().lower().startswith(__WIN__) else False
clearConsole = lambda: system(__CLS__) if isWin() else system(__CLR__)
getUUID = lambda: uuid5(NAMESPACE_X500, stamp()).__str__()