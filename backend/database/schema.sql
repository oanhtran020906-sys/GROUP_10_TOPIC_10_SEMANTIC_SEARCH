DROP DATABASE IF EXISTS semantic_search;
CREATE DATABASE semantic_search;

DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,

    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,

    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),

    price DECIMAL(12, 2) NOT NULL,

    image_path TEXT,

    description TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_products_search_blob 
ON products USING gin (search_blob gin_trgm_ops);

CREATE INDEX idx_products_category_id 
ON products(category_id);

CREATE INDEX idx_products_brand 
ON products(brand);


CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);