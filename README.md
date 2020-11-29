Photog!
=======

Photog! turns a directory tree of source images into a photography
website with nested albums of chronologically sorted photographs. It
is created by [Jaap Joris Vens][1] who uses it for
[his personal photography website][2].

This version of Photog! has been completely rewritten in Python.
You can still find [the original Perl version on GitHub][3].

[1]: https://www.jaapjoris.nl/
[2]: https://www.superformosa.nl/
[3]: https://github.com/rtts/photog-perl


Installation
------------

Photog! requires Python 3. You can check if this is available on your
system by running the following command:

    $ python3

Once you have Python 3, you can easily install Photog! easily using
`pip`:

    $ pip install https://www.github.com/rtts/photog

Depending on your operating system, you might have to substitute `pip`
for `pip3`. Depending on your local configuration, you might have to
run the command as root using `sudo`. So, if the previous command
didn't work, try this one:

    $ sudo pip3 install https://www.github.com/rtts/photog


Usage
-----

First, navigate to your Pictures directory using `cd`:

    $ cd ~/Pictures

Then, run the `photog` command:

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

To change the configuration of a particular directory, open the file
`photog.ini` in a text editor and change the values. Photog! will not
overwrite pre-existing configuration files.


Customization
-------------

Since you probably don't want your website to have _Super Formosa
Photography_ in the header of every page, you should customize [the
default template][4]. Save this file as `template.html` in the root of
your Pictures folder and edit as needed. Then, running `photog` will
use your customized template instead of the default one.

[4]: https://raw.githubusercontent.com/rtts/photog/master/photog/template.html






