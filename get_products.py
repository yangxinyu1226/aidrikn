import db_logic
import sys
sys.stdout.reconfigure(encoding='utf-8')
products = db_logic.get_all_products()
if products:
    print("--- 可销售产品列表 ---")
    for p_id, name, price in products:
        print(f"产品ID: {p_id}, 名称: {name}, 价格: ¥{price:.2f}")
    print("---------------------")
else:
    print("目前没有可销售的产品。")