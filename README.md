[![Python CI](https://github.com/siliconcompiler/scgallery/actions/workflows/python_ci.yml/badge.svg)](https://github.com/siliconcompiler/scgallery/actions/workflows/python_ci.yml)
[![Lint](https://github.com/siliconcompiler/scgallery/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/siliconcompiler/scgallery/actions/workflows/lint.yml)

# SiliconCompiler Design Gallery
Design gallery for [SiliconCompiler](https://github.com/silicompiler/siliconcompiler).
This library uses the rtl2gds flow in SiliconCompiler to compile the designs from RTL to a GDS file.

![Gallery](images/montage.jpg)

# To install:
Utilize the same python environment as SiliconCompiler.

    git clone https://github.com/siliconcompiler/scgallery.git
    cd scgallery
    python3 -m pip install .

# To run a design:

    sc-gallery -design sha512  # Will run on all supported targets
    sc-gallery -design sha512 -target asap7_demo  # Will only run on asap7
    sc-gallery -target asap7_demo  # Will run all designs supported on asap7
    sc-gallery  # Will run all designs on all targets

# Extending with proprietary design and technologies:

    sc-gallery -gallery orfs.gallery -design aes  # Will run on all supported targets in ORFS
    sc-gallery -gallery orfs.gallery  # Will run all designs on all targets in ORFS

# To check rules:

    python3 scgallery/rules.py -cfg <cfg> -rules <rules> -check  # Check if run met the rule requirements.
    python3 scgallery/rules.py -cfg <cfg> -rules <rules> -update  # Update rules based on last run.

# Contributing

## To add a design:
1. Create a folder with the design name (\<design\>) in scgallery/designs
2. add source files to scgallery/designs/\<design\>/src
3. add constraints to scgallery/designs/\<design\>/constraints (using the name of the library it is associated with)
4. create scgallery/designs/\<design\>/\<design\>.py
5. add the design to [scgallery/designs/\_\_init\_\_.py](scgallery/designs/__init__.py)

# Issues / Bugs

We use [GitHub Issues](https://github.com/siliconcompiler/scgallery/issues)
for tracking requests and bugs.

# License

[Apache License 2.0](LICENSE)
