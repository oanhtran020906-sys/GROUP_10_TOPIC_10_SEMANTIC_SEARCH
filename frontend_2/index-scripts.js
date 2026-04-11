
// Dữ liệu mô tả, hãng 
const allProducts = [
    { id: 0, name: "MacBook Pro M3", cat: "laptop", price: "45.990.000đ", brand: "Apple", desc: "Sức mạnh kinh ngạc từ chip M3. Màn hình Liquid Retina XDR đẹp nhất trên laptop. Thời lượng pin lên đến 22 giờ cho mọi công việc sáng tạo." },
    { id: 1, name: "LG Gram 2026", cat: "laptop", price: "35.000.000đ", brand: "LG", desc: "Siêu nhẹ, siêu bền. Màn hình OLED 3K sống động. Lựa chọn hoàn hảo cho những ai thường xuyên di chuyển nhưng vẫn cần hiệu năng mạnh mẽ." },
    { id: 2, name: "Màn hình LG OLED", cat: "màn hình", price: "15.500.000đ", brand: "LG", desc: "Độ tương phản vô hạn, màu đen tuyệt đối. Tần số quét 144Hz giúp mọi chuyển động trong game mượt mà như thật." },
    { id: 3, name: "Bàn phím Techna G1", cat: "bàn phím", price: "2.500.000đ", brand: "TechnaLG", desc: "Sử dụng switch quang học siêu bền, led RGB Magic Sync đồng bộ theo âm nhạc và hệ sinh thái Techna Zenith." },
    { id: 4, name: "iPhone 17 Pro", cat: "điện thoại", price: "32.000.000đ", brand: "Apple", desc: "Camera ẩn dưới màn hình thế hệ mới. Khung viền Titanium mờ cực sang trọng và khả năng xử lý AI vượt trội." }
];

// Hàm render ở trang chủ
function render(list) {
    const container = document.getElementById('product-display');
    if (!container) return; 

    container.innerHTML = list.map(p => `
        <div class="product-card" onclick="goToDetail(${p.id})">
            <div class="product-image">TechnaLG ${p.cat.toUpperCase()}</div>
            <div class="product-name">${p.name}</div>
            <div class="product-price">${p.price}</div>
        </div>
    `).join('');
}
function setMode(mode) {
    const searchInput = document.getElementById('search-input');
    const sqlOpt = document.getElementById('sql-opt');
    const vecOpt = document.getElementById('vec-opt');
    
    sqlOpt.classList.remove('active');
    vecOpt.classList.remove('active');
    
    if (mode === 'sql') {
        sqlOpt.classList.add('active'); 
        searchInput.placeholder = "Tìm kiếm bằng SQL..."; 
        
        searchInput.parentElement.style.borderColor = "rgb(184, 117, 255)";
    } else {
        vecOpt.classList.add('active'); 
        searchInput.placeholder = "Tìm kiếm bằng VECTOR..."; 
        searchInput.parentElement.style.borderColor = "rgb(0, 255, 255)";
    }
}

// Hàm để chuyển trang
function goToDetail(id) {
    window.location.href = `product-detail.html?id=${id}`;
}

function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

function filterBy(cat) {
    toggleMenu();
    document.getElementById('cat-name').innerText = cat.toUpperCase();
    const filtered = allProducts.filter(p => p.cat === cat);
    render(filtered);
    document.getElementById('product-section').scrollIntoView();
}

window.onload = () => {
    const display = document.getElementById('product-display');
    if (display) render(allProducts.slice(0, 4));
};