#!/usr/bin/env python3

import argparse
import json
import os
import tempfile
import zipfile

from PIL import Image
from siliconcompiler import Schema


METRICS = [
    ("write.views", 0, "totalarea"),
    ("write.views", 0, "fmax")
]


def __extract_zip(zip_file, workdir):
    os.makedirs(workdir, exist_ok=True)

    with zipfile.ZipFile(zip_file) as f:
        f.extractall(path=workdir)


def process_images(zip_file, workdir):
    image_dir = os.path.join(workdir, 'images')
    __extract_zip(zip_file, image_dir)

    base_image_dir = image_dir
    base_image_dir = os.path.join(base_image_dir, os.listdir(base_image_dir)[0])

    images = {}
    for file in os.listdir(base_image_dir):
        images[os.path.splitext(file)[0]] = {
            "path": os.path.join(base_image_dir, file),
            "relpath": os.path.relpath(os.path.join(base_image_dir, file), image_dir)
        }
    return images


def process_manifests(zip_file, workdir):
    manifest_dir = os.path.join(workdir, 'manifests')
    __extract_zip(zip_file, manifest_dir)

    data = []

    for design in os.listdir(manifest_dir):
        design_path = os.path.join(manifest_dir, design)
        for variant in os.listdir(design_path):
            if variant == "job0":
                continue

            variant_path = os.path.join(design_path, variant)

            manifest = os.path.join(variant_path, f"{design}.pkg.json")

            design_data = {
                "design": design,
                "variant": variant,
                "manifest": os.path.relpath(manifest, manifest_dir),
                "success": "yes",
                "description": ""
            }

            if not os.path.exists(manifest):
                design_data["success"] = "no"

            schema = Schema(manifest=manifest)

            for step, index, metric in METRICS:
                design_data[f"metric-{metric}"] = schema.get('metric', metric,
                                                             step=step, index=index)

            for step, index in [("write.views", "0"), ("write.gds", "0")]:
                if schema.get('record', 'status', step=step, index=index) != "success":
                    design_data["success"] = "no"

            design_data["pdk"] = schema.get('option', 'pdk')
            design_data["mainlib"] = schema.get('asic', 'logiclib')[0]

            data.append(design_data)
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
        help="Path to image zip",
        metavar="<file>",
        required=True)

    parser.add_argument(
        "--manifests",
        help="Path to manifest zip",
        metavar="<file>",
        required=True)

    parser.add_argument(
        "--merge",
        help="Merge with exisiting data",
        action="store_true")

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as workdir:
        images = process_images(args.images, workdir)
        data = process_manifests(args.manifests, workdir)

        for dat in data:
            image_name = f"{dat['design']}_{dat['variant']}"
            if image_name in images:
                img_path = os.path.join(args.output, images[image_name]["relpath"])
                img_path, _ = os.path.splitext(img_path)
                img_path += ".webp"
                os.makedirs(os.path.dirname(img_path), exist_ok=True)

                # Convert an image to WebP
                img = Image.open(images[image_name]["path"])
                img.save(img_path, "WEBP")

                dat["image"] = os.path.relpath(img_path, args.output)
            else:
                dat["image"] = None

        if args.merge:
            with open(os.path.join(args.output, "summary.json")) as f:
                merge_data = json.load(f)
            data = [*merge_data, *data]

        with open(os.path.join(args.output, "summary.json"), 'w') as f:
            json.dump(data, f, indent=2)
