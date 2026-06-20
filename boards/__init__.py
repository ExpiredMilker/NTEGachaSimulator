# -*- coding: utf-8 -*-

"""
棋盘注册表 - 自动发现并注册所有棋盘 V1.0
========================================

功能：
1. 自动导入boards/目录下的所有棋盘模块
2. 维护全局棋盘注册表（BOARD_REGISTRY）
3. 提供便捷的查询接口

使用示例：
    from boards import get_board, list_boards

    # 获取棋盘实例
    xun_board = get_board("limited_xun")

    # 列出所有可用棋盘
    boards = list_boards()
    for b in boards:
        print(f"{b['id']}: {b['name']}")

新增棋盘步骤：
1. 在boards/目录创建新文件（如 boards/limited_new.py）
2. 继承BaseBoard类并实现必要方法
3. 文件会被自动发现和注册，无需修改此文件

版本历史：
- V1.0: 初始版本（V0.4.2重构）
"""

import os
import sys
from typing import Dict, List, Type, Any, Optional, Tuple

# ============================================================
# 棋盘注册表（全局单例）
# ============================================================
BOARD_REGISTRY: Dict[str, Any] = {}

# ============================================================
# 导入基类（用于类型检查）
# ============================================================
from .base_board import BaseBoard


def register_board(board_instance: BaseBoard) -> None:
    """
    手动注册棋盘到全局表

    参数:
        board_instance: 棋盘实例（必须是BaseBoard子类）

    使用场景：
        - 自动注册失败时的备用方案
        - 动态加载棋盘时使用
    """
    if not isinstance(board_instance, BaseBoard):
        raise TypeError(f"必须传入BaseBoard子类实例，当前类型: {type(board_instance)}")

    board_id = board_instance.board_id

    if board_id in BOARD_REGISTRY:
        print(f"[警告] 棋盘 {board_id} 已存在，将被覆盖")

    BOARD_REGISTRY[board_id] = board_instance
    print(f"[棋盘注册] 已加载: {board_instance.display_name} ({board_id})")


def get_board(board_id: str) -> BaseBoard:
    """
    获取棋盘实例

    参数:
        board_id: 棋盘唯一标识符（如 "limited_xun"）

    返回:
        BaseBoard: 棋盘实例

    异常:
        KeyError: 如果board_id不存在

    示例:
        >>> xun = get_board("limited_xun")
        >>> s_pool = xun.get_s_pool()
    """
    if board_id not in BOARD_REGISTRY:
        available = ", ".join(BOARD_REGISTRY.keys()) or "(无)"
        raise KeyError(
            f"未知棋盘: {board_id}\n"
            f"可用棋盘: {available}"
        )

    return BOARD_REGISTRY[board_id]


def list_boards() -> List[Dict[str, str]]:
    """
    列出所有可用棋盘的基本信息

    返回:
        list: 棋盘信息列表，每个元素包含：
            - id: 棋盘ID
            - name: 显示名称
            - type: 棋盘类型（limited/permanent）
            - enabled: 是否启用

    示例:
        >>> boards = list_boards()
        >>> for b in boards:
        ...     print(f"{b['id']}: {b['name']} (type={b['type']})")
    """
    return [
        {
            "id": bid,
            "name": board.display_name,
            "type": board.board_type,
            "enabled": board.enabled,
        }
        for bid, board in BOARD_REGISTRY.items()
    ]


def get_enabled_boards() -> List[str]:
    """
    获取所有已启用的棋盘ID列表

    返回:
        list: 已启用的board_id列表

    用途：
        UI下拉框填充选项
    """
    return [
        bid for bid, board in BOARD_REGISTRY.items()
        if board.enabled
    ]


def validate_all_boards() -> Dict[str, Tuple[bool, List[str]]]:
    """
    验证所有已注册棋盘的配置完整性

    返回:
        dict: {board_id: (是否有效, 错误信息列表)}

    使用场景：
        - 开发阶段自检
        - 新增棋盘后快速定位问题
    """
    results = {}

    for board_id, board in BOARD_REGISTRY.items():
        try:
            is_valid, errors = board.validate_config()
            results[board_id] = (is_valid, errors)

            if not is_valid:
                print(f"[验证失败] {board_id}:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"[验证通过] {board_id}")

        except Exception as e:
            results[board_id] = (False, [f"验证异常: {e}"])
            print(f"[验证异常] {board_id}: {e}")

    return results


# ============================================================
# 自动发现机制（模块导入时执行）
# ============================================================

def _auto_discover_boards() -> None:
    """
    自动发现boards/目录下的所有棋盘模块

    发现规则：
    1. 扫描当前文件所在目录（boards/）
    2. 查找所有.py文件（排除__init__.py和base_board.py）
    3. 动态导入每个模块
    4. 查找模块中的BaseBoard子类
    5. 实例化并注册到BOARD_REGISTRY

    兼容性：
    - 正常Python运行：使用__file__定位boards目录
    - PyInstaller打包：使用sys._MEIPASS定位解压后的目录
    """
    # 获取当前文件所在目录（兼容PyInstaller打包环境）
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后：从_MEIPASS获取实际路径
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path:
            current_dir = os.path.join(base_path, 'boards')
        else:
            # 回退方案：使用__file__
            current_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        # 正常Python运行
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # 需要跳过的文件
    skip_files = {"__init__.py", "base_board.py"}

    discovered_count = 0

    try:
        for filename in os.listdir(current_dir):
            # 只处理.py文件
            if not filename.endswith(".py"):
                continue

            # 跳过特殊文件
            if filename in skip_files:
                continue

            # 提取模块名（去掉.py后缀）
            module_name = filename[:-3]

            try:
                # 动态导入模块
                # 使用相对导入：from .limited_xun import LimitedXunBoard
                import importlib

                full_module_name = f".{module_name}"
                module = importlib.import_module(full_module_name, package="boards")

                # 查找模块中的BaseBoard子类
                board_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # 检查是否是BaseBoard子类（排除BaseBoard本身）
                    if (isinstance(attr, type) and
                        issubclass(attr, BaseBoard) and
                        attr is not BaseBoard):
                        board_class = attr
                        break

                if board_class is None:
                    print(f"[警告] {filename} 中未找到BaseBoard子类，跳过")
                    continue

                # 实例化并注册
                board_instance = board_class()
                register_board(board_instance)
                discovered_count += 1

            except Exception as e:
                print(f"[警告] 加载棋盘模块失败: {filename} - {e}")
                continue

        print(f"\n[棋盘发现完成] 共发现 {discovered_count} 个棋盘")

    except Exception as e:
        print(f"[错误] 扫描棋盘目录失败: {e}")


# ============================================================
# 启动时自动发现并注册所有棋盘
# ============================================================
_auto_discover_boards()
