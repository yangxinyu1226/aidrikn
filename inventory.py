import db_logic as db

def add_ingredient():
    """Handles user input for adding a new ingredient."""
    name = input("请输入原料名称: ")
    try:
        stock_quantity = float(input("请输入初始库存数量: "))
        low_stock_threshold = float(input("请输入低库存阈值: "))
    except ValueError:
        print("错误: 库存和阈值必须是数字。")
        return
    unit = input("请输入单位 (例如: kg, L, 个): ")
    if not all([name, unit]):
        print("错误: 名称和单位不能为空。")
        return
    
    success, message = db.add_ingredient(name, stock_quantity, unit, low_stock_threshold)
    print(message)

def view_inventory():
    """Displays the current inventory status."""
    ingredients = db.get_all_ingredients()
    if not ingredients:
        print("库存中没有任何原料.")
        return

    print("\n--- 当前库存 ---")
    # id, name, stock_quantity, unit, low_stock_threshold
    for _, name, stock, unit, threshold in ingredients:
        status = "(低库存!)" if stock < threshold else ""
        print(f"{name}: {stock} {unit} {status}")
    print("-----------------")

def update_stock():
    """Handles user input for updating stock of an ingredient."""
    ingredient_name = input("请输入要更新库存的原料名称: ")
    
    all_ingredients = db.get_all_ingredients()
    target_ingredient = None
    # Find the ingredient by name to get its ID
    for ing_id, name, _, _, _ in all_ingredients:
        if name == ingredient_name:
            target_ingredient = (ing_id, name)
            break
            
    if not target_ingredient:
        print(f"错误: 未找到原料 '{ingredient_name}'.")
        return
        
    try:
        quantity_change = float(input(f"请输入为 '{ingredient_name}' 添加入库数量 (正数): "))
        if quantity_change <= 0:
            print("入库数量必须为正数。")
            return
    except ValueError:
        print("错误: 数量必须是数字。")
        return

    success, message = db.update_ingredient_stock(target_ingredient[0], quantity_change)
    print(message)


def inventory_menu():
    """Displays the inventory management menu."""
    while True:
        print("\n--- 库存管理 ---")
        print("1. 添加新原料")
        print("2. 查看当前库存")
        print("3. 更新库存 (采购入库)")
        print("4. 返回主菜单")
        choice = input("请选择操作: ")

        if choice == '1':
            add_ingredient()
        elif choice == '2':
            view_inventory()
        elif choice == '3':
            update_stock()
        elif choice == '4':
            break
        else:
            print("无效输入，请重新选择。")