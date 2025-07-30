

import db_logic as db

def place_order(product_name: str, quantity: int) -> str:
    """
    Places an order for a given product and quantity.

    Args:
        product_name: The name of the product to order.
        quantity: The number of items to order.

    Returns:
        A string indicating the result of the operation.
    """
    if quantity <= 0:
        return "错误: 销售数量必须为正整数。"

    products = db.get_all_products()
    target_product = None
    for pid, name, _ in products:
        if name == product_name:
            target_product = (pid, name)
            break
    
    if not target_product:
        return f"错误: 未找到名为 '{product_name}' 的产品。"
    
    product_id = target_product[0]
    success, message = db.process_sale(product_id, quantity)
    return message

def add_stock(ingredient_name: str, quantity: float) -> str:
    """
    Adds stock for a given ingredient.

    Args:
        ingredient_name: The name of the ingredient to update.
        quantity: The amount of stock to add (must be positive).

    Returns:
        A string indicating the result of the operation.
    """
    if quantity <= 0:
        return "错误: 入库数量必须为正数。"

    ingredients = db.get_all_ingredients()
    target_ingredient = None
    for ing_id, name, _, _, _ in ingredients:
        if name == ingredient_name:
            target_ingredient = (ing_id, name)
            break

    if not target_ingredient:
        return f"错误: 未找到名为 '{ingredient_name}' 的原料。"

    ingredient_id = target_ingredient[0]
    success, message = db.update_ingredient_stock(ingredient_id, quantity)
    return message

def get_inventory_report() -> str:
    """
    Generates a string report of the current inventory status.

    Returns:
        A formatted string with the inventory report.
    """
    ingredients = db.get_all_ingredients()
    if not ingredients:
        return "库存中没有任何原料."

    report_lines = ["--- 当前库存报告 ---"]
    for _, name, stock, unit, threshold in ingredients:
        status = " (低库存!)" if stock < threshold else ""
        report_lines.append(f"{name}: {stock:.2f} {unit}{status}")
    report_lines.append("---------------------")
    return "\n".join(report_lines)

def get_sales_ranking_report() -> str:
    """
    Generates a sales ranking report.

    Returns:
        A formatted string with the sales ranking.
    """
    ranking = db.get_product_sales_ranking()
    if not ranking:
        return "尚无销售记录。"

    report_lines = ["--- 畅销产品榜 ---"]
    for i, (name, qty, total) in enumerate(ranking, 1):
        report_lines.append(f"{i}. {name} - 总销量: {qty}, 总销售额: ¥{total:.2f}")
    report_lines.append("---------------------")
    return "\n".join(report_lines)

def get_daily_summary_report() -> str:
    """
    Generates a summary report for today's sales.

    Returns:
        A formatted string with today's sales summary.
    """
    orders, sales = db.get_today_summary()
    return f"--- 今日销售简报 ---\n今日总订单数: {orders}\n今日总销售额: ¥{sales:.2f}\n---------------------"


