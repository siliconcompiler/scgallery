# SiliconCompiler Design Gallery
Design gallery for SiliconCompiler.
This library uses the rtl2gds flow in SiliconCompiler to compile the designs from RTL to a GDS file.

# To run a design:

    python3 -m scgallery -design sha3  # Will run on all supported targets
    python3 -m scgallery -design sha3 -target asap7_demo  # Will only run on asap7
    python3 -m scgallery -target asap7_demo  # Will run all designs supported on asap7
    python3 -m scgallery  # Will run all designs on all targets

# To check rules:

    python3 scgallery/rules.py -cfg <cfg> -rules <rules> -check  # Check if run met the rule requirements.
    python3 scgallery/rules.py -cfg <cfg> -rules <rules> -update  # Update rules based on last run.

# To convert rules from ORFS (should only be done while supporting a transision):

    scgallery/translate.sh

# To add a design:
1. Create a folder with the design name (<design>) in scgallery/designs
2. add source files to scgallery/designs/<design>/src
3. add constraints to scgallery/designs/<design>/constraints (using the name of the library it is associated with)
4. create scgallery/designs/<design>/<design>.py
5. add <design>.py to scgallery/designs/__init__.py
