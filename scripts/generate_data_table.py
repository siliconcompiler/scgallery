#!/usr/bin/env python3

import argparse
import json
import os
import tempfile
import zipfile

from PIL import Image
from siliconcompiler import Chip, Schema


METRICS = [
    ("write.views", 0, "totalarea"),
    ("write.views", 0, "fmax")
]


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
                "image": None
            }
            for step, index, metric in METRICS:
                design_data[f"metric-{metric}"] = None
            data.append(design_data)

            if not manifest:
                design_data["success"] = "no"
                continue

            schema = Schema(manifest=manifest)

            for step, index, metric in METRICS:
                design_data[f"metric-{metric}"] = schema.get('metric', metric,
                                                             step=step, index=index)

            for step, index in [("write.views", "0"), ("write.gds", "0")]:
                if schema.get('record', 'status', step=step, index=index) != "success":
                    design_data["success"] = "no"

            design_data["pdk"] = schema.get('option', 'pdk')
            design_data["mainlib"] = schema.get('asic', 'logiclib')[0]

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
                dat["manifest"] = manifest_path
            else:
                dat["manifest"] = None

        if args.merge:
            with open(os.path.join(args.output, "summary.json")) as f:
                merge_data = json.load(f)
            data = [*merge_data, *data]

        with open(os.path.join(args.output, "summary.json"), 'w') as f:
            json.dump(data, f, indent=2)
