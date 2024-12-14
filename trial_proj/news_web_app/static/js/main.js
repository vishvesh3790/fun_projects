// Auto-refresh news every 30 minutes
const REFRESH_INTERVAL = 30 * 60 * 1000; // 30 minutes in milliseconds

function getCurrentCategory() {
    const path = window.location.pathname;
    if (path.startsWith('/category/')) {
        return path.split('/')[2];
    }
    return 'top';
}

async function refreshNews() {
    const category = getCurrentCategory();
    try {
        const response = await fetch(`/api/news/${category}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Error fetching news:', data.error);
            return;
        }

        // Update last updated time
        const footerTime = document.querySelector('footer p');
        if (footerTime) {
            footerTime.textContent = `Last updated: ${data.last_updated}`;
        }

        // Reload the page to show new content
        window.location.reload();
    } catch (error) {
        console.error('Error refreshing news:', error);
    }
}

// Set up auto-refresh
setInterval(refreshNews, REFRESH_INTERVAL);

// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add loading animation for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.news-image img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = 1;
        });
        img.style.opacity = 0;
        img.style.transition = 'opacity 0.3s';
    });
});
