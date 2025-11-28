document.addEventListener('DOMContentLoaded', function() {
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

  let unitPrice = parseInt(unitPriceElem?.dataset.price) || 0;

  // گالری تصویر
  thumbnails.forEach(thumb => {
    thumb.addEventListener('click', function() {
      mainImage.src = this.src;
      thumbnails.forEach(t => t.classList.replace('border-emerald-500','border-gray-200'));
      this.classList.replace('border-gray-200','border-emerald-500');
    });
  });

  // تب‌ها
  tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const tabId = this.dataset.tab;
      tabBtns.forEach(tab => tab.classList.remove('active','border-emerald-500','text-emerald-600','font-semibold'));
      this.classList.add('active','border-emerald-500','text-emerald-600','font-semibold');
      tabContents.forEach(c => c.classList.add('hidden'));
      document.getElementById(`tab-${tabId}`)?.classList.remove('hidden');
    });
  });

  // نمایش توضیحات کامل
  if (showMoreBtn && showLessBtn) {
    showMoreBtn.addEventListener('click', function() {
      shortDescription.classList.add('hidden');
      fullDescription.classList.remove('hidden');
      showMoreBtn.classList.add('hidden');
      showLessBtn.classList.remove('hidden');
    });
    showLessBtn.addEventListener('click', function() {
      shortDescription.classList.remove('hidden');
      fullDescription.classList.add('hidden');
      showMoreBtn.classList.remove('hidden');
      showLessBtn.classList.add('hidden');
    });
  }

  // انتخاب واریانت
  variantBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      if (!this.disabled) {
        variantBtns.forEach(v => v.classList.remove('bg-emerald-50','border-emerald-400','shadow-md'));
        this.classList.add('bg-emerald-50','border-emerald-400','shadow-md');
        unitPrice = parseInt(this.dataset.price);
        const inventory = parseInt(this.dataset.inventory);
        quantityInput.max = inventory;
        if (parseInt(quantityInput.value) > inventory) quantityInput.value = inventory;
        updateTotalPrice();
      }
    });
  });

  function updateTotalPrice() {
    let qty = parseInt(quantityInput.value) || 1;
    const maxQty = parseInt(quantityInput.max) || 1;
    if (qty < 1) qty = 1;
    if (qty > maxQty) qty = maxQty;
    quantityInput.value = qty;
    totalPriceElem.textContent = `${(unitPrice * qty).toLocaleString()} تومان`;
  }

  // کنترل تعداد
  quantityBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      let qty = parseInt(quantityInput.value) || 1;
      const action = this.dataset.action;
      if (action==='increase') qty++;
      if (action==='decrease' && qty>1) qty--;
      const maxQty = parseInt(quantityInput.max) || 1;
      if (qty > maxQty) qty = maxQty;
      quantityInput.value = qty;
      updateTotalPrice();
    });
  });

  quantityInput.addEventListener('input', updateTotalPrice);
  quantityInput.addEventListener('blur', function() {
    if (!this.value || parseInt(this.value)<1) this.value = 1;
    updateTotalPrice();
  });

  // افزودن به سبد
  if (addToCartBtn) {
    addToCartBtn.addEventListener('click', function() {
      const originalHTML = this.innerHTML;
      this.innerHTML = `<i class="fas fa-check ml-3 text-lg"></i><span class="font-semibold text-lg">افزوده شد به سبد</span>`;
      this.classList.replace('from-emerald-500','from-green-500');
      this.classList.replace('to-green-500','to-emerald-500');
      setTimeout(()=>{ this.innerHTML = originalHTML; this.classList.replace('from-green-500','from-emerald-500'); this.classList.replace('to-emerald-500','to-green-500'); },2000);
    });
  }

  updateTotalPrice();
});
