#!/usr/bin/env python3
import io
import os
import random
from configparser import ConfigParser
from glob import glob
from zipfile import ZipFile

from jinja2 import Template
from PIL import Image

S = 500
M = 1000
L = 2000
TEMPLATE_NAME = "template.html"

if os.path.exists(TEMPLATE_NAME):
    template_path = TEMPLATE_NAME
else:
    template_path = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)
T = Template(open(template_path, "r").read())


def create_website(root="."):
    """
    Walk the directory tree, rename images, and generate indexes.
    """

    for (dir, dirs, files) in os.walk(root):
        if dir.startswith("./."):
            continue
        if dir.startswith("./static"):
            continue
        if os.path.basename(dir) == "thumbnails":
            continue
        if not any([file.lower().endswith(".jpg") for file in files]):
            continue

        os.makedirs(os.path.join(dir, "thumbnails"), exist_ok=True)
        photos = rename_images(dir)
        generate_index(dir, photos)


def rename_images(dir):
    """
    Rename images sequentially.
    """

    inifile = os.path.join(dir, "photog.ini")
    options = read_inifile(inifile)

    # Store Exif DateTimeOriginal
    photos = []
    for image in glob("*.jpg", root_dir=dir):
        basename = image.split(".", maxsplit=1)[0]
        im = Image.open(os.path.join(dir, image))
        date = im._getexif()[36867]
        photos.append(
            {
                "basename": basename,
                "date": date,
            }
        )

        # Rename
        for alt in glob(f"{basename}.*", root_dir=dir):
            ext = alt.split(".", maxsplit=1)[1]
            src = os.path.join(dir, alt)
            dst = os.path.join(dir, f"_{alt}")
            os.rename(src, dst)

    # Sort
    if options.get("sort") == "random":
        random.shuffle(photos)
    else:
        photos.sort(key=lambda p: p["date"])
        if options.get("sort") == "descending":
            photos.reverse()

    # Re-rename
    for counter, image in enumerate(photos):
        basename = image["basename"]
        for alt in glob(f"_{basename}.*", root_dir=dir):
            ext = alt.split(".", maxsplit=1)[1]
            src = os.path.join(dir, alt)
            dst = os.path.join(dir, f"{counter+1}.{ext}")
            os.rename(src, dst)
        image["basename"] = str(counter + 1)

    return photos


def generate_index(dir, photos):
    """
    Generate index.html
    """

    inifile = os.path.join(dir, "photog.ini")
    options = read_inifile(inifile)
    zippath = os.path.join(dir, "all.zip")
    if options.get("zip", True):
        zipfile = ZipFile(zippath, "w")
    elif os.path.exists(zippath):
        os.remove(zippath)

    for image in photos:
        basename = image["basename"]
        filename = f"{basename}.jpg"
        path = os.path.join(dir, filename)
        small_thumbnail = os.path.join("thumbnails", f"{basename} (small).jpg")
        medium_thumbnail = os.path.join("thumbnails", f"{basename} (medium).jpg")
        large_thumbnail = os.path.join("thumbnails", f"{basename} (large).jpg")
        im = Image.open(path)
        original_width, original_height = im.size
        exif = im.info["exif"]

        try:
            update_file = os.path.getmtime(os.path.join(dir, large_thumbnail)) < os.path.getmtime(path)
        except:
            update_file = True
        if update_file:
            # Generate S, M and L thumbnails
            im.thumbnail((L, 99999))
            im.save(os.path.join(dir, large_thumbnail), quality=95, exif=exif)
            im.thumbnail((M, 99999))
            im.save(os.path.join(dir, medium_thumbnail), quality=95, exif=exif)
            im.thumbnail((S, 99999))
            im.save(os.path.join(dir, small_thumbnail), quality=95, exif=exif)

        # Add original and large thumbnail to zip archive
        if options.get("zip", True):
            zipfile.write(path, os.path.join("print", filename))
            zipfile.write(
                os.path.join(dir, large_thumbnail), os.path.join("web", filename)
            )

        image.update(
            {
                "small": small_thumbnail,
                "medium": medium_thumbnail,
                "large": large_thumbnail,
                "original": filename,
                "s_height": S,
                "m_height": M,
                "l_height": L,
                "s_width": int((S / original_height) * original_width),
                "m_width": int((M / original_height) * original_width),
                "l_width": int((L / original_height) * original_width),
            }
        )

        print(path)

    if options.get("zip", True):
        print(zippath)
        zipfile.close()

    index = T.render(
        {
            "photos": photos,
        }
    )

    try:
        open(os.path.join(dir, "index.html"), "w").write(index)
    except:
        print("Couldn’t write to " + dir)


def read_inifile(inifile):
    """
    Read options from an ini file.
    """

    options = {}
    if os.path.exists(inifile):
        cfg = ConfigParser()
        with open(inifile) as stream:
            stream = io.StringIO("[root]\n" + stream.read())
            cfg.read_file(stream)
        root = cfg["root"]
        options["sort"] = root.get("sort", "ascending")
        options["zip"] = root.get("zip", "true").lower() in ["true", "yes", "on"]
    return options
