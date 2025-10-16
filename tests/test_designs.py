import pytest

from scgallery import designs


@pytest.mark.parametrize("design_cls",
                         [getattr(designs, design) for design in designs.all_designs()])
def test_check_filepaths(design_cls):
    design = design_cls()
    assert design.check_filepaths()
