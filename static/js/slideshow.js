document.addEventListener("DOMContentLoaded", function() {
    const slideshowContainer = document.querySelector(".hero-slideshow");
    if (!slideshowContainer) return;

    const images = slideshowContainer.querySelectorAll("img");
    let currentImageIndex = 0;

    function showImage(index) {
        images.forEach((img, i) => {
            if (i === index) {
                img.classList.add("active");
            } else {
                img.classList.remove("active");
            }
        });
    }

    function nextImage() {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        showImage(currentImageIndex);
    }

    // Initialize slideshow
    showImage(currentImageIndex);
    setInterval(nextImage, 5000); // Change image every 5 seconds
});
