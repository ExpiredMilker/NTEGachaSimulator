# -*- coding: utf-8 -*-

"""
常驻棋盘完整配置 V1.0
======================

棋盘ID: permanent_default
显示名称: 常驻棋盘
棋盘类型: 常驻棋盘（permanent）
S级角色池：6个常驻S级角色（多角色池）

特殊配置：
- 无皮肤系统（返回空字典）
- 同行角色使用随机标记（__RANDOM_A__ / __RANDOM_S__）
- 自定义概率规则（与限定棋盘不同）

版本历史：
- V1.0: 从board_data.py提取（V0.4.2重构）
"""

from typing import Dict, List, Tuple, Any, Optional
from boards.base_board import BaseBoard


class PermanentDefaultBoard(BaseBoard):
    """常驻棋盘（默认配置）"""

    # ============================================================
    # 必须实现的属性
    # ============================================================

    @property
    def board_id(self) -> str:
        return "permanent_default"

    @property
    def display_name(self) -> str:
        return "常驻棋盘"

    @property
    def board_type(self) -> str:
        return "permanent"

    @property
    def enabled(self) -> bool:
        """已启用常驻棋盘"""
        return True

    # ============================================================
    # 角色池配置
    # ============================================================

    def get_s_pool(self) -> list:
        """
        S级角色池 - 6个常驻S级角色（多角色池）

        角色列表：
        - 早雾、白藏、哈索尔、法蒂娅、达芙蒂尔、九原

        概率说明：
        - 综合概率：1.86%（s_rate）
        - 每个角色均分：0.31%（1.86% / 6）
        - 变格后综合概率：19.59%（每个约3.27%）
        """
        s_characters = [
            "早雾", "白藏", "哈索尔", "法蒂娅", "达芙蒂尔", "九原"
        ]
        per_char_rate = 0.0031  # 1.86% / 6 ≈ 0.31%

        return [
            {"name": name, "rate": per_char_rate, "limited": False}
            for name in s_characters
        ]

    def get_a_pool(self) -> list:
        """
        A级角色池 - 6个全部在主池（无赠礼独占池）

        角色列表：
        - 翳、薄荷、哈尼娅、埃德嘉、阿德勒、海月

        概率说明：
        - 综合概率：22.98%（a_rate_total）
        - 每个角色均分：3.83%（22.98% / 6）
        """
        a_characters = [
            "翳", "薄荷", "哈尼娅", "埃德嘉", "阿德勒", "海月"
        ]
        per_char_rate = 0.0383  # 22.98% / 6 ≈ 3.83%

        return [
            {"name": name, "rate": per_char_rate, "gift_only": False}
            for name in a_characters
        ]

    # ============================================================
    # 同行角色映射（使用随机标记）
    # ============================================================

    def get_companions(self) -> Dict[Any, str]:
        """
        同行角色映射（使用随机标记）

        特殊标记说明：
        - __RANDOM_A__: 从A级主池随机选择1个角色
        - __RANDOM_S__: 从S级池随机选择1个角色

        主路径（6个格子）: 全部使用__RANDOM_A__
        分支1（1个格子）: 使用__RANDOM_S__
        """
        return {
            1: "__RANDOM_A__",
            10: "__RANDOM_A__",
            17: "__RANDOM_A__",
            29: "__RANDOM_A__",
            37: "__RANDOM_A__",
            44: "__RANDOM_A__",
            "B1-0": "__RANDOM_S__",   # 分支1起点 → 随机S级
        }

    # ============================================================
    # 皮肤系统（常驻棋盘无皮肤）
    # ============================================================

    def get_skin_character(self) -> Optional[str]:
        """常驻棋盘无皮肤系统"""
        return None

    def get_skin_system(self) -> Dict[str, Any]:
        """常驻棋盘无皮肤系统，返回空字典"""
        return {}

    # ============================================================
    # 自定义概率规则（覆盖限定棋盘模板）
    # ============================================================

    def get_board_rules(self) -> Dict[str, Any]:
        """
        常驻棋盘自定义规则

        与限定棋盘的差异：
        - S级综合概率略低：1.86% vs 1.87%
        - 其他参数相同（变格阈值70次，硬保底90次）
        """
        return {
            "s_rate": 0.0186,              # 6个 x 0.31% = 1.86%
            "s_base_rate_normal": 0.0099,
            "s_base_rate_variant": 0.1959,
            "s_pity_variant_threshold": 70,
            "s_pity_hard": 90,
        }

    # ============================================================
    # 变格变换配置（V0.4.2新增）
    # ============================================================

    def get_variant_transforms(self) -> Dict[int, Dict[str, str]]:
        """
        变格变换配置（三棋盘通用）

        说明：
        - 常驻棋盘的变格规则与限定棋盘完全相同
        - 格子位置一致（基于CSV文件验证）
        """
        # 复用浔的变格配置（结构完全相同）
        from boards.limited_xun import LimitedXunBoard
        xun_board = LimitedXunBoard()
        return xun_board.get_variant_transforms()

    # ============================================================
    # 坐标布局数据（73格）
    # ============================================================

    def generate_layout(self) -> Tuple[List[Tuple[int, int]], List[str], List[str], Dict]:
        """
        生成常驻棋盘布局坐标

        数据来源：常驻棋盘地图手动统计.csv
        布局结构与限定棋盘完全相同（坐标、格子类型一致）
        仅格子名称不同（使用"于此同行（随机A/S）"等占位符）

        返回:
            (cell_positions, cell_types, cell_names, branch_entries)
        """
        # [V0.4.2核心修复] 使用与board_data.py一致的坐标系统
        # 主路径：55格（索引0-54），起点在(4,10)，顺时针蛇形
        cell_positions = [
            # ===== 主路径（55格）：0-54 =====
            (4, 10), (4, 11), (4, 12), (4, 13), (4, 14),
            (3, 14), (2, 14), (1, 14), (1, 15), (1, 16),
            (1, 17), (2, 17), (3, 17), (4, 17), (4, 18),
            (4, 19), (5, 19), (6, 19), (7, 19), (8, 19),
            (9, 19), (10, 19), (10, 18), (10, 17), (10, 16),
            (10, 15), (10, 14), (9, 14), (9, 13), (9, 12),
            (9, 11), (9, 10), (9, 9), (9, 8), (8, 8),
            (8, 7), (8, 6), (8, 5), (8, 4), (7, 4),
            (6, 4), (5, 4), (4, 4), (3, 4), (2, 4),
            (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
            (1, 9), (1, 10), (1, 11), (2, 11), (3, 11),

            # ===== 分支1（9格）：B1-0 ~ B1-8 =====
            (5, 21), (5, 22), (5, 23), (5, 24), (6, 24),
            (7, 24), (7, 23), (7, 22), (7, 21),

            # ===== 分支2（9格）：B2-0 ~ B2-8 =====
            (3, 2), (3, 1), (3, 0), (2, 0), (1, 0),
            (0, 0), (0, 1), (0, 2), (1, 2),
        ]

        # 格子类型（与坐标一一对应）- 包含失纬棋盒
        cell_types = [
            # ===== 主路径（55格）：0-54 =====
            "start", "companion", "apprentice_chest", "lost_treasure_box", "apprentice_chest",
            "apprentice_chest", "brave_chest", "apprentice_chest", "apprentice_chest", "mist_box",
            "companion", "apprentice_chest", "brave_chest", "apprentice_chest", "apprentice_chest",
            "mist_box", "apprentice_chest", "companion", "brave_chest", "apprentice_chest",
            "apprentice_chest", "mist_box", "arcade_blind", "apprentice_chest", "brave_chest",
            "apprentice_chest", "apprentice_chest", "mist_box", "apprentice_chest", "companion",
            "brave_chest", "apprentice_chest", "apprentice_chest", "mist_box", "apprentice_chest",
            "apprentice_chest", "brave_chest", "companion", "apprentice_chest", "mist_box",
            "apprentice_chest", "mist_box", "brave_chest", "apprentice_chest", "companion",
            "mist_box", "apprentice_chest", "apprentice_chest", "brave_chest", "roll_again",
            "apprentice_chest", "arcade_blind", "mist_box", "apprentice_chest", "brave_chest",

            # ===== 分支1（9格）：B1-0 ~ B1-8 =====
            "companion", "lost_treasure_box", "brave_chest", "apprentice_chest", "brave_chest",
            "apprentice_chest", "brave_chest", "apprentice_chest", "brave_chest",

            # ===== 分支2（9格）：B2-0 ~ B2-8 =====
            "brave_chest", "lost_treasure_box", "multi_surprise", "brave_chest", "brave_chest",
            "brave_chest", "brave_chest", "brave_chest", "brave_chest",
        ]

        # 格子名称（显示文本）
        cell_names = [
            # ===== 主路径（55格）：0-54 =====
            "起点", "于此同行（随机A级）", "学徒宝箱", "失纬棋盒（4金）", "学徒宝箱",
            "学徒宝箱", "勇者宝箱", "学徒宝箱", "学徒宝箱", "迷迭棋盒（30白）",
            "于此同行（随机A级）", "学徒宝箱", "勇者宝箱", "学徒宝箱", "学徒宝箱",
            "迷迭棋盒（50白）", "学徒宝箱", "于此同行（随机A级）", "勇者宝箱", "学徒宝箱",
            "学徒宝箱", "迷迭棋盒（30白）", "弧光盲盒+沉眠池", "学徒宝箱", "勇者宝箱",
            "学徒宝箱", "学徒宝箱", "迷迭棋盒（50白）", "学徒宝箱", "于此同行（随机A级）",
            "勇者宝箱", "学徒宝箱", "学徒宝箱", "迷迭棋盒（30白）", "学徒宝箱",
            "学徒宝箱", "勇者宝箱", "于此同行（随机A级）", "学徒宝箱", "迷迭棋盒（30白）",
            "学徒宝箱", "迷迭棋盒（50白）", "勇者宝箱", "学徒宝箱", "于此同行（随机A级）",
            "迷迭棋盒（30白）", "学徒宝箱", "学徒宝箱", "勇者宝箱", "再来一次+沉眠池",
            "学徒宝箱", "弧光盲盒", "迷迭棋盒（30白）", "学徒宝箱", "勇者宝箱",

            # ===== 分支1（9格）：B1-0 ~ B1-8 =====
            "于此同行（随机S级）", "失纬棋盒（16金）", "勇者宝箱", "学徒宝箱", "勇者宝箱",
            "学徒宝箱", "勇者宝箱", "学徒宝箱", "勇者宝箱",

            # ===== 分支2（9格）：B2-0 ~ B2-8 =====
            "勇者宝箱", "失纬棋盒（16金）", "多重惊喜", "勇者宝箱", "勇者宝箱",
            "勇者宝箱", "勇者宝箱", "勇者宝箱", "勇者宝箱",
        ]

        branch_entries = {
            "B1": {
                # [V0.4.2核心修复] 分支1入口=16号格子(6,19)学徒宝箱，出口=18号格子(8,19)勇者宝箱
                "start_main_idx": 16,
                "branch_cells": [
                    ("companion", "于此同行（随机S级）"),
                    ("lost_treasure_box", "失纬棋盒（16金）"),
                    ("brave_chest", "勇者宝箱"),
                    ("apprentice_chest", "学徒宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("apprentice_chest", "学徒宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("apprentice_chest", "学徒宝箱"),
                    ("brave_chest", "勇者宝箱"),
                ],
                "rejoin_main_idx": 18,  # 返回主路径18号格子
            },
            "B2": {
                # [V0.4.2核心修复] 分支2入口=43号格子(4,4)学徒宝箱，出口=45号格子(2,4)迷迭棋盒
                # [重要] CSV确认：43号是分支2入口（多重惊喜/失纬棋盒区域）
                "start_main_idx": 43,
                "branch_cells": [
                    ("brave_chest", "勇者宝箱"),
                    ("lost_treasure_box", "失纬棋盒（16金）"),
                    ("multi_surprise", "多重惊喜"),
                    ("brave_chest", "勇者宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("brave_chest", "勇者宝箱"),
                    ("brave_chest", "勇者宝箱"),
                ],
                "rejoin_main_idx": 45,  # 返回主路径45号格子
            }
        }

        return (cell_positions, cell_types, cell_names, branch_entries)
