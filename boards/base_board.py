# -*- coding: utf-8 -*-

"""
棋盘抽象基类 V1.0
=================

设计目标：
- 统一棋盘接口，支持插件化扩展
- 新增限定棋盘只需继承此类并实现必要方法
- 无需修改核心逻辑代码（game_logic.py / main.py）

使用示例：
    from boards.base_board import BaseBoard

    class MyNewBoard(BaseBoard):
        @property
        def board_id(self): return "limited_new"

        def get_s_pool(self): return [...]
        # ... 其他必须实现的方法

版本历史：
- V1.0: 初始版本（V0.4.2重构）
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional


class BaseBoard(ABC):
    """
    棋盘基类 - 所有棋盘必须实现此接口

    设计原则：
    1. 单一职责：每个棋盘类只负责自己的配置数据
    2. 开闭原则：新增棋盘不修改现有代码
    3. 依赖倒置：核心逻辑依赖抽象接口，不依赖具体实现
    """

    # ============================================================
    # 必须实现的属性（@property装饰器）
    # ============================================================

    @property
    @abstractmethod
    def board_id(self) -> str:
        """
        棋盘唯一标识符

        命名规范：
        - 限定棋盘：limited_[角色拼音] （如 limited_xun, limited_requiem）
        - 常驻棋盘：permanent_[名称] （如 permanent_default）

        返回:
            str: 唯一标识符（用于字典索引、文件命名等）
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        显示名称（中文友好）

        返回:
            str: 在UI中显示的名称（如 "限定棋盘（浔）"）
        """
        pass

    @property
    @abstractmethod
    def board_type(self) -> str:
        """
        棋盘类型

        返回:
            str: "limited"（限定棋盘）或 "permanent"（常驻棋盘）
        """
        pass

    @property
    def enabled(self) -> bool:
        """
        是否启用（默认True，可重写）

        返回:
            bool: True表示可用，False表示隐藏
        """
        return True

    # ============================================================
    # 必须实现的方法（返回配置数据）
    # ============================================================

    @abstractmethod
    def get_s_pool(self) -> list:
        """
        获取S级角色池

        返回:
            list: S级角色列表，格式：[{"name": str, "rate": float, "limited": bool}]

        示例（限定棋盘-单角色）:
            [{"name": "浔", "rate": 0.0187, "limited": True}]

        示例（常驻棋盘-多角色）:
            [
                {"name": "早雾", "rate": 0.0031, "limited": False},
                {"name": "白藏", "rate": 0.0031, "limited": False},
                ...
            ]
        """
        pass

    @abstractmethod
    def get_a_pool(self) -> list:
        """
        获取A级角色池

        返回:
            list: A级角色列表，格式：[{"name": str, "rate": float, "gift_only": bool}]

        示例:
            [
                {"name": "哈尼娅", "rate": 0.0376, "gift_only": False},
                {"name": "翳", "rate": 0.0346, "gift_only": False},
                {"name": "薄荷", "rate": 0.0033, "gift_only": True},
            ]
        """
        pass

    @abstractmethod
    def get_companions(self) -> Dict[Any, str]:
        """
        获取同行角色映射

        返回:
            dict: {格子索引: 角色名}

        格子索引说明：
        - 主路径格子使用整数：1, 10, 29, 37
        - 分支格子使用字符串："B1-0", "B2-2"
        - 特殊标记："__RANDOM_A__"（随机A级）, "__RANDOM_S__"（随机S级）

        示例:
            {
                1: "海月",
                10: "翳",
                29: "哈尼娅",
                37: "哈尼娅",
                "B1-0": "浔",
            }
        """
        pass

    @abstractmethod
    def get_skin_system(self) -> Dict[str, Any]:
        """
        获取皮肤系统配置

        返回:
            dict: 皮肤系统配置字典

        结构示例:
            {
                "today_outfit": {...},
                "vehicle_paint": {...},
                "glider_skin": {...},
            }

        如果该棋盘无皮肤系统，返回空字典 {}
        """
        pass

    @abstractmethod
    def get_variant_transforms(self) -> Dict[int, Dict[str, str]]:
        """
        获取变格变换配置（V0.4.2新增）

        返回:
            dict: 变格变换映射

        结构示例:
            {
                2: {
                    "normal": "apprentice_chest",
                    "variant": "brave_chest",
                    "variant_name": "学徒宝箱变",
                },
                6: {
                    "normal": "brave_chest",
                    "variant": "companion_s",
                    "variant_name": "勇者宝箱变",
                },
            }

        说明：
        - key: 格子索引（整数）
        - value.normal: 正常状态的格子类型
        - value.variant: 变格后的格子类型
        - value.variant_name: 变格后的显示名称
        """
        pass

    @abstractmethod
    def generate_layout(self) -> Tuple[List[Tuple[int, int]], List[str], List[str], Dict]:
        """
        生成棋盘布局数据

        返回:
            tuple: (cell_positions, cell_types, cell_names, branch_entries)

        参数说明：
        - cell_positions: [(x, y), (x, y), ...] 73个格子的坐标列表
        - cell_types: ["companion", "apprentice_chest", ...] 格子类型列表
        - cell_names: ["于此同行（浔）", "学徒宝箱", ...] 格子名称列表
        - branch_entries: 分支元数据字典
        """
        pass

    # ============================================================
    # 可选重写的方法（提供默认实现）
    # ============================================================

    def get_board_rules(self) -> Dict[str, Any]:
        """
        获取自定义概率规则（可选重写）

        返回:
            dict: 规则参数字典

        默认值（限定棋盘模板）:
            {
                "s_rate": 0.0187,
                "s_base_rate_normal": 0.0099,
                "s_base_rate_variant": 0.1959,
                "s_pity_variant_threshold": 70,
                "s_pity_hard": 90,
            }

        注意：
        - 限定棋盘通常不需要重写此方法（使用默认模板）
        - 常驻棋盘可能需要自定义规则（如不同的S级概率）
        """
        return {}

    def get_skin_character(self) -> Optional[str]:
        """
        获取皮肤专属角色名（可选重写）

        返回:
            Optional[str]: 皮肤系统绑定的角色名，或None

        示例:
            浔棋盘返回 "浔"
            安魂曲棋盘返回 "安魂曲"
            常驻棋盘返回 None（无皮肤系统）
        """
        return None

    def get_special_cells(self) -> Dict[int, str]:
        """
        获取特殊格子配置（可选重写）

        返回:
            dict: {格子索引: 特殊类型}

        用于标记需要特殊处理的格子（如双倍惊喜等）
        """
        return {}

    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        验证配置完整性（调试用）

        返回:
            tuple: (是否有效, 错误信息列表)

        使用场景：
        - 开发阶段自检配置是否完整
        - 新增棋盘后快速定位遗漏项
        """
        errors = []

        # 检查必填属性
        try:
            if not self.board_id:
                errors.append("board_id 不能为空")
            if not self.display_name:
                errors.append("display_name 不能为空")
            if self.board_type not in ("limited", "permanent"):
                errors.append(f"board_type 必须是 'limited' 或 'permanent'，当前: {self.board_type}")
        except Exception as e:
            errors.append(f"必填属性检查失败: {e}")

        # 检查方法返回值
        try:
            s_pool = self.get_s_pool()
            if not isinstance(s_pool, list) or len(s_pool) == 0:
                errors.append("get_s_pool() 必须返回非空列表")

            a_pool = self.get_a_pool()
            if not isinstance(a_pool, list) or len(a_pool) == 0:
                errors.append("get_a_pool() 必须返回非空列表")

            companions = self.get_companions()
            if not isinstance(companions, dict):
                errors.append("get_companions() 必须返回字典")

            layout = self.generate_layout()
            if not isinstance(layout, tuple) or len(layout) != 4:
                errors.append("generate_layout() 必须返回4元素元组")
            else:
                positions, types, names, branches = layout
                # [V0.4.2修复] 使用实际坐标数量作为验证标准
                expected_count = len(positions) if len(positions) > 0 else 73
                if len(types) != expected_count:
                    errors.append(f"格子类型数量错误: 期望{expected_count}个，实际{len(types)}个")
                if len(names) != expected_count:
                    errors.append(f"格子名称数量错误: 期望{expected_count}个，实际{len(names)}个")
                # 检查三者是否一致
                if len(positions) != len(types) or len(positions) != len(names):
                    errors.append(f"布局数据数量不一致: 坐标{len(positions)}, 类型{len(types)}, 名称{len(names)}")

            variant_transforms = self.get_variant_transforms()
            if not isinstance(variant_transforms, dict):
                errors.append("get_variant_transforms() 必须返回字典")

        except Exception as e:
            errors.append(f"方法调用检查失败: {e}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def __repr__(self) -> str:
        """字符串表示（用于日志输出）"""
        return f"<{self.__class__.__name__}(id={self.board_id}, name={self.display_name}, type={self.board_type})>"
