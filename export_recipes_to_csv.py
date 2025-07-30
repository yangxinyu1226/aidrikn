import db_logic
import sys
import csv
import io

sys.stdout.reconfigure(encoding='utf-8')

all_products = db_logic.get_all_products()

csv_data = []
csv_data.append(['产品ID', '产品名称', '配料名称', '所需数量', '配料单位'])

for product_id, product_name, _ in all_products:
    recipe = db_logic.get_recipe_for_product(product_id)
    if recipe:
        for ing_id, ing_name, qty_needed, unit in recipe:
            csv_data.append([product_id, product_name, ing_name, qty_needed, unit])
    else:
        csv_data.append([product_id, product_name, '', '', ''])

output_buffer = io.StringIO()
csv_writer = csv.writer(output_buffer)
csv_writer.writerows(csv_data)
print(output_buffer.getvalue())