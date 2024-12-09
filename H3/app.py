from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import secrets

# 加载环境变量
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

# 设置密钥，用于加密session数据
app.secret_key = secrets.token_hex(16)

# 配置session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# 初始化OpenAI客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_request_with_answer():
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": """Generate a random user request that requires one or two AI departments to work together.
                    
                    Department Definitions:
                    1. "text" - AI Text Generation:
                       - Writing new text content
                       - Generating stories, poems, articles
                       - Creating summaries
                       - Completing or continuing text
                       - NOT for finding or searching existing text
                    
                    2. "image" - AI Image Generation:
                       - Creating new images from descriptions
                       - Generating artwork
                       - Editing or modifying images
                       - NOT for finding or searching existing images
                    
                    3. "search" - Information Search:
                       - Finding existing information online
                       - Searching for documents, images, or data
                       - Research and fact-finding
                       - Looking up references or examples
                       - Finding existing images (NOT generating new ones)
                    
                    4. "code" - AI Code Generation:
                       - Writing new code
                       - Debugging existing code
                       - Develope a website, app or game
                       - Explaining code functionality
                       - NOT for finding existing code examples
                    
                    Examples of Correct Department Assignment:
                    - "Find images of famous paintings" → ["search"]
                    - "Generate an image of a sunset" → ["image"]
                    - "Search for research papers about AI" → ["search"]
                    - "Write a poem about nature" → ["text"]
                    - "Create a Python script" → ["code"]
                    - "Find research papers and summarize them" → ["search", "text"]
                    - "Generate an image and write a story about it" → ["image", "text"]
                    - "Find code examples and explain how they work" → ["search", "text"]
                    - "Create a Shopping Website" → ["code"]

                    Output format (JSON):
                    {
                        "request": "the user request",
                        "departments": ["list of required departments"],
                        "keywords": {
                            "word": "department_type"
                        }
                    }"""
                }
            ]
        )
        
        response = json.loads(completion.choices[0].message.content)
        # 确保部门名称格式正确
        response['departments'] = [dept.lower() for dept in response.get('departments', [])]
        print("Generated request:", response)  # 调试信息
        return response
    except Exception as e:
        print(f"Error generating request: {e}")
        return {
            "request": "Write a Python script to analyze poetry patterns",
            "departments": ["code", "text"],
            "keywords": {
                "write": "code",
                "python": "code",
                "analyze": "code",
                "poetry": "text",
                "patterns": "text"
            }
        }

@app.route('/')
def index():
    return render_template('about.html', active='index')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/game')
def game():
    # 初始化游戏数据
    session['score'] = 0
    session['total_requests'] = 0
    session['correct_answers'] = 0
    # 生成第一个请求
    initial_request = generate_request_with_answer()
    return render_template('game.html', initial_request=initial_request)

@app.route('/settlement')
def settlement():
    # 从 session 获取游戏数据
    score = session.get('score', 0)
    total_requests = session.get('total_requests', 0)
    correct_answers = session.get('correct_answers', 0)
    
    # 计算准确率
    accuracy = round((correct_answers / total_requests * 100) if total_requests > 0 else 0, 1)
    
    return render_template('settlement.html',
                         score=score,
                         accuracy=accuracy,
                         total_requests=total_requests,
                         correct_answers=correct_answers)

@app.route('/save_game_stats', methods=['POST'])
def save_game_stats():
    data = request.get_json()
    session['score'] = data.get('score', 0)
    session['total_requests'] = data.get('total_requests', 0)
    session['correct_answers'] = data.get('correct_answers', 0)
    return jsonify({'status': 'success'})

@app.route('/get_new_request')
def get_new_request():
    request_data = generate_request_with_answer()
    print("Debug - Generated request:", request_data)  # 调试信息
    
    # 确保生成的请求数据包含所有必要字段
    if not request_data or 'departments' not in request_data:
        request_data = {
            "request": "Write a Python function to calculate fibonacci numbers",
            "departments": ["code"],
            "keywords": {
                "Write": "code",
                "Python": "code",
                "function": "code"
            }
        }
    
    # 将正确答案存储在session中
    session['current_request'] = request_data
    # 只返回请求文本给前端
    return jsonify({"request": request_data["request"]})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    print("Received data from frontend:", data)  # 调试信息
    
    # 统一部门名称格式为小写
    user_departments = sorted([dept.lower() for dept in data.get('departments', [])])
    
    current_request = session.get('current_request', {})
    # 确保从session获取的部门名称也是小写
    correct_departments = sorted([dept.lower() for dept in current_request.get('departments', [])])
    
    print("User departments:", user_departments)  # 调试信息
    print("Correct departments:", correct_departments)  # 调试信息
    
    # 标准化部门名称
    department_mapping = {
        'text generation': 'text',
        'image generation': 'image',
        'search': 'search',
        'code': 'code',
        'text': 'text',
        'image': 'image'
    }
    
    # 统一部门名称
    user_departments = [department_mapping.get(dept, dept) for dept in user_departments]
    correct_departments = [department_mapping.get(dept, dept) for dept in correct_departments]
    
    # 判定逻辑
    departments_correct = sorted(user_departments) == sorted(correct_departments)
    
    # 计算分数
    score = 10 if departments_correct else 0
    
    response = {
        "correct": departments_correct,
        "score": score,
        "correct_departments": correct_departments,
        "feedback": {
            "departments": correct_departments,
            "user_departments": user_departments
        }
    }
    
    print("Sending response:", response)  # 调试信息
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
