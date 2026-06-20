# -*- coding: utf-8 -*-

"""
限定棋盘（浔）完整配置 V1.0
==========================

棋盘ID: limited_xun
显示名称: 限定棋盘（浔）
棋盘类型: 限定棋盘（limited）
S级角色: 浔

配置内容：
- S级/A级角色池
- 同行角色映射
- 皮肤系统
- 变格变换规则
- 坐标布局数据

版本历史：
- V1.0: 从board_data.py提取（V0.4.2重构）
"""

from typing import Dict, List, Tuple, Any, Optional
from boards.base_board import BaseBoard


class LimitedXunBoard(BaseBoard):
    """限定棋盘（浔）"""

    # ============================================================
    # 必须实现的属性
    # ============================================================

    @property
    def board_id(self) -> str:
        return "limited_xun"

    @property
    def display_name(self) -> str:
        return "限定棋盘（浔）"

    @property
    def board_type(self) -> str:
        return "limited"

    # ============================================================
    # 角色池配置
    # ============================================================

    def get_s_pool(self) -> list:
        """
        S级角色池 - 浔（单角色限定）

        概率说明：
        - 综合概率：1.87%（来自规则模板s_rate）
        - 变格后概率：19.59%（来自规则模板s_base_rate_variant）
        - 硬保底：90次必得S级
        """
        return [{"name": "浔", "rate": 0.0187, "limited": True}]

    def get_a_pool(self) -> list:
        """
        A级角色池

        主池（高概率 ~3.5% each）:
        - 哈尼娅: 3.76%
        - 翳: 3.46%
        - 海月: 3.45%

        赠礼池（低概率 ~0.33% each）:
        - 薄荷: 0.33%（仅赠礼）
        - 埃德嘉: 0.33%（仅赠礼）
        - 阿德勒: 0.33%（仅赠礼）
        """
        return [
            {"name": "哈尼娅", "rate": 0.0376, "gift_only": False},
            {"name": "翳", "rate": 0.0346, "gift_only": False},
            {"name": "海月", "rate": 0.0345, "gift_only": False},
            {"name": "薄荷", "rate": 0.0033, "gift_only": True},
            {"name": "埃德嘉", "rate": 0.0033, "gift_only": True},
            {"name": "阿德勒", "rate": 0.0033, "gift_only": True},
        ]

    # ============================================================
    # 同行角色映射
    # ============================================================

    def get_companions(self) -> Dict[Any, str]:
        """
        同行角色映射

        主路径（4个格子）:
        - 第1格 → 海月（A级）
        - 第10格 → 翳（A级）
        - 第29格 → 哈尼娅（A级）
        - 第37格 → 哈尼娅（A级）

        分支1（1个格子）:
        - B1-0 → 浔（S级）
        """
        return {
            1: "海月",
            10: "翳",
            29: "哈尼娅",
            37: "哈尼娅",
            "B1-0": "浔",
        }

    # ============================================================
    # 皮肤系统配置
    # ============================================================

    def get_skin_character(self) -> Optional[str]:
        """皮肤专属角色名"""
        return "浔"

    def get_skin_system(self) -> Dict[str, Any]:
        """
        皮肤系统配置（浔专属）

        三种皮肤类型：
        1. 今日穿搭（粉色）- 200次领取，重复+16金
        2. 改装时刻·涂装（橙色）- 120次领取，重复+16金
        3. 风向标（蓝色）- 50次领取，重复+4金
        """
        skin_char = self.get_skin_character()

        return {
            "today_outfit": {
                "name": "今日穿搭",
                "enter_rate": 0.0033,
                "first_get_rate": 0.0068,
                "claim_threshold": 200,
                "duplicate_reward_gold": 16,
                "color": "#FF85C0",
                "icon": "\u2661",  # ♥
                "short_name": "穿搭",
                "skins": {skin_char: f"{skin_char}-今日穿搭"},
            },
            "vehicle_paint": {
                "name": "改装时刻·涂装",
                "enter_rate": 0.0033,
                "first_get_rate": 0.0100,
                "claim_threshold": 120,
                "duplicate_reward_gold": 16,
                "color": "#FFB347",
                "icon": "\u2724",  # ✦
                "short_name": "涂装",
                "skins": {skin_char: f"{skin_char}-改装时刻·涂装"},
            },
            "glider_skin": {
                "name": "风向标",
                "enter_rate": 0.0171,
                "first_get_rate": 0.0296,
                "claim_threshold": 50,
                "duplicate_reward_gold": 4,
                "color": "#87CEEB",
                "icon": "\u2708",  # ✈
                "short_name": "滑翔翼",
                "skins": {skin_char: f"{skin_char}-风向标"},
            },
        }

    # ============================================================
    # 变格变换配置（V0.4.2新增）
    # ============================================================

    def get_variant_transforms(self) -> Dict[int, Dict[str, str]]:
        """
        变格变换配置（V0.4.3全面修复）

        [修复内容] 基于CSV全面对比，删除16个错误变格配置
        - 之前: 37个配置（23学徒+14勇者）
        - 现在: 17个配置（5学徒+12勇者）
        [V0.4.4修复] 移除35号错误变格（CSV确认为普通学徒宝箱）

        变格规则：
        1. 学徒宝箱变（5个）→ 勇者宝箱(50%概率S级)
           格子: 2, 14, 26, 38, 50
           注：35号不是变格（CSV确认为普通学徒宝箱）
        2. 勇者宝箱变（12个）→ 必定获得S级角色(100%)
           主路径: 6, 12, 18, 24, 30, 36, 42, 48, 54 (9个)
           分支B1: B1-2, B1-4, B1-6, B1-8 (4个)
           注：CSV显示"勇者宝箱变——分支1"待进一步验证

        数据来源：限定棋盘浔地图手动统计.csv / board_data.py VARIANT_TRANSFORMS
        """
        return {
            # ===== 学徒宝箱变（5个）=====
            # [V0.4.3全面修复] [V0.4.4修复] 只保留CSV中明确带"变"字的格子
            # 数据来源：限定棋盘浔地图手动统计.csv
            # 注意：35号不是变格（CSV确认为普通学徒宝箱）
            2:   {"normal": "apprentice_chest", "variant": "brave_chest", "variant_name": "学徒宝箱变"},
            14:  {"normal": "apprentice_chest", "variant": "brave_chest", "variant_name": "学徒宝箱变"},
            26:  {"normal": "apprentice_chest", "variant": "brave_chest", "variant_name": "学徒宝箱变"},
            38:  {"normal": "apprentice_chest", "variant": "brave_chest", "variant_name": "学徒宝箱变"},
            50:  {"normal": "apprentice_chest", "variant": "brave_chest", "variant_name": "学徒宝箱变"},

            # ===== 勇者宝箱变（12个）→ 必定获得S级角色(100%) =====
            # 主路径9个（CSV确认）
            6:   {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            12:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            18:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            24:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            30:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            36:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            42:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            48:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            54:  {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},
            # 分支4个（CSV确认：分支3/5/7/9为勇者宝箱变）
            "B1-2": {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},  # CSV: 分支3=勇者宝箱变
            "B1-4": {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},  # CSV: 分支5=勇者宝箱变
            "B1-6": {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},  # CSV: 分支7=勇者宝箱变
            "B1-8": {"normal": "brave_chest", "variant": "companion_s", "variant_name": "勇者宝箱变"},  # CSV: 分支9=勇者宝箱变
        }

    # ============================================================
    # 坐标布局数据（73格）
    # ============================================================

    def generate_layout(self) -> Tuple[List[Tuple[int, int]], List[str], List[str], Dict]:
        """
        生成浔棋盘布局坐标

        [V0.4.2修复] 坐标数据与 board_data.py 的 get_limited_board_layout() 完全一致
        数据来源：限定棋盘浔地图手动统计.csv
        布局结构：蛇形路径 + 2个分支（B1、B2）

        返回:
            (cell_positions, cell_types, cell_names, branch_entries)
        """
        # [V0.4.2核心修复] 使用与board_data.py一致的坐标系统
        # 主路径：55格（索引0-54），起点在(5,10)，顺时针蛇形
        cell_positions = [
            # ===== 主路径（55格）：0-54 =====
            # 第1段：向右（0-4）
            (5, 10),   # 0 起点
            (5, 11),   # 1 于此同行（海月）
            (5, 12),   # 2 学徒宝箱
            (5, 13),   # 3 风向标
            (5, 14),   # 4 学徒宝箱
            # 向上（5-8）
            (4, 14),   # 5 学徒宝箱
            (3, 14),   # 6 勇者宝箱
            (2, 14),   # 7 学徒宝箱
            (2, 15),   # 8 学徒宝箱
            (2, 16),   # 9 迷迭棋盒（30个白色棋子）
            # 向右（10-15）
            (2, 17),   # 10 于此同行（翳）
            (3, 17),   # 11 学徒宝箱
            (4, 17),   # 12 勇者宝箱
            (5, 17),   # 13 学徒宝箱
            (5, 18),   # 14 学徒宝箱
            (5, 19),   # 15 迷迭棋盒（50个白色棋子）
            # 向下（16-21）
            (6, 19),   # 16 学徒宝箱 [分支1入口]
            (7, 19),   # 17 于此同行（翳）[跳过]
            (8, 19),   # 18 勇者宝箱 [到达]
            (9, 19),   # 19 学徒宝箱
            (10, 19),  # 20 学徒宝箱
            (11, 19),  # 21 迷迭棋盒（30个白色棋子）
            # 向左（22-27）
            (11, 18),  # 22 弧光盲盒+沉眠池
            (11, 17),  # 23 学徒宝箱
            (11, 16),  # 24 勇者宝箱变
            (11, 15),  # 25 学徒宝箱
            (11, 14),  # 26 学徒宝箱变
            (10, 14),  # 27 迷迭棋盒（50个白色棋子）
            # 向左上（28-33）
            (10, 13),  # 28 学徒宝箱
            (10, 12),  # 29 于此同行（哈尼娅）
            (10, 11),  # 30 勇者宝箱变
            (10, 10),  # 31 学徒宝箱
            (10, 9),   # 32 学徒宝箱
            (10, 8),   # 33 迷迭棋盒（30个白色棋子）
            # 向左下（34-39）
            (9, 8),    # 34 学徒宝箱
            (9, 7),    # 35 学徒宝箱（非变格）
            (9, 6),    # 36 勇者宝箱变
            (9, 5),    # 37 于此同行（哈尼娅）
            (9, 4),    # 38 学徒宝箱
            (8, 4),    # 39 迷迭棋盒（30个白色棋子）
            # 向左下（40-45）
            (7, 4),    # 40 学徒宝箱
            (6, 4),    # 41 迷迭棋盒（50个白色棋子）
            (5, 4),    # 42 勇者宝箱变 [分支2入口]
            (4, 4),    # 43 学徒宝箱
            (3, 4),    # 44 于此同行（海月）[跳过]
            (2, 4),    # 45 迷迭棋盒（30个白色棋子）[结束/到达]
            # 向右（46-54）
            (2, 5),    # 46 学徒宝箱
            (2, 6),    # 47 学徒宝箱
            (2, 7),    # 48 勇者宝箱变
            (2, 8),    # 49 再来一次+沉眠池
            (2, 9),    # 50 学徒宝箱变
            (2, 10),   # 51 弧光盲盒
            (2, 11),   # 52 迷迭棋盒（30个白色棋子）
            (3, 11),   # 53 学徒宝箱
            (4, 11),   # 54 勇者宝箱变 [终点]

            # ===== 分支1（9格）：B1-0 ~ B1-8（索引55-63）=====
            # S级角色区：从(6,21)入口向右→下→左
            (6, 21),   # B1-0 于此同行（浔）[S级角色] 入口
            (6, 22),   # B1-1 改装时刻·涂装
            (6, 23),   # B1-2 勇者宝箱
            (6, 24),   # B1-3 学徒宝箱
            (7, 24),   # B1-4 勇者宝箱
            (8, 24),   # B1-5 学徒宝箱
            (8, 23),   # B1-6 勇者宝箱
            (8, 22),   # B1-7 学徒宝箱
            (8, 21),   # B1-8 勇者宝箱 出口

            # ===== 分支2（9格）：B2-0 ~ B2-8（索引64-72）=====
            # 皮肤惊喜区：从(4,2)入口向左→上→右→下
            (4, 2),    # B2-0 勇者宝箱 入口
            (4, 1),    # B2-1 今日穿搭
            (4, 0),    # B2-2 多重惊喜
            (3, 0),    # B2-3 勇者宝箱
            (2, 0),    # B2-4 勇者宝箱
            (1, 0),    # B2-5 勇者宝箱
            (1, 1),    # B2-6 勇者宝箱
            (1, 2),    # B2-7 勇者宝箱
            (2, 2),    # B2-8 勇者宝箱 出口
        ]

        # 格子类型（与坐标一一对应）
        cell_types = [
            # ===== 主路径（55格）：0-54 =====
            "start",                    # 0 起点
            "companion",                # 1 于此同行（海月）
            "apprentice_chest",         # 2 学徒宝箱
            "glider_skin",              # 3 风向标
            "apprentice_chest",         # 4 学徒宝箱
            "apprentice_chest",         # 5 学徒宝箱
            "brave_chest",              # 6 勇者宝箱
            "apprentice_chest",         # 7 学徒宝箱
            "apprentice_chest",         # 8 学徒宝箱
            "mist_box",                 # 9 迷迭棋盒（30个白色棋子）
            "companion",                # 10 于此同行（翳）
            "apprentice_chest",         # 11 学徒宝箱
            "brave_chest",              # 12 勇者宝箱
            "apprentice_chest",         # 13 学徒宝箱
            "apprentice_chest",         # 14 学徒宝箱
            "mist_box",                 # 15 迷迭棋盒（50个白色棋子）
            "apprentice_chest",         # 16 学徒宝箱 [分支1入口]
            "companion",                # 17 于此同行（翳）[跳过]
            "brave_chest",              # 18 勇者宝箱 [到达]
            "apprentice_chest",         # 19 学徒宝箱
            "apprentice_chest",         # 20 学徒宝箱
            "mist_box",                 # 21 迷迭棋盒（30个白色棋子）
            "arcade_blind",             # 22 弧光盲盒+沉眠池
            "apprentice_chest",         # 23 学徒宝箱
            "brave_chest",              # 24 勇者宝箱变
            "apprentice_chest",         # 25 学徒宝箱
            "apprentice_chest",         # 26 学徒宝箱变
            "mist_box",                 # 27 迷迭棋盒（50个白色棋子）
            "apprentice_chest",         # 28 学徒宝箱
            "companion",                # 29 于此同行（哈尼娅）
            "brave_chest",              # 30 勇者宝箱变
            "apprentice_chest",         # 31 学徒宝箱
            "apprentice_chest",         # 32 学徒宝箱
            "mist_box",                 # 33 迷迭棋盒（30个白色棋子）
            "apprentice_chest",         # 34 学徒宝箱
            "apprentice_chest",         # 35 学徒宝箱（非变格）
            "brave_chest",              # 36 勇者宝箱变
            "companion",                # 37 于此同行（哈尼娅）
            "apprentice_chest",         # 38 学徒宝箱
            "mist_box",                 # 39 迷迭棋盒（30个白色棋子）
            "apprentice_chest",         # 40 学徒宝箱
            "mist_box",                 # 41 迷迭棋盒（50个白色棋子）
            "brave_chest",              # 42 勇者宝箱变 [分支2入口]
            "apprentice_chest",         # 43 学徒宝箱
            "companion",                # 44 于此同行（海月）[跳过]
            "mist_box",                 # 45 迷迭棋盒（30个白色棋子）[结束/到达]
            "apprentice_chest",         # 46 学徒宝箱
            "apprentice_chest",         # 47 学徒宝箱
            "brave_chest",              # 48 勇者宝箱变
            "roll_again",               # 49 再来一次+沉眠池
            "apprentice_chest",         # 50 学徒宝箱变
            "arcade_blind",             # 51 弧光盲盒
            "mist_box",                 # 52 迭棋盒（30个白色棋子）
            "apprentice_chest",         # 53 学徒宝箱
            "brave_chest",              # 54 勇者宝箱变 [终点]

            # ===== 分支1（9格）：B1-0 ~ B1-8 =====
            "companion",                # B1-0 于此同行（浔）[S级角色]
            "vehicle_paint",            # B1-1 改装时刻·涂装
            "brave_chest",              # B1-2 勇者宝箱
            "apprentice_chest",         # B1-3 学徒宝箱
            "brave_chest",              # B1-4 勇者宝箱
            "apprentice_chest",         # B1-5 学徒宝箱
            "brave_chest",              # B1-6 勇者宝箱
            "apprentice_chest",         # B1-7 学徒宝箱
            "brave_chest",              # B1-8 勇者宝箱

            # ===== 分支2（9格）：B2-0 ~ B2-8 =====
            "brave_chest",              # B2-0 勇者宝箱
            "today_outfit",             # B2-1 今日穿搭
            "multi_surprise",           # B2-2 多重惊喜
            "brave_chest",              # B2-3 勇者宝箱
            "brave_chest",              # B2-4 勇者宝箱
            "brave_chest",              # B2-5 勇者宝箱
            "brave_chest",              # B2-6 勇者宝箱
            "brave_chest",              # B2-7 勇者宝箱
            "brave_chest",              # B2-8 勇者宝箱
        ]

        # 格子名称（显示文本）
        cell_names = [
            # ===== 主路径（55格）：0-54 =====
            "起点",                      # 0
            "于此同行（海月）",          # 1
            "学徒宝箱",                  # 2
            "风向标",                    # 3
            "学徒宝箱",                  # 4
            "学徒宝箱",                  # 5
            "勇者宝箱",                  # 6
            "学徒宝箱",                  # 7
            "学徒宝箱",                  # 8
            "迷迭棋盒（30个白色棋子）", # 9
            "于此同行（翳）",            # 10
            "学徒宝箱",                  # 11
            "勇者宝箱",                  # 12
            "学徒宝箱",                  # 13
            "学徒宝箱",                  # 14
            "迷迭棋盒（50个白色棋子）", # 15
            "学徒宝箱",                  # 16 [分支1入口]
            "于此同行（翳）",            # 17 [跳过]
            "勇者宝箱",                  # 18 [到达]
            "学徒宝箱",                  # 19
            "学徒宝箱",                  # 20
            "迷迭棋盒（30个白色棋子）", # 21
            "弧光盲盒+沉眠池",          # 22
            "学徒宝箱",                  # 23
            "勇者宝箱变",                # 24
            "学徒宝箱",                  # 25
            "学徒宝箱变",                # 26
            "迷迭棋盒（50个白色棋子）", # 27
            "学徒宝箱",                  # 28
            "于此同行（哈尼娅）",        # 29
            "勇者宝箱变",                # 30
            "学徒宝箱",                  # 31
            "学徒宝箱",                  # 32
            "迷迭棋盒（30个白色棋子）", # 33
            "学徒宝箱",                  # 34
            "学徒宝箱",                  # 35 （非变格）
            "勇者宝箱变",                # 36
            "于此同行（哈尼娅）",        # 37
            "学徒宝箱",                  # 38
            "迷迭棋盒（30个白色棋子）", # 39
            "学徒宝箱",                  # 40
            "迷迭棋盒（50个白色棋子）", # 41
            "勇者宝箱变",                # 42 [分支2入口]
            "学徒宝箱",                  # 43
            "于此同行（海月）",          # 44 [跳过]
            "迷迭棋盒（30个白色棋子）", # 45 [结束/到达]
            "学徒宝箱",                  # 46
            "学徒宝箱",                  # 47
            "勇者宝箱变",                # 48
            "再来一次+沉眠池",          # 49
            "学徒宝箱变",                # 50
            "弧光盲盒",                  # 51
            "迷迭棋盒（30个白色棋子）", # 52
            "学徒宝箱",                  # 53
            "勇者宝箱变",                # 54 [终点]

            # ===== 分支1（9格）：B1-0 ~ B1-8 =====
            "于此同行（浔）",            # B1-0 [S级角色]
            "改装时刻·涂装",            # B1-1
            "勇者宝箱",                  # B1-2
            "学徒宝箱",                  # B1-3
            "勇者宝箱",                  # B1-4
            "学徒宝箱",                  # B1-5
            "勇者宝箱",                  # B1-6
            "学徒宝箱",                  # B1-7
            "勇者宝箱",                  # B1-8

            # ===== 分支2（9格）：B2-0 ~ B2-8 =====
            "勇者宝箱",                  # B2-0
            "今日穿搭",                  # B2-1
            "多重惊喜",                  # B2-2
            "勇者宝箱",                  # B2-3
            "勇者宝箱",                  # B2-4
            "勇者宝箱",                  # B2-5
            "勇者宝箱",                  # B2-6
            "勇者宝箱",                  # B2-7
            "勇者宝箱",                  # B2-8
        ]

        branch_entries = {
            "B1": {
                # [V0.4.2核心修复] 分支1入口=16号格子(6,19)学徒宝箱，出口=18号格子(8,19)勇者宝箱
                "start_main_idx": 16,
                "branch_cells": [
                    # [V0.4.2修复] 分支1共9格（与CSV序号一致：于此同行浔→改装时刻→勇者宝箱→学徒→勇者→学徒→勇者→学徒→勇者）
                    ("companion", "于此同行（浔）"),   # B1-0 入口(S级角色)
                    ("glider_skin", "改装时刻·涂装"),  # B1-1
                    ("brave_chest", "勇者宝箱"),        # B1-2
                    ("apprentice_chest", "学徒宝箱"),  # B1-3
                    ("brave_chest", "勇者宝箱"),        # B1-4
                    ("apprentice_chest", "学徒宝箱"),  # B1-5
                    ("brave_chest", "勇者宝箱"),        # B1-6
                    ("apprentice_chest", "学徒宝箱"),  # B1-7
                    ("brave_chest", "勇者宝箱"),        # B1-8 出口
                ],
                "rejoin_main_idx": 18,
            },
            "B2": {
                # [V0.4.2核心修复] 分支2入口=43号格子(4,4)学徒宝箱，出口=45号格子(2,4)迷迭棋盒
                # [重要] CSV确认：43号是分支2入口（多重惊喜/今日穿搭区域）
                "start_main_idx": 43,
                "branch_cells": [
                    # [V0.4.2修复] 分支2共9格（与CSV序号一致：多重惊喜→今日穿搭→勇者变→学徒→勇者→学徒→勇者→学徒→勇者）
                    ("multi_surprise", "多重惊喜"),    # B2-0 入口
                    ("glider_skin", "今日穿搭"),       # B2-1
                    ("brave_chest", "勇者宝箱变"),     # B2-2
                    ("apprentice_chest", "学徒宝箱"),  # B2-3
                    ("brave_chest", "勇者宝箱"),        # B2-4
                    ("apprentice_chest", "学徒宝箱"),  # B2-5
                    ("brave_chest", "勇者宝箱"),        # B2-6
                    ("apprentice_chest", "学徒宝箱"),  # B2-7
                    ("brave_chest", "勇者宝箱"),        # B2-8 出口
                ],
                "rejoin_main_idx": 45,
            }
        }

        return (cell_positions, cell_types, cell_names, branch_entries)
