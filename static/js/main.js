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

    // ✅ Mobile menu toggle - optimized version
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileBackdrop = document.getElementById('mobile-backdrop');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');

    function openMobileMenu() {
        mobileMenu.classList.remove('translate-x-full');
        mobileBackdrop.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }

    function closeMobileMenu() {
        mobileMenu.classList.add('translate-x-full');
        mobileBackdrop.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }

    mobileMenuBtn.addEventListener('click', openMobileMenu);
    mobileCloseBtn.addEventListener('click', closeMobileMenu);
    mobileBackdrop.addEventListener('click', closeMobileMenu);

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

     // Retain filter values in shop filter form (sort_by, price_filter)
    const urlParams = new URLSearchParams(window.location.search);
    const sortBy = urlParams.get('sort_by');
    const priceFilter = urlParams.get('price_filter');

    if (sortBy) {
        const sortSelect = document.querySelector('select[name="sort_by"]');
        if (sortSelect) sortSelect.value = sortBy;
    }
    if (priceFilter) {
        const priceSelect = document.querySelector('select[name="price_filter"]');
        if (priceSelect) priceSelect.value = priceFilter;
    }


    // Image thumbnail switcher (used in shop/product/hot_sale pages)
    window.changeMainImage = function (productId, element) {
        const newImageUrl = element.getAttribute('data-image-url');
        const mainImage = document.getElementById('main-image-' + productId);
        if (mainImage) {
            mainImage.src = newImageUrl;
        }
        const selectedColorInput = document.getElementById('selected-color-' + productId);
        if (selectedColorInput) {
            selectedColorInput.value = newImageUrl;
        }
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

    // Promo Code Validation
    let debounceTimeout;
    const promoInput = document.getElementById('promo_code');
    if (promoInput) {
        promoInput.addEventListener('input', function () {
            clearTimeout(debounceTimeout);
            const promoCode = this.value;
            const subtotal = parseFloat(document.getElementById('subtotal')?.innerText.replace("EGP", "").trim()) || 0;

            debounceTimeout = setTimeout(() => {
                document.getElementById('promo-msg')?.remove();

                if (promoCode.length > 1) {
                    fetch(`/validate-promo/?code=${promoCode}&subtotal=${subtotal}`)
                        .then(res => res.json())
                        .then(data => {
                            const discountElem = document.getElementById('discount');
                            if (data.valid) {
                                discountElem.innerHTML = `✅ Discount: <span class="font-bold">-EGP ${data.discount.toFixed(2)}</span>`;
                                discountElem.dataset.amount = data.discount;
                                discountElem.classList.remove('hidden');
                                updateTotals();
                            } else {
                                discountElem.classList.add('hidden');
                                const msg = document.createElement('p');
                                msg.id = 'promo-msg';
                                msg.className = 'text-sm text-red-600 font-semibold mt-1';
                                msg.innerText = data.message || 'Invalid promo code';
                                document.getElementById('promo_code').after(msg);
                            }
                        });
                } else {
                    document.getElementById('discount').classList.add('hidden');
                    document.getElementById('promo-msg')?.remove();
                    updateTotals();
                }
            }, 500);
        });
    }
});
