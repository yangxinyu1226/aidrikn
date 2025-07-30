
import sqlite3
import datetime

DB_FILE = 'nainai_tea.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

# --- Ingredient Logic ---

def add_ingredient(name, stock_quantity, unit, low_stock_threshold):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO ingredients (name, stock_quantity, unit, low_stock_threshold) VALUES (?, ?, ?, ?)",
                  (name, stock_quantity, unit, low_stock_threshold))
        conn.commit()
        return True, f"原料 '{name}' 添加成功！"
    except sqlite3.IntegrityError:
        return False, f"错误: 原料 '{name}' 已存在."
    except sqlite3.Error as e:
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

def get_all_ingredients():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, stock_quantity, unit, low_stock_threshold FROM ingredients ORDER BY name")
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_ingredient_stock(ingredient_id, quantity_change):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE ingredients SET stock_quantity = stock_quantity + ? WHERE id = ?", (quantity_change, ingredient_id))
        c.execute("INSERT INTO inventory_movements (ingredient_id, quantity_change, movement_type) VALUES (?, ?, ?)",
                  (ingredient_id, quantity_change, 'manual_update'))
        conn.commit()
        return True, "库存更新成功！"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

# --- Product Logic ---

def add_product(name, price):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        return True, f"产品 '{name}' 添加成功！"
    except sqlite3.IntegrityError:
        return False, f"错误: 产品 '{name}' 已存在."
    except sqlite3.Error as e:
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

def get_all_products():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, price FROM products ORDER BY name")
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_product_by_name(name):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, price FROM products WHERE name = ?", (name,))
        return c.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Product Attributes Logic ---

def add_product_attribute(product_id, attribute_name, attribute_value):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO product_attributes (product_id, attribute_name, attribute_value) VALUES (?, ?, ?)",
                  (product_id, attribute_name, attribute_value))
        conn.commit()
        return True, f"产品属性 '{attribute_name}: {attribute_value}' 添加成功！"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

def get_product_attributes(product_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT attribute_name, attribute_value FROM product_attributes WHERE product_id = ?", (product_id,))
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Recipe Logic ---

def save_recipe(product_id, ingredients_list):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM recipes WHERE product_id = ?", (product_id,))
        if ingredients_list:
            c.executemany("INSERT INTO recipes (product_id, ingredient_id, quantity_needed) VALUES (?, ?, ?)", 
                          [(product_id, ing_id, qty) for ing_id, qty in ingredients_list])
        conn.commit()
        return True, "配方保存成功！"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

def get_recipe_for_product(product_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT i.id, i.name, r.quantity_needed, i.unit
            FROM recipes r
            JOIN ingredients i ON r.ingredient_id = i.id
            WHERE r.product_id = ?
        """, (product_id,))
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Sales Logic ---

def process_sale(product_id, quantity):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Check stock. Fetch ID, needed quantity, current stock, and name.
        c.execute("""
            SELECT 
                i.id, 
                r.quantity_needed * ?, 
                i.stock_quantity, 
                i.name 
            FROM recipes r 
            JOIN ingredients i ON r.ingredient_id = i.id 
            WHERE r.product_id = ?
        """, (quantity, product_id))
        ingredients_needed = c.fetchall()
        
        if not ingredients_needed:
            return False, "该产品没有配方，无法销售。"

        # First, check if all ingredients are in stock before making any changes.
        for _, needed, stock, name in ingredients_needed:
            if stock < needed:
                return False, f"库存不足: {name}"

        # If all checks pass, then deduct stock.
        for ing_id, needed, _, _ in ingredients_needed:
            c.execute("UPDATE ingredients SET stock_quantity = stock_quantity - ? WHERE id = ?", (needed, ing_id))
            c.execute("INSERT INTO inventory_movements (ingredient_id, quantity_change, movement_type) VALUES (?, ?, ?)",
                      (ing_id, -needed, 'sale_deduction'))

        # Record sale
        c.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        price = c.fetchone()[0]
        total_price = price * quantity
        c.execute("INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (?, ?, ?)", (product_id, quantity, total_price))
        
        conn.commit()
        return True, f"销售成功！总价: {total_price:.2f}"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"数据库错误: {e}"
    finally:
        if conn:
            conn.close()

# --- Reporting Logic ---

def get_today_summary():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(id), SUM(total_price) FROM sales WHERE DATE(sale_time) = ?", (today_str,))
        result = c.fetchone()
        return result[0] or 0, result[1] or 0.0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0, 0.0
    finally:
        if conn:
            conn.close()

def get_product_sales_ranking():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.name, SUM(s.quantity_sold), SUM(s.total_price)
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name
            ORDER BY SUM(s.quantity_sold) DESC
        """)
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_recent_sales(limit=50):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT s.sale_time, p.name, s.quantity_sold, s.total_price
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_time DESC
            LIMIT ?
        """, (limit,))
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()
