// ==========================================
// Main JavaScript - Moto Club Castellazzo Bormida
// ==========================================

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // Navigation & Mobile Menu
    // ==========================================
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const header = document.getElementById('header');
    
    // Toggle mobile menu
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close menu when clicking on nav link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Sticky header on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Active nav link on scroll
    const sections = document.querySelectorAll('section[id]');
    
    function highlightNav() {
        const scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 150;
            const sectionId = section.getAttribute('id');
            
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                document.querySelector(`.nav-link[href="#${sectionId}"]`)?.classList.add('active');
            } else {
                document.querySelector(`.nav-link[href="#${sectionId}"]`)?.classList.remove('active');
            }
        });
    }
    
    window.addEventListener('scroll', highlightNav);
    
    // ==========================================
    // Smooth Scroll
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // ==========================================
    // Dark/Light Mode Toggle
    // ==========================================
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Check for saved theme preference
    const currentTheme = localStorage.getItem('theme') || 'light';
    body.classList.toggle('dark-mode', currentTheme === 'dark');
    updateThemeIcon();
    
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const theme = body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
        updateThemeIcon();
    });
    
    function updateThemeIcon() {
        const icon = themeToggle.querySelector('i');
        if (body.classList.contains('dark-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
    
    // ==========================================
    // Countdown Timer
    // ==========================================
    function updateCountdown() {
        const eventDate = new Date('2026-03-15T09:00:00').getTime();
        const now = new Date().getTime();
        const distance = eventDate - now;
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        document.getElementById('days').textContent = days;
        document.getElementById('hours').textContent = hours;
        document.getElementById('minutes').textContent = minutes;
        document.getElementById('seconds').textContent = seconds;
        
        if (distance < 0) {
            document.getElementById('countdown').innerHTML = '<p>Evento in corso!</p>';
        }
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
    
    // ==========================================
    // Animated Counters
    // ==========================================
    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString();
            }
        };
        
        updateCounter();
    }
    
    // Intersection Observer for counters
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-number').forEach(counter => {
        counterObserver.observe(counter);
    });
    
    // ==========================================
    // Typing Animation
    // ==========================================
    const typingText = document.querySelector('.typing-text');
    if (typingText) {
        const text = 'Moto Club Castellazzo Bormida';
        let index = 0;
        
        function type() {
            if (index < text.length) {
                typingText.textContent += text.charAt(index);
                index++;
                setTimeout(type, 100);
            }
        }
        
        type();
    }
    
    // ==========================================
    // Gallery Filter & Lightbox
    // ==========================================
    const filterBtns = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = lightbox?.querySelector('img');
    const lightboxClose = document.querySelector('.lightbox-close');
    
    // Filter gallery
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            
            galleryItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'block';
                    item.style.animation = 'zoomIn 0.5s ease-out';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Lightbox functionality
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            lightbox.classList.add('active');
            // In a real implementation, you would set the actual image src here
            // lightboxImg.src = item.querySelector('img').src;
        });
    });
    
    lightboxClose?.addEventListener('click', () => {
        lightbox.classList.remove('active');
    });
    
    lightbox?.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            lightbox.classList.remove('active');
        }
    });
    
    // ==========================================
    // Particles.js Configuration
    // ==========================================
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: {
                    value: 80,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: '#D4AF37'
                },
                shape: {
                    type: 'circle'
                },
                opacity: {
                    value: 0.5,
                    random: false
                },
                size: {
                    value: 3,
                    random: true
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#D4AF37',
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: false,
                    straight: false,
                    out_mode: 'out',
                    bounce: false
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: {
                        enable: true,
                        mode: 'repulse'
                    },
                    onclick: {
                        enable: true,
                        mode: 'push'
                    },
                    resize: true
                },
                modes: {
                    repulse: {
                        distance: 100,
                        duration: 0.4
                    },
                    push: {
                        particles_nb: 4
                    }
                }
            },
            retina_detect: true
        });
    }
    
    // ==========================================
    // Leaflet Map
    // ==========================================
    if (typeof L !== 'undefined') {
        const map = L.map('map').setView([44.8983, 8.5914], 15);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Custom marker icon
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: linear-gradient(135deg, #1B263B, #9B1D64, #D4AF37); width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"></div>',
            iconSize: [30, 30]
        });
        
        L.marker([44.8983, 8.5914], { icon: customIcon })
            .addTo(map)
            .bindPopup('<b>Moto Club Castellazzo Bormida</b><br>Via Roma 45, 15073 Castellazzo Bormida (AL)')
            .openPopup();
    }
    
    // ==========================================
    // Form Validation
    // ==========================================
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value.trim();
            
            // Basic validation
            if (!name || !email || !subject || !message) {
                alert('Per favore, compila tutti i campi obbligatori.');
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Per favore, inserisci un indirizzo email valido.');
                return;
            }
            
            // Show success message
            alert('Grazie per averci contattato! Ti risponderemo al più presto.');
            contactForm.reset();
            
            // In a real implementation, you would send the form data to a server here
            console.log('Form data:', { name, email, subject, message });
        });
    }
    
    // ==========================================
    // Newsletter Form
    // ==========================================
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Per favore, inserisci un indirizzo email valido.');
                return;
            }
            
            alert('Grazie per esserti iscritto alla nostra newsletter!');
            emailInput.value = '';
        });
    }
    
    // ==========================================
    // Scroll to Top Button
    // ==========================================
    const scrollToTop = document.getElementById('scrollToTop');
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTop.classList.add('show');
        } else {
            scrollToTop.classList.remove('show');
        }
    });
    
    scrollToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // ==========================================
    // Initialize AOS (Animate On Scroll)
    // ==========================================
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100,
            easing: 'ease-out-cubic'
        });
    }
    
    // ==========================================
    // Testimonial Slider (Simple Auto-rotate)
    // ==========================================
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    let currentTestimonial = 0;
    
    function rotateTestimonials() {
        testimonialCards.forEach((card, index) => {
            card.style.transform = index === currentTestimonial ? 'scale(1.05)' : 'scale(1)';
            card.style.opacity = index === currentTestimonial ? '1' : '0.7';
        });
        
        currentTestimonial = (currentTestimonial + 1) % testimonialCards.length;
    }
    
    if (testimonialCards.length > 0) {
        setInterval(rotateTestimonials, 5000);
    }
    
    // ==========================================
    // Council Card Flip Effect (for touch devices)
    // ==========================================
    const councilCards = document.querySelectorAll('.council-card');
    
    councilCards.forEach(card => {
        let isFlipped = false;
        
        card.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                isFlipped = !isFlipped;
                const front = this.querySelector('.card-front');
                const back = this.querySelector('.card-back');
                
                if (isFlipped) {
                    front.style.transform = 'rotateY(180deg)';
                    back.style.transform = 'rotateY(360deg)';
                } else {
                    front.style.transform = 'rotateY(0deg)';
                    back.style.transform = 'rotateY(180deg)';
                }
            }
        });
    });
    
    // ==========================================
    // News Ticker Animation
    // ==========================================
    const tickerContent = document.querySelector('.ticker-content');
    
    if (tickerContent) {
        // Clone ticker content for seamless loop
        const tickerClone = tickerContent.cloneNode(true);
        tickerContent.parentElement.appendChild(tickerClone);
    }
    
    // ==========================================
    // Event Card Hover Effects
    // ==========================================
    const eventCards = document.querySelectorAll('.event-card');
    
    eventCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // ==========================================
    // Performance Optimization: Lazy Loading
    // ==========================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // ==========================================
    // Prevent default behavior for placeholder links
    // ==========================================
    document.querySelectorAll('a[href="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.getAttribute('href') === '#' && !link.classList.contains('scroll-down')) {
                e.preventDefault();
            }
        });
    });
    
    // ==========================================
    // Console Welcome Message
    // ==========================================
    console.log('%cMoto Club Castellazzo Bormida', 'color: #D4AF37; font-size: 24px; font-weight: bold;');
    console.log('%cDal 1933 la passione su due ruote!', 'color: #1B263B; font-size: 14px;');
    console.log('%c🏍️ Visita il nostro sito: https://mccastellazzob.com', 'color: #9B1D64; font-size: 12px;');
    
    // ==========================================
    // Add page load animation
    // ==========================================
    document.body.style.opacity = '0';
    
    window.addEventListener('load', () => {
        setTimeout(() => {
            document.body.style.transition = 'opacity 0.5s ease-in';
            document.body.style.opacity = '1';
        }, 100);
    });
    
    // ==========================================
    // Easter Egg: Konami Code
    // ==========================================
    let konamiCode = [];
    const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    
    document.addEventListener('keydown', (e) => {
        konamiCode.push(e.key);
        konamiCode.splice(-konamiSequence.length - 1, konamiCode.length - konamiSequence.length);
        
        if (konamiCode.join(',') === konamiSequence.join(',')) {
            alert('🏍️ Hai trovato l\'Easter Egg! Sei un vero motociclista! 🏍️');
            document.body.style.animation = 'rotate360 2s ease-in-out';
            setTimeout(() => {
                document.body.style.animation = '';
            }, 2000);
        }
    });
    
});

// ==========================================
// Additional Utility Functions
// ==========================================

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format date function
function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('it-IT', options);
}

// Smooth scroll with offset
function smoothScrollTo(element, offset = 80) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}
