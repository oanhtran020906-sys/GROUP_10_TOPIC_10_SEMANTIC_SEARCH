import React, { useState } from 'react';

// Dữ liệu mẫu cho sản phẩm (sau này sẽ lấy từ API)
const initialProducts = [
  { id: 1, name: "Cánh Tiên Tử Công Nghệ", brand: "TechnaLG", price: 5000000, image: "https://via.placeholder.com/300?text=Tecna+Wings" },
  { id: 2, name: "Vương Miện Ngôi Sao Phép Thuật", brand: "Alfea", price: 12000000, image: "https://via.placeholder.com/300?text=Winx+Crown" },
  { id: 3, name: "Máy Tính Bảng Ma Thuật", brand: "TechnaLG", price: 25000000, image: "https://via.placeholder.com/300?text=Magic+Tablet" },
  { id: 4, name: "Giày Bay Siêu Tốc", brand: "Zenith", price: 8000000, image: "https://via.placeholder.com/300?text=Speed+Boots" },
];

const Home = () => {
  const [searchMode, setSearchMode] = useState('vector'); // 'sql' hoặc 'vector'
  const [query, setQuery] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Trạng thái đóng/mở sidebar

  return (
    <div className="min-h-screen tech-grid relative pb-20">
      
    {/* --- PHẦN 1: HEADER (Thanh điều hướng trên cùng) --- */}
      <header className="fixed top-0 left-0 w-full p-6 flex justify-between items-center z-50">
        
        {/* NÚT MỞ SIDEBAR (Góc trên bên trái) */}
        <button 
          onClick={() => setIsSidebarOpen(true)}
          className="group flex items-center gap-2 bg-gray-900/80 p-3 px-4 rounded-2xl border border-gray-700 text-[#10b981] hover:neon-glow-green transition-all duration-300 backdrop-blur-sm"
        >
          <div className="relative">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            {/* Chấm tròn nhỏ lấp lánh trên nút menu */}
            <span className="absolute -top-1 -right-1 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
            </span>
          </div>
          <span className="font-mono text-sm font-bold hidden md:block">MENU</span>
        </button>

        {/* CỤM NÚT CHẾ ĐỘ (Góc trên bên phải) */}
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-500 font-mono hidden sm:block uppercase tracking-widest italic">Magic System:</span>
          <div className="flex bg-gray-900/80 p-1 rounded-full border border-gray-700 backdrop-blur-sm shadow-xl">
            <button 
              onClick={() => setSearchMode('sql')}
              className={`px-5 py-2 rounded-full text-sm font-bold font-mono transition-all duration-300 ${
                searchMode === 'sql' 
                ? 'bg-[#10b981] text-white neon-glow-green scale-105' 
                : 'text-gray-400 hover:text-white'
              }`}
            >
              SQL
            </button>
            <button 
              onClick={() => setSearchMode('vector')}
              className={`px-5 py-2 rounded-full text-sm font-bold font-mono transition-all duration-300 ${
                searchMode === 'vector' 
                ? 'bg-[#8b5cf6] text-white neon-glow-purple scale-105' 
                : 'text-gray-400 hover:text-white'
              }`}
            >
              VECTOR
            </button>
          </div>
        </div>
      </header>

      {/* --- PHẦN 2: HERO SECTION (Chính giữa) --- */}
      <section className="flex flex-col items-center justify-center pt-48 pb-24 px-4 sparkle-bg">
        {/* Tên cửa hàng */}
        <div className="flex flex-col items-center mb-16 space-y-2">
          <h1 className="text-7xl font-extrabold tracking-tighter text-center">
            <span className="text-[#8b5cf6]">Techna</span><span className="text-[#10b981]">LG</span>
          </h1>
          <p className="text-xl text-gray-400 font-mono tracking-widest uppercase">
            Magic • Technology • Zenith
          </p>
          <div className="flex space-x-2 text-yellow-300 text-2xl pt-2">
            <span>✦</span><span>★</span><span>✦</span>
          </div>
        </div>

        {/* Thanh tìm kiếm to đùng, biến màu theo chế độ */}
        <div className="w-full max-w-4xl relative group">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className={`w-full p-8 pl-16 text-3xl rounded-3xl border-2 shadow-2xl outline-none transition-all duration-500 font-mono ${searchMode === 'sql' ? 'bg-[#10b981]/10 border-[#10b981] focus:neon-glow-green placeholder-[#10b981]/60' : 'bg-[#8b5cf6]/10 border-[#8b5cf6] focus:neon-glow-purple placeholder-[#8b5cf6]/60'}`}
            placeholder={`Tìm kiếm bằng ${searchMode.toUpperCase()}...`}
          />
          {/* Icon kính lúp phép thuật */}
          <svg className={`absolute left-9 top-1/2 -translate-y-1/2 h-8 w-8 transition-colors duration-500 ${searchMode === 'sql' ? 'text-[#10b981]' : 'text-[#8b5cf6]'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {/* Nút tìm kiếm nhỏ lấp lánh */}
          <button className={`absolute right-7 top-1/2 -translate-y-1/2 p-5 rounded-2xl text-white transition-all duration-500 ${searchMode === 'sql' ? 'bg-[#10b981] neon-glow-green' : 'bg-[#8b5cf6] neon-glow-purple'}`}>
            ✦
          </button>
        </div>
      </section>

      {/* --- PHẦN 3: DANH SÁCH SẢN PHẨM --- */}
      <main className="max-w-7xl mx-auto px-6 py-20 relative">
        <div className="absolute inset-0 tech-grid opacity-20 z-0"></div>
        <div className="flex items-center justify-between mb-12 relative z-10">
          <h2 className="text-4xl font-bold tracking-tight">
            Sản phẩm nổi bật
          </h2>
          <div className="h-1 w-32 bg-gray-700 rounded-full"></div>
        </div>
        
        {/* Lưới sản phẩm */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-10 relative z-10">
          {initialProducts.map(product => (
            <div key={product.id} className="bg-gray-900 p-6 rounded-3xl shadow-lg border border-gray-800 transition-all duration-300 hover:border-[#8b5cf6] hover:neon-glow-purple group">
              <div className="w-full h-56 rounded-2xl bg-gray-800 mb-6 overflow-hidden flex items-center justify-center p-4">
                <img 
                  src={product.image} 
                  alt={product.name} 
                  className="h-full object-contain transition-transform duration-500 group-hover:scale-110"
                />
              </div>
              <div className="space-y-3">
                <span className="text-xs font-bold text-[#10b981] uppercase tracking-widest font-mono">
                  {product.brand}
                </span>
                <h3 className="text-xl font-semibold text-gray-100 line-clamp-2 h-14 leading-tight">
                  {product.name}
                </h3>
                <div className="flex items-center justify-between pt-3">
                  <p className="text-2xl font-bold text-red-500 font-mono">
                    {product.price.toLocaleString('vi-VN')} đ
                  </p>
                  <button className="bg-gray-800 text-white p-3 rounded-xl hover:bg-[#8b5cf6]">
                    ★
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

    {/* --- PHẦN 4: FOOTER --- */}
      <footer className="mt-20 py-10 text-center text-gray-600 bg-black/30 border-t border-gray-800 relative z-10 font-mono text-sm">
        <p>© 2024 TechnaLG Store - Phép thuật Zenith trong từng sản phẩm</p>
      </footer>

      {/* --- SIDEBAR DANH MỤC (Thêm vào cuối cùng để đè lên layer khác) --- */}
      
      {/* 1. Lớp phủ đen khi mở sidebar (Overlay) */}
      <div 
        className={`fixed inset-0 bg-black/70 backdrop-blur-md z-[60] transition-opacity duration-500 ${
          isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setIsSidebarOpen(false)}
      ></div>

      {/* 2. Nội dung Sidebar (Panel) */}
      <div className={`fixed top-0 left-0 h-full w-72 bg-gray-900 border-r border-[#8b5cf6]/40 z-[70] transition-all duration-500 ease-out shadow-2xl transform ${
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Họa tiết lưới caro chìm bên trong Sidebar */}
        <div className="absolute inset-0 tech-grid opacity-10 pointer-events-none"></div>

        <div className="relative p-6 h-full flex flex-col">
          {/* Header của Sidebar */}
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-2xl font-bold text-[#8b5cf6] tracking-tighter">DANH MỤC</h2>
              <div className="h-1 w-10 bg-[#10b981] mt-1"></div>
            </div>
            <button 
              onClick={() => setIsSidebarOpen(false)} 
              className="w-10 h-10 flex items-center justify-center rounded-full bg-gray-800 text-gray-400 hover:text-white hover:bg-red-500/20 transition-all"
            >
              ✕
            </button>
          </div>
          
          {/* Danh sách các item */}
          <ul className="space-y-6 font-mono flex-grow">
            {['Camera', 'Điện Thoại', 'Đồng hồ thông minh', 'Máy tính bảng', 'Bàn phím', 'Màn hình', 'Tai nghe', 'Laptop', 'Chuột máy tính', 'Loa'].map((cat) => (
              <li 
                key={cat} 
                className="text-gray-300 hover:text-[#10b981] cursor-pointer transition-all duration-300 flex items-center gap-4 group"
              >
                <span className="w-2 h-2 rounded-full bg-[#8b5cf6] group-hover:bg-[#10b981] group-hover:scale-150 transition-all shadow-[0_0_8px_#8b5cf6]"></span>
                <span className="tracking-wide group-hover:translate-x-2 transition-transform uppercase text-sm">
                  {cat}
                </span>
                <span className="ml-auto opacity-0 group-hover:opacity-100 text-[#10b981] animate-pulse">✦</span>
              </li>
            ))}
          </ul>
          
          {/* Version & Credits ở dưới cùng Sidebar */}
          <div className="mt-auto pt-10 border-t border-gray-800">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
              <span className="text-[10px] text-gray-500 font-mono uppercase tracking-[0.2em]">TechnaLG OS v1.0</span>
            </div>
            <p className="text-[10px] text-gray-600 font-mono italic">"Phép thuật nằm ở các dòng code"</p>
          </div>
        </div>
      </div>

    </div> // Thẻ đóng của div chính (min-h-screen)
  );
};

export default Home;