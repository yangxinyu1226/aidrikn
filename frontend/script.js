const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

let lastRecommendedDrink = null;

function appendMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // 滚动到底部
}

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (text === '') return;

    appendMessage('user', text);
    userInput.value = '';

    // 检查用户是否意图下单
    if (text.includes('下单') && lastRecommendedDrink) {
        appendMessage('bot', `正在为您下单：${lastRecommendedDrink.recommended_drink}，价格：¥${lastRecommendedDrink.price.toFixed(2)}...`);
        try {
            const response = await fetch('http://localhost:5000/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_name: lastRecommendedDrink.recommended_drink, quantity: 1 }), // 默认数量为1
            });
            const data = await response.json();
            if (response.ok) {
                appendMessage('bot', data.message || '下单成功！');
                lastRecommendedDrink = null; // 下单成功后清空推荐
            } else {
                appendMessage('bot', `下单失败: ${data.error || '未知错误'}`);
            }
        } catch (error) {
            console.error('Error placing order:', error);
            appendMessage('bot', '下单请求发送失败，请检查后端服务。');
        }
    } else {
        // 发送推荐请求
        appendMessage('bot', '正在思考中...');
        try {
            const response = await fetch('http://localhost:5000/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ preference: text }),
            });
            const data = await response.json();
            if (response.ok) {
                if (data.recommended_drink) {
                    lastRecommendedDrink = data; // 保存推荐信息
                    appendMessage('bot', `根据您的偏好，我们推荐：${data.recommended_drink}。价格：¥${data.price.toFixed(2)}。如果您满意，可以说“下单”来购买。`);
                } else {
                    appendMessage('bot', data.message || '抱歉，未能找到符合您偏好的饮品。');
                    lastRecommendedDrink = null;
                }
            } else {
                appendMessage('bot', `推荐失败: ${data.error || '未知错误'}`);
                lastRecommendedDrink = null;
            }
        } catch (error) {
            console.error('Error getting recommendation:', error);
            appendMessage('bot', '推荐请求发送失败，请检查后端服务。');
            lastRecommendedDrink = null;
        }
    }
}

// 初始欢迎消息
appendMessage('bot', '您好！我是您的AI茶饮助手。请告诉我您的偏好，或者问我一些问题吧！');