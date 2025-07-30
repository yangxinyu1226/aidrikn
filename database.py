
import sqlite3

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}, SQLite version: {sqlite3.sqlite_version}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ create tables in the SQLite database """
    try:
        c = conn.cursor()

        # Products table
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL
            );
        """)

        # Ingredients table
        c.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stock_quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                low_stock_threshold REAL NOT NULL DEFAULT 0
            );
        """)

        # Recipes table (many-to-many relationship between products and ingredients)
        c.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                quantity_needed REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
            );
        """)

        # Sales table
        c.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity_sold INTEGER NOT NULL,
                sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_price REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
        """)

        # Inventory Movements table
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_id INTEGER NOT NULL,
                quantity_change REAL NOT NULL, -- Positive for incoming, negative for outgoing
                movement_type TEXT NOT NULL, -- e.g., 'purchase', 'sale_deduction', 'spoilage'
                movement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
            );
        """)

        # Product Attributes table
        c.execute("""
            CREATE TABLE IF NOT EXISTS product_attributes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                attribute_name TEXT NOT NULL,
                attribute_value TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
        """)
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(e)

if __name__ == '__main__':
    db_file = 'nainai_tea.db'
    connection = create_connection(db_file)
    if connection:
        create_tables(connection)
        connection.close()
        print("Database setup complete.")
