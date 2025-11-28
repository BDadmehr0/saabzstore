(function(){
  const apiUrl = apiProductsUrl; // از قالب HTML میاد
  const defaultImage = defaultProductImage;

  const productsContainer = document.getElementById('productsContainer');
  const resetBtn = document.getElementById('resetFiltersBtn');
  const priceRange = document.getElementById('priceRange');
  const displayMaxPrice = document.getElementById('displayMaxPrice');
  const displayMinPrice = document.getElementById('displayMinPrice');
  const maxPriceInput = document.getElementById('maxPriceInput');
  const minPriceInput = document.getElementById('minPriceInput');
  const inStockCheckbox = document.getElementById('inStockCheckbox');
  const sortSelect = document.getElementById('sortSelect');
  const paginationDiv = document.getElementById('pagination');
  const resultsCount = document.getElementById('resultsCount');
  const activeFilters = document.getElementById('activeFilters');

  let currentPage = 1;
  let totalResults = 0;
  let debounceTimer;

  function truncateWords(text, wordLimit){
    const words = text.split(/\s+/);
    return words.length <= wordLimit ? text : words.slice(0, wordLimit).join(' ') + '...';
  }

  function formatFa(n){
    return new Intl.NumberFormat('fa-IR').format(n);
  }

  function updatePriceDisplay(){
    displayMinPrice.textContent = formatFa(minPriceInput.value) + ' تومان';
    displayMaxPrice.textContent = formatFa(maxPriceInput.value) + ' تومان';
  }
  updatePriceDisplay();

  function buildParams(page=1){
    const obj = { page: page, per_page: 12 };
    const qInput = new URLSearchParams(window.location.search).get('q');
    if(qInput) obj.q = qInput;

    const catVals = Array.from(document.querySelectorAll('.filter-category:checked')).map(cb=>cb.value);
    if(catVals.length) obj.categories = catVals.join(',');
    const brandVals = Array.from(document.querySelectorAll('.filter-brand:checked')).map(cb=>cb.value);
    if(brandVals.length) obj.brands = brandVals.join(',');

    obj.min_price = minPriceInput.value;
    obj.max_price = maxPriceInput.value;
    if(inStockCheckbox.checked) obj.in_stock = '1';
    if(sortSelect.value) obj.sort = sortSelect.value;

    return obj;
  }

  function escapeHtml(unsafe){
    return (unsafe+'').replace(/[&<"'>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  }

  function renderActiveFilters(){
    const activeFiltersArray = [];

    document.querySelectorAll('.filter-category:checked').forEach(cb=>{
      const label = document.querySelector(`label[for="${cb.id}"]`);
      activeFiltersArray.push({type:'category', value:cb.value, text:label.textContent, id:cb.id});
    });
    document.querySelectorAll('.filter-brand:checked').forEach(cb=>{
      const label = document.querySelector(`label[for="${cb.id}"]`);
      activeFiltersArray.push({type:'brand', value:cb.value, text:label.textContent, id:cb.id});
    });
    if(maxPriceInput.value < 5000000){
      activeFiltersArray.push({type:'price', value:maxPriceInput.value, text:`تا ${formatFa(maxPriceInput.value)} تومان`, id:'price-filter'});
    }
    if(inStockCheckbox.checked){
      activeFiltersArray.push({type:'stock', value:'1', text:'فقط موجود', id:'stock-filter'});
    }
    if(sortSelect.value){
      const sortText = {'price_asc':'ارزان‌ترین','price_desc':'گران‌ترین','newest':'جدیدترین','oldest':'قدیمی‌ترین'}[sortSelect.value];
      activeFiltersArray.push({type:'sort', value:sortSelect.value, text:`مرتب‌سازی: ${sortText}`, id:'sort-filter'});
    }

    if(activeFiltersArray.length > 0){
      activeFilters.classList.remove('hidden');
      activeFilters.innerHTML = `
        <span class="text-gray-600 text-sm">فیلترهای فعال:</span>
        ${activeFiltersArray.map(filter=>`
          <div class="active-filter-tag">
            ${filter.text}
            <button type="button" onclick="removeFilter('${filter.type}','${filter.id}')" class="text-red-400 hover:text-red-600 transition">
              <i class="fas fa-times text-xs"></i>
            </button>
          </div>
        `).join('')}
        <button type="button" onclick="resetFilters()" class="text-emerald-600 hover:text-emerald-700 text-sm font-semibold">
          حذف همه فیلترها
        </button>
      `;
    } else {
      activeFilters.classList.add('hidden');
    }
  }

  function removeFilter(type, id){
    switch(type){
      case 'category': case 'brand':
        document.getElementById(id).checked = false;
        break;
      case 'price':
        priceRange.value = 5000000;
        maxPriceInput.value = 5000000;
        minPriceInput.value = 0;
        updatePriceDisplay();
        break;
      case 'stock':
        inStockCheckbox.checked = false;
        break;
      case 'sort':
        sortSelect.value = '';
        break;
    }
    loadProducts(1,true);
  }

  function renderProducts(products){
    productsContainer.innerHTML = '';
    if(!products.length){
      productsContainer.innerHTML = `
        <div class="col-span-full text-center py-12">
          <i class="fas fa-search text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 text-lg mb-2">هیچ محصولی مطابق با فیلترهای شما یافت نشد.</p>
          <button onclick="resetFilters()" class="text-emerald-600 hover:text-emerald-700 font-semibold">
            حذف همه فیلترها
          </button>
        </div>
      `;
      return;
    }

    products.forEach(p=>{
      const productDiv = document.createElement('div');
      productDiv.className = 'group relative';
      const imageUrl = p.image ? p.image : defaultImage;
      const description = p.description ? truncateWords(escapeHtml(p.description),1) : 'توضیحات موجود نیست';
      const discountPercent = p.discount_price ? Math.round((1 - p.discount_price / p.price) * 100) : 0;

      productDiv.innerHTML = `
        <a href="/product/${p.id}/${p.slug}/" class="block">
          <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 product-card h-full flex flex-col" data-id="${p.id}">
            <div class="relative bg-gray-50 flex items-center justify-center p-4 h-64">
              <img src="${imageUrl}" alt="${escapeHtml(p.name)}" class="max-w-full max-h-full w-auto h-auto object-contain transition-transform duration-300 group-hover:scale-105">
              ${discountPercent > 0 ? `<div class="absolute top-3 left-3 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">${discountPercent}% تخفیف</div>` : ''}
              <div class="absolute top-3 right-3">
                ${p.inventory > 0 ? `<span class="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold">موجود</span>` : `<span class="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">ناموجود</span>`}
              </div>
            </div>
            <div class="p-4 flex-1 flex flex-col">
              <h3 class="text-lg font-bold text-gray-800 mb-2 leading-relaxed">${escapeHtml(p.name)}</h3>
              <p class="text-gray-600 text-sm mb-3 flex-1 leading-relaxed">${description}</p>
              <div class="mt-auto">
                ${p.discount_price ? `<div class="flex items-center gap-2 mb-2"><span class="text-lg font-bold text-emerald-600">${formatFa(p.discount_price)} تومان</span><span class="text-sm text-gray-500 line-through">${formatFa(p.price)}</span></div>` : `<span class="text-lg font-bold text-emerald-600 mb-2 block">${formatFa(p.price)} تومان</span>`}
                <div class="flex justify-between items-center">
                  <button class="add-to-cart-btn bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition duration-300 flex items-center text-sm font-semibold" data-product-id="${p.id}"><i class="fas fa-cart-plus ml-2"></i> افزودن به سبد</button>
                  <div class="flex items-center text-amber-500 text-sm"><i class="fas fa-star ml-1"></i><span>4.8</span></div>
                </div>
              </div>
            </div>
          </div>
        </a>
      `;
      productsContainer.appendChild(productDiv);
    });

    document.querySelectorAll('.add-to-cart-btn').forEach(btn=>{
      btn.addEventListener('click', function(e){
        e.preventDefault(); e.stopPropagation();
        addToCart(this.getAttribute('data-product-id'));
      });
    });
  }

  function addToCart(productId){
    const btn = document.querySelector(`[data-product-id="${productId}"]`);
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check ml-2"></i> افزوده شد';
    btn.classList.replace('bg-emerald-600','bg-green-600');
    setTimeout(()=>{ btn.innerHTML = originalHTML; btn.classList.replace('bg-green-600','bg-emerald-600'); },2000);
  }

  function renderPagination(pagination){
    paginationDiv.innerHTML = '';
    if(!pagination || pagination.total_pages <= 1) return;
    const createBtn = (text, page, disabled=false, active=false)=>{
      const btn = document.createElement('button');
      btn.className = 'px-4 py-2 rounded-lg border transition duration-300 font-medium';
      if(disabled) btn.className += ' opacity-50 cursor-not-allowed bg-gray-100 text-gray-400 border-gray-200';
      else if(active) btn.className += ' bg-emerald-600 text-white border-emerald-600 hover:bg-emerald-700';
      else btn.className += ' bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400';
      btn.textContent = text;
      if(!disabled) btn.addEventListener('click', ()=>loadProducts(page,true));
      return btn;
    };
    paginationDiv.appendChild(createBtn('‹ قبلی', pagination.page-1, !pagination.has_prev));
    const total = pagination.total_pages, current = pagination.page;
    let startPage = Math.max(1,current-2), endPage = Math.min(total,current+2);
    if(current <=3) endPage = Math.min(5,total);
    if(current >= total-2) startPage = Math.max(1,total-4);
    for(let i=startPage;i<=endPage;i++) paginationDiv.appendChild(createBtn(i,i,false,i===current));
    paginationDiv.appendChild(createBtn('بعدی ›', pagination.page+1,!pagination.has_next));
  }

  async function loadProducts(page=1,pushState=false){
    currentPage = page;
    const paramsObj = buildParams(page);
    const qs = new URLSearchParams(paramsObj).toString();
    const url = apiUrl + '?' + qs + '&_=' + new Date().getTime(); // timestamp برای جلوگیری از cache
    try{
      productsContainer.innerHTML = `<div class="col-span-full text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div><p class="text-gray-600 mt-4">در حال بارگذاری محصولات...</p></div>`;
      const res = await fetch(url, { headers:{'Accept':'application/json'}, credentials:'same-origin', cache:'no-store' });
      if(!res.ok) throw new Error('خطا در دریافت اطلاعات');
      const data = await res.json();
      totalResults = data.count || data.results.length;
      renderProducts(data.results || []);
      renderPagination(data.pagination || {});
      renderActiveFilters();
      resultsCount.textContent = formatFa(totalResults);
      if(pushState) history.pushState(null,'','{% url "store" %}?'+qs);
    }catch(err){
      console.error(err);
      productsContainer.innerHTML = `<div class="col-span-full text-center py-12"><i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i><p class="text-red-600 mb-2">خطا در بارگذاری محصولات</p><button onclick="loadProducts(1,false)" class="text-emerald-600 hover:text-emerald-700 font-semibold">تلاش مجدد</button></div>`;
    }
  }

  function resetFilters(){
    document.querySelectorAll('.filter-category, .filter-brand').forEach(cb=>cb.checked=false);
    inStockCheckbox.checked = false;
    priceRange.value = 5000000;
    maxPriceInput.value = 5000000;
    minPriceInput.value = 0;
    sortSelect.value = '';
    updatePriceDisplay();
    loadProducts(1,true);
  }

  function debounce(func, wait){
    return function(...args){
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(()=>func(...args), wait);
    };
  }

  // Event Listeners
  document.querySelectorAll('.filter-category, .filter-brand').forEach(cb=>cb.addEventListener('change', debounce(()=>loadProducts(1,true),300)));
  inStockCheckbox.addEventListener('change', debounce(()=>loadProducts(1,true),300));
  sortSelect.addEventListener('change', debounce(()=>loadProducts(1,true),300));
  priceRange.addEventListener('input', ()=>{ maxPriceInput.value = priceRange.value; updatePriceDisplay(); loadProducts(1,true); });
  resetBtn.addEventListener('click', resetFilters);

  loadProducts(1,false);

  window.addEventListener('popstate', ()=>{ 
    const page = parseInt(new URLSearchParams(window.location.search).get('page')||'1'); 
    loadProducts(page,false); 
  });

  window.removeFilter = removeFilter;
  window.resetFilters = resetFilters;

})();
