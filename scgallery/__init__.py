try:
    from scgallery._version import __version__
except ImportError:
    # This only exists in installations
    __version__ = None

from .gallery import Gallery

__all__ = [
    "Gallery",
]
