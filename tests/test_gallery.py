import os
import pytest

import siliconcompiler

from scgallery import Gallery
from scgallery.designs import all_designs


def test_has_name():
    assert Gallery(name="testing").has_name


def test_has_no_name():
    assert not Gallery().has_name


def test_name():
    gallery = Gallery(name="testing")

    assert gallery.name == "testing"


def test_no_name():
    gallery = Gallery()

    assert gallery.name is None


def test_path_default():
    gallery = Gallery()

    default_path = os.path.abspath(os.path.join(os.getcwd(),
                                                'gallery',
                                                siliconcompiler.__version__))

    assert gallery.path == default_path


def test_path_default_with_name():
    gallery = Gallery(name="testing")

    default_path = os.path.abspath(os.path.join(os.getcwd(),
                                                'gallery-testing',
                                                siliconcompiler.__version__))

    assert gallery.path == default_path


def test_path_default_with_path():
    path = os.path.abspath('testing')
    gallery = Gallery(path=path)

    assert gallery.path == path


def test_set_path():
    path = os.path.abspath('testing')
    gallery = Gallery()
    gallery.set_path(path)

    assert gallery.path == path


def test_add_target():
    gallery = Gallery()

    assert "testing" not in gallery.get_targets()
    gallery.add_target("testing", None)
    assert "testing" in gallery.get_targets()


def test_remove_target():
    gallery = Gallery()

    gallery.add_target("testing", None)
    assert "testing" in gallery.get_targets()
    gallery.remove_target("testing")
    assert "testing" not in gallery.get_targets()


def test_remove_target_not_found():
    gallery = Gallery()

    assert "testing" not in gallery.get_targets()
    gallery.remove_target("testing")
    assert "testing" not in gallery.get_targets()


def test_default_targets():
    gallery = Gallery()

    assert gallery.get_targets() == ["freepdk45_demo",
                                     "skywater130_demo",
                                     "asap7_demo",
                                     "gf180_demo",
                                     "asap7_asap7sc7p5t_lvt",
                                     "asap7_asap7sc7p5t_slvt",
                                     "gf180_gf180mcu_fd_sc_mcu7t5v0"]


def test_add_design():
    gallery = Gallery()

    assert "testing" not in gallery.get_designs()
    gallery.add_design("testing", None)
    assert "testing" in gallery.get_designs()


def test_remove_design_not_found():
    gallery = Gallery()

    assert "testing" not in gallery.get_designs()
    gallery.remove_design("testing")
    assert "testing" not in gallery.get_designs()


def test_remove_design():
    gallery = Gallery()

    assert "aes" in gallery.get_designs()
    gallery.remove_design("aes")
    assert "aes" not in gallery.get_designs()


@pytest.mark.parametrize("design_name,design_data",
                         [(name, data) for name, data in all_designs().items()])
def test_get_design(design_name, design_data):
    gallery = Gallery()

    info = gallery.get_design(design_name)
    assert info['module'] is design_data["module"]
    assert info['rules'] == design_data["rules"]


def test_get_designs():
    gallery = Gallery()

    assert gallery.get_designs() == list(all_designs().keys())


def test_set_remote():
    gallery = Gallery()

    with open('testing.json', 'w') as f:
        f.write('testfile')

    gallery.set_remote('testing.json')

    assert gallery.is_remote


def test_unset_remote():
    gallery = Gallery()

    with open('testing.json', 'w') as f:
        f.write('testfile')

    gallery.set_remote('testing.json')
    assert gallery.is_remote
    gallery.set_remote(None)
    assert not gallery.is_remote


def test_set_remote_invalid_file():
    gallery = Gallery()

    with pytest.raises(FileNotFoundError):
        gallery.set_remote("file not found")


def test_set_unset_resume():
    gallery = Gallery()

    assert not gallery.is_resume
    gallery.set_resume(True)
    assert gallery.is_resume
    gallery.set_resume(False)
    assert not gallery.is_resume


def test_set_unset_strict():
    gallery = Gallery()

    assert gallery.is_strict
    gallery.set_strict(False)
    assert not gallery.is_strict
    gallery.set_strict(True)
    assert gallery.is_strict


def test_add_design_rules():
    gallery = Gallery()

    with open('testing.json', 'w') as f:
        f.write('testfile')

    gallery.add_design_rule('aes', 'testing.json')
    assert 'testing.json' in gallery.get_design_rules('aes')


def test_add_design_rules_bad_path():
    gallery = Gallery()

    with pytest.raises(FileNotFoundError):
        gallery.add_design_rule('aes', 'testing.json')


def test_clear_design_rules():
    gallery = Gallery()

    with open('testrules.json', 'w') as f:
        f.write('test')

    gallery.add_design_rule('aes', 'testrules.json')
    assert len(gallery.get_design_rules('aes')) != 0
    gallery.clear_design_rules('aes')
    assert len(gallery.get_design_rules('aes')) == 0


@pytest.mark.parametrize("design_name", [*list(all_designs().keys())])
def test_get_design_setup_design_none(design_name):
    gallery = Gallery()

    assert len(gallery.get_design_setup(design_name)) == 0


def test_add_design_setup():
    gallery = Gallery()

    def testing_setup(chip):
        pass

    gallery.add_design_setup('aes', testing_setup)
    assert testing_setup in gallery.get_design_setup('aes')
    assert testing_setup not in gallery.get_design_setup('jpeg')


def test_set_jobname_suffix():
    gallery = Gallery()
    gallery.set_jobname_suffix('testing')
