import io
import os
import random
import shutil
import subprocess
from configparser import ConfigParser
from glob import glob
from zipfile import ZipFile

from jinja2 import Template
from PIL import Image

S = 500
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

        # Process directory if index.html is missing.
        if not os.path.exists(os.path.join(dir, "index.html")):
            photos = dont_rename_images(dir)
            generate_index(dir, photos)
            exit_status = 0

    return exit_status

def dont_rename_images(dir):
    inifile = os.path.join(dir, "photog.ini")
    options = read_inifile(inifile)
    photos = []
    for filename in glob("*.jpg", root_dir=dir) + glob("*.avif", root_dir=dir):
        photos.append({
            "filename": filename,
            "basename": filename.split(".", maxsplit=1)[0],
        })
    try:
        photos.sort(key=lambda p: int(p["basename"]))
    except ValueError:
        photos.sort(key=lambda p: p["basename"])
    if options.get("sort") == "descending":
        photos.reverse()
    if options.get("sort") == "random":
        random.shuffle(photos)
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

    print("Generating thumbnails", end="", flush=True)
    shutil.rmtree(os.path.join(dir, "thumbnails"), ignore_errors=True)
    os.makedirs(os.path.join(dir, "thumbnails"))

    for image in photos:
        print(".", end="", flush=True)
        filename = image["filename"]
        basename = image["basename"]
        path = os.path.join(dir, filename)
        thumbnail = os.path.join("thumbnails", filename)

        # Create thumbnail.
        with Image.open(path) as im:
            original_width, original_height = im.size
            try:
                exif = im.info["exif"]
            except:
                exif = None
            im.thumbnail((S, 99999))
            im.save(os.path.join(dir, thumbnail), quality=95, exif=exif)

        # Add original to zip archive.
        if options.get("zip", True):
            zipfile.write(path, filename)

        image.update(
            {
                "small": thumbnail,
                "original": filename,
                "s_height": S,
                "height": original_height,
                "s_width": int((S / original_height) * original_width),
                "width": original_width,
            }
        )

    print()

    if options.get("zip", True):
        print("Writing zipfile...")
        zipfile.close()

    print("Writing index.html...")
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
