# -*- coding: utf-8 -*-

"""
限定棋盘（真红）完整配置 V1.0
================================

棋盘ID: limited_zhenhong
显示名称: 限定棋盘（真红）
棋盘类型: 限定棋盘（limited）
S级角色: 真红

与安魂曲棋盘的关系：
- 完全复用安魂曲棋盘的坐标布局、变格配置和皮肤系统结构
- 仅替换S级角色名（安魂曲 → 真红）
- A级角色池、同行角色映射均与安魂曲一致

实现说明：
- 独立继承 BaseBoard，避免与安魂曲模块形成循环导入
- 共享数据通过延迟导入 LimitedRequiemBoard 并做名称替换获得

版本历史：
- V1.0: 基于安魂曲棋盘复制（V0.5.3新增）
"""

from typing import Dict, Any
from boards.base_board import BaseBoard


class LimitedZhenhongBoard(BaseBoard):
    """限定棋盘（真红）"""

    # ============================================================
    # 必须实现的属性
    # ============================================================

    @property
    def board_id(self) -> str:
        return "limited_zhenhong"

    @property
    def display_name(self) -> str:
        return "限定棋盘（真红）"

    @property
    def board_type(self) -> str:
        return "limited"

    # ============================================================
    # 共享数据：延迟导入安魂曲棋盘以避免循环导入
    # ============================================================

    def _get_requiem_board(self):
        """延迟导入并返回安魂曲棋盘实例（用于共享数据）"""
        from boards.limited_requiem import LimitedRequiemBoard
        return LimitedRequiemBoard()

    def _replace_requiem_with_zhenhong(self, text: str) -> str:
        """将字符串中的安魂曲替换为真红"""
        return text.replace("安魂曲", "真红")

    # ============================================================
    # 角色池配置
    # ============================================================

    def get_s_pool(self) -> list:
        """
        S级角色池 - 真红（单角色限定）

        概率说明：
        - 综合概率：1.87%（来自规则模板s_rate）
        - 变格后概率：19.59%（来自规则模板s_base_rate_variant）
        - 硬保底：90次必得S级
        """
        return [{"name": "真红", "rate": 0.0187, "limited": True}]

    def get_a_pool(self) -> list:
        """A级角色池（复用安魂曲配置）"""
        return self._get_requiem_board().get_a_pool()

    # ============================================================
    # 同行角色映射
    # ============================================================

    def get_companions(self) -> Dict[Any, str]:
        """
        同行角色映射

        主路径（4个格子）:
        - 第1格 → 阿德勒（A级）
        - 第10格 → 埃德嘉（A级）
        - 第29格 → 薄荷（A级）
        - 第37格 → 薄荷（A级）

        分支1（1个格子）:
        - B1-0 → 真红（S级）
        """
        companions = self._get_requiem_board().get_companions()
        companions["B1-0"] = "真红"
        return companions

    # ============================================================
    # 皮肤系统配置
    # ============================================================

    def get_skin_character(self) -> str:
        """皮肤专属角色名"""
        return "真红"

    def get_skin_system(self) -> Dict[str, Any]:
        """皮肤系统配置（复用安魂曲，替换角色名为真红）"""
        requiem_system = self._get_requiem_board().get_skin_system()
        new_system = {}
        for skin_key, skin_cfg in requiem_system.items():
            new_cfg = skin_cfg.copy()
            new_cfg["skins"] = {
                "真红": self._replace_requiem_with_zhenhong(skin_name)
                for skin_name in skin_cfg["skins"].values()
            }
            new_system[skin_key] = new_cfg
        return new_system

    # ============================================================
    # 变格变换配置
    # ============================================================

    def get_variant_transforms(self) -> Dict[int, Dict[str, str]]:
        """变格变换配置（复用安魂曲）"""
        return self._get_requiem_board().get_variant_transforms()

    # ============================================================
    # 坐标布局数据
    # ============================================================

    def generate_layout(self):
        """
        生成真红棋盘布局坐标

        复用安魂曲坐标，仅将名称中的S级角色替换为真红
        """
        positions, cell_types, cell_names, branch_entries = self._get_requiem_board().generate_layout()

        # 替换所有显示名称中的安魂曲为真红
        new_cell_names = [self._replace_requiem_with_zhenhong(name) for name in cell_names]

        # 替换分支配置中的角色名
        new_branch_entries = {}
        for bkey, bdata in branch_entries.items():
            new_bdata = bdata.copy()
            new_bdata["branch_cells"] = [
                (ctype, self._replace_requiem_with_zhenhong(cname))
                for ctype, cname in bdata["branch_cells"]
            ]
            new_branch_entries[bkey] = new_bdata

        return positions, cell_types, new_cell_names, new_branch_entries
