# -*- coding: utf-8 -*-

"""
棋盘数据配置模块 V2.0
=====================

架构设计：
- 角色ID系统：全局唯一标识，避免硬编码中文名
- 双类型支持：限定棋盘（limited）+ 常驻棋盘（permanent）
- 动态扩展：新增棋盘只需添加配置，无需修改核心逻辑
- 文件适配：支持当前扁平结构 + 未来文件夹结构

版本历史：
- V1.0: 单棋盘硬编码
- V2.0: 多棋盘 + 角色ID系统 + 双类型支持（当前版本）
"""

import os
import sys

# ============================================================
# 资源路径处理函数
# ============================================================
def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径

    自动检测运行环境，返回正确的文件路径，确保在不同环境下都能正确访问数据文件

    参数:
        relative_path: 相对路径（如 "限定棋盘浔地图手动统计.csv"）

    返回:
        str: 资源文件的绝对路径

    使用示例:
        csv_path = get_resource_path("限定棋盘浔地图手动统计.csv")
        with open(csv_path, 'r', encoding='utf-8') as f:
            data = f.read()
    """
    if hasattr(sys, '_MEIPASS'):
        # 特殊环境：使用临时目录路径
        base_path = sys._MEIPASS
    else:
        # 标准环境：使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def check_resource_exists(relative_path):
    """
    检查资源文件是否存在

    参数:
        relative_path: 相对路径

    返回:
        bool: 文件是否存在
    """
    resource_path = get_resource_path(relative_path)
    return os.path.exists(resource_path)


# ============================================================
# 第一层：全局角色数据库（单一数据源）
# ============================================================

class CharIds:
    """
    角色ID常量类
    使用英文ID避免中文拼写错误，提供IDE自动补全支持
    
    命名规范：
    - S级角色: S_[拼音]
    - A级角色: A_[拼音]
    """
    # S级限定角色
    S_XUN = "xun"
    S_REQUIEM = "requiem"
    
    # A级角色（当前池子）
    A_HAIYUE = "haiyue"       # 海月
    A_YI = "yi"               # 翳
    A_HANIYA = "haniya"       # 哈尼娅
    A_BOHE = "bohe"           # 薄荷
    A_AIDEJIA = "aidejia"     # 埃德嘉
    A_ADELE = "adele"         # 阿德勒
    
    # 预留位置：未来新增角色
    # S_CHUN = "chun"          # 示例：第3个S级角色
    # A_LINGXI = "lingxi"      # 示例：新A级角色


CHARACTER_DB = {
    # 全局角色数据库 - 每个角色只定义一次，作为唯一数据源（SSOT）
    # 结构：{role_id: {"name": str, "rarity": str, "type": str}}
    CharIds.S_XUN: {
        "name": "浔",
        "rarity": "S",
        "type": "limited",
    },
    CharIds.S_REQUIEM: {
        "name": "安魂曲",
        "rarity": "S",
        "type": "limited",
    },
    CharIds.A_HAIYUE: {
        "name": "海月",
        "rarity": "A",
        "type": "limited",
    },
    CharIds.A_YI: {
        "name": "翳",
        "rarity": "A",
        "type": "limited",
    },
    CharIds.A_HANIYA: {
        "name": "哈尼娅",
        "rarity": "A",
        "type": "limited",
    },
    CharIds.A_BOHE: {
        "name": "薄荷",
        "rarity": "A",
        "type": "limited",
    },
    CharIds.A_AIDEJIA: {
        "name": "埃德嘉",
        "rarity": "A",
        "type": "limited",
    },
    CharIds.A_ADELE: {
        "name": "阿德勒",
        "rarity": "A",
        "type": "limited",
    },
}


def get_char_name(char_id: str) -> str:
    """
    根据角色ID获取显示名称
    
    参数:
        char_id: 角色ID（如 "xun", "haiyue"）
    
    返回:
        角色中文名称，如果ID不存在则返回 "[未知:ID]"
    
    示例:
        >>> get_char_name("xun")
        '浔'
        >>> get_char_name("unknown")
        '[未知:unknown]'
    """
    char_info = CHARACTER_DB.get(char_id)
    if char_info:
        return char_info["name"]
    print(f"[警告] 未找到角色ID: {char_id}")
    return f"[未知:{char_id}]"


def validate_char_id(char_id: str) -> bool:
    """
    验证角色ID是否存在
    
    参数:
        char_id: 待验证的角色ID
    
    返回:
        True if exists, False otherwise
    """
    return char_id in CHARACTER_DB


# ============================================================
# 第二层：通用规则模板（所有限定棋盘共享）
# ============================================================

LIMITED_BOARD_TEMPLATE = {
    # 限定棋盘通用规则模板 - 所有限定棋盘共享相同的机制和参数，只有角色池不同
    # 注意：常驻棋盘不使用此模板，可能有完全不同的规则
    
    # 规则参数（从规则说明.txt提取）
    "rules": {
        # ===== S级角色概率系统 =====
        "s_rate": 0.0187,              # S级综合概率（含保底）
        "s_base_rate_normal": 0.0099,   # 基准棋盘基础概率
        "s_base_rate_variant": 0.1959,  # 变格棋盘基础概率
        "s_pity_variant_threshold": 70, # 变格触发阈值（连续多少次未出S级）
        "s_pity_hard": 90,              # 硬保底（必定获得）
        
        # ===== A级道具概率系统 =====
        "a_rate_total": 0.2298,         # A级综合概率（含保底和赠礼）
        "a_character_rate": 0.1167,     # A级角色等效概率
        "a_disk_rate": 0.1131,          # A级弧盘概率
        
        # ===== B级弧盘概率 =====
        "b_disk_rate": 0.6533,          # B级弧盘综合概率
        
        # ===== 集点赠礼系统 =====
        "gift_interval": 10,            # 赠礼间隔（每N次掷骰）
        "gift_a_character_rate": 0.20,  # 赠礼中A级角色概率
        "gift_a_disk_rate": 0.80,       # 赠礼中A级弧盘概率
        
        # ===== 格子类型进入概率（暗箱） =====
        "cell_rates": {
            "apprentice_chest": 0.4593,   # 学徒宝箱
            "brave_chest": 0.2007,        # 勇者宝箱
            "companion": 0.1086,          # 于此同行
            "mist_box": 0.1547,           # 迷迭棋盒
            "arcade_blind": 0.0331,       # 弧光盲盒
            "sleep_pool": 0.0315,         # 沉眠池
            "roll_again": 0.0157,         # 再来一次
            "multi_surprise": 0.0038,     # 多重惊喜
            "today_outfit": 0.0033,       # 今日穿搭
            "vehicle_paint": 0.0033,      # 改装时刻·涂装
            "glider_skin": 0.0171,        # 风向标
        },
        
        # ===== 同行角色子概率 =====
        "companion_sub_rates": {
            "s_character": 0.1190,        # S级同行概率
            "a_character": 0.9670,        # A级同行概率（注意：这是条件概率）
        },
        
        # ===== 宝箱S级概率 =====
        "chest_s_rate": {
            "apprentice_chest": 0.002,    # 学徒宝箱S级概率
            "brave_chest": 0.03,          # 勇者宝箱S级概率
        },
        
        # ===== 重复获得补偿规则 =====
        "duplicate_rules": {
            "s_character": {
                "range_2_7": {"fragment": 1, "gold_chip": 40},
                "range_8_plus": {"gold_chip": 80},
            },
            "a_character": {
                "range_2_7": {"fragment": 1, "gold_chip": 6},
                "range_8_plus": {"gold_chip": 12},
            },
            "a_disk": {"extra_gold_chip": 4},
            "b_disk": {"extra_white_chip": 20},
            "skin_today_outfit": {"gold_chip": 16},
            "skin_vehicle_paint": {"gold_chip": 16},
            "skin_glider_skin": {"gold_chip": 4},
        },
        
        # ===== 沉眠池配置 =====
        "sleep_pool": {
            "guardian_flee_distance": 9,
            "max_chase_rounds": 3,
            "guardian_speed": 2,
            "success_reward_gold": 30,
        },
        
        # ===== 迷迭棋盒白色棋子数量池 =====
        "mist_box_white_chips": [15, 20, 25, 30, 35, 40, 45, 50],
        
        # ===== 皮肤累计领取阈值 =====
        "skin_claim_thresholds": {
            "today_outfit": 200,
            "vehicle_paint": 120,
            "glider_skin": 50,
        },
        
        # ===== 皮肤首次获得概率 =====
        "skin_first_get_rates": {
            "today_outfit": 0.0068,
            "vehicle_paint": 0.0100,
            "glider_skin": 0.0296,
        },
    },

    # 弧盘池（所有限定棋盘相同）
    "a_disk_pool": [
        "被遗忘者",
        "开始净空",
        "当心头顶",
        "勿忘伞",
        "拔刀",
    ],

    "b_disk_pool": [
        "成功的第一步",
        "电音狂欢",
        "危险游戏",
        "笑口常开",
        "我们",
    ],

    # 分支配置（所有限定棋盘相同）
    "branches": {
        "s_character_zone": {          # 分支1：S级角色区
            "entry_main_idx": 16,      # 入口：主路径index=16
            "skip_main_idx": 17,       # 跳过点：主路径index=17
            "exit_main_idx": 18,       # 出口：主路径index=18
            "branch_len": 9,           # 分支长度：9格
        },
        "skin_surprise": {             # 分支2：皮肤惊喜区
            "entry_main_idx": 43,
            "skip_main_idx": 44,
            "exit_main_idx": 45,
            "branch_len": 9,
        },
    },
}


# ============================================================
# 第三层：各棋盘差异化配置（通过ID引用角色）
# ============================================================

BOARDS_REGISTRY = {
    # 棋盘注册表 - 所有可用棋盘的配置中心，通过board_id索引
    # 支持两种类型：limited（限定棋盘） / permanent（常驻棋盘）
    # 新增棋盘步骤：1.添加角色 2.添加配置 3.实现布局函数 4.UI自动识别

    # ============================================================
    # 限定棋盘1：浔
    # ============================================================
    "limited_xun": {
        "display_name": "限定棋盘（浔）",
        "board_type": "limited",              # 限定棋盘类型
        
        # S级角色（使用ID引用）
        "s_character_id": CharIds.S_XUN,
        
        # 于此同行角色映射（主路径4格 + 分支1第1格）
        # key: 格子编号（int或str），value: 角色ID
        "companions_id_map": {
            1: CharIds.A_HAIYUE,              # 主路径第1格 → 海月
            10: CharIds.A_YI,                 # 主路径第10格 → 翳
            29: CharIds.A_HANIYA,             # 主路径第29格 → 哈尼娅
            37: CharIds.A_HANIYA,             # 主路径第37格 → 哈尼娅
            "B1-0": CharIds.S_XUN,            # 分支1第0格（S级角色）→ 浔
        },
        
        # A级角色池（使用ID列表）
        "a_pool_main_ids": [                  # 主池（高概率 ~3.5% each）
            CharIds.A_HANIYA,
            CharIds.A_YI,
            CharIds.A_HAIYUE,
        ],
        "a_pool_gift_only_ids": [             # 仅赠礼池（低概率 ~0.33% each）
            CharIds.A_BOHE,
            CharIds.A_AIDEJIA,
            CharIds.A_ADELE,
        ],
        
        # 坐标布局数据（从CSV提取）
        "layout_func": "get_limited_board_layout",
        
        # 文件映射（当前扁平结构，未来可改为文件夹路径）
        "files": {
            "csv": "限定棋盘浔地图手动统计.csv",
            "rules_txt": "限定棋盘浔规则说明.txt",
            "details_txt": "限定棋盘浔详情.txt",
        },
    },

    # ============================================================
    # 限定棋盘2：安魂曲
    # ============================================================
    "limited_requiem": {
        "display_name": "限定棋盘（安魂曲）",
        "board_type": "limited",
        
        # S级角色
        "s_character_id": CharIds.S_REQUIEM,
        
        # 于此同行角色映射
        "companions_id_map": {
            1: CharIds.A_ADELE,              # 主路径第1格 → 阿德勒
            10: CharIds.A_AIDEJIA,           # 主路径第10格 → 埃德嘉
            29: CharIds.A_BOHE,              # 主路径第29格 → 薄荷
            37: CharIds.A_BOHE,              # 主路径第37格 → 薄荷
            "B1-0": CharIds.S_REQUIEM,       # 分支1第0格（S级角色）→ 安魂曲
        },
        
        # A级角色池（与浔互换主池/赠礼池分配）
        "a_pool_main_ids": [
            CharIds.A_BOHE,                  # 薄荷（主池）
            CharIds.A_AIDEJIA,               # 埃德嘉（主池）
            CharIds.A_ADELE,                 # 阿德勒（主池）
        ],
        "a_pool_gift_only_ids": [
            CharIds.A_YI,                    # 翳（仅赠礼）
            CharIds.A_HANIYA,                # 哈尼娅（仅赠礼）
            CharIds.A_HAIYUE,                # 海月（仅赠礼）
        ],
        
        # 坐标布局（与浔坐标完全相同，只是角色名不同）
        "layout_func": "get_requiem_board_layout",
        
        # 文件映射
        "files": {
            "csv": "限定棋盘安魂曲地图手动统计.csv",
            "rules_txt": "限定棋盘安魂曲规则说明.txt",
            "details_txt": "限定棋盘安魂曲详情.txt",
        },
    },

    # ============================================================
    # 常驻棋盘（预留位置，待实现）
    # ============================================================
    # ============================================================
    # 常驻棋盘：默认常驻
    # ============================================================
    "permanent_default": {
        "display_name": "常驻棋盘",
        "board_type": "permanent",
        
        # [新增] 是否可用（False表示暂未开放，UI中会显示但不可选择）
        "enabled": False,

        # 常驻棋盘无S级限定角色
        "s_character_id": None,
        "s_character_name": None,

        # 常驻棋盘无于此同行角色
        "companions_id_map": {},

        # 常驻棋盘的A级角色池（使用全局默认池）
        "a_pool_main_names": [],
        "a_pool_gift_only_names": [],

        # 规则配置
        "rules": {
            "s_rate": 0.0,  # 常驻棋盘无S级角色
        },

        # 分支配置（常驻棋盘可能无特殊分支）
        "branches": {},
    },

    # ============================================================
    # [示例] 限定棋盘3：卡厄斯（未来扩展模板）
    # ============================================================
    # 取消下方注释即可启用卡厄斯棋盘
    # 演示如何为每个棋盘配置完全独立的概率规则
    #
    # "limited_caerus": {
    #     "display_name": "限定棋盘（卡厄斯）",
    #     "board_type": "limited",
    #
    #     # S级角色
    #     "s_character_id": CharIds.S_CAERUS,  # 需要先在CharIds中定义
    #     "s_character_name": "卡厄斯",
    #
    #     # 于此同行角色
    #     "companions_id_map": {
    #         1: CharIds.A_XXX,      # 根据实际文档填写
    #         10: CharIds.A_YYY,
    #         # ... 其他同行角色
    #     },
    #
    #     # A级角色池
    #     "a_pool_main_names": ["角色A", "角色B", "角色C"],  # 主池
    #     "a_pool_gift_only_names": ["角色D", "角色E", "角色F"],  # 赠礼池
    #
    #     # ===== 关键：自定义概率规则（覆盖全局默认值！）=====
    #     "rules": {
    #         # S级概率系统 - 假设卡厄斯的S级概率更高
    #         "s_rate": 0.025,                    # 综合概率 2.5%（默认1.87%）
    #         "s_base_rate_normal": 0.013,         # 基础概率 1.3%（默认0.99%）
    #         "s_base_rate_variant": 0.22,         # 变格概率 22%（默认19.59%）
    #         "s_pity_variant_threshold": 65,      # 变格阈值 65次（默认70次）
    #         "s_pity_hard": 85,                   # 硬保底 85次（默认90次）
    #
    #         # A级概率系统 - 可能也有变化
    #         "a_rate_total": 0.25,                # A级综合概率 25%（默认22.98%）
    #
    #         # 集点赠礼 - 间隔可能不同
    #         "gift_interval": 8,                  # 每8次赠礼（默认10次）
    #         "gift_a_character_rate": 0.25,       # A级角色25%（默认20%）
    #
    #         # 重复补偿规则 - 可能更慷慨或更吝啬
    #         "duplicate_rules": {
    #             "s_character": {
    #                 "range_2_7": {"fragment": 1, "gold_chip": 50},   # +10金（默认40）
    #                 "range_8_plus": {"gold_chip": 100},             # +20金（默认80）
    #             },
    #             # ... 其他重复规则也可以自定义
    #         },
    #
    #         # 沉眠池配置 - 可能不同
    #         "sleep_pool": {
    #             "guardian_flee_distance": 8,    # 守护者逃离距离
    #             "max_chase_rounds": 4,          # 追击回合数
    #             "success_reward_gold": 40,       # 成功奖励金
    #         },
    #
    #         # 皮肤领取阈值 - 可能调整
    #         "skin_claim_thresholds": {
    #             "today_outfit": 180,            # 180次领取（默认200次）
    #             "vehicle_paint": 100,            # 100次领取（默认120次）
    #             "glider_skin": 40,               # 40次领取（默认50次）
    #         },
    #     },
    #
    #     # 分支配置
    #     "branches": {},
    # },
}


# ============================================================
# 第四层：访问接口（自动解析ID → 名称）
# ============================================================

def get_available_boards() -> list:
    """
    获取所有可用棋盘的ID列表（支持双模式）
    
    模式1 - 注册表模式（当前默认）:
        从BOARDS_REGISTRY字典读取硬编码配置
        适用场景：棋盘数量较少（<10个），配置简单
    
    模式2 - 文件夹模式（未来扩展）:
        从boards/目录自动扫描子文件夹
        适用场景：棋盘数量多（>10个），需要模块化管理
        
        文件夹结构示例：
        boards/
        ├── limited_xun/           # 限定棋盘-浔
        │   ├── config.py          # 棋盘配置（必须）
        │   ├── layout.py          # 坐标布局函数（必须）
        │   └── resources/         # 可选资源文件
        │       ├── screenshot.png
        │       └── rules.txt
        ├── limited_requiem/       # 限定棋盘-安魂曲
        │   ├── config.py
        │   └── layout.py
        └── permanent_default/     # 常驻棋盘
            ├── config.py
            └── layout.py
    
    返回:
        board_id列表，如 ["limited_xun", "limited_requiem"]
    
    用途:
        UI下拉框自动填充选项
    """
    registry_boards = list(BOARDS_REGISTRY.keys())
    
    try:
        directory_boards = _scan_boards_directory()
        
        if directory_boards:
            merged = list(set(registry_boards + directory_boards))
            print(f"[信息] 发现 {len(registry_boards)} 个注册表棋盘 + {len(directory_boards)} 个文件夹棋盘")
            return merged
        else:
            return registry_boards
            
    except Exception as e:
        print(f"[警告] 扫描棋盘目录失败: {e}，仅使用注册表配置")
        return registry_boards


def _scan_boards_directory() -> list:
    """
    扫描boards/目录，自动发现新添加的棋盘文件夹
    
    文件夹命名规范：
    - 限定棋盘：limited_[角色拼音] （如 limited_xun, limited_requiem）
    - 常驻棋盘：permanent_[名称] （如 permanent_default）
    
    每个棋盘文件夹必须包含：
    - config.py: 棋盘配置字典（格式同BOARDS_REGISTRY中的条目）
    
    可选文件：
    - layout.py: 坐标布局函数（如果缺失则使用默认布局）
    - resources/: 资源文件（截图、规则说明等）
    
    返回:
       发现的board_id列表（空列表表示未发现或出错）
    """
    boards_dir = os.path.join(os.path.dirname(__file__), "boards")
    
    if not os.path.exists(boards_dir):
        return []
    
    if not os.path.isdir(boards_dir):
        return []
    
    discovered_boards = []
    
    try:
        for folder_name in os.listdir(boards_dir):
            folder_path = os.path.join(boards_dir, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            config_file = os.path.join(folder_path, "config.py")
            
            if not os.path.exists(config_file):
                print(f"[警告] 棋盘文件夹 {folder_name} 缺少config.py，跳过")
                continue
            
            board_id = folder_name
            
            if board_id in BOARDS_REGISTRY:
                print(f"[信息] 文件夹棋盘 {board_id} 已存在于注册表中，跳过")
                continue
            
            try:
                import importlib.util
                
                spec = importlib.util.spec_from_file_location(
                    f"board_config_{board_id}", 
                    config_file
                )
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                if hasattr(config_module, 'BOARD_CONFIG'):
                    board_config = config_module.BOARD_CONFIG
                    
                    BOARDS_REGISTRY[board_id] = board_config
                    discovered_boards.append(board_id)
                    
                    print(f"[成功] 加载文件夹棋盘: {board_id}")
                    
                    layout_file = os.path.join(folder_path, "layout.py")
                    if os.path.exists(layout_file):
                        try:
                            layout_spec = importlib.util.spec_from_file_location(
                                f"board_layout_{board_id}",
                                layout_file
                            )
                            layout_module = importlib.util.module_from_spec(layout_spec)
                            layout_spec.loader.exec_module(layout_module)
                            
                            if hasattr(layout_module, 'get_board_layout'):
                                globals()[f"get_{board_id}_layout"] = layout_module.get_board_layout
                                BOARDS_REGISTRY[board_id]["layout_func"] = f"get_{board_id}_layout"
                                
                        except Exception as layout_err:
                            print(f"[警告] 加载 {board_id} 的layout.py失败: {layout_err}")
                            
                else:
                    print(f"[警告] {folder_name}/config.py 缺少BOARD_CONFIG变量")
                    
            except Exception as e:
                print(f"[错误] 加载 {folder_name}/config.py 失败: {e}")
                continue
                
    except Exception as e:
        print(f"[错误] 扫描boards/目录失败: {e}")
        return []
    
    return discovered_boards


def get_board_config(board_id: str) -> dict:
    """
    获取指定棋盘的完整配置（已解析为可显示的名称）
    
    参数:
        board_id: 棋盘ID（如 "limited_xun"）
    
    返回:
        包含以下字段的字典：
        - display_name: 显示名称
        - board_type: 棋盘类型（"limited"/"permanent"）
        - s_character_name: S级角色名称（已解析）
        - companions: 已解析的同行角色映射 {格子编号: 角色名}
        - a_pool_main_names: A级主池角色名列表
        - a_pool_gift_only_names: A级赠礼池角色名列表
        - layout: 坐标布局数据
        - rules: 规则参数（限定棋盘来自模板，常驻棋盘可能覆盖）
    
    异常:
        KeyError: 如果board_id不存在
    """
    raw_config = BOARDS_REGISTRY[board_id]
    
    # 解析S级角色名称
    s_char_id = raw_config.get("s_character_id")
    s_character_name = get_char_name(s_char_id) if s_char_id else None
    
    # 解析同行角色映射
    resolved_companions = {}
    for cell_idx, char_id in raw_config.get("companions_id_map", {}).items():
        resolved_companions[cell_idx] = get_char_name(char_id)
    
    # 解析A级角色池
    a_pool_main_names = [
        get_char_name(char_id) 
        for char_id in raw_config.get("a_pool_main_ids", [])
    ]
    a_pool_gift_only_names = [
        get_char_name(char_id) 
        for char_id in raw_config.get("a_pool_gift_only_ids", [])
    ]
    
    # 获取坐标布局
    layout_func_name = raw_config.get("layout_func")
    layout = None
    if layout_func_name:
        layout = globals()[layout_func_name]()
    
    # 合并规则（限定棋盘用模板，常驻棋盘可能覆盖）
    if raw_config["board_type"] == "limited":
        rules = LIMITED_BOARD_TEMPLATE["rules"].copy()
        rules.update(raw_config.get("override_rules", {}))
    else:
        rules = raw_config.get("override_rules", {})
    
    return {
        "display_name": raw_config["display_name"],
        "board_type": raw_config["board_type"],
        # [关键] 传递enabled字段（用于UI控制是否可选择）
        "enabled": raw_config.get("enabled", True),  # 默认可用
        "s_character_name": s_character_name,
        "s_character_id": s_char_id,
        "companions": resolved_companions,
        "companions_id_map": raw_config.get("companions_id_map", {}),
        "a_pool_main_names": a_pool_main_names,
        "a_pool_gift_only_names": a_pool_gift_only_names,
        "a_pool_main_ids": raw_config.get("a_pool_main_ids", []),
        "a_pool_gift_only_ids": raw_config.get("a_pool_gift_only_ids", []),
        "layout": layout,
        "rules": rules,
        "files": raw_config.get("files", {}),
    }


def get_limited_boards() -> list:
    """获取所有限定棋盘的ID列表"""
    return [
        bid for bid, config in BOARDS_REGISTRY.items() 
        if config["board_type"] == "limited"
    ]


def get_permanent_boards() -> list:
    """获取所有常驻棋盘的ID列表"""
    return [
        bid for bid, config in BOARDS_REGISTRY.items() 
        if config["board_type"] == "permanent"
    ]


# ============================================================
# 第五层：数据完整性校验
# ============================================================

def validate_board_config(board_id: str) -> tuple:
    """
    验证指定棋盘的配置完整性
    
    参数:
        board_id: 待验证的棋盘ID
    
    返回:
        (is_valid: bool, errors: list[str])
        - is_valid: 是否通过验证
        - errors: 错误信息列表（空列表表示无错误）
    
    校验项目：
    1. S级角色ID存在性
    2. 同行角色ID存在性和唯一性
    3. A级池角色ID存在性
    4. 坐标布局函数可调用
    5. 分支配置一致性
    """
    errors = []
    
    try:
        config = BOARDS_REGISTRY[board_id]
    except KeyError:
        return False, [f"棋盘ID不存在: {board_id}"]
    
    # 1. 检查S级角色ID
    s_char_id = config.get("s_character_id")
    if s_char_id and not validate_char_id(s_char_id):
        errors.append(f"S级角色ID不存在: {s_char_id}")
    
    # 2. 检查同行角色ID
    companions = config.get("companions_id_map", {})
    for cell_idx, char_id in companions.items():
        if not validate_char_id(char_id):
            errors.append(f"格子{cell_idx}的角色ID不存在: {char_id}")
    
    # 3. 检查A级池角色ID
    all_a_pool_ids = (
        config.get("a_pool_main_ids", []) + 
        config.get("a_pool_gift_only_ids", [])
    )
    for char_id in all_a_pool_ids:
        if not validate_char_id(char_id):
            errors.append(f"A级池角色ID不存在: {char_id}")
    
    # 4. 检查坐标布局函数
    layout_func_name = config.get("layout_func")
    if layout_func_name:
        if layout_func_name not in globals():
            errors.append(f"坐标布局函数不存在: {layout_func_name()}")
        else:
            try:
                layout = globals()[layout_func_name]()
                if not layout or "main_path" not in layout:
                    errors.append(f"坐标布局格式错误: 缺少main_path")
            except Exception as e:
                errors.append(f"坐标布局函数调用失败: {e}")
    
    # 5. 检查分支配置（限定棋盘）
    if config["board_type"] == "limited":
        branches = LIMITED_BOARD_TEMPLATE["branches"]
        for branch_name, branch_cfg in branches.items():
            entry = branch_cfg.get("entry_main_idx")
            skip = branch_cfg.get("skip_main_idx")
            exit_idx = branch_cfg.get("exit_main_idx")
            
            if not (entry < skip < exit_idx):
                errors.append(
                    f"分支{branch_name}入口出口顺序错误: "
                    f"entry={entry}, skip={skip}, exit={exit_idx}"
                )
    
    is_valid = len(errors) == 0
    return is_valid, errors


def run_startup_validation() -> bool:
    """
    程序启动时的全面数据校验
    
    打印详细的校验报告到控制台
    
    返回:
        True if all boards pass validation, False otherwise
    """
    print("=" * 70)
    print("棋盘数据完整性校验")
    print("=" * 70)
    
    all_passed = True
    
    for board_id in BOARDS_REGISTRY.keys():
        is_valid, errors = validate_board_config(board_id)
        
        if is_valid:
            print(f"[OK] {board_id}: 配置验证通过")
        else:
            all_passed = False
            print(f"[FAIL] {board_id}: 发现 {len(errors)} 个问题:")
            for err in errors:
                print(f"      - {err}")
    
    # 检查角色ID唯一性
    all_ids = list(CHARACTER_DB.keys())
    if len(all_ids) != len(set(all_ids)):
        print("[FAIL] 存在重复的角色ID！")
        all_passed = False
    else:
        print(f"[OK] 角色ID唯一性检查通过 ({len(all_ids)}个角色)")
    
    print("=" * 70)
    if all_passed:
        print("[SUCCESS] 所有校验通过，系统可以安全运行")
    else:
        print("[WARNING] 发现配置问题，建议修复后再运行")
    print("=" * 70)
    
    return all_passed


# ============================================================
# 第六层：坐标布局数据（从CSV硬编码）
# ============================================================

def get_limited_board_layout():
    """
    获取限定棋盘（浔）的完整布局数据
    
    数据来源：限定棋盘浔地图手动统计.csv
    坐标系：CSV原始行列号（row, col）
    
    返回: dict {
        'main_path': [(row, col, name, idx), ...],  # 55格（0-54号）
        'branch1': [(row, col, name, seq), ...],     # 9格（S级角色区）
        'branch2': [(row, col, name, seq), ...],     # 9格（皮肤惊喜区）
    }
    """
    MAIN_PATH_LAYOUT = [
        (5, 10, "起点", 0),
        (5, 11, "于此同行（海月）", 1),
        (5, 12, "学徒宝箱", 2),
        (5, 13, "风向标", 3),
        (5, 14, "学徒宝箱", 4),
        (4, 14, "学徒宝箱", 5),
        (3, 14, "勇者宝箱", 6),
        (2, 14, "学徒宝箱", 7),
        (2, 15, "学徒宝箱", 8),
        (2, 16, "迷迭棋盒（30个白色棋子）", 9),
        (2, 17, "于此同行（翳）", 10),
        (3, 17, "学徒宝箱", 11),
        (4, 17, "勇者宝箱", 12),
        (5, 17, "学徒宝箱", 13),
        (5, 18, "学徒宝箱", 14),
        (5, 19, "迷迭棋盒（50个白色棋子）", 15),
        (6, 19, "学徒宝箱", 16),
        (7, 19, "于此同行（翳）", 17),
        (8, 19, "勇者宝箱", 18),
        (9, 19, "学徒宝箱", 19),
        (10, 19, "学徒宝箱", 20),
        (11, 19, "迷迭棋盒（30个白色棋子）", 21),
        (11, 18, "弧光盲盒+沉眠池", 22),
        (11, 17, "学徒宝箱", 23),
        (11, 16, "勇者宝箱", 24),
        (11, 15, "学徒宝箱", 25),
        (11, 14, "学徒宝箱", 26),
        (10, 14, "迷迭棋盒（50个白色棋子）", 27),
        (10, 13, "学徒宝箱", 28),
        (10, 12, "于此同行（哈尼娅）", 29),
        (10, 11, "勇者宝箱", 30),
        (10, 10, "学徒宝箱", 31),
        (10, 9, "学徒宝箱", 32),
        (10, 8, "迷迭棋盒（30个白色棋子）", 33),
        (9, 8, "学徒宝箱", 34),
        (9, 7, "学徒宝箱", 35),
        (9, 6, "勇者宝箱", 36),
        (9, 5, "于此同行（哈尼娅）", 37),
        (9, 4, "学徒宝箱", 38),
        (8, 4, "迷迭棋盒（30个白色棋子）", 39),
        (7, 4, "学徒宝箱", 40),
        (6, 4, "迷迭棋盒（50个白色棋子）", 41),
        (5, 4, "勇者宝箱", 42),
        (4, 4, "学徒宝箱", 43),
        (3, 4, "于此同行（海月）", 44),
        (2, 4, "迷迭棋盒（30个白色棋子）", 45),
        (2, 5, "学徒宝箱", 46),
        (2, 6, "学徒宝箱", 47),
        (2, 7, "勇者宝箱", 48),
        (2, 8, "再来一次+沉眠池", 49),
        (2, 9, "学徒宝箱", 50),
        (2, 10, "弧光盲盒", 51),
        (2, 11, "迷迭棋盒（30个白色棋子）", 52),
        (3, 11, "学徒宝箱", 53),
        (4, 11, "勇者宝箱", 54),
    ]

    BRANCH1_LAYOUT = [
        (6, 21, "于此同行（浔）", 1),
        (6, 22, "改装时刻·涂装", 2),
        (6, 23, "勇者宝箱", 3),
        (6, 24, "学徒宝箱", 4),
        (7, 24, "勇者宝箱", 5),
        (8, 21, "勇者宝箱", 9),
        (8, 22, "学徒宝箱", 8),
        (8, 23, "勇者宝箱", 7),
        (8, 24, "学徒宝箱", 6),
    ]

    BRANCH2_LAYOUT = [
        (4, 2, "勇者宝箱", 1),
        (4, 1, "今日穿搭", 2),
        (4, 0, "多重惊喜", 3),
        (3, 0, "勇者宝箱", 4),
        (2, 0, "勇者宝箱", 5),
        (2, 2, "勇者宝箱", 9),
        (1, 2, "勇者宝箱", 8),
        (1, 1, "勇者宝箱", 7),
        (1, 0, "勇者宝箱", 6),
    ]

    return {
        "main_path": MAIN_PATH_LAYOUT,
        "branch1": BRANCH1_LAYOUT,
        "branch2": BRANCH2_LAYOUT,
    }


def get_requiem_board_layout():
    """
    获取限定棋盘（安魂曲）的完整布局数据
    
    注意：与浔棋盘坐标完全相同，只有角色名不同
    数据来源：限定棋盘安魂曲地图手动统计.csv
    """
    MAIN_PATH_LAYOUT = [
        (5, 10, "起点", 0),
        (5, 11, "于此同行（阿德勒）", 1),
        (5, 12, "学徒宝箱", 2),
        (5, 13, "风向标", 3),
        (5, 14, "学徒宝箱", 4),
        (4, 14, "学徒宝箱", 5),
        (3, 14, "勇者宝箱", 6),
        (2, 14, "学徒宝箱", 7),
        (2, 15, "学徒宝箱", 8),
        (2, 16, "迷迭棋盒（30个白色棋子）", 9),
        (2, 17, "于此同行（埃德嘉）", 10),
        (3, 17, "学徒宝箱", 11),
        (4, 17, "勇者宝箱", 12),
        (5, 17, "学徒宝箱", 13),
        (5, 18, "学徒宝箱", 14),
        (5, 19, "迷迭棋盒（50个白色棋子）", 15),
        (6, 19, "学徒宝箱", 16),
        (7, 19, "于此同行（埃德嘉）", 17),
        (8, 19, "勇者宝箱", 18),
        (9, 19, "学徒宝箱", 19),
        (10, 19, "学徒宝箱", 20),
        (11, 19, "迷迭棋盒（30个白色棋子）", 21),
        (11, 18, "弧光盲盒+沉眠池", 22),
        (11, 17, "学徒宝箱", 23),
        (11, 16, "勇者宝箱", 24),
        (11, 15, "学徒宝箱", 25),
        (11, 14, "学徒宝箱", 26),
        (10, 14, "迷迭棋盒（50个白色棋子）", 27),
        (10, 13, "学徒宝箱", 28),
        (10, 12, "于此同行（薄荷）", 29),
        (10, 11, "勇者宝箱", 30),
        (10, 10, "学徒宝箱", 31),
        (10, 9, "学徒宝箱", 32),
        (10, 8, "迷迭棋盒（30个白色棋子）", 33),
        (9, 8, "学徒宝箱", 34),
        (9, 7, "学徒宝箱", 35),
        (9, 6, "勇者宝箱", 36),
        (9, 5, "于此同行（薄荷）", 37),
        (9, 4, "学徒宝箱", 38),
        (8, 4, "迷迭棋盒（30个白色棋子）", 39),
        (7, 4, "学徒宝箱", 40),
        (6, 4, "迷迭棋盒（50个白色棋子）", 41),
        (5, 4, "勇者宝箱", 42),
        (4, 4, "学徒宝箱", 43),
        (3, 4, "于此同行（阿德勒）", 44),
        (2, 4, "迷迭棋盒（30个白色棋子）", 45),
        (2, 5, "学徒宝箱", 46),
        (2, 6, "学徒宝箱", 47),
        (2, 7, "勇者宝箱", 48),
        (2, 8, "再来一次+沉眠池", 49),
        (2, 9, "学徒宝箱", 50),
        (2, 10, "弧光盲盒", 51),
        (2, 11, "迷迭棋盒（30个白色棋子）", 52),
        (3, 11, "学徒宝箱", 53),
        (4, 11, "勇者宝箱", 54),
    ]

    BRANCH1_LAYOUT = [
        (6, 21, "于此同行（安魂曲）", 1),
        (6, 22, "改装时刻·涂装", 2),
        (6, 23, "勇者宝箱", 3),
        (6, 24, "学徒宝箱", 4),
        (7, 24, "勇者宝箱", 5),
        (8, 21, "勇者宝箱", 9),
        (8, 22, "学徒宝箱", 8),
        (8, 23, "勇者宝箱", 7),
        (8, 24, "学徒宝箱", 6),
    ]

    BRANCH2_LAYOUT = [
        (4, 2, "勇者宝箱", 1),
        (4, 1, "今日穿搭", 2),
        (4, 0, "多重惊喜", 3),
        (3, 0, "勇者宝箱", 4),
        (2, 0, "勇者宝箱", 5),
        (2, 2, "勇者宝箱", 9),
        (1, 2, "勇者宝箱", 8),
        (1, 1, "勇者宝箱", 7),
        (1, 0, "勇者宝箱", 6),
    ]

    return {
        "main_path": MAIN_PATH_LAYOUT,
        "branch1": BRANCH1_LAYOUT,
        "branch2": BRANCH2_LAYOUT,
    }


# ============================================================
# 向后兼容接口（保持旧代码正常工作）
# ============================================================

BOARD_CONFIG = {
    "limited": {
        "name": "限定棋盘",
        "dice_type": "red",
    },
}

S_POOL_LIMITED = [{"name": "浔", "rate": 0.0187, "limited": True}]
A_POOL_LIMITED = [
    {"name": "哈尼娅", "rate": 0.0376, "gift_only": False},
    {"name": "翳", "rate": 0.0346, "gift_only": False},
    {"name": "海月", "rate": 0.0345, "gift_only": False},
    {"name": "薄荷", "rate": 0.0033, "gift_only": True},
    {"name": "埃德嘉", "rate": 0.0033, "gift_only": True},
    {"name": "阿德勒", "rate": 0.0033, "gift_only": True},
]

COMPANIONS_LIMITED = [
    {"name": "浔", "rank": "S"},
    {"name": "哈尼娅", "rank": "A"},
    {"name": "海月", "rank": "A"},
    {"name": "翳", "rank": "A"},
]

SKIN_CHARACTER = "浔"

SKIN_SYSTEM = {
    "today_outfit": {
        "name": "\u4eca\u65e5\u7a7f\u642d",
        "enter_rate": 0.0033,
        "first_get_rate": 0.0068,
        "claim_threshold": 200,
        "duplicate_reward_gold": 16,
        "color": "#FF85C0",
        "icon": "\u2661",
        "short_name": "\u7a7f\u642d",
        "skins": {SKIN_CHARACTER: f"{SKIN_CHARACTER}-\u4eca\u65e5\u7a7f\u642d"},
    },
    "vehicle_paint": {
        "name": "\u6539\u88c5\u65f6\u523b\u00b7\u6d82\u88c5",
        "enter_rate": 0.0033,
        "first_get_rate": 0.0100,
        "claim_threshold": 120,
        "duplicate_reward_gold": 16,
        "color": "#FFB347",
        "icon": "\u2724",
        "short_name": "\u6d82\u88c5",
        "skins": {SKIN_CHARACTER: f"{SKIN_CHARACTER}-\u6539\u88c5\u65f6\u523b\u00b7\u6d82\u88c5"},
    },
    "glider_skin": {
        "name": "\u98ce\u5411\u6807",
        "enter_rate": 0.0171,
        "first_get_rate": 0.0296,
        "claim_threshold": 50,
        "duplicate_reward_gold": 4,
        "color": "#87CEEB",
        "icon": "\u2708",
        "short_name": "\u6ed1\u7ff1\u7ffc",
        "skins": {SKIN_CHARACTER: f"{SKIN_CHARACTER}-\u98ce\u5411\u6807"},
    },
}

# ============================================================
# 第七层：动态奖励接口（支持多棋盘）
# ============================================================

def get_s_pool(board_id: str = "limited_xun") -> list:
    """
    获取指定棋盘的S级角色池
    
    参数:
        board_id: 棋盘ID（如 "limited_xun", "limited_requiem"）
    
    返回:
        S级角色列表，格式：[{"name": str, "rate": float, "limited": bool}]
    
    示例:
        >>> get_s_pool("limited_xun")
        [{'name': '浔', 'rate': 0.0187, 'limited': True}]
        
        >>> get_s_pool("limited_requiem")
        [{'name': '安魂曲', 'rate': 0.0187, 'limited': True}]
    """
    try:
        config = get_board_config(board_id)
        s_char_name = config.get("s_character_name")
        
        if not s_char_name:
            print(f"[警告] 棋盘 {board_id} 无S级角色，使用默认池")
            return S_POOL_LIMITED
        
        rules = config.get("rules", {})
        s_rate = rules.get("s_rate", 0.0187)
        
        return [{
            "name": s_char_name,
            "rate": s_rate,
            "limited": True,
        }]
        
    except Exception as e:
        print(f"[警告] 获取 {board_id} 的S级池失败: {e}")
        return S_POOL_LIMITED


def get_a_pool(board_id: str = "limited_xun") -> list:
    """
    获取指定棋盘的A级角色池（根据文档详情动态生成）
    
    参数:
        board_id: 棋盘ID
    
    返回:
        A级角色列表，格式：[{"name": str, "rate": float, "gift_only": bool}]
    
    数据来源：
    - 主池角色（高概率 ~3.5% each）：来自 a_pool_main_ids
    - 赠礼池角色（低概率 ~0.33% each）：来自 a_pool_gift_only_ids
    
    概率分配规则（从文档提取）：
    - 主池第1个角色：3.76%
    - 主池第2个角色：3.46%
    - 主池第3个角色：3.45%
    - 赠礼池每个角色：0.33%
    """
    try:
        config = get_board_config(board_id)
        
        main_names = config.get("a_pool_main_names", [])
        gift_only_names = config.get("a_pool_gift_only_names", [])
        
        # 标准概率分布（从文档提取）
        main_rates = [0.0376, 0.0346, 0.0345]  # 主池3个角色的概率
        gift_rate = 0.0033                      # 赠礼池每个角色的概率
        
        pool = []
        
        # 添加主池角色（按顺序分配概率）
        for i, name in enumerate(main_names):
            rate = main_rates[i] if i < len(main_rates) else 0.03
            pool.append({
                "name": name,
                "rate": rate,
                "gift_only": False,
            })
        
        # 添加赠礼池角色
        for name in gift_only_names:
            pool.append({
                "name": name,
                "rate": gift_rate,
                "gift_only": True,
            })
        
        if not pool:
            print(f"[警告] 棋盘 {board_id} 无A级角色池，使用默认池")
            return A_POOL_LIMITED
        
        return pool
        
    except Exception as e:
        print(f"[警告] 获取 {board_id} 的A级池失败: {e}")
        return A_POOL_LIMITED


def get_skin_character(board_id: str = "limited_xun") -> str:
    """
    获取指定棋盘的皮肤绑定角色名
    
    参数:
        board_id: 棋盘ID
    
    返回:
        皮肤绑定的S级角色名称（如 "浔", "安魂曲"）
    
    说明：
    - 所有限定棋盘的皮肤系统都绑定到该棋盘的S级角色
    - 例如：浔棋盘的皮肤都是"浔"的时装/涂装/滑翔翼
    """
    try:
        config = get_board_config(board_id)
        s_char_name = config.get("s_character_name")
        
        if s_char_name:
            return s_char_name
        
        print(f"[警告] 棋盘 {board_id} 无S级角色，使用默认皮肤角色")
        return SKIN_CHARACTER
        
    except Exception as e:
        print(f"[警告] 获取 {board_id} 的皮肤角色失败: {e}")
        return SKIN_CHARACTER


def get_skin_system(board_id: str = "limited_xun") -> dict:
    """
    获取指定棋盘的皮肤系统配置
    
    参数:
        board_id: 棋盘ID
    
    返回:
        皮肤系统字典，格式与SKIN_SYSTEM相同，但skins中的角色名已更新为当前棋盘的S级角色
    
    说明：
    - 复制全局SKIN_SYSTEM模板
    - 更新所有皮肤条目的角色绑定为目标棋盘的S级角色
    """
    skin_char = get_skin_character(board_id)
    
    dynamic_skins = {}
    
    for skin_key, skin_cfg in SKIN_SYSTEM.items():
        new_cfg = skin_cfg.copy()
        new_cfg["skins"] = {
            skin_char: f"{skin_char}-{skin_cfg['short_name']}"
        }
        dynamic_skins[skin_key] = new_cfg
    
    return dynamic_skins


def get_companions_list(board_id: str = "limited_xun") -> list:
    """
    获取指定棋盘的同行角色列表
    
    参数:
        board_id: 棋盘ID
    
    返回:
        同行角色列表，格式：[{"name": str, "rank": str}]
    
    排序规则：
    - S级角色排第一
    - 其余A级角色按 companions_id_map 中的顺序排列
    """
    try:
        config = get_board_config(board_id)
        s_char_name = config.get("s_character_name")
        companions = config.get("companions", {})
        
        result = []
        
        # 添加S级角色
        if s_char_name:
            result.append({"name": s_char_name, "rank": "S"})
        
        # 添加A级同行角色（去重并保持顺序）
        seen_a_chars = set()
        for cell_idx, char_name in companions.items():
            if char_name != s_char_name and char_name not in seen_a_chars:
                result.append({"name": char_name, "rank": "A"})
                seen_a_chars.add(char_name)
        
        if not result:
            return COMPANIONS_LIMITED
        
        return result
        
    except Exception as e:
        print(f"[警告] 获取 {board_id} 的同行角色失败: {e}")
        return COMPANIONS_LIMITED


def get_board_rules(board_id: str = "limited_xun") -> dict:
    """
    获取指定棋盘的完整规则配置（支持每个棋盘独立配置）
    
    参数:
        board_id: 棋盘ID（如 "limited_xun", "limited_requiem", "limited_caerus"）
    
    返回:
        完整的规则字典，包含所有概率参数、保底机制、补偿规则等
    
    核心特性：
    1. 默认值回退：如果棋盘未自定义某项规则，自动使用全局默认值
    2. 深度合并：支持部分覆盖（只修改需要改变的参数）
    3. 类型安全：所有数值都有合理范围检查
    4. 完整性保证：确保返回的字典包含所有必需字段
    
    使用示例：
        >>> rules = get_board_rules("limited_xun")
        >>> s_rate = rules["s_rate"]                    # S级综合概率
        >>> pity_hard = rules["s_pity_hard"]            # 硬保底阈值
        >>> duplicate = rules["duplicate_rules"]["s_character"]  # 重复补偿
        
        >>> # 卡厄斯棋盘可能有不同的概率
        >>> rules_caerus = get_board_rules("limited_caerus")
        >>> s_rate_caerus = rules_caerus["s_rate"]      # 可能是 0.025 而不是 0.0187
    
    架构说明：
    - 全局默认值来源：LIMITED_BOARD_TEMPLATE["rules"]
    - 棋盘自定义值来源：BOARDS_REGISTRY[board_id]["rules"]
    - 合并策略：棋盘自定义 > 全局默认（深度字典合并）
    """
    try:
        config = get_board_config(board_id)
        
        # 获取棋盘的自定义规则（可能为空或None）
        custom_rules = config.get("rules", {}) or {}
        
        # 获取全局默认规则模板
        default_rules = LIMITED_BOARD_TEMPLATE.get("rules", {})
        
        if not default_rules:
            print(f"[错误] 未找到默认规则模板 LIMITED_BOARD_TEMPLATE['rules']")
            return _create_fallback_rules()
        
        # 深度合并：自定义规则覆盖默认规则
        merged_rules = _deep_merge_rules(default_rules, custom_rules)
        
        # 验证关键字段存在
        required_keys = [
            "s_rate", "s_base_rate_normal", "s_base_rate_variant",
            "s_pity_variant_threshold", "s_pity_hard",
            "duplicate_rules"
        ]
        
        for key in required_keys:
            if key not in merged_rules:
                print(f"[警告] 规则缺少必需字段: {key}, 使用默认值")
        
        return merged_rules
        
    except Exception as e:
        print(f"[警告] 获取 {board_id} 的规则失败: {e}")
        return _create_fallback_rules()


def _deep_merge_rules(default_dict: dict, custom_dict: dict) -> dict:
    """
    深度合并两个规则字典（支持嵌套结构）
    
    参数:
        default_dict: 默认规则字典（基础层）
        custom_dict: 自定义规则字典（覆盖层）
    
    返回:
        合并后的新字典（不修改原字典）
    
    合并策略：
    - 如果custom_dict中有某个key，则使用custom_dict的值
    - 如果值是字典，则递归合并
    - 如果值是列表或其他类型，直接替换
    """
    result = default_dict.copy()
    
    for key, custom_value in custom_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(custom_value, dict):
            # 递归合并嵌套字典
            result[key] = _deep_merge_rules(result[key], custom_value)
        else:
            # 直接覆盖（列表、数字、字符串等）
            result[key] = custom_value
    
    return result


def _create_fallback_rules() -> dict:
    """
    创建应急回退规则（当无法从配置读取时使用）
    
    返回:
        最小可用规则集，确保程序不会崩溃
    """
    return {
        "s_rate": 0.0187,
        "s_base_rate_normal": 0.0099,
        "s_base_rate_variant": 0.1959,
        "s_pity_variant_threshold": 70,
        "s_pity_hard": 90,
        "a_rate_total": 0.2298,
        "gift_interval": 10,
        "duplicate_rules": {
            "s_character": {"range_2_7": {"fragment": 1, "gold_chip": 40},
                           "range_8_plus": {"gold_chip": 80}},
            "a_character": {"range_2_7": {"fragment": 1, "gold_chip": 6},
                           "range_8_plus": {"gold_chip": 12}},
        },
    }


SKIN_TYPE_KEYS = list(SKIN_SYSTEM.keys())

CELL_TYPES = {
    "apprentice_chest": {
        "name": "\u5b66\u5f92\u5b9d\u7bb1",
        "enter_rate": 0.4593,
        "color": "#E8A838",
        "rewards": [
            {"type": "s_character", "name": None, "rate": 0.002},
            {"type": "b_disk", "name": None, "rate": 0.998},
        ],
    },
    "brave_chest": {
        "name": "\u52c7\u8005\u5b9d\u7bb1",
        "enter_rate": 0.2007,
        "color": "#F5C542",
        "extra_gold": 2,
        "rewards": [
            {"type": "s_character", "name": None, "rate": 0.03},
            {"type": "b_disk", "name": None, "rate": 0.97},
        ],
    },
    "companion": {
        "name": "\u4e8e\u6b64\u540c\u884c",
        "enter_rate": 0.1086,
        "sub_rates": {
            "s_character": 0.0119,
            "a_character": 0.0967,
        },
        "color_s": "#C850C0",
        "color_a": "#C850C0",
        "guaranteed": True,
    },
    "mist_box": {
        "name": "\u8ff7\u8fed\u68cb\u76d2",
        "enter_rate": 0.1547,
        "color": "#E8E8F0",
        "white_chip_range": (10, 50),
    },
    "arcade_blind": {
        "name": "\u5f27\u5149\u76f2\u76d2",
        "enter_rate": 0.0331,
        "color": "#5090D0",
        "reward_type": "random_a_disk",
    },
    "sleep_pool": {
        "name": "\u6c89\u7720\u6c60",
        "enter_rate": 0.0315,
        "color": "#3D2B55",
        "trigger_chase": True,
    },
    "roll_again": {
        "name": "\u518d\u6765\u4e00\u6b21",
        "enter_rate": 0.0157,
        "color": "#45B060",
        "dice_reward": 1,
    },
    "multi_surprise": {
        "name": "\u591a\u91cd\u60ca\u559c",
        "enter_rate": 0.0038,
        "color": "#FF5090",
        "dice_reward": 5,
    },
    "today_outfit": {
        "name": "\u4eca\u65e5\u7a7f\u642d",
        "enter_rate": 0.0033,
        "skin_type": "today_outfit",
        "color": SKIN_SYSTEM["today_outfit"]["color"],
    },
    "vehicle_paint": {
        "name": "\u6539\u88c5\u65f6\u523b\u00b7\u6d82\u88c5",
        "enter_rate": 0.0033,
        "skin_type": "vehicle_paint",
        "color": SKIN_SYSTEM["vehicle_paint"]["color"],
    },
    "glider_skin": {
        "name": "\u98ce\u5411\u6807",
        "enter_rate": 0.0171,
        "skin_type": "glider_skin",
        "color": SKIN_SYSTEM["glider_skin"]["color"],
    },
}

_total_rate = sum(c["enter_rate"] for c in CELL_TYPES.values())
CELL_RATE_BOUNDS = []
_cumulative = 0.0
for cell_key, cell_info in CELL_TYPES.items():
    _start = _cumulative
    _normalized_rate = cell_info["enter_rate"] / _total_rate
    _end = _cumulative + _normalized_rate
    CELL_RATE_BOUNDS.append((cell_key, _start, _end))
    _cumulative = _end

PITY_CONFIG = {
    "s_pity": {
        "variant_threshold": 70,
        "hard_pity": 90,
        "base_rate_normal": 0.0099,
        "base_rate_variant": 0.1959,
    },
    "gift_pity": {
        "interval": 10,
        "a_character_rate": 0.20,
        "a_disk_rate": 0.80,
    },
}

DUPLICATE_RULES = {
    "s_character": {
        "range_2_7": {"fragment": 1, "gold_chip": 40},
        "range_8_plus": {"gold_chip": 80},
    },
    "a_character": {
        "range_2_7": {"fragment": 1, "gold_chip": 6},
        "range_8_plus": {"gold_chip": 12},
    },
    "a_disk": {
        "extra_gold_chip": 4,
    },
    "b_disk": {
        "extra_white_chip": 20,
    },
    "skin_today_outfit": {
        "gold_chip": 16,
    },
    "skin_vehicle_paint": {
        "gold_chip": 16,
    },
    "skin_glider_skin": {
        "gold_chip": 4,
    },
}

SLEEP_POOL_CONFIG = {
    "guardian_flee_distance": 9,
    "max_chase_rounds": 3,
    "guardian_speed": 2,
    "success_reward_gold": 30,
}

MIST_BOX_WHITE_CHIPS = [15, 20, 25, 30, 35, 40, 45, 50]

A_DISK_POOL = LIMITED_BOARD_TEMPLATE["a_disk_pool"]
B_DISK_POOL = LIMITED_BOARD_TEMPLATE["b_disk_pool"]

# ============================================================
# [新增] Phase 4: 氪金系统配置（预留）
# ============================================================

RECHARGE_PACKS = {
    """
    充值套餐配置 - 人民币购买环石
    
    数据结构说明：
    - key: 套餐ID（如 "pack_6", "pack_30"）
    - value: dict {
        "rmb_price": 人民币价格（元）,
        "ring_stones": 获得的环石数量,
        "bonus_stones": 额外赠送环石数量（0表示无赠送）,
        "total_stones": 实际获得总数 = ring_stones + bonus_stones,
        "name": 套餐显示名称,
        "description": 套餐描述（用于UI提示）,
        "is_recommended": 是否推荐（True时在UI中高亮）,
        "first_time_bonus": 首充额外奖励（可选）,
    }
    
    使用示例：
        >>> pack = RECHARGE_PACKS["pack_6"]
        >>> print(f"{pack['name']}: {pack['rmb_price']}元 -> {pack['total_stones']}环石")
    
    注意：
    - 价格和数量需要根据官方实际数据填写
    - 当前为示例数据，待官方公布后更新
    - bonus_stones 用于促销活动或首充奖励
    """
    
    # ===== 基础套餐 =====
    "pack_1": {
        "rmb_price": 1.0,
        "ring_stones": 10,
        "bonus_stones": 0,
        "total_stones": 10,
        "name": "新手礼包",
        "description": "适合初次体验",
        "is_recommended": False,
        "first_time_bonus": 5,  # 首充额外送5环石
    },
    
    "pack_6": {
        "rmb_price": 6.0,
        "ring_stones": 60,
        "bonus_stones": 0,
        "total_stones": 60,
        "name": "标准充值",
        "description": "性价比较高的选择",
        "is_recommended": True,  # 推荐套餐
        "first_time_bonus": 10,  # 首充额外送10环石
    },
    
    "pack_30": {
        "rmb_price": 30.0,
        "ring_stones": 300,
        "bonus_stones": 30,  # 送30环石
        "total_stones": 330,
        "name": "超值礼包",
        "description": "额外赠送10%环石",
        "is_recommended": True,
        "first_time_bonus": 50,  # 首充额外送50环石
    },
    
    "pack_68": {
        "rmb_price": 68.0,
        "ring_stones": 680,
        "bonus_stones": 100,  # 送100环石
        "total_stones": 780,
        "name": "豪华礼包",
        "description": "额外赠送约15%环石",
        "is_recommended": False,
        "first_time_bonus": 120,
    },
    
    "pack_128": {
        "rmb_price": 128.0,
        "ring_stones": 1280,
        "bonus_stones": 220,  # 送220环石
        "total_stones": 1500,
        "name": "至尊礼包",
        "description": "额外赠送约17%环石，最划算！",
        "is_recommended": True,
        "first_time_bonus": 280,
    },
    
    "pack_328": {
        "rmb_price": 328.0,
        "ring_stones": 3280,
        "bonus_stones": 650,  # 送650环石
        "total_stones": 3930,
        "name": "钻石礼包",
        "description": "额外赠送约20%环石，土豪专属",
        "is_recommended": False,
        "first_time_bonus": 700,
    },
    
    "pack_648": {
        "rmb_price": 648.0,
        "ring_stones": 6480,
        "bonus_stones": 1500,  # 送1500环石
        "total_stones": 7980,
        "name": "传说礼包",
        "description": "额外赠送约23%环石，最强性价比！",
        "is_recommended": True,
        "first_time_bonus": 1600,
    },
}

# 充值汇率配置
RECHARGE_EXCHANGE_RATE = {
    """
    环石兑换率配置
    
    说明：
    - base_rate: 基础汇率（1元人民币 = 多少环石）
    - 这个汇率用于估算需要充值多少钱
    
    注意：
    - 实际兑换率因套餐不同而不同（有赠送）
    - 此配置仅用于快速估算
    - 推荐使用 RECHARGE_PACKS 进行精确计算
    """
    "base_rate": 10.0,  # 基础汇率：1元 ≈ 10环石（不含赠送）
    "average_rate_with_bonus": 12.5,  # 平均汇率（含赠送）：1元 ≈ 12.5环石
}

# 单抽价格配置
DICE_PRICE_CONFIG = {
    """
    抽取价格配置
    
    说明：
    - single_roll_price: 单抽消耗的环石数
    - ten_roll_price: 10连抽总消耗（通常= single_roll_price * 10）
    - dice_equivalent: 1个骰子等价于多少环石
    """
    "single_roll_ring_stones": 160,      # 单抽：160环石
    "ten_roll_ring_stones": 1600,         # 10连：1600环石
    "dice_to_ring_stone_ratio": 160,     # 1骰子 = 160环石
}


def get_recharge_pack(pack_id):
    """
    获取指定充值套餐信息
    
    参数:
        pack_id: 套餐ID（如 "pack_6", "pack_30"）
    
    返回:
        套餐字典，如果不存在则返回None
    
    使用示例：
        >>> pack = get_recharge_pack("pack_6")
        >>> if pack:
        ...     print(f"{pack['name']}: {pack['rmb_price']}元")
    """
    return RECHARGE_PACKS.get(pack_id)


def get_all_recharge_packs():
    """
    获取所有可用充值套餐列表（按价格排序）
    
    返回:
        list: 套餐字典列表，按价格从低到高排序
    
    使用示例：
        >>> packs = get_all_recharge_packs()
        >>> for pack in packs:
        ...     if pack["is_recommended"]:
        ...         print(f"[推荐] {pack['name']}")
    """
    return sorted(
        RECHARGE_PACKS.values(),
        key=lambda x: x["rmb_price"]
    )


def get_recommended_packs():
    """
    获取推荐的充值套餐
    
    返回:
        list: 推荐套餐列表
    """
    return [
        pack for pack in RECHARGE_PACKS.values()
        if pack.get("is_recommended", False)
    ]


def calculate_best_value_pack(needed_ring_stones):
    """
    根据需要的环石数量，计算最优充值方案（贪心算法）
    
    参数:
        needed_ring_stones: 需要的环石数量
    
    返回:
        dict: {
            "total_rmb": 总花费（元）,
            "total_ring_stones": 总共获得的环石,
            "excess_ring_stones": 多余的环石,
            "packs_used": [(套餐名, 数量), ...],  # 使用的套餐组合
            "savings": 相比单买1元包节省的金额,
        }
    
    使用示例：
        >>> result = calculate_best_value_pack(500)
        >>> print(f"最优方案: {result['total_rmb']}元")
        >>> for pack_name, count in result["packs_used"]:
        ...     print(f"  {count}个 {pack_name}")
    """
    if needed_ring_stones <= 0:
        return {
            "total_rmb": 0,
            "total_ring_stones": 0,
            "excess_ring_stones": 0,
            "packs_used": [],
            "savings": 0,
        }
    
    # 按性价比排序（从高到低）
    sorted_packs = sorted(
        RECHARGE_PACKS.values(),
        key=lambda x: x["total_stones"] / x["rmb_price"],
        reverse=True
    )
    
    total_rmb = 0.0
    total_stones = 0
    packs_used = []
    
    remaining = needed_ring_stones
    
    for pack in sorted_packs:
        if remaining <= 0:
            break
        
        # 计算需要多少个这个套餐
        count = remaining // pack["total_stones"]
        
        if count > 0:
            total_rmb += count * pack["rmb_price"]
            total_stones += count * pack["total_stones"]
            packs_used.append((pack["name"], count))
            remaining -= count * pack["total_stones"]
    
    # 如果还有剩余，补充最小套餐
    if remaining > 0:
        min_pack = min(RECHARGE_PACKS.values(), key=lambda x: x["rmb_price"])
        total_rmb += min_pack["rmb_price"]
        total_stones += min_pack["total_stones"]
        packs_used.append((min_pack["name"], 1))
        remaining = 0
    
    # 计算相比单买的节省金额
    base_cost_per_stone = 1.0 / RECHARGE_EXCHANGE_RATE["base_rate"]  # 单买每环石成本
    actual_cost_per_stone = total_rmb / total_stones if total_stones > 0 else 0
    savings = (base_cost_per_stone - actual_cost_per_stone) * total_stones
    
    return {
        "total_rmb": round(total_rmb, 2),
        "total_ring_stones": total_stones,
        "excess_ring_stones": total_stones - needed_ring_stones,
        "packs_used": packs_used,
        "savings": round(savings, 2),
    }


if __name__ == "__main__":
    """
    测试代码：运行此模块时执行数据校验
    """
    import sys
    
    print("\n" + "=" * 70)
    print("棋盘数据模块 V2.0 自检")
    print("=" * 70 + "\n")
    
    # 执行启动校验
    all_ok = run_startup_validation()
    
    # 测试访问接口
    print("\n[测试] 访问接口功能:")
    print("-" * 50)
    
    boards = get_available_boards()
    print(f"可用棋盘数量: {len(boards)}")
    for bid in boards:
        config = get_board_config(bid)
        print(f"\n  棋盘: {config['display_name']}")
        print(f"  类型: {config['board_type']}")
        print(f"  S级角色: {config['s_character_name']}")
        print(f"  同行角色: {list(config['companions'].values())}")
        print(f"  A级主池: {config['a_pool_main_names']}")
        print(f"  A级赠礼池: {config['a_pool_gift_only_names']}")
    
    sys.exit(0 if all_ok else 1)
