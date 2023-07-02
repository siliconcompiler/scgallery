try:
    from scgallery._version import __version__
except ImportError:
    # This only exists in installations
    __version__ = None

from .gallery import Gallery
from .gallery import main as _main

__all__ = [
    "Gallery",
    "_main"
]
