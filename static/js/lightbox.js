/**
 * Simple Lightbox Gallery
 * Enables click-to-view functionality for gallery images
 */

document.addEventListener('DOMContentLoaded', function() {
    const galleryLinks = document.querySelectorAll('.gallery-link');
    
    // Create lightbox modal
    const lightbox = createLightbox();
    
    galleryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const imageUrl = this.href;
            const title = this.getAttribute('data-title') || 'Image';
            const lightboxGroup = this.getAttribute('data-lightbox');
            
            // Get all images in the same lightbox group
            const groupImages = Array.from(galleryLinks)
                .filter(l => l.getAttribute('data-lightbox') === lightboxGroup)
                .map(l => ({
                    url: l.href,
                    title: l.getAttribute('data-title') || 'Image'
                }));
            
            // Find current image index
            const currentIndex = groupImages.findIndex(img => img.url === imageUrl);
            
            openLightbox(lightbox, imageUrl, title, groupImages, currentIndex);
        });
    });
    
    // Close lightbox on background click
    lightbox.addEventListener('click', function(e) {
        if (e.target === this) {
            closeLightbox(lightbox);
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLightbox(lightbox);
        }
    });
});

function createLightbox() {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <button class="lightbox-close">&times;</button>
            <button class="lightbox-prev">&#10094;</button>
            <img class="lightbox-image" src="" alt="">
            <button class="lightbox-next">&#10095;</button>
            <div class="lightbox-caption"></div>
        </div>
    `;
    
    document.body.appendChild(lightbox);
    
    const closeBtn = lightbox.querySelector('.lightbox-close');
    closeBtn.addEventListener('click', function() {
        closeLightbox(lightbox);
    });
    
    return lightbox;
}

function openLightbox(lightbox, imageUrl, title, groupImages, currentIndex) {
    const image = lightbox.querySelector('.lightbox-image');
    const caption = lightbox.querySelector('.lightbox-caption');
    const prevBtn = lightbox.querySelector('.lightbox-prev');
    const nextBtn = lightbox.querySelector('.lightbox-next');
    
    image.src = imageUrl;
    caption.textContent = title;
    
    lightbox.classList.add('active');
    
    // Navigation
    prevBtn.onclick = function() {
        const newIndex = (currentIndex - 1 + groupImages.length) % groupImages.length;
        openLightbox(lightbox, groupImages[newIndex].url, groupImages[newIndex].title, groupImages, newIndex);
    };
    
    nextBtn.onclick = function() {
        const newIndex = (currentIndex + 1) % groupImages.length;
        openLightbox(lightbox, groupImages[newIndex].url, groupImages[newIndex].title, groupImages, newIndex);
    };
}

function closeLightbox(lightbox) {
    lightbox.classList.remove('active');
}
