import db_logic as db

def add_product():
    """Handles user input for adding a new product."""
    name = input("请输入产品名称: ")
    try:
        price = float(input("请输入产品价格: "))
    except ValueError:
        print("错误: 价格必须是数字。")
        return

    if not name:
        print("错误: 产品名称不能为空。")
        return

    success, message = db.add_product(name, price)
    print(message)

def record_sale():
    """Guides the user through recording a sale."""
    products = db.get_all_products()
    if not products:
        print("系统中没有产品，请先添加。")
        return

    print("\n--- 选择要销售的产品 ---")
    for i, (pid, name, price) in enumerate(products):
        print(f"{i + 1}. {name} - ¥{price:.2f}")

    try:
        product_choice = int(input("请选择产品序号: ")) - 1
        if not 0 <= product_choice < len(products):
            print("无效的序号。")
            return
        product_id, product_name, _ = products[product_choice]
    except (ValueError, IndexError):
        print("无效输入。")
        return

    try:
        quantity = int(input(f"请输入 '{product_name}' 的销售数量: "))
        if quantity <= 0:
            print("销售数量必须为正整数。")
            return
    except ValueError:
        print("无效输入，请输入一个整数。")
        return

    # The core logic is now handled by db_logic.process_sale
    success, message = db.process_sale(product_id, quantity)
    print(message)

def sales_menu():
    """Displays the sales management menu."""
    while True:
        print("\n--- 销售管理 ---")
        print("1. 添加新产品")
        print("2. 记录一笔销售")
        print("3. 返回主菜单")
        choice = input("请选择操作: ")

        if choice == '1':
            add_product()
        elif choice == '2':
            record_sale()
        elif choice == '3':
            break
        else:
            print("无效输入，请重新选择。")