# -*- coding: utf-8 -*-

"""
棋盘数据配置模块
包含角色池、概率表、格子类型、保底参数、皮肤系统等所有静态配置
支持多棋盘扩展（当前仅实现限定棋盘）
"""

# ============================================================
# 棋盘总配置（多棋盘预留）
# ============================================================
BOARD_CONFIG = {
    "limited": {
        "name": "限定棋盘",
        "dice_type": "red",
    },
}

# ============================================================
# 限定棋盘 - S级角色池
# ============================================================
S_POOL_LIMITED = [
    {"name": "浔", "rate": 0.0187, "limited": True},
]

# ============================================================
# 限定棋盘 - A级角色池
# ============================================================
A_POOL_LIMITED = [
    {"name": "哈尼娅", "rate": 0.0376, "gift_only": False},
    {"name": "翳", "rate": 0.0346, "gift_only": False},
    {"name": "海月", "rate": 0.0345, "gift_only": False},
    {"name": "薄荷", "rate": 0.0033, "gift_only": True},
    {"name": "埃德嘉", "rate": 0.0033, "gift_only": True},
    {"name": "阿德勒", "rate": 0.0033, "gift_only": True},
]

# ============================================================
# 弧盘池
# ============================================================
A_DISK_POOL = [
    "被遗忘者",
    "开始净空",
    "当心头顶",
    "勿忘伞",
    "拔刀",
]

B_DISK_POOL = [
    "成功的第一步",
    "电音狂欢",
    "危险游戏",
    "笑口常开",
    "我们",
]

# ============================================================
# 于此同行 - 可用角色列表（限定棋盘）
# ============================================================
COMPANIONS_LIMITED = [
    {"name": "浔", "rank": "S"},
    {"name": "哈尼娅", "rank": "A"},
    {"name": "海月", "rank": "A"},
    {"name": "翳", "rank": "A"},
]

# ============================================================
# 装扮礼遇 - 皮肤系统
# 只有S级角色拥有专属皮肤
# ============================================================
SKIN_CHARACTER = "浔"  # S级角色

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

# 所有皮肤类型的key列表
SKIN_TYPE_KEYS = list(SKIN_SYSTEM.keys())

# ============================================================
# 格子类型及概率分布（含装扮礼遇格子）
# ============================================================
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

# 格子类型概率累积区间（用于快速判定落格类型）
# 归一化处理：确保总概率恰好为1.0
_total_rate = sum(c["enter_rate"] for c in CELL_TYPES.values())
CELL_RATE_BOUNDS = []
_cumulative = 0.0
for cell_key, cell_info in CELL_TYPES.items():
    _start = _cumulative
    _normalized_rate = cell_info["enter_rate"] / _total_rate
    _end = _cumulative + _normalized_rate
    CELL_RATE_BOUNDS.append((cell_key, _start, _end))
    _cumulative = _end

# ============================================================
# 保底参数配置
# ============================================================
PITY_CONFIG = {
    # S级角色保底
    "s_pity": {
        "variant_threshold": 70,
        "hard_pity": 90,
        "base_rate_normal": 0.0099,
        "base_rate_variant": 0.1959,
    },
    # 集点赠礼
    "gift_pity": {
        "interval": 10,
        "a_character_rate": 0.20,
        "a_disk_rate": 0.80,
    },
}

# ============================================================
# 重复获得补偿规则
# ============================================================
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

# ============================================================
# 沉眠池追击参数
# ============================================================
SLEEP_POOL_CONFIG = {
    "guardian_flee_distance": 9,
    "max_chase_rounds": 3,
    "guardian_speed": 2,
    "success_reward_gold": 30,
}

# ============================================================
# 迷迭棋盒白色棋子范围
# ============================================================
MIST_BOX_WHITE_CHIPS = [15, 20, 25, 30, 35, 40, 45, 50]
