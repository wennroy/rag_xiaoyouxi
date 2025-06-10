# 🕵️ RAG特工黑客松 - 零道具·全数字版RAG竞技场

一个基于Streamlit的RAG（检索增强生成）竞技游戏，让参与者通过实际操作RAG系统来学习和竞技。

## 🎮 游戏概述

**游戏名称**：RAG特工黑客松  
**核心设定**：3组玩家化身"数据特工"，使用RAG系统破解「机密任务」  
**技术栈**：Streamlit + Python + RAG后端系统  
**竞技亮点**：纯键盘操作 | 实时排行榜 | 错误路径可视化

## 🏆 三阶段游戏设计

### 第一阶段：检索风暴（5分钟）
- **任务**：从干扰文档中定位关键证据
- **操作**：运行检索代码，提交top3相关段落编号
- **计分**：正确段落+2分/条，选中干扰文档-3分

### 第二阶段：重排攻防战（8分钟）
- **任务**：优化初始检索结果
- **操作**：删除2条最不相关段落，添加1条外部知识
- **计分**：合理删除+3分，有效添加+5分

### 第三阶段：生成终极战（10分钟）
- **任务**：生成可信报告并防御攻击
- **操作**：生成答案，防御"幻觉炸弹"挑战
- **计分**：答案完整性10分，成功防御+8分

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/macOS/Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd rag_xiaoyouxi
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **生成游戏文档**
```bash
python generate_documents.py
```

4. **启动游戏**
```bash
streamlit run app.py
```

5. **打开浏览器**
访问 `http://localhost:8501` 开始游戏

## 📁 项目结构

```
rag_xiaoyouxi/
├── app.py                 # 主Streamlit应用
├── rag_backend.py         # RAG后端函数（默认实现）
├── generate_documents.py  # 文档生成脚本
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
└── documents/            # 游戏文档
    ├── real/            # 真实专业文档
    │   ├── 化妆品成分安全报告.docx
    │   ├── 敏感肌护肤指南.docx
    │   ├── 孕期化妆品安全指南.docx
    │   ├── 抗衰老成分研究.docx
    │   ├── 精华液配方分析.docx
    │   └── 临床试验报告.docx
    └── fake/            # 混淆文档
        ├── 广告软文.docx
        ├── 错误信息文档.docx
        └── 伪科学报告.docx
```

## 🔧 RAG后端集成

### 当前状态
`rag_backend.py` 文件包含所有必需的RAG函数，但返回默认值。这些函数包括：

- `search_documents()` - 文档检索
- `rerank_results()` - 结果重排序
- `generate_answer()` - 答案生成
- `get_document_content()` - 文档内容获取
- `evaluate_answer()` - 答案评估

### 集成真实RAG系统

要集成您的RAG系统，请替换 `rag_backend.py` 中的函数实现：

```python
# 示例：集成向量数据库
def search_documents(query: str, top_k: int = 10):
    # TODO: 替换为您的向量检索实现
    # 例如：使用Chroma、Pinecone、Faiss等
    
    # 您的代码：
    # results = your_vector_db.search(query, top_k)
    # return format_results(results)
    
    # 当前返回默认值
    return default_search_results()
```

### 推荐的RAG技术栈

- **向量数据库**：Chroma, Pinecone, Faiss
- **嵌入模型**：OpenAI Embeddings, Sentence-BERT
- **重排序模型**：Cohere Rerank, BGE Reranker
- **生成模型**：OpenAI GPT, Claude, 本地LLM

## 🎯 游戏配置

### 任务配置
游戏包含三个预设任务：
1. **Team 1**：找出敏感肌可用的玻尿酸面膜核心成分
2. **Team 2**：识别孕妇可安全使用的口红配方要求
3. **Team 3**：确定抗衰老精华中的有效活性成分

### 文档库配置
- **真实文档**：6份专业化妆品文档
- **干扰文档**：3份包含错误信息的文档
- **格式**：所有文档均为docx格式

### 评分系统
- **检索阶段**：正确选择+2分，错误选择-3分
- **重排阶段**：优化操作+3-5分
- **生成阶段**：答案质量+防御能力，最高18分

## 🎨 界面特性

### 游戏控制台
- 团队选择器
- 实时记分板
- 阶段进度显示
- 游戏控制按钮

### 主游戏区域
- 任务说明面板
- 检索操作界面
- 结果展示区域
- 答案提交表单

### 可视化元素
- 相关性分数图表
- 重排序前后对比
- 实时分数更新
- 错误路径高亮

## 🔍 教育价值

### 技术学习点
1. **向量检索 vs 关键词检索**的差异
2. **重排序模型**的重要性
3. **生成模型幻觉**的识别和防御
4. **RAG系统**的完整工作流程

### 实践技能
- 检索查询优化
- 结果质量评估
- 信息源可信度判断
- 系统性能调优

## 🚨 故障排除

### 常见问题

**Q: Streamlit启动失败**
```bash
# 检查Python版本
python --version  # 需要3.8+

# 重新安装依赖
pip install --upgrade streamlit
```

**Q: 文档生成失败**
```bash
# 安装文档处理库
pip install python-docx

# 检查权限
# 确保有写入documents/目录的权限
```

**Q: 游戏界面显示异常**
```bash
# 清除Streamlit缓存
streamlit cache clear

# 重启应用
streamlit run app.py --server.port 8502
```

### 性能优化

- **文档加载**：预加载文档内容到内存
- **检索速度**：使用向量数据库索引
- **并发处理**：支持多团队同时操作
- **缓存策略**：缓存检索结果和生成答案

## 🎪 游戏运营建议

### 现场部署
1. **硬件要求**：3台参赛电脑 + 1台主控电脑
2. **网络环境**：局域网或云服务器部署
3. **投影设备**：显示实时排行榜和关键操作

### 主持人指南
1. **开场介绍**：RAG技术背景和游戏规则
2. **过程引导**：关键节点的技术讲解
3. **结果分析**：复盘各队策略和技术要点

### 扩展玩法
- **自定义文档库**：根据不同主题准备文档
- **难度调节**：调整干扰文档比例
- **团队协作**：增加多人协作环节
- **实时对抗**：队伍间相互干扰机制

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**🎉 祝您游戏愉快，学习进步！**