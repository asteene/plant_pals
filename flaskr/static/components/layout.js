document.addEventListener("DOMContentLoaded", function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const img = link.querySelector('img');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active-btn'); 
            img.classList.add('active-icon');
            link.classList.remove('nav-color'); 

            if (currentPath === '/profile' ) {
                img.classList.remove('active-icon'); // Remove active-icon class
                // You can add any other styles or classes specific to the profile page here
            }
            if (currentPath === '/friends' ) {
                img.classList.remove('active-icon');
                link.classList.remove('active-btn');
            }
        }
    });
});