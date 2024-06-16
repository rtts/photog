#!/usr/bin/env python3
import io
import os
import random
from configparser import ConfigParser
from glob import glob
from zipfile import ZipFile

from jinja2 import Template
from PIL import Image

S = 500  # for album
L = 2160  # for homepage
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

    # Somewhat unfair, but it's nice to say
    # `if photog; then aws s3 sync` in Bash
    exit_status = 1

    for (dir, dirs, files) in os.walk(root):
        if dir.startswith("./."):
            continue
        if dir.startswith("./static"):
            continue
        if os.path.basename(dir) == "thumbnails":
            continue
        if not any([file.lower().endswith(".jpg") for file in files]):
            continue

        # Process directory once, entirely, if either index.html or a
        # single thumbnail is off.
        if not os.path.exists(os.path.join(dir, "index.html")):
            exit_status = 0
            process_directory(dir)
        else:
            for image in glob("*.jpg", root_dir=dir):
                basename = image.split(".", maxsplit=1)[0]
                thumbnail = os.path.join(dir, "thumbnails", basename + " (large)" + ".jpg")
                if not os.path.exists(thumbnail) or os.path.getmtime(thumbnail) < os.path.getmtime(os.path.join(dir, image)):
                    exit_status = 0
                    process_directory(dir)
                    break

    return exit_status


def process_directory(dir):
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
        try:
            date = im._getexif()[36867]
        except:
            date = "zzz"  # Sort images without EXIF date last
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
            if os.path.exists(dst):
                raise FileExistsError(dst)
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
            if os.path.exists(dst):
                raise FileExistsError(dst)
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
        large_thumbnail = os.path.join("thumbnails", f"{basename} (large).jpg")
        im = Image.open(path)
        original_width, original_height = im.size
        exif = im.info["exif"]

        try:
            raise  # because the following leads to thumbnail
                   # mismatches when renaming images:
            update_file = os.path.getmtime(
                os.path.join(dir, large_thumbnail)
            ) < os.path.getmtime(path)
        except:
            update_file = True
        if update_file:
            # Generate S, M and L thumbnails
            print(f"Generating thumbnails for {path}...")
            im.thumbnail((L, 99999))
            im.save(os.path.join(dir, large_thumbnail), quality=95, exif=exif)
            im.thumbnail((S, 99999))
            im.save(os.path.join(dir, small_thumbnail), quality=95, exif=exif)

        # Add original to zip archive
        if options.get("zip", True):
            zipfile.write(path, os.path.join(filename))

        image.update(
            {
                "small": small_thumbnail,
                # "large": large_thumbnail,
                "original": filename,
                "s_height": S,
                "height": original_height,
                "s_width": int((S / original_height) * original_width),
                "width": original_width,
            }
        )

    if options.get("zip", True):
        print("(Re)creating all.zip...")
        zipfile.close()

    index = T.render({"photos": photos})
    open(os.path.join(dir, "index.html"), "w").write(index)


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
