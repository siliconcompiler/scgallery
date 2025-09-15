from typing import Callable

from siliconcompiler import Design, Project


class GalleryDesign(Design):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.__setup = {}

    def add_target_setup(self, target: str, func: Callable[[Project], None]) -> None:
        self.__setup.setdefault(target, set()).add(func)

    def process_setups(self, target: str, project: Project) -> None:
        for func in self.__setup.get(target, set()):
            func(project)
