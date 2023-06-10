import importlib
import inspect
import sys

from scgallery import Gallery


# Need to load file from cli
# Find class which is a Gallery class
def __process_cli_class(name):
    module = importlib.import_module(name)
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if obj is Gallery:
                continue
            elif issubclass(obj, Gallery):
                return obj
    return None


def main():
    cli_class = None
    if "-gallery" in sys.argv:
        idx = sys.argv.index('-gallery')
        if len(sys.argv) > idx + 1:
            cli_class = __process_cli_class(sys.argv[idx + 1])

    if not cli_class:
        cli_class = Gallery
    return cli_class.main()


if __name__ == "__main__":
    sys.exit(main())
