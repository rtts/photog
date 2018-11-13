Photog!
=======

Photog! turns a directory tree of source images into a photography
website with nested albums of chronologically sorted photographs. It
is created by [Jaap Joris Vens][1] who uses it for
[his personal photography website][2]. Photog also has
[it's own website][3] with detailed installation instructions, online
manual pages, and nice fonts.

[1]: http://rtts.eu/about/
[2]: http://www.superformosa.nl/
[3]: http://photog.created.today/

Installation
------------

This version of Photog! has been completely rewritten in Python.
You can still find [the original Perl version on GitHub][4].

[4]: https://github.com/rtts/photog

Installation, configuration and the general workings of Photog! are
now massively simplified. Simply install and run like this:

    $ pip install -r requirements.txt
    $ cd ~/My_Pictures
    $ path/to/photog

Just like the original Photog!, this will traverse your pictures
folder and generate HTML files and image thumbnails. However, in
contrast to the original Photog! there is no "destination folder".
All indexes are simply placed in their respective directories, and the
thumbnails are placed in a `thumbnails` subdirectory. After Photog!
has completed it's run, simply point your webserver to `~/My_Pictures`
(or do as the author does and upload the whole tree to AWS S3).

Configuration
-------------

After running Photog! you will notice it has placed empty files called
`photog.ini` in all of the processed directories. These hold the
optional configuration variables per album. The configuration options
are:

### Sorting
- `sort = ascending` to sort photos ascending according to EXIF date
- `sort = descending` to sort photos descending according to EXIF date
- `sort = alphabetical` to sort alphabetically according to file name
- `sort = random` to randomize the order of photos

### Zipping (new!)
- `zipping = true` creates a zipfile called `all.zip` of each album
- `zipping = false` disables the creation of zipfiles
