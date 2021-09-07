HEIGHTS = [];
MAX_HEIGHT = 183;

function getheight(images, width) {
    width -= images.length * 5;
    var h = 0;
    for (var i = 0; i < images.length; ++i) {
        h += $(images[i]).data('width') / $(images[i]).data('height');
    }
    return width / h;
}

function setheight(images, height) {
    HEIGHTS.push(height);
    for (var i = 0; i < images.length; ++i) {
        $(images[i]).css({
            width: height * $(images[i]).data('width') / $(images[i]).data('height'),
            height: height
        });
        $(images[i]).attr('src', $(images[i]).attr('src').replace(/w[0-9]+-h[0-9]+/, 'w' + $(images[i]).width() + '-h' + $(images[i]).height()));
    }
}

function resize(images, width) {
    setheight(images, getheight(images, width));
}

function resize_images() {
    var size = $('#album').width() - 4;
    var n = 0;
    var images = $('#album img, #album video');
    w: while (images.length > 0) {
        for (var i = 1; i < images.length + 1; ++i) {
            var slice = images.slice(0, i);
            var h = getheight(slice, size);
            if (h < MAX_HEIGHT) {
                setheight(slice, h);
                n++;
                images = images.slice(i);
                continue w;
            }
        }
        setheight(slice, Math.min(MAX_HEIGHT, h));
        n++;
        break;
    }
}

$(function() {
    $(window).on('resize', resize_images);
    resize_images();
});

