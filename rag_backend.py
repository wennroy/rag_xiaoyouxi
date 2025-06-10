"""RAG后端函数模块

这个模块包含所有RAG相关的后端函数。
当前实现返回默认值，用户需要根据实际RAG系统进行替换。
"""

import random
import time
from typing import List, Dict, Any
import json

def search_documents(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    文档检索函数
    
    Args:
        query: 检索查询
        top_k: 返回结果数量
    
    Returns:
        检索结果列表，每个结果包含文档名、内容、相关度分数
    """
    import json
    import os
    
    # 模拟检索延迟
    time.sleep(1)
    
    # JSON文件路径映射
    json_files = {
        "敏感肌": "json/找出敏感肌可用的玻尿酸面膜核心成分.json",
        "玻尿酸": "json/找出敏感肌可用的玻尿酸面膜核心成分.json",
        "面膜": "json/找出敏感肌可用的玻尿酸面膜核心成分.json",
        "抗衰老": "json/确定抗衰老精华中的有效活性成分.json",
        "精华": "json/确定抗衰老精华中的有效活性成分.json",
        "活性成分": "json/确定抗衰老精华中的有效活性成分.json",
        "孕妇": "json/识别孕妇可安全使用的口红配方要求.json",
        "口红": "json/识别孕妇可安全使用的口红配方要求.json",
        "安全": "json/识别孕妇可安全使用的口红配方要求.json"
    }
    
    # 根据查询关键词选择对应的JSON文件
    selected_file = None
    for keyword, file_path in json_files.items():
        if keyword in query:
            selected_file = file_path
            break
    
    # 如果没有匹配的关键词，默认使用第一个文件
    if not selected_file:
        selected_file = "json/找出敏感肌可用的玻尿酸面膜核心成分.json"
    
    try:
        # 读取JSON文件
        with open(selected_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取documents数据并转换为所需格式
        results = []
        documents = data.get('documents', [])
        
        for doc in documents[:top_k]:
            result = {
                "document": doc.get('metadata', {}).get('document_display_name', 'Unknown Document'),
                "content": doc.get('text', ''),
                "score": doc.get('score', 0.0),
                "paragraph_id": doc.get('uid', '')
            }
            results.append(result)
        
        return results
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # 如果读取JSON文件失败，返回默认结果
        print(f"Error reading JSON file: {e}")
        
        # 默认返回值 - 模拟化妆品相关文档检索结果
        default_results = [
            {
                "document": "化妆品成分安全报告.docx",
                "content": "玻尿酸（透明质酸）是一种天然存在的多糖，具有卓越的保湿能力。分子量不同的玻尿酸具有不同的渗透性，小分子玻尿酸能够深入肌肤底层，大分子玻尿酸在肌肤表面形成保护膜。",
                "score": 0.95,
                "paragraph_id": "para_001"
            },
            {
                "document": "敏感肌护肤指南.docx",
                "content": "敏感肌肤在选择护肤品时应避免含有酒精、香精、防腐剂等刺激性成分。推荐使用含有神经酰胺、烟酰胺等舒缓成分的产品。玻尿酸作为温和的保湿成分，通常适合敏感肌使用。",
                "score": 0.88,
                "paragraph_id": "para_002"
            },
            {
                "document": "面膜产品评测.docx",
                "content": "市面上的玻尿酸面膜种类繁多，价格从几元到几百元不等。消费者在选择时应注意查看成分表，避免选择含有过多添加剂的产品。优质的玻尿酸面膜应该质地温和，不含刺激性成分。",
                "score": 0.82,
                "paragraph_id": "para_003"
            },
            {
                "document": "广告软文.docx",
                "content": "立即购买我们的超级玻尿酸面膜！现在下单立享8折优惠，买二送一！我们的面膜采用进口玻尿酸，效果立竿见影，让你的肌肤瞬间水润光滑！",
                "score": 0.45,
                "paragraph_id": "para_004"
            },
            {
                "document": "化学成分词典.docx",
                "content": "透明质酸钠（Sodium Hyaluronate）是玻尿酸的钠盐形式，分子量较小，更容易被肌肤吸收。在化妆品中常用作保湿剂，浓度通常在0.1%-2%之间。",
                "score": 0.79,
                "paragraph_id": "para_005"
            },
            {
                "document": "错误信息文档.docx",
                "content": "所有化学成分都对肌肤有害，天然成分才是最安全的选择。玻尿酸虽然听起来像化学物质，但实际上是完全天然的，可以大量使用而不会有任何副作用。",
                "score": 0.35,
                "paragraph_id": "para_006"
            }
        ]
        
        return default_results[:top_k]

def rerank_results(initial_results: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
    """
    重排序检索结果
    
    Args:
        initial_results: 初始检索结果
        query: 原始查询（可选）
    
    Returns:
        重排序后的结果列表
    
    TODO: 替换为真实的重排序模型实现
    """
    # 模拟重排序延迟
    time.sleep(0.5)
    
    # 简单的重排序逻辑：根据质量分数重新排序
    reranked = []
    for result in initial_results:
        new_result = result.copy()
        
        # 模拟重排序分数计算
        quality_penalty = 0
        if "优惠" in result['content'] or "购买" in result['content']:
            quality_penalty = -0.3  # 广告内容降权
        elif "所有" in result['content'] and "都" in result['content']:
            quality_penalty = -0.2  # 绝对化表述降权
        elif "临床" in result['content'] or "研究" in result['content']:
            quality_penalty = 0.1   # 科学内容加权
        
        new_result['new_score'] = result['score'] + quality_penalty
        new_result['rerank_reason'] = f"质量调整: {quality_penalty:+.1f}"
        reranked.append(new_result)
    
    # 按新分数排序
    reranked.sort(key=lambda x: x['new_score'], reverse=True)
    
    return reranked

def generate_answer(context: str, query: str = "") -> str:
    """
    基于上下文生成答案
    
    Args:
        context: 检索到的上下文信息
        query: 原始查询
    
    Returns:
        生成的答案文本
    
    TODO: 替换为真实的生成模型实现
    """
    # 模拟生成延迟
    time.sleep(2)
    
    # 默认答案模板
    default_answers = {
        "玻尿酸": """
基于文档分析，敏感肌可用的玻尿酸面膜应具备以下核心成分特征：

**主要活性成分：**
1. 透明质酸钠（Sodium Hyaluronate）- 小分子玻尿酸，浓度0.1-2%
2. 大分子透明质酸 - 在肌肤表面形成保护膜
3. 神经酰胺 - 修复肌肤屏障
4. 烟酰胺 - 舒缓抗炎

**应避免成分：**
- 酒精（乙醇）
- 人工香精
- 刺激性防腐剂
- 过多添加剂

**安全性建议：**
敏感肌用户应选择成分简单、经过敏感性测试的产品，建议先进行局部测试。
        """,
        
        "孕妇口红": """
基于安全性分析，孕妇可安全使用的口红应满足以下配方要求：

**安全成分：**
1. 天然蜡类（蜂蜡、棕榈蜡）
2. 植物油脂（荷荷巴油、乳木果油）
3. 维生素E（抗氧化剂）
4. 天然色素（胭脂虫红、氧化铁）

**严格禁用成分：**
- 铅（<10mg/kg，建议<5mg/kg）
- 汞（<1mg/kg）
- 视黄醇及其衍生物
- 水杨酸
- 对苯二酚

**选择建议：**
优先选择有机认证、孕妇专用标识的产品，避免长时间佩戴，使用后及时清洁。
        """,
        
        "抗衰老精华": """
基于科学研究，抗衰老精华中的有效活性成分包括：

**一级活性成分：**
1. 维生素C（L-抗坏血酸）- 浓度10-20%
   - 促进胶原蛋白合成
   - 抗氧化，淡化色斑

2. 视黄醇（维生素A）- 浓度0.25-1%
   - 加速细胞更新
   - 改善细纹和毛孔

3. 胜肽复合物 - 浓度2-5%
   - 刺激胶原蛋白生成
   - 紧致肌肤

**辅助成分：**
- 透明质酸：保湿锁水
- 烟酰胺：提亮肤色
- 抗氧化剂：保护成分稳定性

**使用注意：**
建议晚间使用，白天需配合防晒。初次使用应从低浓度开始，逐步建立耐受性。
        """
    }
    
    # 根据上下文内容选择合适的答案
    if "玻尿酸" in context or "敏感肌" in context:
        return default_answers["玻尿酸"]
    elif "孕妇" in context or "口红" in context:
        return default_answers["孕妇口红"]
    elif "抗衰老" in context or "精华" in context:
        return default_answers["抗衰老精华"]
    else:
        return """
基于提供的文档信息，我已为您整理了相关的专业建议。

请注意，以上信息仅供参考，具体产品选择建议咨询专业皮肤科医生或化妆品专家。
在使用任何新产品前，建议先进行过敏性测试。
        """

def get_document_content(document_name: str) -> str:
    """
    获取文档完整内容
    
    Args:
        document_name: 文档名称
    
    Returns:
        文档内容
    
    TODO: 替换为真实的文档存储系统
    """
    # 模拟文档内容
    documents = {
        "化妆品成分安全报告.docx": "这是一份详细的化妆品成分安全性分析报告...",
        "敏感肌护肤指南.docx": "敏感肌肤护理的完整指南...",
        "面膜产品评测.docx": "各类面膜产品的专业评测...",
        "孕期化妆品安全指南.docx": "孕妇化妆品使用安全指南...",
        "抗衰老成分研究.docx": "抗衰老成分的科学研究报告..."
    }
    
    return documents.get(document_name, "文档内容未找到")

def evaluate_answer(answer: str, reference: str = "") -> int:
    """
    评估答案质量
    
    Args:
        answer: 待评估的答案
        reference: 参考答案（可选）
    
    Returns:
        评估分数
    
    TODO: 替换为真实的答案评估模型
    """
    # 简单的评估逻辑
    score = 0
    
    # 长度评估
    if len(answer) > 100:
        score += 3
    if len(answer) > 300:
        score += 2
    
    # 结构评估
    if "**" in answer or "##" in answer:  # 包含格式化
        score += 2
    
    # 内容评估
    key_terms = ["成分", "浓度", "安全", "建议", "避免", "推荐"]
    for term in key_terms:
        if term in answer:
            score += 1
    
    # 专业性评估
    professional_terms = ["透明质酸", "神经酰胺", "烟酰胺", "视黄醇", "胜肽"]
    for term in professional_terms:
        if term in answer:
            score += 1
    
    return min(score, 10)  # 最高10分

def vector_search(query: str, collection_name: str = "default") -> List[Dict[str, Any]]:
    """
    向量检索接口
    
    Args:
        query: 查询文本
        collection_name: 向量集合名称
    
    Returns:
        检索结果
    
    TODO: 替换为真实的向量数据库实现（如Chroma、Pinecone等）
    """
    # 调用主检索函数
    return search_documents(query)

def hybrid_search(query: str, alpha: float = 0.7) -> List[Dict[str, Any]]:
    """
    混合检索（向量+关键词）
    
    Args:
        query: 查询文本
        alpha: 向量检索权重
    
    Returns:
        混合检索结果
    
    TODO: 实现真实的混合检索逻辑
    """
    # 简化实现：直接返回向量检索结果
    return search_documents(query)

def get_embedding(text: str) -> List[float]:
    """
    获取文本嵌入向量
    
    Args:
        text: 输入文本
    
    Returns:
        嵌入向量
    
    TODO: 替换为真实的嵌入模型（如OpenAI、Sentence-BERT等）
    """
    # 返回随机向量作为示例
    return [random.random() for _ in range(768)]

def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算向量相似度
    
    Args:
        vec1: 向量1
        vec2: 向量2
    
    Returns:
        相似度分数
    
    TODO: 实现真实的相似度计算（余弦相似度等）
    """
    # 简化实现
    return random.uniform(0.3, 0.95)

# 游戏相关的辅助函数
def get_game_documents() -> List[str]:
    """
    获取游戏中使用的文档列表
    
    Returns:
        文档名称列表
    """
    return [
        "化妆品成分安全报告.docx",
        "敏感肌护肤指南.docx",
        "面膜产品评测.docx",
        "孕期化妆品安全指南.docx",
        "口红成分分析.docx",
        "抗衰老成分研究.docx",
        "精华液配方分析.docx",
        "临床试验报告.docx",
        "广告软文.docx",  # 干扰文档
        "错误信息文档.docx"  # 干扰文档
    ]

def validate_rag_system() -> Dict[str, bool]:
    """
    验证RAG系统各组件状态
    
    Returns:
        各组件状态字典
    
    TODO: 实现真实的系统健康检查
    """
    return {
        "vector_db": True,
        "embedding_model": True,
        "rerank_model": True,
        "generation_model": True,
        "document_store": True
    }

if __name__ == "__main__":
    # 测试函数
    print("测试RAG后端函数...")
    
    # 测试检索
    results = search_documents("玻尿酸面膜敏感肌")
    print(f"检索结果数量: {len(results)}")
    
    # 测试重排序
    reranked = rerank_results(results)
    print(f"重排序完成，新分数: {[r['new_score'] for r in reranked[:3]]}")
    
    # 测试生成
    answer = generate_answer("玻尿酸相关内容")
    print(f"生成答案长度: {len(answer)}")
    
    print("所有函数测试完成！")