import os

import siliconcompiler


def get_image_directory():
    image_dir = os.path.join(os.path.dirname(__file__), 'images', siliconcompiler.__version__)
    os.makedirs(image_dir, exist_ok=True)
    return image_dir


def get_designs_directory():
    design_dir = os.path.join(os.path.dirname(__file__), 'designs')
    return os.path.abspath(design_dir)
