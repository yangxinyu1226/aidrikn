import gemini_api
import sys
sys.stdout.reconfigure(encoding='utf-8')
result = gemini_api.place_order(product_name='柠檬草莓多多', quantity=5)
print(result)