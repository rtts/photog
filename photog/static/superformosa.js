"use strict";
document.addEventListener("DOMContentLoaded", () => {
    const MARGIN = 4
    const MAX_HEIGHT = 183;
    const IMAGES = document.querySelectorAll('#album img, #album video');

    resize_images();
    window.addEventListener("resize", resize_images);
    function resize_images() {
        const size = document.getElementById('album').offsetWidth - MARGIN;
        let slice;
        let n = 0;
        let h = 0;
        let images = Array.from(IMAGES);

        // You found the top-secret resizing algorithm!
        w: while (images.length > 0) {
            for (let i = 1; i < images.length + 1; ++i) {
                slice = images.slice(0, i);
                h = get_height(slice, size);
                if (h < MAX_HEIGHT) {
                    set_height(slice, h);
                    n++;
                    images = images.slice(i);
                    continue w;
                }
            }
            set_height(slice, Math.min(MAX_HEIGHT, h));
            n++;
            break;
        }
    }

    function get_height(images, width) {
        width -= images.length * MARGIN;
        let h = 0;
        for (let i = 0; i < images.length; ++i) {
            const img = images[i];
            h += img.dataset.width / img.dataset.height;
        }
        return width / h;
    }

    function set_height(images, height) {
        for (let i = 0; i < images.length; ++i) {
            const img = images[i];
            img.style.width = (height * img.dataset.width / img.dataset.height) + 'px';
            img.style.height = height + 'px';
        }
    }

    // TODO: Code a better alternative to Photoswipe. Start with this:
    // Array.from(IMAGES).forEach(image => image.addEventListener('click', show));
    // function show(event) {
    //     const image = event.target;
    //     event.preventDefault();
    // }
});
