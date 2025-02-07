#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import tempfile
import zipfile

from PIL import Image
from siliconcompiler import Chip, Schema
from scgallery import designs as gallery_designs


def __format_totalarea(value):
    return f"{int(round(value))} μm²"


def __format_fmax(value):
    value = value / 1e6
    return f"{value:.1f} MHz"


METRICS = [
    ("write.views", 0, "totalarea", __format_totalarea),
    ("write.views", 0, "fmax", __format_fmax)
]

LINK_BASE = "https://github.com/siliconcompiler/scgallery/tree/main/scgallery/designs/"


def __extract_zip(zip_file, workdir):
    os.makedirs(workdir, exist_ok=True)

    with zipfile.ZipFile(zip_file) as f:
        f.extractall(path=workdir)


def process_images(img_file, workdir):
    image_dir = os.path.join(workdir, 'images')
    _, ext = os.path.splitext(img_file)
    if ext == "":
        image_dir = img_file
    if ext == ".zip":
        __extract_zip(img_file, image_dir)

    base_image_dir = image_dir
    base_image_dir = os.path.join(base_image_dir, os.listdir(base_image_dir)[0])

    images = {}
    for file in os.listdir(base_image_dir):
        name, ext = os.path.splitext(file)
        if ext == ".png":
            images[name] = {
                "path": os.path.join(base_image_dir, file),
                "relpath": os.path.relpath(os.path.join(base_image_dir, file), image_dir)
            }
    return images


def process_manifests(manifest_file, workdir):
    manifest_dir = os.path.join(workdir, 'manifests')
    _, ext = os.path.splitext(manifest_file)
    if ext == "":
        manifest_dir = manifest_file
    if ext == ".zip":
        __extract_zip(manifest_file, manifest_dir)

    data = []

    designs = gallery_designs.all_designs()

    for design in os.listdir(manifest_dir):
        design_path = os.path.join(manifest_dir, design)
        for variant in os.listdir(design_path):
            if variant == "job0":
                continue

            variant_path = os.path.join(design_path, variant)

            manifest = os.path.join(variant_path, f"{design}.pkg.json")
            if not os.path.exists(manifest):
                manifest = None

            design_data = {
                "design": design,
                "variant": variant,
                "manifest": manifest,
                "success": "yes",
                "description": "",
                "pdk": None,
                "mainlib": None,
                "image": None,
                "title": variant,
                "link": None
            }
            for step, index, metric, fmt in METRICS:
                design_data[f"metric-{metric}"] = None
            data.append(design_data)

            if design in designs:
                design_data["link"] = LINK_BASE + \
                    os.path.relpath(designs[design]["module"].__file__,
                                    os.path.dirname(gallery_designs.__file__))
                desc = designs[design]["module"].__doc__
                if not desc:
                    desc = ""
                desc = desc.splitlines()
                while len(desc) > 0 and not desc[0]:
                    desc = desc[1:]
                while len(desc) > 0 and not desc[-1]:
                    desc = desc[:-1]
                design_data["description"] = "\n".join(desc)

            if not manifest:
                design_data["success"] = "no"

                if variant.startswith("job0_"):
                    # Attempt to get pdk and mainlib
                    pdk, *mainlib = variant[5:].split("_")
                    if not pdk:
                        print(mainlib)
                        pdk, mainlib = mainlib

                    design_data["pdk"] = pdk
                    design_data["mainlib"] = "_".join(mainlib)
                    design_data["title"] = design_data["pdk"]
                continue

            schema = Schema(manifest=manifest)

            for step, index, metric, fmt in METRICS:
                value = schema.get('metric', metric, step=step, index=index)
                if value is not None:
                    value = fmt(value)
                design_data[f"metric-{metric}"] = value

            for step, index in [("write.views", "0"), ("write.gds", "0")]:
                if schema.get('record', 'status', step=step, index=index) != "success":
                    design_data["success"] = "no"

            design_data["pdk"] = schema.get('option', 'pdk')
            design_data["mainlib"] = schema.get('asic', 'logiclib')[0]
            design_data["title"] = design_data["pdk"]

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Helper to generate a summary json",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--output",
        default="summary",
        help="Output folder",
        metavar="<dir>")

    parser.add_argument(
        "--images",
        help="Path to image",
        metavar="<file/dir>",
        required=True)

    parser.add_argument(
        "--manifests",
        help="Path to manifest",
        metavar="<file/dir>",
        required=True)

    parser.add_argument(
        "--merge",
        help="Merge with exisiting data",
        action="store_true")

    parser.add_argument(
        "--save_manifest",
        help="Preserve manufest data",
        action="store_true")

    args = parser.parse_args()

    if not args.merge:
        try:
            shutil.rmtree(args.output)
        except FileNotFoundError:
            pass

    with tempfile.TemporaryDirectory() as workdir:
        images = process_images(args.images, workdir)
        data = process_manifests(args.manifests, workdir)

        for dat in data:
            image_name = f"{dat['design']}_{dat['variant']}"
            if image_name in images:
                img_path = os.path.join(args.output,
                                        os.path.basename(images[image_name]["relpath"]))
                img_path, _ = os.path.splitext(img_path)
                img_path += ".webp"
                os.makedirs(os.path.dirname(img_path), exist_ok=True)

                # Convert an image to WebP
                img = Image.open(images[image_name]["path"])
                img.save(img_path, "WEBP")

                dat["image"] = os.path.relpath(img_path, args.output)

            if dat["manifest"] and args.save_manifest:
                chip = Chip("")
                chip.schema = Schema(manifest=dat["manifest"])
                manifest_path = os.path.join(args.output,
                                             os.path.basename(dat["manifest"]) + ".gz")
                chip.write_manifest(manifest_path)
                dat["manifest"] = os.path.relpath(manifest_path, args.output)
            else:
                dat["manifest"] = None

        if args.merge:
            with open(os.path.join(args.output, "summary.json")) as f:
                merge_data = json.load(f)
            data = [*merge_data, *data]

        # Filter
        for variant in ("job0_gf180_gf180mcu_fd_sc_mcu7t5v0",):
            data = [dat for dat in data if dat["variant"] != variant]

        with open(os.path.join(args.output, "summary.json"), 'w') as f:
            json.dump(data, f, indent=2)
