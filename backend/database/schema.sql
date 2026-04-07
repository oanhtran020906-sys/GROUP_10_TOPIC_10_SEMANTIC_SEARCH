CREATE TABLE products (
    id SERIAL PRIMARY KEY,

    category_id INTEGER REFERENCES categories(id),

    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),

    price DECIMAL(12, 2) NOT NULL, -- ví dụ: 11000000.00

    image_url TEXT,

    -- Mô tả chi tiết (dùng cho SQL + embedding)
    description TEXT NOT NULL,

    -- Field tối ưu search (SQL + vector)
    search_blob TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);