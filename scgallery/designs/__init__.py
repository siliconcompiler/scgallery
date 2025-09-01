from os import path

from .heartbeat.heartbeat import HeartbeatDesign

__designs = (
    HeartbeatDesign,
)


__name_map = {
}


__designs_nonstandard = {
}


def all_designs():
    designs = {}
    for design in __designs:
        if not design:
            continue
        if design in __name_map:
            name = __name_map[design]
        else:
            name = design().name

        designs[name] = design

    for name, design in __designs_nonstandard.items():
        if not design:
            continue

        designs[name] = design

    return designs


__all__ = [
    *all_designs().keys()
]


def root():
    return path.dirname(path.abspath(__file__))
