import os
import sys


def init_zerosoc():
    path = os.path.join(os.path.dirname(__file__), 'zerosoc')
    if path not in sys.path:
        sys.path.append(path)
