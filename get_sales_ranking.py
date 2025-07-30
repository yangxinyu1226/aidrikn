import db_logic
import sys
sys.stdout.reconfigure(encoding='utf-8')
ranking = db_logic.get_product_sales_ranking()
if ranking:
    print("--- 产品销售排行榜 ---")
    for i, (name, qty, total) in enumerate(ranking, 1):
        print(f"{i}. {name} - 总销量: {qty}, 总销售额: ¥{total:.2f}")
    print("---------------------")
else:
    print("目前没有销售记录。")