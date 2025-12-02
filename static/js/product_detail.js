document.addEventListener('DOMContentLoaded', function () {

  /* ===========================
     عناصر اصلی صفحه
  ============================ */

  const mainImage = document.getElementById('main-image');
  const thumbnails = document.querySelectorAll('.thumbnail');
  const quantityInput = document.getElementById('quantity');
  const quantityBtns = document.querySelectorAll('.quantity-btn');
  const unitPriceElem = document.getElementById('unit-price');
  const totalPriceElem = document.getElementById('total-price');
  const variantBtns = document.querySelectorAll('.variant-btn');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const showMoreBtn = document.getElementById('show-more');
  const showLessBtn = document.getElementById('show-less');
  const shortDescription = document.getElementById('short-description');
  const fullDescription = document.getElementById('full-description');
  const addToCartBtn = document.getElementById('add-to-cart');
  const ratingBox = document.querySelector('.rating-box');
  const productId = window.PRODUCT_ID; // مقداردهی از template

  let unitPrice = parseInt(unitPriceElem?.dataset.price) || 0;

  function formatFa(n){
    return new Intl.NumberFormat('fa-IR').format(n);
  }

  /* ===========================
     گالری تصاویر
  ============================ */

  thumbnails.forEach(thumb => {
    thumb.addEventListener('click', function () {
      mainImage.src = this.src;
      thumbnails.forEach(t => t.classList.replace('border-emerald-500', 'border-gray-200'));
      this.classList.replace('border-gray-200', 'border-emerald-500');
    });
  });

  /* ===========================
     تب‌ها
  ============================ */

  tabBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const tabId = this.dataset.tab;
      tabBtns.forEach(tab =>
        tab.classList.remove('active','border-emerald-500','text-emerald-600','font-semibold')
      );
      this.classList.add('active','border-emerald-500','text-emerald-600','font-semibold');
      tabContents.forEach(c => c.classList.add('hidden'));
      document.getElementById(`tab-${tabId}`)?.classList.remove('hidden');
    });
  });

  /* ===========================
     نمایش کوتاه/کامل توضیحات
  ============================ */

  if (showMoreBtn && showLessBtn) {
    showMoreBtn.addEventListener('click', function () {
      shortDescription.classList.add('hidden');
      fullDescription.classList.remove('hidden');
      showMoreBtn.classList.add('hidden');
      showLessBtn.classList.remove('hidden');
    });
    showLessBtn.addEventListener('click', function () {
      shortDescription.classList.remove('hidden');
      fullDescription.classList.add('hidden');
      showMoreBtn.classList.remove('hidden');
      showLessBtn.classList.add('hidden');
    });
  }

  /* ===========================
     انتخاب واریانت
  ============================ */

  variantBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      if (!this.disabled) {
        variantBtns.forEach(v =>
          v.classList.remove('bg-emerald-50','border-emerald-400','shadow-md')
        );
        this.classList.add('bg-emerald-50','border-emerald-400','shadow-md');
        unitPrice = parseInt(this.dataset.price);
        const inventory = parseInt(this.dataset.inventory);
        quantityInput.max = inventory;
        if (parseInt(quantityInput.value) > inventory) quantityInput.value = inventory;
        updateTotalPrice();
      }
    });
  });

  /* ===========================
     محاسبه قیمت کل
  ============================ */

  function updateTotalPrice() {
    let qty = parseInt(quantityInput.value) || 1;
    const maxQty = parseInt(quantityInput.max) || 1;
    if (qty < 1) qty = 1;
    if (qty > maxQty) qty = maxQty;
    quantityInput.value = qty;
    totalPriceElem.textContent = `${formatFa(unitPrice * qty)} تومان`;
  }

  /* ===========================
     کنترل تعداد
  ============================ */

  quantityBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      let qty = parseInt(quantityInput.value) || 1;
      const action = this.dataset.action;
      if (action === 'increase') qty++;
      if (action === 'decrease' && qty > 1) qty--;
      const maxQty = parseInt(quantityInput.max) || 1;
      if (qty > maxQty) qty = maxQty;
      quantityInput.value = qty;
      updateTotalPrice();
    });
  });

  quantityInput.addEventListener('input', updateTotalPrice);
  quantityInput.addEventListener('blur', function () {
    if (!this.value || parseInt(this.value) < 1) this.value = 1;
    updateTotalPrice();
  });

  /* ===========================
     افزودن به سبد
  ============================ */

  if (addToCartBtn) {
    addToCartBtn.addEventListener('click', function () {
      const originalHTML = this.innerHTML;
      this.innerHTML = `
        <i class="fas fa-check ml-3 text-lg"></i>
        <span class="font-semibold text-lg">افزوده شد به سبد</span>
      `;
      this.classList.replace('from-emerald-500','from-green-500');
      this.classList.replace('to-green-500','to-emerald-500');
      setTimeout(() => {
        this.innerHTML = originalHTML;
        this.classList.replace('from-green-500','from-emerald-500');
        this.classList.replace('to-emerald-500','to-green-500');
      }, 2000);
    });
  }

  /* ===========================
     ⭐ سیستم کامل نظرات ⭐
  ============================ */

  loadReviews();

  async function loadReviews() {
    const container = document.getElementById("reviews-list");
    if (!container) return;

    const res = await fetch(`/api/product/${productId}/reviews/`);
    const data = await res.json();

    container.innerHTML = "";

    if (ratingBox) {
      ratingBox.innerHTML = `
        <i class="fas fa-star ml-1 text-amber-400"></i>
        <span>${data.avg_rating.toFixed(1)}</span>
        <span class="text-amber-500 mx-1">•</span>
        <span>${data.count} نظر</span>
      `;
    }

    if (data.reviews.length === 0) {
      container.innerHTML = `<p class="text-gray-500 text-center">هنوز نظری ثبت نشده.</p>`;
      return;
    }

    data.reviews.forEach(r => {
      container.innerHTML += `
        <div class="border-b py-4" id="review-${r.id}">
          <div class="flex items-center mb-2">
            <span class="font-semibold">${r.user}</span>
            <span class="text-yellow-500 ml-3">${"★".repeat(r.rating)}</span>
            ${r.can_delete ? `<button class="ml-auto text-red-500 delete-review-btn" data-id="${r.id}">حذف</button>` : ''}
          </div>
          <p class="text-gray-700">${r.comment}</p>
        </div>
      `;
    });

    // دکمه حذف
    document.querySelectorAll(".delete-review-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const reviewId = btn.dataset.id;
        const res = await fetch(`/api/review/${reviewId}/delete/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        const result = await res.json();
        if (result.success) loadReviews();
        else alert(result.error);
      });
    });
  }

  const submitReviewBtn = document.getElementById("submit-review");
  if (submitReviewBtn) {
    submitReviewBtn.addEventListener("click", async function () {
      const rating = document.getElementById("rating").value;
      const comment = document.getElementById("comment").value;

      const res = await fetch(`/api/product/${productId}/add-review/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ rating, comment })
      });

      const data = await res.json();
      if (data.success) {
        loadReviews();
        document.getElementById("comment").value = "";
        document.getElementById("rating").value = "5";
      } else alert(data.error || "خطا در ثبت نظر");
    });
  }

  /* ===========================
     ابزار گرفتن CSRF
  ============================ */

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  updateTotalPrice();
});
