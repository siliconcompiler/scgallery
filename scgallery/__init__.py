try:
    from scgallery._version import __version__
except ImportError:
    # This only exists in installations
    __version__ = None

from .gallery import Gallery
from .design import GalleryDesign

__all__ = [
    "Gallery",
    "GalleryDesign"
]
