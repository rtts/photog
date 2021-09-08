Photog!
=======

**Photog! turns a directory tree of source images into a photography
website with nested albums of chronologically sorted photographs.**

It was created by
[Return to the Source](https://returntothesource.nl/en/)
for
[Super Formosa Photography](https://www.superformosa.nl/)
and provided here for everyone to use under the terms of the
[AGPL](https://www.gnu.org/licenses/agpl-3.0.html)
license as part of our
[free and open source philosophy](https://www.gnu.org/licenses/copyleft.en.htm)l.

![Screenshot of Super Formosa Photography](https://raw.githubusercontent.com/rtts/photog/main/www.superformosa.nl.png)


Features
--------

Photog! stands on the shoulders of giants.

- The thumbnails are displayed in a responsive gallery that
  recalculates the correct image dimensions in an aesthetically
  pleasing way, thanks to the algorithm from
  <https://github.com/ptgamr/google-image-layout>.

- Clicking a thumbnail opens the [PhotoSwipe](https://photoswipe.com/)
  gallery by @dimsemenov, with the following features of its own:
  - Touch gestures
  - Browser History API
  - Progressive loading
  - Fullscreen support
  - Share button

- Adding `/all.zip` to the end of the URL will download a ZIP file
  containing all the images in two different resolutions:
  1. The original images, unmodified, in the subfolder "print"
  2. Images scaled to a width of 2000 pixels, in the subfolder "web"

- The default template shows the logo <span
  style="font-variant:small-caps">Super Formosa Photography</span>
  at the top and license terms at the bottom. To override this, see
  the section "Customization" below.


Installation
------------

Photog! requires Python 3.8 or higher. You can check if this is
available on your system by running the following command:

    $ python3 --version

Then, create a [virtual environment](https://docs.python.org/3/library/venv.html):

    $ mkdir -p ~/.virtualenvs
    $ python3 -m venv ~/.virtualenvs/photog
    $ . ~/.virtualenvs/photog/bin/activate

This is not strictly necessary, but good practice.

Now you can install Photog! with `pip`:

    $ pip install git+https://www.github.com/rtts/photog


Usage
-----

First, activate your virtual environment:

    $ . ~/.virtualenvs/bin/activate

Then, navigate to your Pictures directory:

    $ cd ~/Pictures

Now, run the `photog` command:

    $ photog

Photog! will now traverse your pictures folder and generate HTML files
and image thumbnails. If you run `photog` a second time, nothing will
happen unless something has changed since the previous run.

After Photog! has completed its run, you can use Python's built-in
webserver to view your website:

    $ python3 -m http.server

Your website will now be available at the following URL:
`http://localhost:8000/`


Configuration
-------------

After running Photog! you will notice it has placed a file called
`photog.ini` in all of the processed directories. These files hold the
configuration variables per album. The configuration options are:

### Sorting
- `sort = ascending` to sort photos ascending according to EXIF date
- `sort = descending` to sort photos descending according to EXIF date
- `sort = alphabetical` to sort alphabetically according to file name
- `sort = random` to randomize the order of photos

### Zipping
- `zipping = true` creates a zipfile called `all.zip` of each album
- `zipping = false` disables the creation of zipfiles

The default configuration is:

    sort = ascending
    zipping = true

To change the configuration of a particular directory, open the file
`photog.ini` in a text editor and change the values. Photog! will not
overwrite pre-existing configuration files.


Customization
-------------

It is expected that you customize [the default template][1]. Save this
file as `template.html` in the root of your Pictures folder and edit
as needed. Then, run `photog` to use your customized template instead
of the default one.

[1]: https://raw.githubusercontent.com/rtts/photog/master/photog/template.html
