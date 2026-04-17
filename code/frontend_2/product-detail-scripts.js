const API_URL = "http://127.0.0.1:8000";
const TECHNA_ICON = "₸"; 

window.onload = async () => {
    // 1. Lấy ID từ URL (?id=...)
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    if (!productId) {
        alert("Không tìm thấy mã sản phẩm!");
        window.location.href = "index.html";
        return;
    }

    try {
        // 2. Gọi API từ Backend
        const response = await fetch(`${API_URL}/products/${productId}`);
        
        if (!response.ok) {
            throw new Error("Sản phẩm không tồn tại");
        }

        const product = await response.json();

        // 3. Đổ dữ liệu vào các thẻ HTML tương ứng
        document.title = `${product.name} | TechnaLG`;
        
        // Tên sản phẩm
        document.getElementById('product-title').innerText = product.name;
        
        // Giá sản phẩm + Icon lấp lánh
        const formattedPrice = Number(product.price).toLocaleString();
        document.getElementById('product-price').innerText = `Giá: ${formattedPrice} ${TECHNA_ICON}`;
        
        // Mô tả sản phẩm
        document.getElementById('product-desc').innerHTML = `<p>${product.description}</p>`;

        // Ảnh sản phẩm
        const imgElement = document.getElementById('product-img');
        imgElement.src = `${API_URL}/static/${product.image_path}`;
        
        // Xử lý nếu ảnh lỗi
        imgElement.onerror = () => { 
            imgElement.src = 'logo 1.png'; 
        };

    } catch (error) {
        console.error("Lỗi:", error);
        document.querySelector('main').innerHTML = `
            <div style="text-align:center; padding: 50px; color: white;">
                <h1>404</h1>
                <p>Sản phẩm không tồn tại hoặc đã bị xóa khỏi hệ thống TechnaLG.</p>
                <a href="index.html" style="color: #00ffff;">Quay lại cửa hàng</a>
            </div>`;
    }
};

document.getElementById('back_button').addEventListener('click', function() {
    // Kiểm tra xem có trang trước đó trong lịch sử không
    if (document.referrer.includes(window.location.hostname)) {
        window.history.back();
    } else {
        // Nếu vào trực tiếp bằng link, quay về trang chủ
        window.location.href = 'index.html';
    }

});

