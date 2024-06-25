import siliconcompiler
from scgallery.apps import sc_gallery
import pytest


def test_help(monkeypatch, capfd):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', ['sc-gallery', '-h'])

    with pytest.raises(SystemExit):
        sc_gallery.main()

    out, _ = capfd.readouterr()
    assert "Targets: " in out
    assert "Designs: " in out
    assert f"SiliconCompiler {siliconcompiler.__version__}" in out


@pytest.mark.eda
def test_end2end_gcd(monkeypatch):
    '''
    Check if app runs through
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-design', 'gcd',
        '-target', 'freepdk45_demo',
        '-skip_rules', 'runtime*'])

    assert sc_gallery.main() == 0
