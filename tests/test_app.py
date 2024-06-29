import siliconcompiler
from scgallery.apps import sc_gallery
import pytest
import json
import os


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


def test_glob_args_designs(monkeypatch):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-json', 'test.json',
        '-design', 's*'])

    assert sc_gallery.main() == 0

    assert os.path.exists('test.json')

    with open('test.json') as f:
        config = json.load(f)

    assert all([c['design'] in ('swerv', 'spi') for c in config])


def test_glob_args_multi_designs(monkeypatch):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-json', 'test.json',
        '-design', 's*',
        '-design', 'a*'])

    assert sc_gallery.main() == 0

    assert os.path.exists('test.json')

    with open('test.json') as f:
        config = json.load(f)

    assert all([c['design'] in ('swerv', 'spi', 'aes', 'ariane') for c in config])


def test_glob_args_designs_no_target(monkeypatch):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-json', 'test.json',
        '-design', 'zerosoc*'])

    assert sc_gallery.main() == 0

    assert os.path.exists('test.json')

    with open('test.json') as f:
        config = json.load(f)

    assert len(config) == 2


def test_glob_args_targets(monkeypatch):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-json', 'test.json',
        '-target', 'asap*'])

    assert sc_gallery.main() == 0

    assert os.path.exists('test.json')

    with open('test.json') as f:
        config = json.load(f)

    assert all([c['target'].startswith('asap7_') for c in config])


def test_glob_args_multi_targets(monkeypatch):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', [
        'sc-gallery',
        '-json', 'test.json',
        '-target', 'asap*',
        '-target', 'gf180*'])

    assert sc_gallery.main() == 0

    assert os.path.exists('test.json')

    with open('test.json') as f:
        config = json.load(f)

    assert all(
        [c['target'].startswith('asap7_') or c['target'].startswith('gf180') for c in config])


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
