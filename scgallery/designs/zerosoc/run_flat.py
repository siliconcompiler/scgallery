import os

def run():
    chip = build.build_top_flat(verify=False,
                                remote=True,
                                resume=False,
                                floorplan=False)
    png = os.path.join(chip.get('option', 'builddir'), f'{chip.design}.png')
    if os.path.isfile(png):
        return png
    return None


if __name__ == "__main__":
    print('PNG file:', run())
