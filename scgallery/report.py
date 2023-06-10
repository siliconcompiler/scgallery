from jinja2 import Environment, FileSystemLoader
import os
import glob
import base64
import re
import siliconcompiler
from PIL import Image
from io import BytesIO, StringIO
from siliconcompiler.report.report import make_metric_dataframe


def __get_template(template):
    gallery_template = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(gallery_template))
    return env.get_template(template)


def __load_image(path, max_dim=None):
    if os.path.isfile(path):
        im = Image.open(path)

        if max_dim:
            width, height = im.size
            scale_factor = float(max_dim) / max(width, height)
            if scale_factor > 1:
                scale_factor = 1.0
            new_width = int(scale_factor * width)
            new_height = int(scale_factor * height)
            im = im.resize(size=(new_width, new_height))

        with BytesIO() as im_file:
            im.save(im_file, format='webp')
            return base64.b64encode(im_file.getvalue()).decode('utf-8')
    return None


def __get_favicon():
    return __load_image(os.path.join(os.path.dirname(siliconcompiler.__file__),
                                     'data',
                                     'logo.png'),
                        max_dim=32)


def generate_overview(title, images_data, path):
    platforms = set()
    designs = set()
    data = {}
    for image in images_data:
        platforms.add(image['platform'])
        designs.add(image['design'])

        data.setdefault(image['platform'], {})[image['design']] = image
        image['data'] = __load_image(image['path'])

    with open(path, 'w', encoding='utf-8') as wf:
        wf.write(__get_template('overview.html').render(
            title=title,
            favicon=__get_favicon(),
            platforms=sorted(list(platforms)),
            designs=sorted(list(designs)),
            images=data
        ))


def __generate_design_detail(title, chips):
    views = {
        "optimizer": {
            "step": "export",
            "index": "1",
            "path": "reports/images/*.optimizer.png"
        },
        "routing": {
            "step": "export",
            "index": "1",
            "path": "reports/images/*.routing.png"
        },
        "placement": {
            "step": "export",
            "index": "1",
            "path": "reports/images/*.placement.png"
        },
        "clocks": {
            "step": "export",
            "index": "1",
            "path": "reports/images/*.clocks.png"
        },
        "clocktree": {
            "step": "export",
            "index": "1",
            "path": "reports/images/clocktree/*.png",
            "detail_regex": re.compile(r'/([a-zA-Z0-9_]+).png')
        }
    }
    platforms = set()

    design = None

    images_data = {}
    metrics_data = {}
    rules_data = {}

    for chip_data in chips:
        chip = chip_data['chip']
        design = chip.design
        platform = chip.get('asic', 'logiclib')[0]
        platforms.add(platform)

        with StringIO() as f:
            make_metric_dataframe(chip).to_html(f)
            metrics_data[platform] = f.getvalue()

        if chip_data['rules']:
            rules_data[platform] = chip_data['rules']

        view_names = []
        images_data[platform] = {}
        for view, specs in views.items():
            paths = glob.glob(os.path.join(chip._getworkdir(step=specs['step'],
                                                            index=specs['index']),
                                           specs['path']))
            if paths:
                for path in paths:
                    view_name = view
                    if "detail_regex" in specs:
                        match = specs["detail_regex"].search(path)
                        if match:
                            view_name = f'{view} - "{match.group(1)}"'

                    if view_name not in view_names:
                        view_names.append(view_name)
                    images_data[platform][view_name] = __load_image(path)
            else:
                images_data[platform][view] = None

    for platform in list(platforms):
        if all([images_data[platform][view] is None for view in images_data[platform]]):
            platforms.remove(platform)

    return __get_template('design_detailed.html').render(
        title=title,
        favicon=__get_favicon(),
        design=design,
        platforms=sorted(list(platforms)),
        views=view_names,
        images=images_data,
        metrics=metrics_data,
        rules=rules_data)


def generate_details(title, designs, path):
    pages = {}
    for design, design_data in designs.items():
        page_data = __generate_design_detail(title, design_data)
        pages[design] = base64.b64encode(bytes(page_data, 'utf-8')).decode('utf-8')

    design_set = sorted(list(designs.keys()))
    with open(path, 'w', encoding='utf-8') as wf:
        wf.write(__get_template('details.html').render(
            title=title,
            favicon=__get_favicon(),
            initial_design=design_set[0],
            designs=design_set,
            pages=pages))
