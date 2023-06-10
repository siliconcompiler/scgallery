import siliconcompiler
from scgallery.apps import sc_gallery


def test_help(monkeypatch, capfd):
    '''
    Check for details in help output
    '''
    monkeypatch.setattr('sys.argv', ['sc-gallery', '-h'])

    try:
        sc_gallery.main()
    except SystemExit:
        pass

    out, _ = capfd.readouterr()
    assert "Targets: " in out
    assert "Designs: " in out
    assert f"SiliconCompiler {siliconcompiler.__version__}" in out
