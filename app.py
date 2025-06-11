import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
import os
from typing import List, Dict, Any

# 导入后端RAG函数
from rag_backend import (
    search_documents,
    rerank_results,
    generate_answer,
    get_document_content,
    evaluate_answer
)

# 导入第四阶段功能
from stage4_coding_game import stage4_coding_game

# 页面配置
st.set_page_config(
    page_title="RAG特工黑客松",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'current_stage': 0,
        'total_score': 0,
        'selected_query': '找出敏感肌可用的玻尿酸面膜核心成分',
        'stage1_results': {},
        'stage2_results': {},
        'stage3_results': {},
        'stage4_results': {},
        'game_started': False
    }

def main():
    st.title("🕵️ RAG特工黑客松")
    # st.markdown("### 💻 数据特工竞技场 - 用RAG系统破解机密任务")
    
    # 侧边栏 - 游戏控制
    with st.sidebar:
        st.header("🎮 游戏控制台")
        
        # 阶段选择
        st.header("🎯 阶段选择")
        stage_options = {
            0: "🏠 游戏主页",
            1: "🔍 第一阶段：检索风暴",
            2: "⚡ 第二阶段：重排攻防战",
            3: "🎯 第三阶段：生成终极战",
            4: "💻 第四阶段：代码撰写小游戏",
            5: "📊 查看文档数据"
        }
        
        selected_stage = st.radio(
            "选择游戏阶段",
            options=list(stage_options.keys()),
            format_func=lambda x: stage_options[x],
            index=st.session_state.game_state['current_stage']
        )
        
        if selected_stage != st.session_state.game_state['current_stage']:
            st.session_state.game_state['current_stage'] = selected_stage
            if selected_stage > 0:
                st.session_state.game_state['game_started'] = True
            st.rerun()
        
        # 当前阶段显示
        # if st.session_state.game_state['current_stage'] > 0:
        #     st.markdown(f"**当前阶段**: {st.session_state.game_state['current_stage']}/3")
        
        # # 实时记分板
        # st.header("📊 实时记分板")
        # st.metric("当前分数", st.session_state.game_state.get('total_score', 0))
        
        # 游戏控制按钮
        # if st.button("🚀 开始游戏"):
        #     st.session_state.game_state['game_started'] = True
        #     st.rerun()
        
        if st.button("🔄 重置游戏"):
            # 删除所有_rerank.json文件
            import os
            import glob
            import sqlite3
            
            try:
                # 删除json文件夹中的_rerank.json文件
                rerank_files = glob.glob(os.path.join('json', '*_rerank.json'))
                for file_path in rerank_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        st.success(f"已删除文件: {file_path}")
                
                # 重置stage4数据库
                conn = sqlite3.connect('stage4_game.db')
                cursor = conn.cursor()
                
                # 清空所有表的数据
                cursor.execute('DELETE FROM chat_history')
                cursor.execute('DELETE FROM code_history')
                cursor.execute('DELETE FROM teams')
                
                conn.commit()
                conn.close()
                st.success("已重置Stage4数据库")
                
            except Exception as e:
                st.error(f"重置过程中出现错误: {e}")
            
            # 重置游戏状态
            st.session_state.game_state = {
                'current_stage': 0,
                'total_score': 0,
                'selected_query': '找出敏感肌可用的玻尿酸面膜核心成分',
                'stage1_results': {},
                'stage2_results': {},
                'stage3_results': {},
                'stage4_results': {},
                'game_started': False
            }
            st.success("游戏状态已重置")
            st.rerun()
    
    # 主游戏区域
    current_stage = st.session_state.game_state['current_stage']
    if current_stage == 0:
        show_game_intro()
    elif current_stage == 1:
        stage1_retrieval_storm()
    elif current_stage == 2:
        stage2_rerank_battle()
    elif current_stage == 3:
        stage3_generation_war()
    elif current_stage == 4:
        stage4_coding_game()
    else:
        show_game_results()

def show_game_intro():
    """显示游戏介绍"""
    st.markdown("""
    ## 🎯 游戏规则
    
    ### 第一阶段：检索风暴
    - 通过检索查询到相关文档
    - 提交top3相关段落的编号
    
    ### 第二阶段：重排攻防战
    - 优化初始检索结果
    - 删除完全不想关或者混淆视听的段落
    - 保存修改并提交
    
    ### 第三阶段：生成终极战
    - 提供防御prompt，让LLM减少幻觉
    - 生成检索之后的结果
    
    ### 第四阶段：代码撰写小游戏
    - 与AI助手对话获取编程指导
    - 编写Python代码生成Plotly可视化
    - 实时预览可视化结果
    - 谁画的图好看，谁就是赢家
    """)

def stage1_retrieval_storm():
    """第一阶段：检索风暴"""
    st.header("🔍 第一阶段：检索风暴")
    st.markdown("**任务**: 提交top3相关段落的编号")
    
    # 查询选择
    st.subheader("🔍 选择检索任务")
    query_options = {
        "query1": "找出敏感肌可用的玻尿酸面膜核心成分",
        "query2": "识别孕妇可安全使用的口红配方要求",
        "query3": "确定抗衰老精华中的有效活性成分"
    }
    
    selected_query_key = st.radio(
        "选择检索任务",
        options=list(query_options.keys()),
        format_func=lambda x: query_options[x],
        index=0 if 'selected_query_key' not in st.session_state.game_state else list(query_options.keys()).index(st.session_state.game_state.get('selected_query_key', 'query1'))
    )
    
    if selected_query_key != st.session_state.game_state.get('selected_query_key'):
        st.session_state.game_state['selected_query_key'] = selected_query_key
        st.session_state.game_state['selected_query'] = query_options[selected_query_key]
        st.rerun()
    
    # 获取选择的查询
    selected_query = st.session_state.game_state.get('selected_query', query_options['query1'])
    
    st.info(f"**当前任务**: {selected_query}")
    if 'stage1_query' not in st.session_state:
        st.session_state.stage1_query = None
    # 检索界面
    col1, col2 = st.columns([2, 1])
    query_input = None
    with col1:
        st.subheader("🔎 检索操作")
        query_input = st.text_input("当前检索查询", value=selected_query, disabled=True)
        if st.session_state.stage1_query is None or st.session_state.stage1_query != query_input:
            st.session_state.stage1_query = query_input
            st.session_state.search_results = []
        if st.button("🚀 执行检索"):
            with st.spinner("正在检索文档..."):
                # 调用后端检索函数
                results = search_documents(query_input)
                st.session_state.search_results = results
        
        # 显示检索结果
        if 'search_results' in st.session_state and st.session_state.search_results:
            st.subheader("📋 检索结果")
            for i, result in enumerate(st.session_state.search_results):
                with st.expander(f"段落 {i+1} - 相关度分数: {result['score']:.3f}"):
                    st.write(f"**文档**: {result['document']}")
                    st.write(f"**内容**: {result['content']}")
    
    with col2:
        st.subheader("📝 提交答案")
        if 'search_results' in st.session_state and st.session_state.search_results:
            selected_paragraphs = st.multiselect(
                "选择top3相关段落",
                options=list(range(len(st.session_state.search_results))),
                format_func=lambda x: f"段落 {x+1}",
                max_selections=3
            )
            
            if st.button("✅ 提交选择") and len(selected_paragraphs) == 3:
                # 评估答案并更新分数
                if query_input is None:
                    st.error("请先执行检索!!")
                score = evaluate_stage1_answer(selected_paragraphs, query_input)
                st.session_state.game_state['total_score'] += score
                st.session_state.game_state['stage1_results'] = {
                    'selected': selected_paragraphs,
                    'score': score
                }
                # st.success(f"提交成功！获得 {score} 分！请勿重复点击刷分")
                
                # if st.button("➡️ 进入第二阶段"):
                #     st.session_state.game_state['current_stage'] = 2
                #     st.rerun()

def stage2_rerank_battle():
    """第二阶段：重排攻防战"""
    st.header("⚔️ 第二阶段：重排攻防战")
    st.markdown("**任务**: 优化初始检索结果")
    
    # 添加query选择功能
    st.subheader("🔍 选择检索任务")
    query_options = {
        "query1": "找出敏感肌可用的玻尿酸面膜核心成分",
        "query2": "识别孕妇可安全使用的口红配方要求",
        "query3": "确定抗衰老精华中的有效活性成分"
    }
    
    selected_query_key = st.radio(
        "选择检索任务",
        options=list(query_options.keys()),
        format_func=lambda x: query_options[x],
        index=0 if 'stage2_selected_query_key' not in st.session_state.game_state else list(query_options.keys()).index(st.session_state.game_state.get('stage2_selected_query_key', 'query1')),
        key="stage2_query_selection"
    )
    
    # 保存选择的query
    st.session_state.game_state['stage2_selected_query_key'] = selected_query_key
    selected_query = query_options[selected_query_key]
    st.session_state.game_state['stage2_query'] = selected_query
    
    st.info(f"当前选择的任务: {selected_query}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔄 重排序操作")
        
        # 显示初始检索结果（包含低质量段落）
        if st.button("📥 加载初始检索结果"):
            with st.spinner("加载中..."):
                initial_results = get_initial_results_with_noise()
                st.session_state.initial_results = initial_results
        
        if 'initial_results' in st.session_state:
            st.write("**初始检索结果（从JSON文件加载）**:")
            for i, result in enumerate(st.session_state.initial_results):
                with st.expander(f"段落 {result['index']} - 相关度分数: {result['quality']:.3f}"):
                    st.write(f"**文档**: {result.get('metadata', {}).get('document_display_name', '未知文档')}")
                    st.write(f"**内容**: {result['text']}")
                    if 'uid' in result:
                        st.write(f"**文档ID**: {result['uid']}")
            
            if st.button("🎯 执行重排序"):
                with st.spinner("重排序中..."):
                    reranked_results = st.session_state.initial_results
                    # st.write(reranked_results)
                    # 按分数排序（默认排序）
                    reranked_results.sort(key=lambda x: x.get('new_score', x.get('score', 0)), reverse=True)
                    st.session_state.reranked_results = reranked_results
                    # 初始化拖拽排序状态
                    if 'dragged_order' not in st.session_state:
                        st.session_state.dragged_order = list(range(len(reranked_results)))
                    
                    st.success("重排序完成！")
        
        # 拖拽排序界面
        if 'reranked_results' in st.session_state:
            st.subheader("📋 用户手动排序")
            st.markdown("**默认按分数排序，您可以手动调整顺序**")
            
            # 显示当前排序
            reranked_results = st.session_state.reranked_results
            current_order = st.session_state.get('dragged_order', list(range(len(reranked_results))))
            
            # 创建可拖拽的排序界面
            st.write("**当前排序**:")
            
            # 使用selectbox来模拟拖拽排序
            new_order = []
            for pos in range(len(reranked_results)):
                available_items = [i for i in range(len(reranked_results)) if i not in new_order]
                if pos < len(current_order) and current_order[pos] in available_items:
                    default_idx = available_items.index(current_order[pos])
                else:
                    default_idx = 0
                
                selected = st.selectbox(
                    f"位置 {pos + 1}",
                    options=available_items,
                    format_func=lambda x: f"段落 {reranked_results[x]['index']}: {reranked_results[x]['text'][:50]}...",
                    index=default_idx,
                    key=f"order_{pos}"
                )
                new_order.append(selected)
            
            if st.button("💾 保存排序"):
                st.session_state.dragged_order = new_order
                st.success("排序已保存！")
            
            # 显示当前排序结果
            st.write("**当前排序结果**:")
            for i, idx in enumerate(st.session_state.get('dragged_order', list(range(len(reranked_results))))):
                result = reranked_results[idx]
                # st.write(result)
                with st.expander(f"段落 {result['index']} - 相关度分数: {result.get('score', 0):.3f}"):
                    st.write(f"**文档**: {result.get('metadata', {}).get('document_display_name', '未知文档')}")
                    st.write(f"**内容**: {result['text']}")
                    # if 'rerank_reason' in result:
                    #     st.write(f"**重排理由**: {result['rerank_reason']}")
    
    with col2:
        st.subheader("✂️ 优化操作")
        
        if 'reranked_results' in st.session_state and 'dragged_order' in st.session_state:
            reranked_results = st.session_state.reranked_results
            current_order = st.session_state.dragged_order

            # 多选删除低质量段落
            to_remove = st.multiselect(
                "选择要删除的低质量段落",
                options=list(range(len(reranked_results))),
                format_func=lambda x: f"段落 {reranked_results[x]['index']}: {reranked_results[x]['text'][:30]}...",
                help="可以选择多个要删除的段落"
            )
            
            # removal_reason = st.text_area("说明删除理由")
            
            # # 添加外部知识
            # external_knowledge = st.text_area("添加外部知识（30秒谷歌搜索结果）")
            
            # 保存修改按钮
            if st.button("💾 保存修改"):
                save_reranked_results(reranked_results, current_order, to_remove)
                st.success("修改已保存到新的JSON文件！")
            
            # if st.button("✅ 提交优化结果") and len(to_remove) >= 1:
            #     score = evaluate_stage2_answer(to_remove, removal_reason, external_knowledge)
            #     st.session_state.game_state['total_score'] += score
            #     st.session_state.game_state['stage2_results'] = {
            #         'removed': to_remove,
            #         'reason': removal_reason,
            #         'external': external_knowledge,
            #         'score': score,
            #         'final_order': current_order
            #     }
            #     st.success(f"提交成功！获得 {score} 分")

def stage3_generation_war():
    """第三阶段：生成终极战"""
    st.header("🎯 第三阶段：生成终极战")
    st.markdown("**任务**: 输入防御Prompt使LLM更准确地回答问题")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 幻觉炸弹挑战
        st.subheader("💣 幻觉炸弹挑战")
        
        hallucination_bombs = [
            "找出敏感肌可用的玻尿酸面膜核心成分",
            "识别孕妇可安全使用的口红配方要求",
            "确定抗衰老精华中的有效活性成分"
        ]
        
        selected_bomb = st.selectbox("选择要防御的幻觉炸弹", hallucination_bombs)
        
        if selected_bomb:
            st.warning(f"💣 幻觉炸弹攻击: {selected_bomb}")
            
            # 显示检索到的文档
            retrieval_docs = load_retrieval_documents(selected_bomb)
            if retrieval_docs:
                st.subheader("📄 检索到的文档")
                with st.expander("查看检索文档", expanded=False):
                    for i, doc in enumerate(retrieval_docs):
                        st.write(f"**文档 {i+1}**: {doc.get('metadata', {}).get('document_display_name', '未知文档')}")
                        st.write(f"**内容**: {doc['text'][:200]}...")
                        st.write("---")
            
            defense_prompt = st.text_area(
                "请输入您的防御prompt（用于指导LLM更准确地回答问题）",
                placeholder="例如：请基于提供的文档内容，仔细分析并回答问题。注意区分真实信息和虚假信息...",
                height=150
            )
            
            if st.button("🚀 提交prompt并生成答案") and defense_prompt:
                with st.spinner("正在调用DeepSeek生成答案..."):
                    generated_answer = generate_answer_with_deepseek(selected_bomb, retrieval_docs, defense_prompt)
                    st.session_state.generated_answer = generated_answer
                    st.session_state.selected_query = selected_bomb
                    st.session_state.defense_prompt = defense_prompt
    
    with col2:
        st.subheader("📊 生成结果")
        if 'generated_answer' in st.session_state:
            st.write("**查询问题**:")
            st.info(st.session_state.get('selected_query', ''))
            
            st.write("**您的防御prompt**:")
            defense_prompt = st.session_state.get('defense_prompt', '')
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid #4CAF50;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="
                        background: rgba(255,255,255,0.95);
                        padding: 12px;
                        border-radius: 8px;
                        color: #333;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.3;
                        min-height: 60px;
                        white-space: pre-wrap;
                    ">{defense_prompt if defense_prompt else '暂无防御prompt'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.write("**DeepSeek生成的答案**:")
            generated_answer = st.session_state.generated_answer
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid #FF6B6B;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="
                        background: rgba(255,255,255,0.95);
                        padding: 15px;
                        border-radius: 8px;
                        color: #333;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.0;
                        min-height: 200px;
                        max-height: 400px;
                        overflow-y: auto;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    ">{generated_answer.strip() if generated_answer else '暂无生成答案'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # if st.button("🏆 提交最终答案"):
            #     # 保存结果到session state
            #     st.session_state.game_state['stage3_results'] = {
            #         'query': st.session_state.get('selected_query', ''),
            #         'defense_prompt': st.session_state.get('defense_prompt', ''),
            #         'generated_answer': st.session_state.generated_answer
            #     }
                
            #     st.success("第三阶段完成！答案已提交")
                
            #     if st.button("➡️ 进入第四阶段"):
            #         st.session_state.game_state['current_stage'] = 4
            #         st.rerun()

def show_game_results():
    """显示相关文档浏览器"""
    import os
    import pandas as pd
    import json
    
    st.header("📁 相关文档浏览器")
    
    # 定义文件夹路径
    folders = {
        "📊 CSV数据文件": "csv_data",
        "📄 文档文件": "documents", 
        "🔧 JSON配置文件": "json"
    }
    
    # 创建选项卡
    tabs = st.tabs(list(folders.keys()))
    
    for i, (tab_name, folder_path) in enumerate(folders.items()):
        with tabs[i]:
            st.subheader(f"{tab_name}")
            
            # 检查文件夹是否存在
            if not os.path.exists(folder_path):
                st.error(f"文件夹 {folder_path} 不存在")
                continue
            
            # 获取文件列表
            try:
                files = []
                for root, dirs, filenames in os.walk(folder_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, folder_path)
                        file_size = os.path.getsize(file_path)
                        file_modified = os.path.getmtime(file_path)
                        files.append({
                            "文件名": filename,
                            "相对路径": rel_path,
                            "大小(字节)": file_size,
                            "修改时间": pd.to_datetime(file_modified, unit='s').strftime('%Y-%m-%d %H:%M:%S'),
                            "完整路径": file_path
                        })
                
                if not files:
                    st.info(f"文件夹 {folder_path} 为空")
                    continue
                
                # 显示文件列表
                df = pd.DataFrame(files)
                st.dataframe(df[["文件名", "相对路径", "大小(字节)", "修改时间"]], use_container_width=True)
                
                # 文件预览功能
                st.subheader("📖 文件预览")
                selected_file = st.selectbox(
                    "选择要预览的文件:", 
                    options=["请选择文件..."] + [f["文件名"] for f in files],
                    key=f"file_selector_{i}"
                )
                
                if selected_file != "请选择文件...":
                    # 找到选中的文件
                    selected_file_info = next(f for f in files if f["文件名"] == selected_file)
                    file_path = selected_file_info["完整路径"]
                    
                    try:
                        # 根据文件类型进行预览
                        if file_path.endswith('.csv'):
                            st.write("**CSV文件内容:**")
                            csv_df = pd.read_csv(file_path)
                            st.dataframe(csv_df, use_container_width=True)
                            # st.info(f"显示前20行，总共 {len(csv_df)} 行")
                            
                        elif file_path.endswith('.json'):
                            st.write("**JSON文件内容:**")
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json_data = json.load(f)
                            st.json(json_data)
                            
                        elif file_path.endswith(('.txt', '.md')):
                            st.write("**文本文件内容:**")
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            st.text_area("文件内容", content, height=300)
                            
                        elif file_path.endswith('.docx'):
                            st.write("**Word文档信息:**")
                            st.info(f"文件: {selected_file}\n大小: {selected_file_info['大小(字节)']} 字节\n修改时间: {selected_file_info['修改时间']}")
                            st.warning("Word文档需要专门的工具打开，这里只显示文件信息")
                            
                        else:
                            st.write("**文件信息:**")
                            st.info(f"文件: {selected_file}\n大小: {selected_file_info['大小(字节)']} 字节\n修改时间: {selected_file_info['修改时间']}")
                            st.warning("此文件类型暂不支持预览")
                            
                    except Exception as e:
                        st.error(f"读取文件时出错: {str(e)}")
                        
            except Exception as e:
                st.error(f"访问文件夹时出错: {str(e)}")

# 辅助函数
def evaluate_stage1_answer(selected_paragraphs, query):
    """评估第一阶段答案"""
    result = 0
    if query.strip() == "找出敏感肌可用的玻尿酸面膜核心成分":
        for selected_paragraph in selected_paragraphs:
            if selected_paragraph in [0, 1, 2, 4, 5]:
                result += 1
        st.success(f"回答得分: {result}分。这里面段落4为不太相关的文档。其他都有一定的关联。")
    elif query.strip() == "识别孕妇可安全使用的口红配方要求":
        result = 3
        if result == 3:
            st.success(f"回答得分: {result}分。在这个使用用例中，所有的文档都有一定的关联。")
    elif query.strip() == "确定抗衰老精华中的有效活性成分":
        for selected_paragraph in selected_paragraphs:
            if selected_paragraph in [0, 1, 3, 4, 5]:
                result += 1
        st.success(f"回答得分: {result}分。这里面段落3为不太相关的文档。其他都有一定的关联。")
    return result

def evaluate_stage2_answer(removed_paragraphs, reason, external_knowledge):
    """评估第二阶段答案"""
    score = 0
    if len(removed_paragraphs) == 2:
        score += 3
    if external_knowledge.strip():
        score += 5
    return score

def evaluate_defense(defense_answer, attack):
    """评估防御答案"""
    if len(defense_answer.strip()) > 50:
        return 8
    return 0

def get_initial_results_with_noise():
    """从JSON文件获取初始结果"""
    import json
    import os
    
    # 获取当前查询 - 优先使用第二阶段的query选择，如果没有则使用第一阶段的
    query = st.session_state.game_state.get('stage2_query', '') or st.session_state.game_state.get('stage1_results', {}).get('query', '')
    # 根据查询映射到对应的JSON文件
    query_mapping = {
        '敏感肌': '找出敏感肌可用的玻尿酸面膜核心成分.json',
        '玻尿酸': '找出敏感肌可用的玻尿酸面膜核心成分.json',
        '面膜': '找出敏感肌可用的玻尿酸面膜核心成分.json',
        '抗衰老': '确定抗衰老精华中的有效活性成分.json',
        '精华': '确定抗衰老精华中的有效活性成分.json',
        '孕妇': '识别孕妇可安全使用的口红配方要求.json',
        '口红': '识别孕妇可安全使用的口红配方要求.json'
    }
    
    # 查找匹配的JSON文件
    json_file = None
    for keyword, filename in query_mapping.items():
        if keyword in query:
            json_file = filename
            break
    
    if not json_file:
        # 默认使用第一个文件
        json_file = '找出敏感肌可用的玻尿酸面膜核心成分.json'
    
    json_path = os.path.join('json', json_file)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            documents = data.get('documents', [])
            
            # 转换为统一格式
            results = []
            for i, doc in enumerate(documents):
                results.append({
                    'index': i+1,
                    'text': doc.get('text', ''),
                    'score': doc.get('score', 0.0),
                    'quality': doc.get('score', 0.0),  # 使用score作为quality
                    'metadata': doc.get('metadata', {}),
                    'uid': doc.get('uid', '')
                })
            return results[:10]  # 限制返回前10个结果
            
    except Exception as e:
        st.error(f"读取JSON文件失败: {e}")
        # 返回默认结果
        return [
            {'text': '玻尿酸是一种天然保湿成分，适合敏感肌使用', 'score': 0.9, 'quality': 0.9},
            {'text': '购买我们的面膜，立即享受8折优惠！', 'score': 0.2, 'quality': 0.2},
            {'text': '透明质酸钠具有优异的保湿性能', 'score': 0.8, 'quality': 0.8},
            {'text': '所有化妆品都含有化学成分', 'score': 0.3, 'quality': 0.3},
            {'text': '敏感肌应避免使用含酒精的产品', 'score': 0.7, 'quality': 0.7}
        ]

def save_reranked_results(reranked_results, current_order, to_remove):
    """保存重排序和优化后的结果到新的JSON文件"""
    import json
    import os
    from datetime import datetime
    
    # 获取原始查询 - 优先使用第二阶段的query选择，如果没有则使用第一阶段的
    query = st.session_state.game_state.get('stage2_query', '') or st.session_state.game_state.get('stage1_results', {}).get('query', '')
    
    # 根据查询确定原始文件名
    query_mapping = {
        '敏感肌': '找出敏感肌可用的玻尿酸面膜核心成分',
        '玻尿酸': '找出敏感肌可用的玻尿酸面膜核心成分',
        '面膜': '找出敏感肌可用的玻尿酸面膜核心成分',
        '抗衰老': '确定抗衰老精华中的有效活性成分',
        '精华': '确定抗衰老精华中的有效活性成分',
        '孕妇': '识别孕妇可安全使用的口红配方要求',
        '口红': '识别孕妇可安全使用的口红配方要求'
    }
    
    # 查找匹配的文件名
    base_filename = None
    for keyword, filename in query_mapping.items():
        if keyword in query:
            base_filename = filename
            break
    
    if not base_filename:
        base_filename = '找出敏感肌可用的玻尿酸面膜核心成分'
    
    # 创建新的文件名
    new_filename = f"{base_filename}_rerank.json"
    new_filepath = os.path.join('json', new_filename)
    
    # 按照用户排序重新组织结果
    reordered_results = []
    for idx in current_order:
        if idx not in to_remove:  # 排除被删除的段落
            result = reranked_results[idx].copy()
            # 简化metadata，只保留document_display_name
            if 'metadata' in result:
                result['metadata'] = {
                    'document_display_name': result['metadata'].get('document_display_name', '未知文档')
                }
            # 移除new_score和rerank_reason等重排序相关字段，保持原始格式
            if 'new_score' in result:
                del result['new_score']
            if 'rerank_reason' in result:
                del result['rerank_reason']
            reordered_results.append(result)
    
    # 构建保存的数据结构，与原始JSON格式一致
    save_data = {
        "documents": reordered_results
    }
    
    try:
        # 确保json目录存在
        os.makedirs('json', exist_ok=True)
        
        # 保存到新文件
        with open(new_filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        st.info(f"结果已保存到: {new_filepath}")
        
    except Exception as e:
        st.error(f"保存文件失败: {e}")

def load_retrieval_documents(query):
    """根据查询加载检索文档，优先加载_rerank.json文件"""
    import json
    import os
    
    # 查询到文件名的映射
    query_mapping = {
        '找出敏感肌可用的玻尿酸面膜核心成分': '找出敏感肌可用的玻尿酸面膜核心成分',
        '识别孕妇可安全使用的口红配方要求': '识别孕妇可安全使用的口红配方要求',
        '确定抗衰老精华中的有效活性成分': '确定抗衰老精华中的有效活性成分'
    }
    
    base_filename = query_mapping.get(query)
    if not base_filename:
        return []
    
    # 优先尝试加载_rerank.json文件
    rerank_filepath = os.path.join('json', f'{base_filename}_rerank.json')
    original_filepath = os.path.join('json', f'{base_filename}.json')
    
    try:
        # 首先尝试加载_rerank文件
        if os.path.exists(rerank_filepath):
            with open(rerank_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('documents', [])
        # 如果没有_rerank文件，加载原始文件
        elif os.path.exists(original_filepath):
            with open(original_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('documents', [])
        else:
            st.error(f"未找到相关文档文件: {base_filename}")
            return []
    except Exception as e:
        st.error(f"加载文档失败: {e}")
        return []

def generate_answer_with_deepseek(query, retrieval_docs, defense_prompt):
    """使用DeepSeek生成答案"""
    from deepseek_utils import ChatBot
    
    # 构建system prompt
    system_prompt = f"""
你是一个专业助手。你的任务是基于提供的检索文档来回答用户的问题。

请注意：
1. 严格基于提供的文档内容进行回答
2. 区分真实可靠的信息和可能的虚假信息
3. 如果文档中包含相互矛盾的信息，请指出并说明
4. 提供准确、专业的分析和建议
5. 如果文档信息不足以回答问题，请明确说明

用户的防御指导：{defense_prompt}
"""
    
    # 构建检索文档内容
    docs_content = ""
    for i, doc in enumerate(retrieval_docs):
        doc_name = doc.get('metadata', {}).get('document_display_name', f'文档{i+1}')
        docs_content += f"\n=== {doc_name} ===\n{doc['text']}\n"
    
    # 构建user prompt
    user_prompt = f"""
基于以下检索到的文档内容，请回答问题：

问题：{query}

检索文档：{docs_content}

请基于上述文档内容，提供详细、准确的回答。
"""
    
    try:
        # 创建ChatBot实例
        chatbot = ChatBot(system_prompt=system_prompt, temperature=0.5)
        
        # 生成回答
        answer = chatbot.chat(user_prompt)
        
        return answer
    except Exception as e:
        return f"生成答案时出错: {str(e)}"

def get_context_from_previous_stages():
    """从前两阶段获取上下文"""
    stage1_results = st.session_state.game_state.get('stage1_results', {})
    stage2_results = st.session_state.game_state.get('stage2_results', {})
    
    context = f"基于检索和重排序的结果的分析..."
    return context

if __name__ == "__main__":
    main()
