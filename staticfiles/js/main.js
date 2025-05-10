// ------------------ AOS Animation Init ------------------
document.addEventListener("DOMContentLoaded", function () {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            once: true,
            duration: 1200,
        });
    }

    // Hero subtitle animation (home.html)
    const heroSubtitle = document.querySelector(".hero-subtitle");
    if (heroSubtitle) {
        heroSubtitle.classList.remove("opacity-0", "translate-y-5");
    }

    // Auto-hide Django messages
    const msg = document.getElementById("message-container");
    if (msg) {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 3000);
    }

    // Desktop shop menu toggle (base.html)
    const desktopShopToggleBtn = document.getElementById('desktop-shop-toggle-btn');
    const desktopShopMenu = document.getElementById('desktop-shop-menu');
    if (desktopShopToggleBtn && desktopShopMenu) {
        desktopShopToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            desktopShopMenu.classList.toggle('opacity-0');
            desktopShopMenu.classList.toggle('scale-95');
            desktopShopMenu.classList.toggle('invisible');
        });

        document.addEventListener('click', (e) => {
            if (!desktopShopToggleBtn.contains(e.target) && !desktopShopMenu.contains(e.target)) {
                desktopShopMenu.classList.add('opacity-0', 'scale-95', 'invisible');
            }
        });
    }

    // Desktop submenu toggle
    document.querySelectorAll('.desktop-submenu-toggle').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = this.dataset.target;
            const submenu = document.getElementById(targetId);
            if (submenu) {
                submenu.classList.toggle('hidden');
            }
        });
    });

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileBackdrop = document.getElementById('mobile-backdrop');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');
    if (mobileMenu && mobileMenuBtn && mobileBackdrop && mobileCloseBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('translate-x-full');
            mobileBackdrop.classList.remove('hidden');
        });
        mobileCloseBtn.addEventListener('click', () => {
            mobileMenu.classList.add('translate-x-full');
            mobileBackdrop.classList.add('hidden');
        });
        mobileBackdrop.addEventListener('click', () => {
            mobileMenu.classList.add('translate-x-full');
            mobileBackdrop.classList.add('hidden');
        });
    }

    // Mobile submenu toggle
    document.querySelectorAll('.mobile-submenu-toggle').forEach(button => {
        button.addEventListener('click', function () {
            this.classList.toggle('active');
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.classList.toggle('hidden');
            }
        });
    });

    // Countdown (home.html)
    const countdownEl = document.getElementById("countdown");
    if (countdownEl) {
        const countdownDate = new Date().getTime() + (3 * 24 * 60 * 60 * 1000);
        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = countdownDate - now;

            if (distance < 0) {
                countdownEl.innerHTML = "🔥 Hurry! Sale Ends Soon!";
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            countdownEl.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        };

        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    // Image thumbnail switcher (used in shop/product/hot_sale pages)
    window.changeMainImage = function (productId, element) {
        const newUrl = element.getAttribute("data-image-url");
        const mainImage = document.getElementById("main-image-" + productId);
        if (mainImage) {
            mainImage.src = newUrl;
        }

        // Optional: highlight selected thumbnail
        const thumbnails = document.querySelectorAll(`#thumbnails img`);
        thumbnails.forEach(img => img.classList.remove('ring-2', 'ring-blue-500'));
        element.classList.add('ring-2', 'ring-blue-500');
    };

    // Checkout shipping fee + total calculation
    const govSelect = document.getElementById('government');
    if (govSelect) {
        govSelect.addEventListener('change', () => {
            const selected = govSelect.options[govSelect.selectedIndex];
            const shippingFee = parseFloat(selected.getAttribute('data-shipping-fee')) || 0;
            const subtotal = parseFloat(document.getElementById('subtotal')?.innerText.replace("EGP", "").trim()) || 0;
            const discount = parseFloat(document.getElementById('discount')?.dataset.amount || 0);
            const total = subtotal - discount + shippingFee;

            document.getElementById('shipping').innerText = 'EGP ' + shippingFee.toFixed(2);
            document.getElementById('total').innerText = 'EGP ' + total.toFixed(2);
        });
    }
});
