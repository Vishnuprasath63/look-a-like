/* ==========================================
   StarMatch AI — JavaScript
   ========================================== */

document.addEventListener('DOMContentLoaded', function () {
    // ---- Mobile Nav Toggle ----
    const mobileToggle = document.getElementById('mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
            mobileToggle.classList.toggle('open');
        });

        // Close on link click
        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('active');
                mobileToggle.classList.remove('open');
            });
        });
    }

    // ---- Auto-dismiss alerts after 5 seconds ----
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert, index) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000 + (index * 500));
    });

    // ---- Navbar shrink on scroll ----
    const navbar = document.getElementById('main-nav');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(10, 10, 26, 0.95)';
            } else {
                navbar.style.background = 'rgba(10, 10, 26, 0.8)';
            }
        });
    }

    // ---- Intersection Observer for fade-in animations ----
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -40px 0px',
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.step-card, .feature-card').forEach(function (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Add visible class styles
    const style = document.createElement('style');
    style.textContent = `
        .step-card.visible, .feature-card.visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
});
