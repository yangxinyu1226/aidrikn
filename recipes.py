import db_logic as db

def add_or_edit_recipe():
    """Guides the user to create or modify a recipe for a product."""
    products = db.get_all_products()
    if not products:
        print("请先添加产品后再创建配方。")
        return

    print("\n--- 选择要添加/修改配方的产品 ---")
    for i, (pid, name, price) in enumerate(products):
        print(f"{i + 1}. {name}")
    
    try:
        product_choice = int(input("请选择产品序号: ")) - 1
        if not 0 <= product_choice < len(products):
            print("无效的序号。")
            return
        product_id, product_name, _ = products[product_choice]
    except (ValueError, IndexError):
        print("无效输入。")
        return

    ingredients = db.get_all_ingredients()
    if not ingredients:
        print("请先添加原料后再创建配方。")
        return

    # Display current recipe for reference
    print(f"\n正在为 '{product_name}' 编辑配方。当前配方为:")
    current_recipe = db.get_recipe_for_product(product_id)
    if not current_recipe:
        print(" (无)")
    else:
        for _, name, qty, unit in current_recipe:
            print(f"  - {name}: {qty} {unit}")

    selected_ingredients = []
    print("\n--- 请选择原料并输入用量 (输入0完成) ---")
    while True:
        for i, (iid, name, _, unit, _) in enumerate(ingredients):
            print(f"{i + 1}. {name} ({unit})")
        print("0. 完成并保存")

        try:
            ingredient_choice = int(input("请选择原料序号: "))
            if ingredient_choice == 0:
                break
            if not 0 < ingredient_choice <= len(ingredients):
                print("无效的序号。")
                continue
            
            ing_id, ing_name, _, _, _ = ingredients[ingredient_choice - 1]
            quantity_needed = float(input(f"制作一份 '{product_name}' 需要多少 '{ing_name}'? "))
            if quantity_needed <= 0:
                print("用量必须是正数。")
                continue
            
            selected_ingredients.append((ing_id, quantity_needed))
            print(f"已添加: {quantity_needed} 的 {ing_name}")

        except (ValueError, IndexError):
            print("无效输入。")

    if not selected_ingredients:
        # Ask if user wants to clear the recipe
        confirm_clear = input(f"没有选择任何原料。是否要清空 '{product_name}' 的配方? (y/n): ").lower()
        if confirm_clear != 'y':
            print("操作已取消。")
            return

    success, message = db.save_recipe(product_id, selected_ingredients)
    print(message)

def view_recipes():
    """View all recipes for all products."""
    products = db.get_all_products()
    if not products:
        print("系统中没有产品。")
        return

    print("\n--- 所有产品配方 ---")
    found_any_recipe = False
    for pid, name, _ in products:
        recipe_data = db.get_recipe_for_product(pid)
        if recipe_data:
            found_any_recipe = True
            print(f"\n产品: {name}")
            for _, ing_name, quantity, unit in recipe_data:
                print(f"  - {ing_name}: {quantity} {unit}")
    
    if not found_any_recipe:
        print("尚未为任何产品创建配方。")
    print("---------------------")

def recipe_menu():
    """Displays the recipe management menu."""
    while True:
        print("\n--- 配方管理 ---")
        print("1. 添加/修改产品配方")
        print("2. 查看所有配方")
        print("3. 返回主菜单")
        choice = input("请选择操作: ")

        if choice == '1':
            add_or_edit_recipe()
        elif choice == '2':
            view_recipes()
        elif choice == '3':
            break
        else:
            print("无效输入，请重新选择。")