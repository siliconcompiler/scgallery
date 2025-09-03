import pytest

from scgallery.designs import all_designs


@pytest.mark.parametrize("design_cls",
                         [data for _, data in all_designs().items()])
def test_check_filepaths(design_cls):
    design = design_cls()
    assert design.check_filepaths()
