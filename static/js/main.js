document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.main-header');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop) {
            // Scroll down
            header.classList.add('hidden');
        } else {
            // Scroll up
            header.classList.remove('hidden');
        }
        lastScrollTop = scrollTop;
    });

    // Lógica para el menú hamburguesa
    const hamburgerButton = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    if (hamburgerButton && navLinks) {
        hamburgerButton.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
});