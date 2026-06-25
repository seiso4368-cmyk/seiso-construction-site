// Portfolio Filter Functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    function applyFilter(filterValue) {
        // Update active button
        filterButtons.forEach(btn => {
            if (btn.getAttribute('data-filter') === filterValue) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Filter portfolio items
        portfolioItems.forEach(item => {
            if (filterValue === 'all') {
                item.classList.remove('hidden');
            } else {
                const itemCategory = item.getAttribute('data-category');
                if (itemCategory === filterValue) {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            }
        });
    }

    // Check for category in URL hash on load
    const hash = window.location.hash.replace('#', '');
    if (hash && ['residential', 'commercial', 'renovation'].includes(hash)) {
        applyFilter(hash);
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterValue = this.getAttribute('data-filter');
            
            // Update URL hash without jumping
            if (filterValue === 'all') {
                history.pushState("", document.title, window.location.pathname + window.location.search);
            } else {
                window.location.hash = filterValue;
            }
            
            applyFilter(filterValue);
        });
    });
});
