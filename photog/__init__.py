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
        if not any([file.lower().endswith(".jpg") for file in files]):
            continue

        # Process directory if index.html is missing.
        if not os.path.exists(os.path.join(dir, "index.html")):
            photos = rename_images(dir)
            generate_index(dir, photos)
            exit_status = 0

    return exit_status

def dont_rename_images(dir):
    photos = []
    print("Getting EXIF dates", end="", flush=True)
    for image in glob("*.jpg", root_dir=dir):
        print(f".", end="", flush=True)
        photos.append({
            "basename": image.split(".", maxsplit=1)[0],
            "date": subprocess.check_output(["exiftool", "-SubSecDateTimeOriginal", "-DateTimeOriginal", os.path.join(dir, image)]).decode('utf-8').strip(),
        })
    photos.sort(key=lambda p: p["date"])
    print()
    return photos

def rename_images(dir):
    """
    Rename images sequentially.
    """

    inifile = os.path.join(dir, "photog.ini")
    options = read_inifile(inifile)

    photos = []
    print("Renumbering by EXIF date", end="", flush=True)
    for image in glob("*.jpg", root_dir=dir):
        print(f".", end="", flush=True)
        basename = image.split(".", maxsplit=1)[0]

        # Shell out because &^%$#@! Python can't figure this out...
        date = subprocess.check_output(["exiftool", "-SubSecDateTimeOriginal", "-DateTimeOriginal", os.path.join(dir, image)]).decode('utf-8').strip()

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

    print()

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

    print("Generating thumbnails", end="", flush=True)
    shutil.rmtree(os.path.join(dir, "thumbnails"), ignore_errors=True)
    os.makedirs(os.path.join(dir, "thumbnails"))

    photos_and_cinemagraphs = []
    for image in photos:
        print(".", end="", flush=True)
        basename = image["basename"]
        filename = f"{basename}.jpg"
        path = os.path.join(dir, filename)
        thumbnail = os.path.join("thumbnails", filename)

        # Create thumbnail.
        with Image.open(path) as im:
            original_width, original_height = im.size
            exif = im.info["exif"]
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
        photos_and_cinemagraphs.append(image)

        # Insert cinemagraph if exists:
        if os.path.exists(f"{basename}.avif"):
            filename = f"{basename}.avif"
            if options.get("zip", True):
                zipfile.write(os.path.join(dir, filename), filename)

            photos_and_cinemagraphs.append({
                "basename": basename,
                "small": filename,
                "original": filename,
                "s_height": S,
                "height": 1080,
                "s_width": int((S / 1080) * 1920),
                "width": 1920,
            })

    print()

    if options.get("zip", True):
        print("Writing zipfile...")
        zipfile.close()

    print("Writing index.html...")
    index = T.render({"photos": photos_and_cinemagraphs})
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
