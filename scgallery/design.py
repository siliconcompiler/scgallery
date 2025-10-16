"""Module for managing gallery designs with target-specific setups."""

from typing import Callable, Union, Optional, Dict, Set

from siliconcompiler import Lint, ASIC
from siliconcompiler import Design


class GalleryDesign(Design):
    """A specialized Design class for managing target-specific setups.

    This class extends the base `Design` to allow for associating
    setup functions with specific targets (e.g., 'freepdk45', 'sky130').
    These setup functions can then be applied to a project to configure it
    for that particular target.
    """

    def __init__(self, name: Optional[str] = None):
        """Initializes a new GalleryDesign instance.

        Args:
            name (str, optional): The name of the design. Defaults to None.
        """
        super().__init__(name)
        self.__setup: Dict[str, Set[Callable[[Union[ASIC, Lint]], None]]] = {}

    def add_target_setup(self, target: str,
                         func: Callable[[Union[ASIC, Lint]], None]) -> None:
        """Adds a setup function for a specific target.

        This method registers a function that will be called to configure a
        project when 'process_setups' is invoked for the given target.

        Args:
            target (str): The name of the target (e.g., 'freepdk45').
            func (Callable[[Union[ASIC, Lint]], None]): The setup function to
                associate with the target. This function should accept a
                project object (ASIC or Lint) as its only argument.
        """
        self.__setup.setdefault(target, set()).add(func)

    def process_setups(self, target: str, project: Union[ASIC, Lint]) -> None:
        """Executes all setup functions for a given target.

        This method retrieves all setup functions registered for the specified
        target and calls each one, passing the provided project object to it.

        Args:
            target (str): The name of the target for which to process setups.
            project (Union[ASIC, Lint]): The project object to be configured by
                the setup functions.
        """
        for func in self.__setup.get(target, set()):
            func(project)
