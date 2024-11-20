document.addEventListener("DOMContentLoaded", function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const img = link.querySelector('img');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active-btn'); 
            img.classList.add('active-icon');
            link.classList.remove('nav-color'); 

           
            if (currentPath.startsWith('/friends') ) {
                img.classList.remove('active-icon');
                h5.classList.remove('friends-font');
            }
        }
    });
});