begin;
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE budgets (
    budget_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,

    category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
	budget_id int  REFERENCES budgets(budget_id) ON DELETE SET NULL,

    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),

    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),

    image_path TEXT,

    description TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_products_description
ON products USING gin (description gin_trgm_ops);

CREATE INDEX idx_products_category_id 
ON products(category_id);

CREATE INDEX idx_products_brand 
ON products(brand);

CREATE INDEX idx_products_name_gin ON products USING gin (name gin_trgm_ops);

CREATE INDEX idx_products_price ON products(price);

commit;


