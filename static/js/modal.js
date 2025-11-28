// باز کردن مودال جستجو
function openSearchModal() {
    const modal = document.getElementById("searchModal");
    if (modal) {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }
}

// بستن مودال جستجو
function closeSearchModal() {
    const modal = document.getElementById("searchModal");
    if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }
}
