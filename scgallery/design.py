from typing import Callable, Union

from siliconcompiler import Lint, ASIC
from siliconcompiler import Design


class GalleryDesign(Design):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.__setup = {}

    def add_target_setup(self, target: str,
                         func: Callable[[Union[ASIC, Lint]], None]) -> None:
        self.__setup.setdefault(target, set()).add(func)

    def process_setups(self, target: str, project: Union[ASIC, Lint]) -> None:
        for func in self.__setup.get(target, set()):
            func(project)
