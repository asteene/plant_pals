document.addEventListener("DOMContentLoaded", function() {
    function toggleDropdown(event) {
        event.stopPropagation();
    
        const allDropdowns = document.querySelectorAll('.dropdown-menu');
        allDropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });

        const dropdown = event.target.closest('.card').querySelector('.dropdown-menu');
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }

    const dotsIcons = document.querySelectorAll('.dots-icon');
    dotsIcons.forEach(icon => {
        icon.onclick = toggleDropdown;
    });

    window.onclick = function() {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    };
});