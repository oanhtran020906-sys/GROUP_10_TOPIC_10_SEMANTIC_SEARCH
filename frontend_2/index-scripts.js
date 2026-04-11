const API_URL = "http://127.0.0.1:8000";
let currentSearchMode = 'vec'; 

// 1. Hàm render dữ liệu lên màn hình
function render(list) {
    const container = document.getElementById('product-display');
    if (!container) return; 

    if (!list || list.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: cyan;">Không tìm thấy sản phẩm nào phù hợp.</p>';
        return;
    }

    container.innerHTML = list.map(p => {
        // Nối link ảnh từ Backend
        const imageUrl = p.image_path ? `${API_URL}/static/${p.image_path}` : 'logo 1.png';
        
        return `
            <div class="product-card" onclick="goToDetail(${p.id})">
                <div class="product-image">
                    <img src="${imageUrl}" onerror="this.src='logo 1.png'" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">
                </div>
                <div class="product-name">${p.name}</div>
                <div class="product-price">${Number(p.price).toLocaleString()}đ</div>
                ${p.similarity_score ? `<div style="color: #00ffcc; font-size: 11px; margin-top:5px;">Khớp: ${p.similarity_score}%</div>` : ''}
            </div>
        `;
    }).join('');
}

// 2. Hàm gọi API lấy sản phẩm nổi bật (Thay thế window.onload cũ)
async function loadInitialProducts() {
    try {
        const response = await fetch(`${API_URL}/products?limit=8`);
        const data = await response.json();
        render(data);
    } catch (error) {
        console.error("Lỗi load sản phẩm:", error);
    }
}

// 3. Hàm lọc theo danh mục (Sửa lỗi allProducts is not defined)
async function filterBy(catId, catName) {
    // 1. Đóng menu lại cho đẹp
    toggleMenu(); 
    
    // 2. Đổi tên tiêu đề trên màn hình
    document.getElementById('cat-name').innerText = catName.toUpperCase();
    
    try {
        // 3. Gọi API với category_id (con số)
        const response = await fetch(`${API_URL}/products?category_id=${catId}&limit=12`);
        const data = await response.json();
        
        // 4. Hiển thị kết quả
        render(data);
        
        // 5. Cuộn xuống phần sản phẩm
        document.getElementById('product-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error("Lỗi lọc danh mục:", error);
    }
}

// 4. Hàm Search (SQL & Vector)
async function handleSearch() {
    const query = document.getElementById('search-input').value;
    if (!query.trim()) return;

    const endpoint = currentSearchMode === 'sql' ? '/search/sql' : '/search/vector';
    
    try {
        const response = await fetch(`${API_URL}${endpoint}?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        render(data);
        document.getElementById('cat-name').innerText = "KẾT QUẢ";
        document.getElementById('product-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error("Lỗi search:", error);
    }
}

// --- Các hàm hỗ trợ UI ---
function setMode(mode) {
    currentSearchMode = mode;
    const sqlOpt = document.getElementById('sql-opt');
    const vecOpt = document.getElementById('vec-opt');
    const input = document.getElementById('search-input');

    sqlOpt.classList.toggle('active', mode === 'sql');
    vecOpt.classList.toggle('active', mode === 'vec');
    input.placeholder = mode === 'sql' ? "Tìm kiếm bằng SQL..." : "Tìm kiếm bằng VECTOR...";
}

function goToDetail(id) {
    window.location.href = `product-detail.html?id=${id}`;
}

function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

// Khởi chạy khi trang web sẵn sàng
window.onload = () => {
    loadInitialProducts();
    
    // Gán sự kiện Enter cho ô search
    const input = document.getElementById('search-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }
};