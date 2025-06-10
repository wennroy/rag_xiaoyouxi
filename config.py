"""RAG竞技场游戏配置文件

包含游戏的所有配置参数，可以根据需要调整
"""

# 游戏基础配置
GAME_CONFIG = {
    # 基础设置
    "game_name": "RAG特工黑客松",
    "version": "1.0.0",
    "max_teams": 3,
    "stages": 3,
    
    # 时间设置（分钟）
    "stage_time_limits": {
        1: 5,   # 检索风暴
        2: 8,   # 重排攻防战
        3: 10   # 生成终极战
    },
    
    # 评分设置
    "scoring": {
        # 阶段1：检索风暴
        "stage1": {
            "correct_paragraph": 2,    # 正确段落得分
            "wrong_paragraph": -3,     # 错误段落扣分
            "max_selections": 3        # 最大选择数量
        },
        
        # 阶段2：重排攻防战
        "stage2": {
            "remove_correct": 3,       # 正确删除得分
            "add_external": 5,         # 添加外部知识得分
            "required_removals": 2     # 必须删除的段落数
        },
        
        # 阶段3：生成终极战
        "stage3": {
            "generation_base": 10,     # 生成答案基础分
            "defense_success": 8,      # 防御成功得分
            "quality_bonus": 5         # 质量奖励分
        }
    },
    
    # 文档配置
    "documents": {
        "real_docs_path": "documents/real",
        "fake_docs_path": "documents/fake",
        "interference_ratio": 0.3,  # 干扰文档比例
        "shuffle_order": True       # 是否随机打乱文档顺序
    },
    
    # 界面配置
    "ui": {
        "theme": "light",
        "show_scores_realtime": True,
        "enable_animations": True,
        "auto_refresh_interval": 5  # 秒
    }
}

# 队伍任务配置
TEAM_TASKS = {
    "Team 1": {
        "task": "找出敏感肌可用的玻尿酸面膜核心成分",
        "domain": "敏感肌护理",
        "key_terms": ["玻尿酸", "敏感肌", "面膜", "成分"],
        "expected_docs": ["化妆品成分安全报告.docx", "敏感肌护肤指南.docx"]
    },
    "Team 2": {
        "task": "识别孕妇可安全使用的口红配方要求",
        "domain": "孕期化妆品安全",
        "key_terms": ["孕妇", "口红", "安全", "配方"],
        "expected_docs": ["孕期化妆品安全指南.docx"]
    },
    "Team 3": {
        "task": "确定抗衰老精华中的有效活性成分",
        "domain": "抗衰老护肤",
        "key_terms": ["抗衰老", "精华", "活性成分"],
        "expected_docs": ["抗衰老成分研究.docx", "精华液配方分析.docx"]
    }
}

# 幻觉炸弹配置
HALLUCINATION_BOMBS = {
    "Team 1": "所有防腐剂都有致癌风险，应该完全避免使用",
    "Team 2": "孕妇可以安全使用任何标注为'天然'的化学成分",
    "Team 3": "维生素C浓度越高抗衰老效果越好，建议使用50%以上浓度"
}

# RAG系统配置
RAG_CONFIG = {
    # 检索配置
    "retrieval": {
        "top_k": 10,
        "similarity_threshold": 0.3,
        "max_doc_length": 1000,
        "chunk_size": 200,
        "chunk_overlap": 50
    },
    
    # 重排序配置
    "reranking": {
        "enabled": True,
        "model_name": "default",
        "top_k_rerank": 5,
        "score_threshold": 0.5
    },
    
    # 生成配置
    "generation": {
        "max_length": 500,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.1
    }
}

# 系统监控配置
MONITORING_CONFIG = {
    "log_level": "INFO",
    "log_file": "game.log",
    "metrics_collection": True,
    "performance_tracking": True,
    "error_reporting": True
}

# 安全配置
SECURITY_CONFIG = {
    "enable_input_validation": True,
    "max_query_length": 200,
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_minute": 30
    },
    "content_filtering": {
        "enabled": True,
        "blocked_terms": ["hack", "exploit", "injection"]
    }
}

# 导出配置
EXPORT_CONFIG = {
    "formats": ["json", "csv", "xlsx"],
    "include_timestamps": True,
    "include_metadata": True,
    "compress_output": False
}

# 开发配置
DEV_CONFIG = {
    "debug_mode": False,
    "mock_rag_responses": True,  # 使用模拟RAG响应
    "enable_profiling": False,
    "test_data_generation": True
}

# 获取配置的辅助函数
def get_config(section: str = None):
    """获取配置信息
    
    Args:
        section: 配置节名称，如果为None则返回所有配置
    
    Returns:
        配置字典
    """
    all_configs = {
        "game": GAME_CONFIG,
        "teams": TEAM_TASKS,
        "hallucination": HALLUCINATION_BOMBS,
        "rag": RAG_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "security": SECURITY_CONFIG,
        "export": EXPORT_CONFIG,
        "dev": DEV_CONFIG
    }
    
    if section:
        return all_configs.get(section, {})
    return all_configs

def update_config(section: str, key: str, value):
    """更新配置值
    
    Args:
        section: 配置节名称
        key: 配置键
        value: 新值
    """
    configs = {
        "game": GAME_CONFIG,
        "teams": TEAM_TASKS,
        "hallucination": HALLUCINATION_BOMBS,
        "rag": RAG_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "security": SECURITY_CONFIG,
        "export": EXPORT_CONFIG,
        "dev": DEV_CONFIG
    }
    
    if section in configs and key in configs[section]:
        configs[section][key] = value
        return True
    return False

def validate_config():
    """验证配置的有效性
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # 验证基础配置
    if GAME_CONFIG["max_teams"] < 2:
        errors.append("队伍数量不能少于2个")
    
    if GAME_CONFIG["stages"] != 3:
        errors.append("当前版本只支持3个阶段")
    
    # 验证时间配置
    for stage, time_limit in GAME_CONFIG["stage_time_limits"].items():
        if time_limit < 1:
            errors.append(f"阶段{stage}的时间限制不能少于1分钟")
    
    # 验证评分配置
    if GAME_CONFIG["scoring"]["stage1"]["wrong_paragraph"] >= 0:
        errors.append("错误段落应该是负分")
    
    # 验证队伍任务
    if len(TEAM_TASKS) != GAME_CONFIG["max_teams"]:
        errors.append("队伍任务数量与最大队伍数不匹配")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    # 配置验证
    is_valid, errors = validate_config()
    
    if is_valid:
        print("✅ 配置验证通过")
        print(f"游戏名称: {GAME_CONFIG['game_name']}")
        print(f"版本: {GAME_CONFIG['version']}")
        print(f"最大队伍数: {GAME_CONFIG['max_teams']}")
        print(f"阶段数: {GAME_CONFIG['stages']}")
    else:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")