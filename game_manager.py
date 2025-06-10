"""游戏管理脚本

为RAG竞技场游戏提供管理功能，包括：
- 游戏状态监控
- 分数统计
- 文档管理
- 系统健康检查
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from typing import Dict, List, Any

# 导入RAG后端
from rag_backend import validate_rag_system, get_game_documents

def create_admin_interface():
    """创建管理员界面"""
    st.set_page_config(
        page_title="RAG竞技场 - 管理控制台",
        page_icon="🎮",
        layout="wide"
    )
    
    st.title("🎮 RAG竞技场 - 游戏管理控制台")
    
    # 侧边栏 - 管理功能
    with st.sidebar:
        st.header("🔧 管理功能")
        
        admin_mode = st.selectbox(
            "选择管理模式",
            ["游戏监控", "分数统计", "文档管理", "系统检查", "游戏设置"]
        )
        
        st.markdown("---")
        
        # 快速操作
        st.subheader("⚡ 快速操作")
        
        if st.button("🚀 启动新游戏"):
            reset_game_state()
            st.success("游戏已重置！")
        
        if st.button("⏸️ 暂停游戏"):
            st.warning("游戏已暂停")
        
        if st.button("📊 导出数据"):
            export_game_data()
            st.success("数据已导出")
    
    # 主界面根据选择的模式显示不同内容
    if admin_mode == "游戏监控":
        show_game_monitoring()
    elif admin_mode == "分数统计":
        show_score_statistics()
    elif admin_mode == "文档管理":
        show_document_management()
    elif admin_mode == "系统检查":
        show_system_health()
    elif admin_mode == "游戏设置":
        show_game_settings()

def show_game_monitoring():
    """显示游戏监控界面"""
    st.header("📊 实时游戏监控")
    
    # 创建三列布局
    col1, col2, col3 = st.columns(3)
    
    # 模拟游戏状态数据
    game_status = get_current_game_status()
    
    with col1:
        st.metric(
            "当前阶段",
            f"第{game_status['current_stage']}阶段",
            delta=None
        )
        
        st.metric(
            "参与队伍",
            game_status['active_teams'],
            delta=None
        )
    
    with col2:
        st.metric(
            "游戏时长",
            f"{game_status['elapsed_time']}分钟",
            delta=f"+{game_status['time_delta']}分钟"
        )
        
        st.metric(
            "完成进度",
            f"{game_status['completion']}%",
            delta=f"+{game_status['progress_delta']}%"
        )
    
    with col3:
        st.metric(
            "系统状态",
            "正常运行",
            delta=None
        )
        
        st.metric(
            "响应时间",
            f"{game_status['response_time']}ms",
            delta=f"-{game_status['response_delta']}ms"
        )
    
    # 实时分数图表
    st.subheader("📈 实时分数变化")
    
    # 生成模拟分数数据
    score_data = generate_score_timeline()
    
    fig = px.line(
        score_data,
        x='时间',
        y='分数',
        color='队伍',
        title='各队伍分数变化趋势',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="游戏时间",
        yaxis_title="累计分数",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 当前排行榜
    st.subheader("🏆 当前排行榜")
    
    leaderboard = pd.DataFrame({
        '排名': [1, 2, 3],
        '队伍': ['Team 2', 'Team 1', 'Team 3'],
        '总分': [28, 25, 22],
        '阶段1': [8, 6, 4],
        '阶段2': [12, 11, 10],
        '阶段3': [8, 8, 8],
        '状态': ['已完成', '进行中', '进行中']
    })
    
    st.dataframe(
        leaderboard,
        use_container_width=True,
        hide_index=True
    )

def show_score_statistics():
    """显示分数统计分析"""
    st.header("📊 分数统计分析")
    
    # 总体统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 各阶段得分分布")
        
        stage_scores = pd.DataFrame({
            '阶段': ['检索风暴', '重排攻防', '生成终极战'],
            'Team 1': [6, 11, 8],
            'Team 2': [8, 12, 8],
            'Team 3': [4, 10, 8]
        })
        
        fig_bar = px.bar(
            stage_scores.melt(id_vars='阶段', var_name='队伍', value_name='得分'),
            x='阶段',
            y='得分',
            color='队伍',
            title='各阶段得分对比',
            barmode='group'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("🥧 总分占比")
        
        total_scores = [25, 28, 22]
        team_names = ['Team 1', 'Team 2', 'Team 3']
        
        fig_pie = px.pie(
            values=total_scores,
            names=team_names,
            title='总分占比分布'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # 详细分析
    st.subheader("📈 详细表现分析")
    
    analysis_data = pd.DataFrame({
        '指标': ['检索准确率', '重排优化率', '生成质量', '防御成功率', '平均响应时间'],
        'Team 1': [75, 85, 80, 100, 2.3],
        'Team 2': [90, 90, 85, 100, 1.8],
        'Team 3': [60, 80, 85, 100, 2.1],
        '单位': ['%', '%', '%', '%', '秒']
    })
    
    st.dataframe(analysis_data, use_container_width=True, hide_index=True)
    
    # 趋势分析
    st.subheader("📊 表现趋势")
    
    trend_data = generate_performance_trend()
    
    fig_trend = go.Figure()
    
    for team in ['Team 1', 'Team 2', 'Team 3']:
        fig_trend.add_trace(go.Scatter(
            x=trend_data['阶段'],
            y=trend_data[team],
            mode='lines+markers',
            name=team,
            line=dict(width=3)
        ))
    
    fig_trend.update_layout(
        title='各队伍表现趋势',
        xaxis_title='游戏阶段',
        yaxis_title='表现评分',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

def show_document_management():
    """显示文档管理界面"""
    st.header("📚 文档管理")
    
    # 文档统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("真实文档", "6个", delta=None)
    with col2:
        st.metric("混淆文档", "3个", delta=None)
    with col3:
        st.metric("总文档数", "9个", delta=None)
    
    # 文档列表
    st.subheader("📄 文档清单")
    
    # 获取文档列表
    documents = get_game_documents()
    
    doc_info = []
    for doc in documents:
        doc_type = "真实文档" if "广告" not in doc and "错误" not in doc and "伪科学" not in doc else "混淆文档"
        file_path = f"documents/{'real' if doc_type == '真实文档' else 'fake'}/{doc}"
        
        # 检查文件是否存在
        exists = os.path.exists(file_path)
        size = os.path.getsize(file_path) if exists else 0
        
        doc_info.append({
            '文档名称': doc,
            '类型': doc_type,
            '大小': f"{size/1024:.1f} KB" if exists else "未找到",
            '状态': "✅ 正常" if exists else "❌ 缺失"
        })
    
    doc_df = pd.DataFrame(doc_info)
    st.dataframe(doc_df, use_container_width=True, hide_index=True)
    
    # 文档内容预览
    st.subheader("👀 文档预览")
    
    selected_doc = st.selectbox(
        "选择要预览的文档",
        documents
    )
    
    if selected_doc:
        doc_type = "real" if "广告" not in selected_doc and "错误" not in selected_doc and "伪科学" not in selected_doc else "fake"
        file_path = f"documents/{doc_type}/{selected_doc}"
        
        if os.path.exists(file_path):
            st.success(f"文档路径: {file_path}")
            st.info("注意：这里显示的是文档路径，实际内容需要通过docx库读取")
        else:
            st.error("文档文件不存在")
    
    # 文档操作
    st.subheader("🔧 文档操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 重新生成文档"):
            st.info("执行: python generate_documents.py")
    
    with col2:
        if st.button("✅ 验证文档完整性"):
            missing_docs = []
            for doc in documents:
                doc_type = "real" if "广告" not in doc and "错误" not in doc and "伪科学" not in doc else "fake"
                file_path = f"documents/{doc_type}/{doc}"
                if not os.path.exists(file_path):
                    missing_docs.append(doc)
            
            if missing_docs:
                st.error(f"缺失文档: {', '.join(missing_docs)}")
            else:
                st.success("所有文档完整")
    
    with col3:
        if st.button("📦 打包文档"):
            st.info("文档打包功能待实现")

def show_system_health():
    """显示系统健康检查"""
    st.header("🔍 系统健康检查")
    
    # 执行系统检查
    system_status = validate_rag_system()
    
    # 系统组件状态
    st.subheader("🖥️ 系统组件状态")
    
    components = [
        ('向量数据库', system_status['vector_db']),
        ('嵌入模型', system_status['embedding_model']),
        ('重排序模型', system_status['rerank_model']),
        ('生成模型', system_status['generation_model']),
        ('文档存储', system_status['document_store'])
    ]
    
    for component, status in components:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{component}**")
        with col2:
            if status:
                st.success("✅ 正常")
            else:
                st.error("❌ 异常")
    
    # 性能指标
    st.subheader("⚡ 性能指标")
    
    perf_metrics = {
        '检索响应时间': '1.2秒',
        '重排序响应时间': '0.8秒',
        '生成响应时间': '2.3秒',
        '系统内存使用': '45%',
        'CPU使用率': '23%'
    }
    
    cols = st.columns(len(perf_metrics))
    for i, (metric, value) in enumerate(perf_metrics.items()):
        with cols[i]:
            st.metric(metric, value)
    
    # 错误日志
    st.subheader("📋 系统日志")
    
    log_data = [
        {'时间': '14:23:15', '级别': 'INFO', '消息': '游戏开始'},
        {'时间': '14:25:32', '级别': 'INFO', '消息': 'Team 1 完成检索'},
        {'时间': '14:27:18', '级别': 'WARN', '消息': '检索响应时间较长'},
        {'时间': '14:30:45', '级别': 'INFO', '消息': 'Team 2 进入第二阶段'}
    ]
    
    log_df = pd.DataFrame(log_data)
    st.dataframe(log_df, use_container_width=True, hide_index=True)

def show_game_settings():
    """显示游戏设置界面"""
    st.header("⚙️ 游戏设置")
    
    # 基础设置
    st.subheader("🎮 基础设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_count = st.number_input("参赛队伍数量", min_value=2, max_value=5, value=3)
        stage_time = st.slider("每阶段时间限制（分钟）", 3, 15, 8)
        difficulty = st.selectbox("游戏难度", ["简单", "中等", "困难"])
    
    with col2:
        enable_hints = st.checkbox("启用提示功能", value=True)
        enable_penalties = st.checkbox("启用错误惩罚", value=True)
        real_time_scoring = st.checkbox("实时计分", value=True)
    
    # 评分设置
    st.subheader("📊 评分设置")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**阶段1：检索风暴**")
        correct_score = st.number_input("正确选择得分", value=2)
        wrong_penalty = st.number_input("错误选择扣分", value=3)
    
    with col2:
        st.write("**阶段2：重排攻防**")
        optimize_score = st.number_input("优化操作得分", value=3)
        external_score = st.number_input("外部知识得分", value=5)
    
    with col3:
        st.write("**阶段3：生成终极战**")
        generation_score = st.number_input("生成质量得分", value=10)
        defense_score = st.number_input("防御成功得分", value=8)
    
    # 文档设置
    st.subheader("📚 文档设置")
    
    doc_ratio = st.slider("干扰文档比例", 0.1, 0.5, 0.3, 0.1)
    shuffle_docs = st.checkbox("随机打乱文档顺序", value=True)
    
    # 保存设置
    if st.button("💾 保存设置"):
        settings = {
            'team_count': team_count,
            'stage_time': stage_time,
            'difficulty': difficulty,
            'enable_hints': enable_hints,
            'enable_penalties': enable_penalties,
            'real_time_scoring': real_time_scoring,
            'scoring': {
                'correct_score': correct_score,
                'wrong_penalty': wrong_penalty,
                'optimize_score': optimize_score,
                'external_score': external_score,
                'generation_score': generation_score,
                'defense_score': defense_score
            },
            'doc_ratio': doc_ratio,
            'shuffle_docs': shuffle_docs
        }
        
        # 保存到文件
        with open('game_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        st.success("设置已保存！")

# 辅助函数
def get_current_game_status() -> Dict[str, Any]:
    """获取当前游戏状态"""
    return {
        'current_stage': 2,
        'active_teams': 3,
        'elapsed_time': 15,
        'time_delta': 2,
        'completion': 65,
        'progress_delta': 15,
        'response_time': 850,
        'response_delta': 150
    }

def generate_score_timeline() -> pd.DataFrame:
    """生成分数时间线数据"""
    import numpy as np
    
    times = ['0分钟', '5分钟', '10分钟', '15分钟', '20分钟']
    
    data = []
    for team in ['Team 1', 'Team 2', 'Team 3']:
        base_scores = [0, 6, 15, 23, 25] if team == 'Team 1' else \
                     [0, 8, 18, 26, 28] if team == 'Team 2' else \
                     [0, 4, 12, 20, 22]
        
        for i, (time, score) in enumerate(zip(times, base_scores)):
            data.append({
                '时间': time,
                '分数': score,
                '队伍': team
            })
    
    return pd.DataFrame(data)

def generate_performance_trend() -> pd.DataFrame:
    """生成表现趋势数据"""
    return pd.DataFrame({
        '阶段': ['阶段1', '阶段2', '阶段3'],
        'Team 1': [75, 85, 80],
        'Team 2': [90, 90, 85],
        'Team 3': [60, 80, 85]
    })

def reset_game_state():
    """重置游戏状态"""
    # 这里应该重置所有游戏相关的状态
    pass

def export_game_data():
    """导出游戏数据"""
    # 这里应该导出游戏统计数据
    pass

if __name__ == "__main__":
    create_admin_interface()