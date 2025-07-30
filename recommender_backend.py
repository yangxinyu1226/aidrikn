from flask import Flask, request, jsonify
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import db_logic
from openai import OpenAI
import gemini_api # 导入 gemini_api

app = Flask(__name__)
CORS(app) 

# 从环境变量获取DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set.")

# 初始化DeepSeek客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

@app.route('/order', methods=['POST'])
def create_order():
    product_name = request.json.get('product_name')
    quantity = request.json.get('quantity')

    if not product_name or not quantity:
        return jsonify({"error": "产品名称或数量未提供"}), 400

    # 验证产品是否存在
    product_data = db_logic.get_product_by_name(product_name)
    if not product_data:
        return jsonify({"error": f"产品 '{product_name}' 不存在，请检查产品名称。"}), 404

    try:
        # 调用下单API
        order_result = gemini_api.place_order(product_name=product_name, quantity=quantity)
        
        return jsonify({"message": "订单已成功处理。", "order_details": order_result}), 200

    except Exception as e:
        print(f"处理订单时发生错误: {e}")
        return jsonify({"error": f"订单服务暂时不可用，请稍后再试。错误信息: {str(e)}"}), 500


@app.route('/recommend', methods=['POST'])
def recommend_drink():
    user_preference = request.json.get('preference')
    if not user_preference:
        return jsonify({"error": "Preference not provided"}), 400

    # 1. 获取所有产品及其属性
    all_products_data = db_logic.get_all_products()
    products_with_attributes = []
    product_name_map = {}

    for p_id, name, price in all_products_data:
        attributes = db_logic.get_product_attributes(p_id)
        attr_str = ", ".join([f"{attr[0]}: {attr[1]}" for attr in attributes])
        products_with_attributes.append(f"产品名称: {name}, 价格: ¥{price:.2f}, 属性: {attr_str}")
        product_name_map[name] = {"id": p_id, "price": price}

    if not products_with_attributes:
        return jsonify({"message": "目前没有可推荐的饮品数据。"}), 200

    # 2. 构建Prompt
    system_prompt = (
        "你是一个专业的茶饮店智能推荐师。你的任务是根据用户的偏好，从提供的饮品列表中推荐最适合的一款饮品。\n"
        "请严格按照以下步骤进行：\n"
        "1. 仔细阅读用户的偏好。\n"
        "2. 从提供的饮品列表中，选择最符合用户偏好的一款饮品。\n"
        "3. 你的回答必须只包含推荐的饮品名称，不要有任何其他文字、解释或标点符号。\n"
        "例如：\n"
        "柠檬草莓多多"
    )

    user_prompt = (
        f"用户偏好: {user_preference}\n\n"
        f"可供选择的饮品列表:\n{';\n'.join(products_with_attributes)}\n\n"
        "请推荐一款饮品。"
    )

    try:
        # 3. 调用DeepSeek API
        chat_completion = client.chat.completions.create(
            model="deepseek-chat", # 或者其他DeepSeek模型，如 deepseek-coder
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7, # 控制生成文本的随机性
            max_tokens=50 # 限制DeepSeek的输出长度，只返回饮品名称
        )

        recommended_drink_name = chat_completion.choices[0].message.content.strip()
        
        # 4. 验证推荐结果并返回
        if recommended_drink_name in product_name_map:
            recommended_product_info = product_name_map[recommended_drink_name]
            return jsonify({
                "recommended_drink": recommended_drink_name,
                "price": recommended_product_info["price"],
                "message": f"根据您的偏好，我们推荐：{recommended_drink_name}。"
            })
        else:
            # 如果DeepSeek推荐了一个不在我们列表中的饮品，或者格式不正确
            print(f"DeepSeek推荐了未知饮品或格式错误: {recommended_drink_name}")
            return jsonify({"message": "抱歉，未能找到符合您偏好的饮品，请尝试更具体的描述。"}), 200

    except Exception as e:
        print(f"调用DeepSeek API时发生错误: {e}")
        return jsonify({"error": f"推荐服务暂时不可用，请稍后再试。错误信息: {str(e)}"}), 500

@app.route('/')
def index():
    return "AI Drink Recommender Backend is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)