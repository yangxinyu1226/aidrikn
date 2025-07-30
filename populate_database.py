import sqlite3
import random

def clear_existing_data(c):
    """Clears products, recipes, and ingredients tables."""
    print("Clearing existing products, recipes, sales, and inventory movements...")
    c.execute("DELETE FROM sales")
    c.execute("DELETE FROM inventory_movements")
    c.execute("DELETE FROM recipes")
    c.execute("DELETE FROM products")
    c.execute("DELETE FROM ingredients")
    print("Data cleared.")

def populate_ingredients(c):
    """Populates the ingredients table with a base set of ingredients."""
    print("Populating base ingredients...")
    ingredients = [
        # Teas (unit: kg)
        ('锡兰红茶', 10.0, 'kg', 1.0), ('阿萨姆红茶', 10.0, 'kg', 1.0),
        ('茉莉绿茶', 10.0, 'kg', 1.0), ('四季春乌龙', 10.0, 'kg', 1.0),
        ('金萱乌龙', 10.0, 'kg', 1.0), ('白桃乌龙', 10.0, 'kg', 1.0),
        
        # Milks (unit: L)
        ('鲜牛奶', 50.0, 'L', 5.0), ('纯牛奶', 50.0, 'L', 5.0),
        ('厚乳', 30.0, 'L', 3.0), ('燕麦奶', 20.0, 'L', 2.0),
        ('椰奶', 30.0, 'L', 3.0),

        # Fruits (unit: kg)
        ('新鲜柠檬', 20.0, 'kg', 2.0), ('新鲜草莓', 15.0, 'kg', 1.5),
        ('新鲜葡萄', 15.0, 'kg', 1.5), ('新鲜芒果', 15.0, 'kg', 1.5),
        ('新鲜百香果', 10.0, 'kg', 1.0), ('新鲜西瓜', 30.0, 'kg', 3.0),
        ('新鲜桃子', 15.0, 'kg', 1.5), ('新鲜橙子', 20.0, 'kg', 2.0),

        # Toppings (unit: kg)
        ('黑糖珍珠', 20.0, 'kg', 2.0), ('寒天晶球', 20.0, 'kg', 2.0),
        ('椰果', 20.0, 'kg', 2.0), ('烧仙草', 20.0, 'kg', 2.0),
        ('红豆', 15.0, 'kg', 1.5), ('布丁', 15.0, 'kg', 1.5),
        ('奶盖粉', 10.0, 'kg', 1.0), ('奥利奥碎', 10.0, 'kg', 1.0),

        # Syrups & Others (unit: L)
        ('果糖', 40.0, 'L', 4.0), ('黑糖糖浆', 10.0, 'L', 1.0),
        ('蜂蜜', 10.0, 'L', 1.0), ('冰块', 500.0, 'kg', 20.0)
    ]
    c.executemany("INSERT INTO ingredients (name, stock_quantity, unit, low_stock_threshold) VALUES (?, ?, ?, ?)", ingredients)
    print(f"{len(ingredients)} ingredients populated.")
    return {name: (i+1, unit) for i, (name, _, unit, _) in enumerate(ingredients)}

def generate_products_and_recipes(c, ingredient_map):
    """Generates a list of products and their recipes."""
    print("Generating products and recipes...")
    teas = ['锡兰红茶', '阿萨姆红茶', '茉莉绿茶', '四季春乌龙', '金萱乌龙', '白桃乌龙']
    milks = ['鲜牛奶', '纯牛奶', '厚乳', '燕麦奶', '椰奶']
    fruits = ['柠檬', '草莓', '葡萄', '芒果', '百香果', '西瓜', '桃子', '橙子']
    toppings = ['黑糖珍珠', '寒天晶球', '椰果', '烧仙草', '红豆', '布丁', '奶盖粉', '奥利奥碎']
    sweeteners = ['果糖', '黑糖糖浆', '蜂蜜']

    generated_products = set()
    products_to_insert = []
    recipes_to_insert = []

    # Generate ~60 classic milk teas
    for _ in range(60):
        tea = random.choice(teas)
        milk = random.choice(milks)
        topping1 = random.choice(toppings)
        topping2 = random.choice(toppings)
        
        name = f"{tea.replace('红茶','').replace('绿茶','').replace('乌龙','')}{milk.replace('鲜牛','').replace('纯','')}{topping1.replace('黑糖','')}"
        if topping1 != topping2 and random.random() > 0.6:
            name = f"{name}{topping2.replace('黑糖','')}"
        
        if name not in generated_products:
            price = round(random.uniform(8, 20), 1)
            products_to_insert.append((name, price))
            generated_products.add(name)
            product_id = len(products_to_insert)
            
            # Create recipe
            recipes_to_insert.append((product_id, ingredient_map[tea][0], round(random.uniform(0.08, 0.12), 3)))
            recipes_to_insert.append((product_id, ingredient_map[milk][0], round(random.uniform(0.1, 0.15), 3)))
            recipes_to_insert.append((product_id, ingredient_map[topping1][0], round(random.uniform(0.05, 0.08), 3)))
            if topping1 != topping2 and random.random() > 0.6:
                recipes_to_insert.append((product_id, ingredient_map[topping2][0], round(random.uniform(0.04, 0.06), 3)))
            recipes_to_insert.append((product_id, ingredient_map[random.choice(sweeteners)][0], round(random.uniform(0.01, 0.02), 3)))
            recipes_to_insert.append((product_id, ingredient_map['冰块'][0], 0.15))

    # Generate ~40 fruit teas
    for _ in range(40):
        tea = random.choice(teas[:3]) # Use more basic teas for fruit tea
        fruit1 = random.choice(fruits)
        fruit2 = random.choice(fruits)
        topping = random.choice(toppings[:3]) # Common toppings for fruit tea

        name = f"满杯{fruit1}"
        if fruit1 != fruit2 and random.random() > 0.7:
            name = f"{fruit1}{fruit2}多多"

        if name not in generated_products:
            price = round(random.uniform(12, 20), 1)
            products_to_insert.append((name, price))
            generated_products.add(name)
            product_id = len(products_to_insert)

            # Create recipe
            recipes_to_insert.append((product_id, ingredient_map[f'新鲜{fruit1}'][0], round(random.uniform(0.1, 0.15), 3)))
            if fruit1 != fruit2 and random.random() > 0.7:
                recipes_to_insert.append((product_id, ingredient_map[f'新鲜{fruit2}'][0], round(random.uniform(0.08, 0.12), 3)))
            recipes_to_insert.append((product_id, ingredient_map[tea][0], round(random.uniform(0.08, 0.12), 3)))
            if random.random() > 0.5:
                 recipes_to_insert.append((product_id, ingredient_map[topping][0], round(random.uniform(0.05, 0.08), 3)))
            recipes_to_insert.append((product_id, ingredient_map[random.choice(sweeteners)][0], round(random.uniform(0.015, 0.025), 3)))
            recipes_to_insert.append((product_id, ingredient_map['冰块'][0], 0.20))

    c.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products_to_insert)
    c.executemany("INSERT INTO recipes (product_id, ingredient_id, quantity_needed) VALUES (?, ?, ?)", recipes_to_insert)
    print(f"{len(products_to_insert)} products and their recipes have been generated.")

if __name__ == '__main__':
    db_file = 'nainai_tea.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        # Run the process
        clear_existing_data(c)
        ingredient_map = populate_ingredients(c)
        generate_products_and_recipes(c, ingredient_map)
        
        conn.commit()
        print("\nDatabase population complete! Your system is ready.")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()
