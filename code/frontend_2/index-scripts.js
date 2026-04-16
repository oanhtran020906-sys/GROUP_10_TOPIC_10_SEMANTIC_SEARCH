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
                <div class="product-price">${Number(p.price).toLocaleString()}₸</div>
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

// 4. Hàm Search (SQL, Vector, Hybrid)
async function handleSearch() {
    const query = document.getElementById('search-input').value;
    if (!query.trim()) return;

    const container = document.getElementById('product-display');
    const loading = document.getElementById('loading');
    
    // --- BẮT ĐẦU LOADING ---
    container.style.opacity = "0.3"; // Làm mờ danh sách cũ
    loading.style.display = "block"; // Hiện thông báo loading

    const endpoint = currentSearchMode === 'sql'
    ? '/search/sql'
    : currentSearchMode === 'vec'
        ? '/search/vector'
        : '/search/hybrid';
    
    try {
        const response = await fetch(`${API_URL}${endpoint}?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        render(data);
        document.getElementById('cat-name').innerText = "KẾT QUẢ";
        document.getElementById('product-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error("Lỗi search:", error);
    } finally {
        // --- KẾT THÚC LOADING ---
        loading.style.display = "none";
        container.style.opacity = "1";
    }
}


// --- Các hàm hỗ trợ UI ---
function setMode(mode) {
    currentSearchMode = mode;
    const sqlOpt = document.getElementById('sql-opt');
    const vecOpt = document.getElementById('vec-opt');
    const hybridOpt = document.getElementById('hybrid-opt');
    const input = document.getElementById('search-input');

    sqlOpt.classList.toggle('active', mode === 'sql');
    vecOpt.classList.toggle('active', mode === 'vec');
    hybridOpt.classList.toggle('active', mode === 'hybrid');
    input.placeholder = mode === 'sql' 
    ? "Tìm kiếm bằng SQL..."
    : mode === 'vec'
    ? "Tìm kiếm bằng VECTOR..."
    : "Tìm kiếm bằng HYBRID...";
}

function goToDetail(id) {
    window.location.href = `product-detail.html?id=${id}`;
}

function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

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

const modal = document.getElementById("modal");
const inputfile = document.getElementById("inputfile");

function handleImageSearch() {
    modal.style.display = "flex";
}

function closePopup() {
    modal.style.display = "none";
}

let selectedFile = null;

function uploadImage() {
    // Kích hoạt chọn file
    document.getElementById('inputfile').click();
}

// Xử lý khi chọn file xong
document.getElementById('inputfile').onchange = function (event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            const previewImg = document.getElementById('preview-img');
            const defaultIcon = document.getElementById('default-icon');
            const searchBtn = document.getElementById('search-btn');
            const uploadText = document.getElementById('upload-text');

            // Hiển thị ảnh preview
            previewImg.src = e.target.result;
            previewImg.style.display = "block";
            previewImg.style.filter = "none"; // Chống đảo màu
            
            // Ẩn icon cũ
            defaultIcon.style.display = "none";
            
            // Hiện nút bấm
            searchBtn.style.display = "inline-block";
            uploadText.innerText = "CHANGE IMAGE";
        };
        reader.readAsDataURL(file);
    }
};

async function executeImageSearch() {
    if (!selectedFile) return;

    const container = document.getElementById('product-display');
    const searchBtn = document.getElementById('search-btn');

    // Vừa hiện loading vừa đổi text nút search cho ngầu
    container.style.opacity = "0.3";
    searchBtn.innerText = "ANALYZING...";
    searchBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${API_URL}/search/image?limit=8`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        render(data);
        document.getElementById('cat-name').innerText = "KẾT QUẢ ẢNH";
        document.getElementById('product-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error("Lỗi search ảnh:", error);
    } finally {
        // Trả lại trạng thái cũ
        container.style.opacity = "1";
        searchBtn.innerText = "SEARCH NOW";
        searchBtn.disabled = false;
    }
}

function closePopup() {
    const modal = document.getElementById("modal");
    modal.style.display = "none";
    
    // Reset trạng thái
    selectedFile = null;
    document.getElementById('inputfile').value = "";
    document.getElementById('preview-img').style.display = "none";
    document.getElementById('default-icon').style.display = "block";
    document.getElementById('search-btn').style.display = "none";
    document.getElementById('upload-text').innerText = "UPLOAD IMAGE";
}