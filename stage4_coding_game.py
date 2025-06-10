import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from deepseek_utils import ChatBot

# 数据库初始化
def init_database():
    """初始化SQLite数据库"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    
    # 创建团队表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建聊天记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            message_type TEXT NOT NULL,  -- 'user' or 'ai'
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_name) REFERENCES teams (team_name)
        )
    ''')
    
    # 创建代码历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_name) REFERENCES teams (team_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_teams():
    """获取所有团队"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT team_name FROM teams ORDER BY team_name')
    teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teams

def create_team(team_name):
    """创建新团队"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO teams (team_name) VALUES (?)', (team_name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_chat_history(team_name):
    """获取团队聊天历史"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message_type, message, timestamp 
        FROM chat_history 
        WHERE team_name = ? 
        ORDER BY timestamp
    ''', (team_name,))
    history = cursor.fetchall()
    conn.close()
    return history

def save_chat_message(team_name, message_type, message):
    """保存聊天消息"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (team_name, message_type, message) 
        VALUES (?, ?, ?)
    ''', (team_name, message_type, message))
    conn.commit()
    conn.close()

def get_code_history(team_name):
    """获取团队代码历史"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, code, description, timestamp 
        FROM code_history 
        WHERE team_name = ? 
        ORDER BY timestamp DESC
    ''', (team_name,))
    history = cursor.fetchall()
    conn.close()
    return history

def save_code(team_name, code, description=""):
    """保存代码"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO code_history (team_name, code, description) 
        VALUES (?, ?, ?)
    ''', (team_name, code, description))
    conn.commit()
    conn.close()

def reset_team_data(team_name):
    """重置团队数据"""
    conn = sqlite3.connect('stage4_game.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE team_name = ?', (team_name,))
    cursor.execute('DELETE FROM code_history WHERE team_name = ?', (team_name,))
    conn.commit()
    conn.close()

def execute_plotly_code(code):
    """执行Plotly代码并返回图表"""
    try:
        # 创建一个新的命名空间来执行代码
        namespace = {
            'pd': pd,
            'px': px,
            'go': go,
            'st': st,
            'fig': None
        }
        
        # 捕获输出
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            exec(code, namespace)
        
        # 获取图表对象
        fig = namespace.get('fig')
        output = output_buffer.getvalue()
        error = error_buffer.getvalue()
        
        return fig, output, error
    except Exception as e:
        return None, "", str(e)

def get_ai_response(user_message, team_name, current_code=""):
    """使用DeepSeek API获取AI响应"""
    
    # 初始prompt，专门针对化妆品销售数据分析
    initial_prompt = """
你是一个专业的数据分析师和Python编程助手，专门帮助用户使用Plotly分析化妆品销售数据。

**任务背景：**
我们有三个化妆品品牌的销售数据需要分析：
1. 安心唐 - 专注孕期护肤，年均增长15%，细分市场领导者
2. 康水期 - 大众市场明星产品，年均增长12%，居家护肤需求强劲
3. 赢飞凡 - 高端市场稳定增长，年均增长8%，主打抗衰老

**数据位置：**
- CSV数据文件存储在：c:/Users/roywen/PycharmProjects/rag_xiaoyouxi/csv_data/
- 文件名格式：[品牌名]_销量数据_2018-2025.csv
- 数据字段：year, month, sales_volume, sales_amount, unit_price

**分析目标：**
帮助用户逐步使用Plotly创建各种图表来分析三个品牌的年销售额关系，包括：
- 年度销售额对比
- 增长趋势分析
- 品牌间相关性分析
- 市场份额变化
- 季节性销售模式

**编程要求：**
1. 使用pandas读取CSV数据
2. 使用plotly.express或plotly.graph_objects创建图表
3. 确保代码中包含'fig'变量用于显示图表
4. 提供清晰的代码注释
5. 根据用户需求逐步完善代码

请根据用户的问题，提供具体的Python代码建议和数据分析指导。
"""
    
    try:
        # 创建ChatBot实例
        chatbot = ChatBot(
            system_prompt=initial_prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        # 构建完整的用户消息，包含当前代码上下文
        full_message = user_message
        if current_code.strip():
            full_message += f"\n\n当前代码框中的内容：\n```python\n{current_code}\n```\n\n请基于当前代码进行修改或优化。"
        
        # 获取AI响应
        response = chatbot.chat(full_message)
        return response
        
    except Exception as e:
        return f"AI响应出错：{str(e)}\n\n请检查API配置或网络连接。"

def stage4_coding_game():
    """第四阶段：代码撰写小游戏"""
    st.header("💻 第四阶段：代码撰写小游戏")
    
    # 初始化数据库
    init_database()
    
    # 团队选择区域
    st.subheader("👥 团队选择")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        teams = get_teams()
        if teams:
            selected_team = st.selectbox("选择团队", teams, key="team_selector")
        else:
            selected_team = None
            st.info("还没有团队，请先创建一个团队")
    
    with col2:
        # 创建新团队
        with st.expander("创建新团队"):
            new_team_name = st.text_input("团队名称", key="new_team_input")
            if st.button("创建团队", key="create_team_btn"):
                if new_team_name.strip():
                    if create_team(new_team_name.strip()):
                        st.success(f"团队 '{new_team_name}' 创建成功！")
                        st.rerun()
                    else:
                        st.error("团队名称已存在！")
                else:
                    st.error("请输入团队名称！")
    
    if not selected_team:
        st.warning("请先选择或创建一个团队")
        return
    
    # 重置团队数据按钮
    if st.button("🗑️ 重置团队历史记录", key="reset_team_btn", type="secondary"):
        if st.session_state.get('confirm_reset', False):
            reset_team_data(selected_team)
            st.success(f"团队 '{selected_team}' 的历史记录已重置！")
            st.session_state['confirm_reset'] = False
            st.rerun()
        else:
            st.session_state['confirm_reset'] = True
            st.warning("再次点击确认重置")
    
    st.divider()
    
    # 上半部分：AI聊天区域
    st.subheader("🤖 AI 助手对话")
    
    # 聊天历史显示
    chat_container = st.container(height=600)
    with chat_container:
        chat_history = get_chat_history(selected_team)
        for message_type, message, timestamp in chat_history:
            if message_type == 'user':
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)
    
    # 用户输入
    user_input = st.chat_input("向AI助手提问...")
    if user_input:
        # 保存用户消息
        save_chat_message(selected_team, 'user', user_input)
        
        # 获取当前代码内容
        current_code = st.session_state.get('code_editor', '')
        
        # 获取AI响应
        ai_response = get_ai_response(user_input, selected_team, current_code)
        save_chat_message(selected_team, 'ai', ai_response)
        
        st.rerun()
    
    st.divider()
    
    # 下半部分：代码编辑和可视化
    st.subheader("💻 代码编辑与可视化")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**Python 代码编辑器**")
        
        # 历史代码选择
        code_history = get_code_history(selected_team)
        if code_history:
            st.markdown("**选择历史代码：**")
            history_options = ["新建代码"] + [f"代码 {i+1}: {desc or '无描述'} ({timestamp})" for i, (_, _, desc, timestamp) in enumerate(code_history)]
            selected_history = st.selectbox("历史代码", history_options, key="history_selector")
            
            if selected_history != "新建代码":
                history_index = history_options.index(selected_history) - 1
                selected_code = code_history[history_index][1]  # 获取代码内容
            else:
                selected_code = ""
        else:
            selected_code = ""
        
        # 默认示例代码
        if not selected_code:
            selected_code = """import plotly.express as px
import pandas as pd
import os

# 化妆品销售数据分析 - 开始您的数据探索之旅！
# 数据文件位置：csv_data文件夹
# 三个品牌：安心唐、康水期、赢飞凡

# 示例：读取一个品牌的数据
data_path = 'csv_data/安心唐_销量数据_2018-2025.csv'
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    
    # 计算年度销售额
    yearly_sales = df.groupby('year')['sales_amount'].sum().reset_index()
    
    # 创建年度销售额趋势图
    fig = px.line(yearly_sales, x='year', y='sales_amount',
                  title='安心唐年度销售额趋势',
                  labels={'sales_amount': '销售额', 'year': '年份'})
    fig.update_layout(width=600, height=400)
else:
    # 如果数据文件不存在，创建示例图表
    sample_data = {'year': [2018, 2019, 2020, 2021, 2022], 
                   'sales': [100000, 120000, 140000, 160000, 180000]}
    df = pd.DataFrame(sample_data)
    fig = px.line(df, x='year', y='sales', title='示例销售趋势')
    fig.update_layout(width=600, height=400)

# 提示：向AI助手询问如何分析三个品牌的销售关系！"""
        
        # 代码编辑器
        code = st.text_area(
            "编写您的Plotly代码：",
            value=selected_code,
            height=400,
            key="code_editor"
        )
        
        # 代码操作按钮
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("▶️ 运行代码", key="run_code_btn", type="primary"):
                st.session_state['run_code'] = True
        
        with col_btn2:
            code_description = st.text_input("代码描述（可选）", key="code_desc_input")
            if st.button("💾 保存代码", key="save_code_btn"):
                save_code(selected_team, code, code_description)
                st.success("代码已保存！")
                st.rerun()
    
    with col_right:
        st.markdown("**可视化结果**")
        
        # 运行代码并显示结果
        if st.session_state.get('run_code', False) or code:
            if code.strip():
                fig, output, error = execute_plotly_code(code)
                
                if error:
                    st.error(f"代码执行错误：\n{error}")
                else:
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("代码执行成功，但没有生成图表。请确保代码中包含 'fig' 变量。")
                    
                    if output:
                        st.text(f"输出：\n{output}")
            else:
                st.info("请输入代码并点击运行")
        
        # 重置运行状态
        if 'run_code' in st.session_state:
            del st.session_state['run_code']

if __name__ == "__main__":
    stage4_coding_game()