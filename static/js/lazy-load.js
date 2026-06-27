// Lazy load images when they come into view
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll("img[data-src]");
    console.log("Lazy-load script loaded. Found images:", images.length);
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    console.log("Image intersecting:", img.alt || img.src);
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.classList.add("loaded");
                    console.log("Image loaded:", img.alt || img.src);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
});
