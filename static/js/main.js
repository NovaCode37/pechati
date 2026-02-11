document.addEventListener('DOMContentLoaded', () => {

    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            mobileMenu.classList.toggle('open');
            const icon = mobileMenuBtn.querySelector('i');
            if (mobileMenu.classList.contains('open')) {
                icon.className = 'fas fa-times text-xl text-gray-600';
            } else {
                icon.className = 'fas fa-bars text-xl text-gray-600';
            }
        });
    }

    const track = document.getElementById('reviewsTrack');
    const prevBtn = document.getElementById('prevReview');
    const nextBtn = document.getElementById('nextReview');

    if (track && prevBtn && nextBtn) {
        let position = 0;
        const cards = track.children;
        const cardWidth = cards[0]?.offsetWidth || 350;
        const gap = 0;
        const visibleWidth = track.parentElement.offsetWidth;
        const totalWidth = cards.length * (cardWidth + gap);
        const maxScroll = Math.max(0, totalWidth - visibleWidth);

        function updateSlider() {
            track.style.transform = `translateX(-${position}px)`;
        }

        nextBtn.addEventListener('click', () => {
            position = Math.min(position + cardWidth, maxScroll);
            updateSlider();
        });

        prevBtn.addEventListener('click', () => {
            position = Math.max(position - cardWidth, 0);
            updateSlider();
        });

        let touchStartX = 0;
        let touchEndX = 0;

        track.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        track.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    position = Math.min(position + cardWidth, maxScroll);
                } else {
                    position = Math.max(position - cardWidth, 0);
                }
                updateSlider();
            }
        }, { passive: true });

        let autoSlide = setInterval(() => {
            position = position >= maxScroll ? 0 : position + cardWidth;
            updateSlider();
        }, 5000);

        track.parentElement.addEventListener('mouseenter', () => clearInterval(autoSlide));
        track.parentElement.addEventListener('mouseleave', () => {
            autoSlide = setInterval(() => {
                position = position >= maxScroll ? 0 : position + cardWidth;
                updateSlider();
            }, 5000);
        });
    }

    const faqToggles = document.querySelectorAll('.faq-toggle');

    faqToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const answer = toggle.nextElementSibling;
            const icon = toggle.querySelector('i');
            const isOpen = answer.classList.contains('open');

            faqToggles.forEach(t => {
                const a = t.nextElementSibling;
                const ic = t.querySelector('i');
                if (a !== answer) {
                    a.classList.remove('open');
                    ic.style.transform = 'rotate(0deg)';
                }
            });

            if (isOpen) {
                answer.classList.remove('open');
                icon.style.transform = 'rotate(0deg)';
            } else {
                answer.classList.add('open');
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card-hover').forEach(el => {
        observer.observe(el);
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    document.querySelectorAll('[class*="bg-green-50"], [class*="bg-blue-50"]').forEach(msg => {
        if (msg.closest('main') || msg.closest('.max-w-7xl')) {
            setTimeout(() => {
                msg.style.transition = 'opacity 0.5s ease, max-height 0.5s ease';
                msg.style.opacity = '0';
                msg.style.maxHeight = '0';
                msg.style.overflow = 'hidden';
                msg.style.padding = '0';
                msg.style.margin = '0';
                setTimeout(() => msg.remove(), 500);
            }, 5000);
        }
    });

    const phoneInput = document.querySelector('input[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value[0] === '7' || value[0] === '8') {
                    if (value.length > 1) {
                        let formatted = '+7 (';
                        formatted += value.substring(1, 4);
                        if (value.length > 4) formatted += ') ' + value.substring(4, 7);
                        if (value.length > 7) formatted += '-' + value.substring(7, 9);
                        if (value.length > 9) formatted += '-' + value.substring(9, 11);
                        e.target.value = formatted;
                    }
                }
            }
        });
    }
});
