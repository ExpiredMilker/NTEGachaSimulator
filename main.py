# -*- coding: utf-8 -*-

"""
抽卡模拟器主程序 - GUI界面（Tkinter）
包含动画棋盘、骰子滚动、棋子移动、落格高亮、获得弹窗、皮肤系统
版本: v3.0 - 全新渲染引擎 + 多棋盘架构 + 5档速度控制
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from game_logic import GameEngine


class AnimatedBoardCanvas:
    """动画棋盘画布 - 全新渲染引擎 v3.0"""

    # ====== 速度模式常量 ======
    SPEED_SLOW = "0.5x"
    SPEED_NORMAL = "1x"
    SPEED_FAST = "2x"
    SPEED_VERY_FAST = "4x"
    SPEED_SKIP = "skip"

    # ====== 格子颜色映射 ======
    CELL_COLORS = {
        "apprentice_chest": "#E8A838",
        "brave_chest": "#F5C542",
        "companion": "#C850C0",
        "mist_box": "#E8E8F0",
        "arcade_blind": "#5090D0",
        "sleep_pool": "#3D2B55",
        "roll_again": "#45B060",
        "multi_surprise": "#FF5090",
        "glider_skin": "#7CB342",
        "vehicle_paint": "#FF7043",
        "today_outfit": "#AB47BC",
    }

    # ====== 格子样式配置 v4.0 - 增强版 ======
    CELL_STYLES = {
        "start": {
            "color": "#4CAF50", "border": "#1B5E20", "text": "#fff",
            "shape": "star8", "icon": "\u25CF", "short_name": "起点",
            "desc": "起点 (循环不入)",
            "gradient_top": "#81C784", "gradient_bottom": "#388E3C"
        },
        "apprentice_chest": {
            "color": "#FFB74D", "border": "#E65100", "text": "#fff",
            "shape": "round_rect", "icon": "\u2605", "short_name": "学徒",
            "desc": "学徒宝箱 (B/A弧盘)",
            "gradient_top": "#FFCC80", "gradient_bottom": "#FB8C00"
        },
        "brave_chest": {
            "color": "#FFD54F", "border": "#F57C00", "text": "#5D4037",
            "shape": "diamond", "icon": "\u2606", "short_name": "勇者",
            "desc": "勇者宝箱 (S级/弧盘)",
            "gradient_top": "#FFE082", "gradient_bottom": "#FFB300"
        },
        "companion": {
            "color": "#CE93D8", "border": "#7B1FA2", "text": "#fff",
            "shape": "hexagon", "icon": "\u2665", "short_name": "同行",
            "desc": "于此同行 (S/A角色)",
            "gradient_top": "#E1BEE7", "gradient_bottom": "#AB47BC"
        },
        "mist_box": {
            "color": "#CFD8DC", "border": "#546E7A", "text": "#37474F",
            "shape": "rect", "icon": "\u2691", "short_name": "迷迭",
            "desc": "迷迭棋盒 (白棋)",
            "gradient_top": "#ECEFF1", "gradient_bottom": "#B0BEC5"
        },
        "arcade_blind": {
            "color": "#64B5F6", "border": "#1565C0", "text": "#fff",
            "shape": "oval", "icon": "\u2726", "short_name": "盲盒",
            "desc": "弧光盲盒 (A级弧盘)",
            "gradient_top": "#90CAF9", "gradient_bottom": "#1E88E5"
        },
        "sleep_pool": {
            "color": "#9575CD", "border": "#4527A0", "text": "#fff",
            "shape": "star", "icon": "\u2620", "short_name": "沉眠",
            "desc": "沉眠池 (追击游戏)",
            "gradient_top": "#B39DDB", "gradient_bottom": "#673AB7"
        },
        "roll_again": {
            "color": "#81C784", "border": "#2E7D32", "text": "#fff",
            "shape": "circle", "icon": "\u2694", "short_name": "再来",
            "desc": "再来一次 (+1红骰)",
            "gradient_top": "#A5D6A7", "gradient_bottom": "#43A047"
        },
        "multi_surprise": {
            "color": "#F06292", "border": "#AD1457", "text": "#fff",
            "shape": "burst", "icon": "\u272A", "short_name": "惊喜",
            "desc": "多重惊喜 (+5红骰)",
            "gradient_top": "#F48FB1", "gradient_bottom": "#EC407A"
        },
        "glider_skin": {
            "color": "#AED581", "border": "#558B2F", "text": "#33691E",
            "shape": "triangle", "icon": "\u2708", "short_name": "滑翔",
            "desc": "滑翔机皮肤",
            "gradient_top": "#C5E1A5", "gradient_bottom": "#7CB342"
        },
        "vehicle_paint": {
            "color": "#FF8A65", "border": "#BF360C", "text": "#fff",
            "shape": "shield", "icon": "\u260F", "short_name": "涂装",
            "desc": "改装时刻·涂装",
            "gradient_top": "#FFAB91", "gradient_bottom": "#FF5722"
        },
        "today_outfit": {
            "color": "#BA68C8", "border": "#6A1B9A", "text": "#fff",
            "shape": "clothing", "icon": "\u2600", "short_name": "穿搭",
            "desc": "今日穿搭",
            "gradient_top": "#CE93D8", "gradient_bottom": "#9C27B0"
        }
    }

    # ====== 格子图标映射 ======
    CELL_ICONS = {
        "apprentice_chest": "\u2605",
        "brave_chest": "\u2606",
        "companion": "\u2665",
        "mist_box": "\u2691",
        "arcade_blind": "\u2726",
        "sleep_pool": "\u2620",
        "roll_again": "\u2694",
        "multi_surprise": "\u272A",
        "glider_skin": "\u2708",
        "vehicle_paint": "\u260F",
        "today_outfit": "\u2600",
    }

    # ====== 格子短名称映射 ======
    CELL_NAMES = {
        "apprentice_chest": "学徒",
        "brave_chest": "勇者",
        "companion": "同行",
        "mist_box": "迷迭",
        "arcade_blind": "盲盒",
        "sleep_pool": "沉眠",
        "roll_again": "再来",
        "multi_surprise": "惊喜",
        "glider_skin": "滑翔",
        "vehicle_paint": "涂装",
        "today_outfit": "穿搭",
    }

    def __init__(self, parent, engine, board_config=None):
        self.engine = engine
        self.parent = parent
        self.cell_size = 32
        self.is_animating = False
        self.speed_mode = tk.StringVar(value=self.SPEED_NORMAL)
        self.cell_positions = []
        self.cell_types = []
        self.total_cells = 0
        self.start_cell_idx = 0
        self.cycle_start_idx = 1
        self.branch_entries = {}
        self.board_name = ""
        self.board_type = "limited"

        if board_config:
            self._load_board_config(board_config)
        else:
            self._generate_limited_board()

        self.piece_pos_idx = 0
        self.piece_ids = []
        self.highlight_id = None
        self.dice_display_id = None
        self.dice_text_id = None

        self.target_canvas_w = 620
        self.target_canvas_h = 450
        self._calc_canvas_size()
        self.canvas = tk.Canvas(
            parent,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="#f8f4e8",
            highlightthickness=2,
            highlightbackground="#c9b896"
        )
        self.canvas.pack(padx=6, pady=6, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._render_full_board()

    def _on_canvas_resize(self, event):
        """画布大小改变时重新计算并渲染"""
        if event.width < 10 or event.height < 10:
            return
        new_w = event.width
        new_h = event.height
        if abs(new_w - self.canvas_w) > 20 or abs(new_h - self.canvas_h) > 20:
            self.target_canvas_w = new_w
            self.target_canvas_h = new_h
            self._calc_adaptive_size()
            self.canvas.delete("all")
            self._render_full_board()

    def _calc_canvas_size(self):
        """计算画布尺寸和偏移量（初始计算）"""
        if not self.cell_positions:
            self.canvas_w, self.canvas_h = 520, 400
            self.offset_x, self.offset_y = 60, 20
            return

        all_x = [p[0] for p in self.cell_positions]
        all_y = [p[1] for p in self.cell_positions]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)

        self.logical_w = int(self.max_x - self.min_x) + self.cell_size
        self.logical_h = int(self.max_y - self.min_y) + self.cell_size

        pad_x = self.cell_size + 30
        pad_y = self.cell_size + 50
        self.offset_x = (pad_x // 2) - self.min_x + (self.cell_size // 2)
        self.offset_y = (pad_y // 2) - self.min_y + (self.cell_size // 2)
        self.canvas_w = self.logical_w + pad_x
        self.canvas_h = self.logical_h + pad_y

    def _calc_adaptive_size(self):
        """根据目标画布尺寸自适应计算cell_size"""
        if not self.cell_positions:
            return

        legend_width = 110
        header_margin = 20
        left_margin = 25
        right_margin = 120

        avail_w = self.target_canvas_w - left_margin - right_margin
        avail_h = self.target_canvas_h - header_margin - 10

        if avail_w <= 0 or avail_h <= 0:
            return

        scale_x = avail_w / self.logical_w if self.logical_w > 0 else 1
        scale_y = avail_h / self.logical_h if self.logical_h > 0 else 1
        scale = min(scale_x, scale_y, 1.5)

        old_cell_size = self.cell_size
        self.cell_size = max(22, min(38, int(32 * scale)))

        if abs(self.cell_size - old_cell_size) > 1:
            pad_x_left = self.cell_size + 20
            pad_x_right = legend_width + 20
            pad_y = self.cell_size + 40
            self.offset_x = (pad_x_left // 2) - self.min_x + (self.cell_size // 2)
            self.offset_y = (pad_y // 2) - self.min_y + (self.cell_size // 2)
            self.canvas_w = self.logical_w * (self.cell_size / 32) + pad_x_left + pad_x_right
            self.canvas_h = self.logical_h * (self.cell_size / 32) + pad_y

    def _ox(self, x):
        """坐标转换：逻辑X -> 画布X"""
        return x + self.offset_x

    def _oy(self, y):
        """坐标转换：逻辑Y -> 画布Y"""
        return y + self.offset_y

    def _cycle_pos(self, current_idx, steps):
        """
        计算移动后的位置（逐步移动）
        起点索引0不参与循环，只作为初始位置
        循环范围：1 到 main_path_len-1（只在主路径内循环，不包括分支）
        """
        if not hasattr(self, 'main_path_len'):
            self.main_path_len = self.total_cells  # 兼容旧代码

        cycle_end = self.main_path_len - 1  # 主路径最后一个索引

        # 逐步移动，每一步都调用_next_single_step
        new_idx = current_idx
        for _ in range(steps):
            new_idx = self._next_single_step(new_idx, cycle_end)

        return new_idx

    def _next_single_step(self, current_idx, cycle_end):
        """单步移动逻辑（处理起点跳过和循环）"""
        # 特殊情况：从起点出发，第一步到循环起点
        if current_idx == self.start_cell_idx:
            return self.cycle_start_idx

        # 正常情况：当前位置+1
        next_idx = current_idx + 1

        # 检查是否超出循环范围
        if next_idx > cycle_end:
            # 循环回到起点（但不包括start_cell_idx）
            next_idx = self.cycle_start_idx

        return next_idx

    def _next_pos(self, current_idx):
        """获取下一个位置（跳过起点）"""
        return self._cycle_pos(current_idx, 1)

    def _delay(self, base_ms):
        """根据速度模式计算延迟时间"""
        mode = self.speed_mode.get()
        speed_map = {
            self.SPEED_SLOW: base_ms * 2,
            self.SPEED_NORMAL: base_ms,
            self.SPEED_FAST: max(10, base_ms // 2),
            self.SPEED_VERY_FAST: max(5, base_ms // 4),
            self.SPEED_SKIP: 1,
        }
        return speed_map.get(mode, base_ms)

    def _generate_limited_board(self):
        """生成限定棋盘布局（浔）- 基于CSV文档形状 v8.0

        核心思路：
        1. 从CSV提取所有格子的实际坐标（用于视觉显示，保持形状）
        2. 按txt文档顺序排列游戏逻辑索引（确保起点在index=0）
        3. 建立映射：游戏索引 → CSV坐标
        """
        self.board_name = "限定棋盘(浔)"
        self.board_type = "limited"
        cs = self.cell_size

        # 类型映射表
        T = {
            "起点": "start",
            "于此同行（海月）": "companion",
            "于此同行（翳）": "companion",
            "于此同行（哈尼娅）": "companion",
            "于此同行（浔）": "companion",
            "学徒宝箱": "apprentice_chest",
            "勇者宝箱": "brave_chest",
            "迷迭棋盒（30个白色棋子）": "mist_box",
            "迷迭棋盒（50个白色棋子）": "mist_box",
            "风向标": "glider_skin",
            "弧光盲盒+沉眠池": "arcade_blind",
            "弧光盲盒": "arcade_blind",
            "再来一次+沉眠池": "roll_again",
            "今日穿搭": "today_outfit",
            "改装时刻·涂装": "vehicle_paint",
            "多重惊喜": "multi_surprise",
        }

        import csv as csv_module
        from os import path as os_path
        import re

        # 步骤1：读取CSV文件并解析带编号的格式
        csv_path = os_path.join(os_path.dirname(__file__), "棋盘地图手动统计.csv")

        board_raw = []
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv_module.reader(f)
            for row in reader:
                board_raw.append(row)

        # 正则表达式匹配格式：
        # 主路径：原名——数字（如 "起点——0", "风向标——3"）
        # 分支：原名——分支数字（如 "浔同行——分支1", "勇者——分支6"）
        # 注意：分支数字是格子序号（1-9），不是分支ID！
        pattern_main = re.compile(r'^(.+?)——(\d+)$')
        pattern_branch = re.compile(r'^(.+?)——分支(\d+)$')

        main_path_data = []    # [(row, col, type_name, idx), ...]
        branch_raw_data = []   # [(row, col, type_name, branch_seq), ...]  暂存所有分支

        print("=" * 80)
        print("开始解析CSV文件（新格式：带编号）")
        print("=" * 80)

        for row_idx, row in enumerate(board_raw[1:], 1):  # 跳过标题行
            for col_idx, cell in enumerate(row):
                if not cell or not cell.strip() or cell.startswith('限定'):
                    continue

                cell = cell.strip()
                x = col_idx * cs + cs // 2
                y = row_idx * cs

                # 尝试匹配主路径编号
                match_main = pattern_main.match(cell)
                if match_main:
                    name = match_main.group(1)
                    idx = int(match_main.group(2))

                    if 0 <= idx <= 54:  # 主路径范围
                        main_path_data.append((row_idx, col_idx, name, idx, (x, y)))
                        print(f"[主路径{idx:2d}] ({row_idx:2d},{col_idx:2d}) {name}")
                    continue

                # 尝试匹配分支编号
                match_branch = pattern_branch.match(cell)
                if match_branch:
                    name = match_branch.group(1)
                    seq = int(match_branch.group(2))  # 分支内的格子序号（1-9）

                    # 暂存所有分支数据，稍后按位置分配到branch1/branch2
                    branch_raw_data.append((row_idx, col_idx, name, seq, (x, y)))
                    print(f"[分支?-{seq}]   ({row_idx:2d},{col_idx:2d}) {name}")
                    continue

                # 未匹配到的格子
                print(f"[警告] 未识别的格式: '{cell}' at ({row_idx},{col_idx})")

        # 根据位置将分支分配到branch1或branch2
        # 分支1（S级角色区）：右侧竖列（col >= 20）
        # 分支2（皮肤惊喜区）：左侧区域（col < 10 且 row < 5）
        branch1_data = []
        branch2_data = []

        print("\n开始分配分支...")
        for row, col, name, seq, coord in branch_raw_data:
            if col >= 20:  # 右侧 → 分支1
                branch1_data.append((row, col, name, seq, coord))
            else:  # 左侧 → 分支2
                branch2_data.append((row, col, name, seq, coord))

        # 按编号排序（编号代表走棋顺序）
        # 主路径：按数字编号排序（0, 1, 2, ..., 54）
        main_path_data.sort(key=lambda x: x[3])
        # 分支：按原序号排序（1, 2, 3, ..., 9）
        branch1_data.sort(key=lambda x: x[3])  # 按seq（原序号）排序
        branch2_data.sort(key=lambda x: x[3])  # 按seq（原序号）排序

        # 输出排序后的分支顺序
        print("\n分支1排序后（按原序号1-9）:")
        for i, (row, col, name, seq, coord) in enumerate(branch1_data):
            print(f"  B1-{i}: {name} (原序号{seq})")
        print("\n分支2排序后（按原序号1-9）:")
        for i, (row, col, name, seq, coord) in enumerate(branch2_data):
            print(f"  B2-{i}: {name} (原序号{seq})")

        print("\n" + "=" * 80)
        print(f"解析完成！主路径: {len(main_path_data)}格, 分支1: {len(branch1_data)}格, 分支2: {len(branch2_data)}格")
        print("=" * 80)

        # 步骤2：构建最终数据
        self.cell_positions = []
        self.cell_types = []
        self.cell_names = []  # 存储格子的原始名称（用于同行等需要具体角色的格子）

        def append_parsed_data(data_list, label="路径"):
            """辅助函数：添加已解析的数据"""
            count = 0
            for row, col, name, idx, coord in data_list:
                self.cell_positions.append(coord)
                self.cell_types.append(T.get(name, "apprentice_chest"))
                self.cell_names.append(name)  # 存储原始名称
                count += 1
            return count

        # 依次添加主路径、分支1、分支2
        main_count = append_parsed_data(main_path_data, "主路径")
        self.main_path_len = len(self.cell_types)  # 主路径长度（包含起点）
        b1_start = len(self.cell_types)
        b1_count = append_parsed_data(branch1_data, "分支1")
        b2_start = len(self.cell_types)
        b2_count = append_parsed_data(branch2_data, "分支2")

        self.total_cells = len(self.cell_types)

        # 创建格子编号映射数组（用于调试输出）
        # 主路径：使用原始编号（0-54）
        # 分支：使用 B1-X 或 B2-X 格式（X为0-based索引，对应原序号X+1）
        self.cell_numbers = []
        for item in main_path_data:
            self.cell_numbers.append(item[3])  # idx字段
        for i, item in enumerate(branch1_data):
            self.cell_numbers.append(f"B1-{i}")  # 使用enumerate索引
        for i, item in enumerate(branch2_data):
            self.cell_numbers.append(f"B2-{i}")  # 使用enumerate索引

        print(f"\n格子编号数组（共{len(self.cell_numbers)}个）:")
        for i, num in enumerate(self.cell_numbers):
            print(f"  [{i:2d}] 编号={num}, 类型={self.cell_types[i]}")

        # 分支元数据配置 - 基于新的索引
        self.branch_entries = {
            "s_character": {
                "name": "S级角色区(浔)",
                "entry_main_idx": 16,      # 学徒宝箱(6,19) [分支1入口 - 编号16]
                "skip_main_idx": 17,       # 翳同行(7,19) [跳过的格子]
                "exit_main_idx": 18,       # 勇者宝箱(8,19) [分支出口 - 编号18]
                "branch_start": b1_start,
                "branch_len": b1_count,
                "s_pos_in_branch": 0,     # 浔同行在分支第0位
                # "need_extra_roll_1": True,  # 已移除：S级角色必定获得，无需额外掷骰
            },
            "skin_surprise": {
                "name": "皮肤惊喜区",
                "entry_main_idx": 43,      # 学徒宝箱(4,4) [分支2入口 - 编号43]
                "skip_main_idx": 44,       # 海月同行(3,4) [跳过的格子]
                "exit_main_idx": 45,       # 迷迭棋盒(2,4) [分支出口 - 编号45]
                "branch_start": b2_start,
                "branch_len": b2_count,
            },
        }

    def _generate_permanent_board(self):
        """生成常驻棋盘布局（预留扩展）"""
        self.board_name = "常驻棋盘"
        self.board_type = "permanent"
        cs = self.cell_size

        T = {
            "apprentice": "apprentice_chest",
            "brave": "brave_chest",
            "mist30": "mist_box",
            "arcade": "arcade_blind",
            "roll_sleep": "roll_again",
        }

        # 简化的常驻棋盘（圆形布局）
        permanent_types = ["apprentice"] * 36 + ["brave"] * 12 + ["mist30"] * 6
        permanent_positions = []

        # 圆形路径布局
        center_x, center_y = 5 * cs, 5 * cs
        radius_base = 4 * cs

        for i in range(len(permanent_types)):
            angle = i * (360 / len(permanent_types)) * 3.14159 / 180
            r_var = radius_base * (1 + 0.3 * (i % 5) / 5)
            x = center_x + r_var * (1 if i < len(permanent_types) // 2 else -0.8) * ((i + 1) % 3 - 1)
            y = center_y + r_var * 0.7 * (1 if i % 2 == 0 else -1) * (0.5 + 0.5 * (i // 10) / 5)
            permanent_positions.append((x, y))

        self.cell_positions = permanent_positions
        self.cell_types = [T[t] for t in permanent_types]
        self.total_cells = len(self.cell_types)
        self.branch_entries = {}

    def _load_board_config(self, config):
        """加载外部棋盘配置"""
        self.board_name = config.get("name", "未知棋盘")
        self.board_type = config.get("type", "limited")
        self.cell_positions = config.get("positions", [])
        self.cell_types = config.get("types", [])
        self.total_cells = len(self.cell_types)
        self.branch_entries = config.get("branches", {})

    def get_main_path_idx(self, global_idx):
        """获取全局索引对应的主路径索引"""
        if global_idx < 55:
            return global_idx
        for bkey, bdata in self.branch_entries.items():
            bs = bdata["branch_start"]
            be = bs + bdata["branch_len"]
            if bs <= global_idx < be:
                return bdata["entry_main_idx"]
        return global_idx % 55

    def is_in_branch_zone(self, global_idx):
        """判断是否在分支区域内"""
        return global_idx >= 55

    def _get_cell_color(self, cell_key):
        """获取格子颜色"""
        from board_data import SKIN_SYSTEM
        if cell_key in SKIN_SYSTEM:
            return SKIN_SYSTEM[cell_key]["color"]
        return self.CELL_COLORS.get(cell_key, "#888")

    def _get_cell_icon(self, cell_key):
        """获取格子图标"""
        from board_data import SKIN_SYSTEM
        if cell_key in SKIN_SYSTEM:
            return SKIN_SYSTEM[cell_key]["icon"]
        return self.CELL_ICONS.get(cell_key, "")

    def _get_cell_name(self, cell_key):
        """获取格子短名称"""
        from board_data import SKIN_SYSTEM
        if cell_key in SKIN_SYSTEM:
            return SKIN_SYSTEM[cell_key]["short_name"]
        return self.CELL_NAMES.get(cell_key, "?")

    # ===== 旧版渲染代码已备注（v4.0）- 开始 =====
    if False:
        def _render_full_board(self):
            """完整渲染棋盘（全新引擎 v4.0）"""
        self._draw_background_layer()
        self._draw_grid_cells()
        self._draw_connection_paths()
        self._draw_branch_indicators()
        self._draw_player_piece()
        self._draw_dice_display()
        self._draw_board_header()
        self._draw_speed_badge()
        self._draw_legend()

    def _draw_background_layer(self):
        """绘制背景层"""
        if not self.cell_positions:
            return

        margin = self.cell_size // 2 + 15

        # 外边框阴影
        self.canvas.create_rectangle(
            self._ox(self.min_x) - margin + 4,
            self._oy(self.min_y) - margin + 4,
            self._ox(self.max_x) + margin + 4,
            self._oy(self.max_y) + margin + 4,
            fill="#d0c4a8", outline="", tags="bg_shadow"
        )

        # 主背景板
        self.canvas.create_rectangle(
            self._ox(self.min_x) - margin,
            self._oy(self.min_y) - margin,
            self._ox(self.max_x) + margin,
            self._oy(self.max_y) + margin,
            fill="#ede4d4", outline="#b8a882", width=3, tags="bg_main"
        )

        # 内边框装饰线
        inner_margin = margin - 6
        self.canvas.create_rectangle(
            self._ox(self.min_x) - inner_margin,
            self._oy(self.min_y) - inner_margin,
            self._ox(self.max_x) + inner_margin,
            self._oy(self.max_y) + inner_margin,
            fill="", outline="#d4c4a4", width=1, dash=(4, 2), tags="bg_inner"
        )

    def _draw_grid_cells(self):
        """绘制所有格子 - 增强版 v4.0"""
        half = self.cell_size // 2 - 2

        for idx, (cx, cy) in enumerate(self.cell_positions):
            cell_key = self.cell_types[idx]
            style = self.CELL_STYLES.get(cell_key, self.CELL_STYLES["mist_box"])

            px, py = self._ox(cx), self._oy(cy)
            x1, y1 = px - half, py - half
            x2, y2 = px + half, py + half

            is_special = cell_key in ("companion", "multi_surprise")
            is_branch_point = self._is_branch_related(idx)

            shadow_off = 3
            self.canvas.create_rectangle(
                x1 + shadow_off, y1 + shadow_off,
                x2 + shadow_off, y2 + shadow_off,
                fill="#aaa", outline="", tags=f"shadow_{idx}"
            )

            border_col = "#FFD700" if is_special else ("#E65100" if is_branch_point else style["border"])
            border_wid = 3 if is_special else (2 if is_branch_point else 2)

            shape_type = style["shape"]
            if shape_type == "round_rect":
                self._draw_round_rect(x1, y1, x2, y2, style["color"], border_col, border_wid, idx)
            elif shape_type == "diamond":
                self._draw_diamond(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "hexagon":
                self._draw_hexagon(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "oval":
                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=style["color"], outline=border_col, width=border_wid,
                    tags=f"cell_{idx}"
                )
            elif shape_type == "circle":
                r = int(half * 0.9)
                self.canvas.create_oval(
                    px - r, py - r, px + r, py + r,
                    fill=style["color"], outline=border_col, width=border_wid,
                    tags=f"cell_{idx}"
                )
            elif shape_type == "star":
                self._draw_star(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "triangle":
                self._draw_triangle(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "burst":
                self._draw_burst(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "shield":
                self._draw_shield(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "clothing":
                self._draw_clothing(px, py, half, style["color"], border_col, border_wid, idx)
            elif shape_type == "star8":
                self._draw_star8(px, py, half, style["color"], border_col, border_wid, idx)
            else:
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=style["color"], outline=border_col, width=border_wid,
                    tags=f"cell_{idx}"
                )

            if is_special:
                glow_r = half + 6
                self.canvas.create_oval(
                    px - glow_r, py - glow_r,
                    px + glow_r, py + glow_r,
                    outline=style["color"], width=2, dash=(4, 4),
                    tags=f"glow_{idx}"
                )

            num_font = ("Arial", max(6, min(8, self.cell_size // 5)))
            self.canvas.create_text(
                px, py - half + max(7, half // 2),
                text=str(idx + 1), font=num_font, fill="#555",
                tags=f"num_{idx}"
            )

            icon_size = max(9, min(14, self.cell_size // 3))
            text_color = style["text"]
            icon_y = py + max(2, half // 3)

            if cell_key == "companion":
                self.canvas.create_text(
                    px, icon_y,
                    text="\u2665", font=("Arial", icon_size + 2, "bold"),
                    fill=text_color, tags=f"icon_{idx}"
                )
            elif cell_key == "brave_chest":
                self.canvas.create_text(
                    px, icon_y,
                    text="\u2606", font=("Arial", icon_size + 1, "bold"),
                    fill=text_color, tags=f"icon_{idx}"
                )
            elif cell_key == "multi_surprise":
                self.canvas.create_text(
                    px, icon_y,
                    text="\u272A", font=("Arial", icon_size + 2, "bold"),
                    fill=text_color, tags=f"icon_{idx}"
                )
            else:
                short_name = style["short_name"]
                name_font = ("Microsoft YaHei", max(6, min(8, self.cell_size // 5)), "bold")
                self.canvas.create_text(
                    px, icon_y,
                    text=short_name[:2], font=name_font,
                    fill=text_color, tags=f"text_{idx}"
                )

    def _draw_round_rect(self, x1, y1, x2, y2, color, border, width, idx):
        """绘制圆角矩形"""
        r = 4
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    smooth=True, tags=f"cell_{idx}")

    def _draw_diamond(self, cx, cy, half, color, border, width, idx):
        """绘制菱形"""
        h = int(half * 0.85)
        points = [cx, cy - h, cx + h, cy, cx, cy + h, cx - h, cy]
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    tags=f"cell_{idx}")

    def _draw_hexagon(self, cx, cy, half, color, border, width, idx):
        """绘制六边形"""
        import math
        h = int(half * 0.85)
        points = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            x = cx + h * math.cos(angle)
            y = cy + h * math.sin(angle)
            points.extend([x, y])
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    smooth=False, tags=f"cell_{idx}")

    def _draw_star(self, cx, cy, half, color, border, width, idx):
        """绘制五角星"""
        import math
        outer_r = int(half * 0.9)
        inner_r = int(outer_r * 0.4)
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.extend([x, y])
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    tags=f"cell_{idx}")

    def _draw_triangle(self, cx, cy, half, color, border, width, idx):
        """绘制三角形"""
        h = int(half * 0.9)
        points = [cx, cy - h, cx + h, cy + h * 0.7, cx - h, cy + h * 0.7]
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    tags=f"cell_{idx}")

    def _draw_burst(self, cx, cy, half, color, border, width, idx):
        """绘制爆炸形（多角星）"""
        import math
        outer_r = int(half * 0.9)
        inner_r = int(outer_r * 0.5)
        points = []
        for i in range(16):
            angle = -math.pi / 2 + i * math.pi / 8
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.extend([x, y])
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    tags=f"cell_{idx}")

    def _draw_shield(self, cx, cy, half, color, border, width, idx):
        """绘制盾牌形"""
        w = int(half * 0.85)
        h_top = int(half * 0.6)
        h_bottom = int(half * 0.9)
        points = [
            cx - w, cy - h_top,
            cx + w, cy - h_top,
            cx + w, cy,
            cx, cy + h_bottom,
            cx - w, cy
        ]
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    smooth=True, tags=f"cell_{idx}")

    def _draw_clothing(self, cx, cy, half, color, border, width, idx):
        """绘制衣服形"""
        w = int(half * 0.75)
        h_top = int(half * 0.65)
        h_bottom = int(half * 0.85)
        points = [
            cx - w, cy - h_top,
            cx + w, cy - h_top,
            cx + w * 0.6, cy,
            cx + w * 0.8, cy + h_bottom,
            cx - w * 0.8, cy + h_bottom,
            cx - w * 0.6, cy
        ]
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    smooth=True, tags=f"cell_{idx}")

    def _draw_star8(self, cx, cy, half, color, border, width, idx):
        """绘制八角星（起点专用）"""
        import math
        outer_r = int(half * 0.95)
        inner_r = int(outer_r * 0.5)
        points = []
        for i in range(16):
            angle = -math.pi / 2 + i * math.pi / 8
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.extend([x, y])
        self.canvas.create_polygon(points, fill=color, outline=border, width=width,
                                    tags=f"cell_{idx}")
        inner_r2 = int(outer_r * 0.3)
        self.canvas.create_oval(
            cx - inner_r2, cy - inner_r2, cx + inner_r2, cy + inner_r2,
            fill="#fff", outline=border, width=1, tags=f"cell_center_{idx}"
        )

    def _is_branch_related(self, idx):
        """判断索引是否与分支相关"""
        for bdata in self.branch_entries.values():
            if idx in (bdata["entry_main_idx"], bdata["skip_main_idx"], bdata["exit_main_idx"]):
                return True
        return False

    def _draw_connection_paths(self):
        """绘制路径连接线"""
        main_len = 55

        for i in range(min(main_len - 1, len(self.cell_positions) - 1)):
            x1, y1 = self.cell_positions[i]
            x2, y2 = self.cell_positions[i + 1]

            is_important = (self.cell_types[i] == "companion" or
                           self.cell_types[i + 1] == "companion")
            line_color = "#888" if is_important else "#ccc"
            line_width = 2 if is_important else 1

            self.canvas.create_line(
                self._ox(x1), self._oy(y1),
                self._ox(x2), self._oy(y2),
                fill=line_color, width=line_width, tags="path_main"
            )

        for bkey, bdata in self.branch_entries.items():
            start = bdata["branch_start"]
            end = start + bdata["branch_len"]

            entry_pos = self.cell_positions[bdata["entry_main_idx"]]
            branch_start_pos = self.cell_positions[start]
            self.canvas.create_line(
                self._ox(entry_pos[0]), self._oy(entry_pos[1]),
                self._ox(branch_start_pos[0]), self._oy(branch_start_pos[1]),
                fill="#E53935", width=2, dash=(5, 3), tags=f"path_entry_{bkey}"
            )

            exit_pos = self.cell_positions[bdata["exit_main_idx"]]
            branch_end_pos = self.cell_positions[end - 1]
            self.canvas.create_line(
                self._ox(branch_end_pos[0]), self._oy(branch_end_pos[1]),
                self._ox(exit_pos[0]), self._oy(exit_pos[1]),
                fill="#43A047", width=2, dash=(5, 3), tags=f"path_exit_{bkey}"
            )

            for i in range(start, end - 1):
                x1, y1 = self.cell_positions[i]
                x2, y2 = self.cell_positions[i + 1]
                self.canvas.create_line(
                    self._ox(x1), self._oy(y1),
                    self._ox(x2), self._oy(y2),
                    fill="#FB8C00", width=1, dash=(3, 2), tags=f"path_inner_{bkey}"
                )

    def _draw_branch_indicators(self):
        """绘制分支标记指示器"""
        for bkey, bdata in self.branch_entries.items():
            entry_idx = bdata["entry_main_idx"]
            if entry_idx < len(self.cell_positions):
                cx, cy = self.cell_positions[entry_idx]
                px, py = self._ox(cx), self._oy(cy)
                marker_r = self.cell_size // 2 + 8
                self.canvas.create_oval(
                    px - marker_r, py - marker_r,
                    px + marker_r, py + marker_r,
                    outline="#E53935", width=2, dash=(4, 2),
                    tags=f"marker_entry_{bkey}"
                )
                self.canvas.create_text(
                    px + marker_r + 10, py,
                    text="\u2192", font=("Arial", 10, "bold"), fill="#E53935",
                    tags=f"arrow_entry_{bkey}"
                )

            exit_idx = bdata["exit_main_idx"]
            if exit_idx < len(self.cell_positions):
                cx, cy = self.cell_positions[exit_idx]
                px, py = self._ox(cx), self._oy(cy)
                marker_r = self.cell_size // 2 + 8
                self.canvas.create_oval(
                    px - marker_r, py - marker_r,
                    px + marker_r, py + marker_r,
                    outline="#43A047", width=2, dash=(4, 2),
                    tags=f"marker_exit_{bkey}"
                )
                self.canvas.create_text(
                    px - marker_r - 10, py,
                    text="\u2190", font=("Arial", 10, "bold"), fill="#43A047",
                    tags=f"arrow_exit_{bkey}"
                )

    def _draw_player_piece(self):
        """绘制玩家棋子"""
        for pid in self.piece_ids:
            self.canvas.delete(pid)
        self.piece_ids = []

        if not self.cell_positions or self.piece_pos_idx >= len(self.cell_positions):
            return

        cx, cy = self.cell_positions[self.piece_pos_idx]
        px, py = self._ox(cx), self._oy(cy)
        r = self.cell_size // 3.0

        for i in range(3, 0, -1):
            glow_r = r + i * 4
            glow_colors = ["#FFF59D", "#FFEE58", "#FFD600"]
            glow = self.canvas.create_oval(
                px - glow_r, py - glow_r,
                px + glow_r, py + glow_r,
                fill="", outline=glow_colors[i-1], width=1, tags="piece"
            )
            self.piece_ids.append(glow)

        shadow = self.canvas.create_oval(
            px - r + 3, py - r + 3,
            px + r + 3, py + r + 3,
            fill="#000", outline="", stipple="gray50", tags="piece"
        )
        self.piece_ids.append(shadow)

        piece_outer = self.canvas.create_oval(
            px - r, py - r,
            px + r, py + r,
            fill="#D32F2F", outline="#FFF", width=2, tags="piece"
        )
        self.piece_ids.append(piece_outer)

        inner_r = r * 0.65
        piece_inner = self.canvas.create_oval(
            px - inner_r, py - inner_r,
            px + inner_r, py + inner_r,
            fill="#EF5350", outline="", tags="piece"
        )
        self.piece_ids.append(piece_inner)

        mark = self.canvas.create_text(
            px, py, text="\u2605",
            font=("Arial", int(r * 0.85), "bold"), fill="#FFD700", tags="piece"
        )
        self.piece_ids.append(mark)

        for pid in self.piece_ids:
            self.canvas.tag_raise(pid)

    def _draw_dice_display(self):
        """绘制骰子显示面板 - 右上角"""
        # 计算右上角位置
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100:
            canvas_w = self.canvas_w

        dx = canvas_w - 85  # 右上角位置
        dy = 10
        dw, dh = 70, 75

        self.canvas.create_rectangle(
            dx + 4, dy + 4, dx + dw + 4, dy + dh + 4,
            fill="#bbb", outline="", tags="dice_bg_shadow"
        )

        self.canvas.create_rectangle(
            dx, dy, dx + dw, dy + dh,
            fill="#FFF8E1", outline="#8D6E63", width=2, tags="dice_bg"
        )

        self.canvas.create_rectangle(
            dx + 5, dy + 5, dx + dw - 5, dy + dh - 5,
            fill="", outline="#FFD700", width=1, tags="dice_border"
        )

        self.dice_display_id = self.canvas.create_text(
            dx + dw // 2, dy + 28,
            text="?", font=("Arial", 26, "bold"), fill="#BF360C", tags="dice_num"
        )

        self.dice_text_id = self.canvas.create_text(
            dx + dw // 2, dy + 58,
            text="骰子",
            font=("Microsoft YaHei", 11, "bold"), fill="#8D6E63", tags="dice_label"
        )

    def _draw_board_header(self):
        """绘制棋盘标题栏 - 放在右侧图例区域顶部"""
        board_right = self._ox(self.max_x) + self.cell_size // 2 + 12
        actual_w = self.canvas.winfo_width()
        if actual_w < 50:
            actual_w = self.canvas_w

        legend_x = board_right + 8
        legend_right = actual_w - 8
        title_y = self._oy(self.min_y) - 20

        if legend_right - legend_x < 90:
            return

        type_icons = {"limited": "\u2605", "permanent": "\u2665"}
        icon = type_icons.get(self.board_type, "")
        title_text = f"{icon} {self.board_name}" if icon else self.board_name

        self.canvas.create_rectangle(
            legend_x, title_y - 14,
            legend_right, title_y + 14,
            fill="#FFFDE7", outline="#FFD700", width=1, tags="title_bg"
        )

        self.canvas.create_text(
            (legend_x + legend_right) / 2,
            title_y,
            text=title_text,
            font=("Microsoft YaHei", 12, "bold"), fill="#5D4037", tags="title_text"
        )

    def _draw_speed_badge(self):
        """绘制速度指示徽章"""
        speed_labels = {
            self.SPEED_SLOW: "0.5x",
            self.SPEED_NORMAL: "1x",
            self.SPEED_FAST: "2x",
            self.SPEED_VERY_FAST: "4x",
            self.SPEED_SKIP: "跳过",
        }
        current_speed = self.speed_mode.get()
        speed_text = speed_labels.get(current_speed, "1x")

        badge_x = self._ox(self.min_x) + 50
        badge_y = 18

        self.canvas.create_rectangle(
            badge_x - 28, badge_y - 10,
            badge_x + 28, badge_y + 10,
            fill="#E3F2FD", outline="#1976D2", width=1, tags="speed_badge"
        )

        self.canvas.create_text(
            badge_x, badge_y,
            text=speed_text,
            font=("Arial", 10, "bold"), fill="#1565C0", tags="speed_label"
        )

    def _draw_legend(self):
        """绘制图例 - 右侧显示所有格子类型的说明（紧凑版）"""
        board_right = self._ox(self.max_x) + self.cell_size // 2 + 12
        board_top = self._oy(self.min_y) + 10

        actual_w = self.canvas.winfo_width()
        actual_h = self.canvas.winfo_height()
        if actual_w < 50:
            actual_w = self.canvas_w
        if actual_h < 50:
            actual_h = self.canvas_h

        legend_x = board_right + 8
        legend_y = max(board_top, 10)
        legend_right = actual_w - 8
        legend_bottom = min(actual_h - 6, self._oy(self.max_y) + self.cell_size // 2 + 4)

        if legend_right - legend_x < 85 or legend_bottom - legend_y < 60:
            return

        self.canvas.create_rectangle(
            legend_x, legend_y,
            legend_right, legend_bottom,
            fill="#FFFDE7", outline="#F9A825", width=1,
            tags="legend_bg"
        )

        title_y = legend_y + 11
        self.canvas.create_text(
            (legend_x + legend_right) / 2, title_y,
            text="图例 Legend",
            font=("Microsoft YaHei", 8, "bold"), fill="#F57F17",
            tags="legend_title"
        )

        cell_types_in_board = sorted(set(self.cell_types))
        cols = 2
        available_width = legend_right - legend_x - 14
        col_width = available_width // cols
        item_size = 13
        text_offset = item_size + 5
        items_per_col = (len(cell_types_in_board) + cols - 1) // cols

        for i, cell_key in enumerate(cell_types_in_board):
            style = self.CELL_STYLES.get(cell_key)
            if not style:
                continue

            col = i // items_per_col
            row = i % items_per_col

            item_x = legend_x + 7 + col * col_width
            item_y = title_y + 15 + row * (item_size + 3)

            half_s = item_size // 2 - 1
            cx, cy = item_x + half_s, item_y + half_s

            shape_type = style["shape"]
            if shape_type == "diamond":
                h = int(half_s * 0.7)
                points = [cx, cy - h, cx + h, cy, cx, cy + h, cx - h, cy]
                self.canvas.create_polygon(points, fill=style["color"],
                                            outline=style["border"], width=1,
                                            tags=f"legend_{cell_key}")
            elif shape_type == "star8":
                import math
                outer_r = int(half_s * 0.85)
                inner_r = int(outer_r * 0.5)
                pts = []
                for j in range(16):
                    angle = -math.pi / 2 + j * math.pi / 8
                    r = outer_r if j % 2 == 0 else inner_r
                    x = cx + r * math.cos(angle)
                    y = cy + r * math.sin(angle)
                    pts.extend([x, y])
                self.canvas.create_polygon(pts, fill=style["color"],
                                            outline=style["border"], width=1,
                                            tags=f"legend_{cell_key}")
            elif shape_type in ("oval", "circle"):
                r = int(half_s * 0.8)
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                         fill=style["color"], outline=style["border"],
                                         width=1, tags=f"legend_{cell_key}")
            elif shape_type == "hexagon":
                import math
                h = int(half_s * 0.75)
                pts = []
                for j in range(6):
                    angle = math.pi / 6 + j * math.pi / 3
                    x = cx + h * math.cos(angle)
                    y = cy + h * math.sin(angle)
                    pts.extend([x, y])
                self.canvas.create_polygon(pts, fill=style["color"],
                                            outline=style["border"], width=1,
                                            tags=f"legend_{cell_key}")
            elif shape_type == "triangle":
                h = int(half_s * 0.75)
                pts = [cx, cy - h, cx + h, cy + h * 0.65, cx - h, cy + h * 0.65]
                self.canvas.create_polygon(pts, fill=style["color"],
                                            outline=style["border"], width=1,
                                            tags=f"legend_{cell_key}")
            elif shape_type == "star":
                import math
                outer_r = int(half_s * 0.85)
                inner_r = int(outer_r * 0.4)
                pts = []
                for j in range(10):
                    angle = -math.pi / 2 + j * math.pi / 5
                    r = outer_r if j % 2 == 0 else inner_r
                    x = cx + r * math.cos(angle)
                    y = cy + r * math.sin(angle)
                    pts.extend([x, y])
                self.canvas.create_polygon(pts, fill=style["color"],
                                            outline=style["border"], width=1,
                                            tags=f"legend_{cell_key}")
            else:
                self.canvas.create_rectangle(
                    item_x, item_y, item_x + item_size, item_y + item_size,
                    fill=style["color"], outline=style["border"], width=1,
                    tags=f"legend_{cell_key}"
                )

            label_x = item_x + text_offset
            label_cy = cy
            short_name = style["short_name"]
            desc_text = f"{short_name} - {style.get('desc', '')[:8]}"
            self.canvas.create_text(
                label_x, label_cy,
                text=short_name,
                font=("Microsoft YaHei", 7), fill="#424242",
                anchor=tk.W, tags=f"legend_text_{cell_key}"
            )
    # ===== 旧版渲染代码已备注（v4.0）- 结束 =====

    def _render_full_board(self):
        """渲染棋盘（全新引擎 v5.0 - 简洁版）"""
        self.canvas.delete("all")

        if not self.cell_positions:
            return

        cs = self.cell_size
        half = cs // 2

        for idx, (pos, cell_type) in enumerate(zip(self.cell_positions, self.cell_types)):
            x, y = pos
            ox = x + self.offset_x
            oy = y + self.offset_y

            style = self.CELL_STYLES.get(cell_type, self.CELL_STYLES["apprentice_chest"])
            color = style["color"]
            border = style["border"]

            x1, y1 = ox - half + 2, oy - half + 2
            x2, y2 = ox + half - 2, oy + half - 2

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color, outline=border, width=2,
                tags=f"cell_{idx}"
            )

            short_name = style.get("short_name", "?")
            font_size = max(6, min(9, cs // 4))
            self.canvas.create_text(
                ox, oy,
                text=short_name,
                font=("Microsoft YaHei", font_size, "bold"),
                fill=style.get("text", "#fff"),
                tags=f"text_{idx}"
            )

            # 格子编号：起点特殊标记
            if idx == 0:
                num_text = "0(起)"
                num_color = "#4CAF50"  # 绿色标记起点
            elif idx == self.main_path_len - 1:
                num_text = f"{idx}(终)"  # 循环结束点
                num_color = "#F44336"  # 红色标记终点
            else:
                num_text = str(idx)
                num_color = "#666"

            num_font = max(5, cs // 5)
            self.canvas.create_text(
                ox, oy + half - 4,
                text=num_text,
                font=("Arial", num_font),
                fill=num_color,
                tags=f"num_{idx}"
            )

        if 0 <= self.piece_pos_idx < len(self.cell_positions):
            px, py = self.cell_positions[self.piece_pos_idx]
            px += self.offset_x
            py += self.offset_y

            piece_r = half - 3
            self.canvas.create_oval(
                px - piece_r, py - piece_r,
                px + piece_r, py + piece_r,
                fill="#FF5722", outline="#BF360C", width=3,
                tags="piece"
            )
            self.canvas.create_text(
                px, py,
                text="\u265E",
                font=("Arial", int(piece_r * 0.8), "bold"),
                fill="#fff",
                tags="piece_text"
            )

        # 绘制骰子显示面板
        self._draw_dice_display()

        # 绘制棋盘名称（右侧）
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100:
            canvas_w = self.canvas_w

        name_x = canvas_w - 85
        name_y = 95  # 骰子下方

        # 棋盘名称背景
        self.canvas.create_rectangle(
            name_x - 5, name_y - 5,
            name_x + 75, name_y + 25,
            fill="#E3F2FD", outline="#1976D2", width=1, tags="board_name_bg"
        )

        # 棋盘名称文字
        board_short = self.board_name.replace("限定棋盘(", "").replace(")", "") if "限定" in self.board_name else self.board_name
        self.canvas.create_text(
            name_x + 35, name_y + 10,
            text=board_short,
            font=("Microsoft YaHei", 10, "bold"), fill="#1565C0",
            tags="board_name"
        )

    def animate_roll(self, dice_value, target_cell_key, callback, target_idx_override=None,
                     branch_exit_info=None):
        """
        完整掷骰动画流程（支持5档速度）
        阶段1: 骰子数字滚动
        阶段2: 棋子逐步移动
        阶段3: 落格高亮闪烁

        参数:
            dice_value: 骰子点数
            target_cell_key: 目标格子类型（用于显示）
            callback: 动画结束回调
            target_idx_override: 强制指定的目标索引（用于分支进入等特殊情况）
                             如果为None，则自动计算
            branch_exit_info: 离开分支时的信息字典（可选）
                {
                    'branch_end': 分支末尾全局索引 (如63或72),
                    'exit_main_idx': 主路径出口索引 (如18或45),
                    'branch_key': 分支标识 (如's_character'或'skin_surprise')
                }
        """
        if self.is_animating:
            return
        self.is_animating = True

        # 调试日志：记录所有关键参数
        print(f"\n[animate_roll] === 开始动画 ===")
        print(f"[animate_roll] dice_value={dice_value}, target_cell_key={target_cell_key}")
        print(f"[animate_roll] target_idx_override={target_idx_override}")
        print(f"[animate_roll] branch_exit_info={branch_exit_info}")
        print(f"[animate_roll] 当前piece_pos_idx={self.piece_pos_idx}")

        # 使用强制目标位置或自动计算
        if target_idx_override is not None:
            target_idx = target_idx_override
            current_in_branch = (self.piece_pos_idx >= 55)  # 当前是否在分支内
            is_leaving_branch = (current_in_branch and target_idx < 55 and branch_exit_info)

            if target_idx >= 55:
                # 目标在分支内：使用完整的骰子点数（包括从主路径进入分支）
                steps = dice_value
                print(f"\n[动画] 分支移动: {self.piece_pos_idx} → {target_idx}, 步数={steps}")
            elif is_leaving_branch:
                # 从分支离开到主路径：使用完整的骰子点数（两段式移动）
                steps = dice_value
                print(f"\n[动画] 离开分支: {self.piece_pos_idx}(分支) → {target_idx}(主路径), 步数={steps}")
                print(f"[动画] 出口信息: branch_end={branch_exit_info['branch_end']}, exit_main={branch_exit_info['exit_main_idx']}")
            else:
                # 其他强制位置（一般不应该发生）
                steps = 1
                print(f"\n[动画] 强制跳转到: {target_idx}（步数={steps}）")
        else:
            target_idx = self._cycle_pos(self.piece_pos_idx, dice_value)
            steps = dice_value

        # 详细走棋日志输出
        print("\n" + "=" * 60)
        print(f"[掷骰] 点数={dice_value}")
        print(f"  当前位置索引: {self.piece_pos_idx}")
        print(f"  目标位置索引: {target_idx}")

        # 输出当前格子的完整信息（编号+类型+名称）
        if hasattr(self, 'cell_numbers') and self.piece_pos_idx < len(self.cell_numbers):
            current_num = self.cell_numbers[self.piece_pos_idx]
            current_type = self.cell_types[self.piece_pos_idx] if self.piece_pos_idx < len(self.cell_types) else "N/A"
            print(f"  当前格子: 编号={current_num}, 类型={current_type}")
        else:
            print(f"  当前格子: 索引={self.piece_pos_idx}, 类型={self.cell_types[self.piece_pos_idx] if self.piece_pos_idx < len(self.cell_types) else 'N/A'}")

        # 输出目标格子的完整信息
        if hasattr(self, 'cell_numbers') and target_idx < len(self.cell_numbers):
            target_num = self.cell_numbers[target_idx]
            target_type = self.cell_types[target_idx] if target_idx < len(self.cell_types) else "N/A"
            print(f"  目标格子: 编号={target_num}, 类型={target_type}")
        else:
            print(f"  目标格子: 索引={target_idx}, 类型={self.cell_types[target_idx] if target_idx < len(self.cell_types) else 'N/A'}")

        # 输出将要经过的所有格子（包含编号和类型）
        path_cells = []
        temp_idx = self.piece_pos_idx

        # 判断是否为分支相关移动（进入分支 + 分支内移动 + 离开分支）
        # 注意：is_leaving_branch 和 branch_exit_info 可能在前面的 if 块中定义
        # 安全处理：同时检查两个变量是否存在
        is_leaving_branch_safe = False
        has_valid_exit_info = False
        
        if ('is_leaving_branch' in dir() and is_leaving_branch and 
            'branch_exit_info' in dir() and branch_exit_info):
            is_leaving_branch_safe = True
            has_valid_exit_info = True
        elif 'is_leaving_branch' in dir() and is_leaving_branch:
            # is_leaving_branch=True 但 branch_exit_info 缺失或不完整
            print(f"\n[警告] is_leaving_branch=True 但 branch_exit_info 缺失或不完整")
            print(f"[警告] 将降级为普通分支移动（无两段式离开逻辑）")

        is_branch_move = (
            (target_idx_override is not None and target_idx_override >= 55) or  # 目标在分支内
            is_leaving_branch_safe  # 从分支离开到主路径（安全版本）
        )

        # 离开分支时的辅助变量
        # 注意：必须在函数开头初始化所有变量，避免UnboundLocalError
        steps_in_branch_to_exit = 0  # 段1: 在分支内需要走的步数（到达末尾）
        branch_end_local = 0         # 分支末尾索引（局部副本）
        exit_main_local = 0          # 主路径出口索引（局部副本）

        if is_leaving_branch_safe and has_valid_exit_info:
            branch_end_local = branch_exit_info['branch_end']
            exit_main_local = branch_exit_info['exit_main_idx']
            steps_in_branch_to_exit = branch_end_local - temp_idx  # 在分支内需要走的步数（不含跳转步）
            print(f"\n[路径预计算] 离开分支两段式移动:")
            print(f"[路径预计算] 当前={temp_idx}, 分支末尾={branch_end_local}, 出口={exit_main_local}")
            print(f"[路径预计算] 段1步数(分支内)={steps_in_branch_to_exit}, 跳转步=1, 段2步数(主路径)={steps - steps_in_branch_to_exit - 1}")

        for i in range(steps):
            if is_branch_move:
                if temp_idx < 55 and target_idx >= 55:
                    # 从主路径进入分支：计算每一步的位置
                    # 恢复+1：因为target_global_pos已经修正为branch_start+dv-1，所以这里需要+1来补偿
                    temp_idx = target_idx_override - steps + i + 1
                    print(f"\n[路径详情] 第{i+1}步: 进入分支，位置={temp_idx}")
                elif is_leaving_branch_safe and has_valid_exit_info:
                    # 从分支离开到主路径：两段式移动（简化版逻辑）
                    # 使用步数索引i直接判断当前阶段，无需状态变量has_jumped_to_exit
                    if i < steps_in_branch_to_exit:
                        # 段1: 在分支内走到末尾（包括到达末尾的那一步）
                        temp_idx = temp_idx + 1
                        print(f"\n[路径详情] 第{i+1}步: 分支内移动，位置={temp_idx}（段1: {i+1}/{steps_in_branch_to_exit}）")

                        # 仅在段1最后一步打印提示（用于日志可读性）
                        if i == steps_in_branch_to_exit - 1 and temp_idx >= branch_end_local:
                            print(f"[路径详情] → 到达分支末尾{temp_idx}，下步将跳转到出口")
                    elif i == steps_in_branch_to_exit:
                        # 关键一步：跳转到出口（段1结束，段2开始）
                        temp_idx = exit_main_local
                        print(f"\n[路径详情] 第{i+1}步: 跳转到出口，位置={temp_idx}（段2开始）")
                    else:
                        # 段2: 在主路径上继续移动（i > steps_in_branch_to_exit）
                        temp_idx = self._next_pos(temp_idx)
                        step_in_phase2 = i - steps_in_branch_to_exit
                        print(f"\n[路径详情] 第{i+1}步: 主路径移动，位置={temp_idx}（段2: 第{step_in_phase2}步）")
                elif temp_idx >= 55:
                    # 已在分支内：简单的+1
                    temp_idx = temp_idx + 1
            else:
                # 主路径移动：使用_next_pos（处理循环等逻辑）
                temp_idx = self._next_pos(temp_idx)
            cell_info = ""
            if hasattr(self, 'cell_numbers') and temp_idx < len(self.cell_numbers):
                num = self.cell_numbers[temp_idx]
                typ = self.cell_types[temp_idx] if temp_idx < len(self.cell_types) else "?"
                cell_info = f"{num}({typ})"
            elif temp_idx < len(self.cell_types):
                cell_info = f"{temp_idx}({self.cell_types[temp_idx]})"
            else:
                cell_info = "?"
            path_cells.append(cell_info)

        print(f"  经过路径: {' -> '.join(map(str, path_cells))}")
        print("=" * 60 + "\n")

        def phase1_dice_scroll(count=0):
            total_rolls = 18
            if count < total_rolls:
                random_val = random.randint(1, 6)
                if self.dice_display_id:
                    self.canvas.itemconfig(self.dice_display_id, text=str(random_val))

                scroll_delay = max(30, 100 - count * 5)
                self.canvas.after(
                    self._delay(scroll_delay),
                    lambda: phase1_dice_scroll(count + 1)
                )
            else:
                if self.dice_display_id:
                    self.canvas.itemconfig(self.dice_display_id, text=str(dice_value))
                self.canvas.after(
                    self._delay(300),
                    lambda: phase2_move_piece(target_idx, 0)
                )

        def phase2_move_piece(target, step):
            if step < steps:
                # 判断是否分支移动
                if is_branch_move:
                    if self.piece_pos_idx < 55 and target_idx >= 55:
                        # 从主路径进入分支：第一步到达分支起点
                        # 恢复+1：与路径计算保持一致（target_global_pos已修正）
                        current_in_branch = target_idx_override - steps + step + 1
                        self.piece_pos_idx = current_in_branch
                    elif is_leaving_branch_safe and has_valid_exit_info:
                        # 从分支离开到主路径：两段式移动（与路径计算逻辑完全一致）
                        # 使用步数索引step直接判断当前阶段，无需状态变量
                        if step < steps_in_branch_to_exit:
                            # 段1: 在分支内走到末尾（包括到达末尾的那一步）
                            self.piece_pos_idx = self.piece_pos_idx + 1
                        elif step == steps_in_branch_to_exit:
                            # 关键一步：跳转到出口（段1结束，段2开始）
                            self.piece_pos_idx = exit_main_local
                        else:
                            # 段2: 在主路径上继续移动（step > steps_in_branch_to_exit）
                            self.piece_pos_idx = self._next_pos(self.piece_pos_idx)
                    elif is_leaving_branch_safe and not has_valid_exit_info:
                        # 异常情况：标记为离开分支但缺少出口信息
                        # 降级处理：如果还在分支内就简单+1，否则使用主路径逻辑
                        if self.piece_pos_idx >= 55:
                            print(f"[警告-phase2] 缺少出口信息，在分支内简单+1: {self.piece_pos_idx}")
                            self.piece_pos_idx = self.piece_pos_idx + 1
                        else:
                            print(f"[警告-phase2] 缺少出口信息且不在分支内，使用主路径逻辑")
                            self.piece_pos_idx = self._next_pos(self.piece_pos_idx)
                    elif self.piece_pos_idx >= 55:
                        # 已在分支内：简单+1
                        self.piece_pos_idx = self.piece_pos_idx + 1
                else:
                    # 主路径：使用_next_pos
                    self.piece_pos_idx = self._next_pos(self.piece_pos_idx)

                # 确保位置不超出范围（安全检查）
                if self.piece_pos_idx >= len(self.cell_positions):
                    print(f"[警告] phase2: 位置{self.piece_pos_idx}超出范围，限制为{target}")
                    self.piece_pos_idx = target

                self._draw_player_piece()

                if step % 3 == 0:
                    self._animate_piece_flash()

                move_delay = 120 if step < steps - 1 else 160
                self.canvas.after(
                    self._delay(move_delay),
                    lambda: phase2_move_piece(target, step + 1)
                )
            else:
                # 动画结束：强制设置最终位置（确保正确）
                if target_idx_override is not None and self.piece_pos_idx != target_idx_override:
                    print(f"\n[动画结束] 修正位置: {self.piece_pos_idx} → {target_idx_override}（强制对齐）")
                    self.piece_pos_idx = target_idx_override
                    self._draw_player_piece()

                self.canvas.after(
                    self._delay(200),
                    lambda: phase3_highlight_flash(target, 0)
                )

        def phase3_highlight_flash(tidx, flash_count):
            try:
                if self.highlight_id:
                    self.canvas.delete(self.highlight_id)
                    self.highlight_id = None

                total_flashes = 10
                if flash_count < total_flashes:
                    # 确保索引有效
                    if tidx >= len(self.cell_positions):
                        print(f"[警告] phase3: 目标索引{tidx}超出范围({len(self.cell_positions)})，跳过高亮")
                        self.canvas.after(
                            self._delay(140),
                            lambda: phase3_highlight_flash(tidx, flash_count + 1)
                        )
                        return

                    cx, cy = self.cell_positions[tidx]
                    px, py = self._ox(cx), self._oy(cy)
                    highlight_radius = self.cell_size // 2 + 7

                    flash_colors = ["#FFD700", "#FF5252", "#00E676", "#FFD700"]
                    current_color = flash_colors[flash_count % len(flash_colors)]

                    if flash_count % 2 == 0:
                        self.highlight_id = self.canvas.create_oval(
                            px - highlight_radius, py - highlight_radius,
                            px + highlight_radius, py + highlight_radius,
                            outline=current_color, width=3, tags="highlight"
                        )

                    self.canvas.after(
                        self._delay(140),
                        lambda: phase3_highlight_flash(tidx, flash_count + 1)
                    )
                else:
                    # 最终高亮
                    if tidx < len(self.cell_positions):
                        cx, cy = self.cell_positions[tidx]
                        px, py = self._ox(cx), self._oy(cy)
                        final_radius = self.cell_size // 2 + 6
                        self.highlight_id = self.canvas.create_oval(
                            px - final_radius, py - final_radius,
                            px + final_radius, py + final_radius,
                            outline="#D32F2F", width=3, tags="highlight_final"
                        )
                    else:
                        print(f"[警告] phase3最终: 目标索引{tidx}超出范围，跳过最终高亮")

                    self.is_animating = False
                    callback()
            except Exception as e:
                print(f"[错误] phase3_highlight_flash异常: {e}")
                print(f"[错误] tidx={tidx}, flash_count={flash_count}, cell_positions长度={len(self.cell_positions) if hasattr(self, 'cell_positions') else 'N/A'}")
                # 确保无论如何都重置动画状态
                self.is_animating = False
                try:
                    callback()
                except Exception as cb_err:
                    print(f"[错误] callback执行失败: {cb_err}")

        phase1_dice_scroll()

    def _animate_piece_flash(self):
        """棋子移动时的闪烁效果"""
        if not self.piece_ids:
            return

        for pid in self.piece_ids[-3:]:
            try:
                current_fill = self.canvas.itemcget(pid, "fill")
                if current_fill and current_fill != "":
                    self.canvas.itemconfig(pid, fill="#FFEB3B")
                    self.canvas.after(60, lambda p=pid: self._restore_piece_color(p))
            except Exception:
                pass

    def _restore_piece_color(self, item_id):
        """恢复棋子颜色"""
        try:
            if item_id in self.piece_ids:
                idx = self.piece_ids.index(item_id)
                if idx == len(self.piece_ids) - 3:
                    self.canvas.itemconfig(item_id, fill="#D32F2F")
                elif idx == len(self.piece_ids) - 2:
                    self.canvas.itemconfig(item_id, fill="#EF5350")
        except Exception:
            pass

    def reset_board(self):
        """重置棋盘状态"""
        self.piece_pos_idx = 0

        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None

        if self.dice_display_id:
            self.canvas.itemconfig(self.dice_display_id, text="?")

        self.canvas.delete("highlight")
        self.canvas.delete("highlight_final")
        self._draw_player_piece()

    @classmethod
    def get_available_boards(cls):
        """获取可用棋盘列表"""
        return [
            {
                "id": "limited_xun",
                "name": "限定棋盘(浔)",
                "type": "limited",
                "description": "限时角色浔专属棋盘，含S级角色和皮肤分支",
            },
            {
                "id": "permanent",
                "name": "常驻棋盘",
                "type": "permanent",
                "description": "常驻奖励棋盘，基础奖励为主（开发中）",
            },
        ]

    @classmethod
    def get_available_speeds(cls):
        """获取可用速度列表"""
        return [
            (cls.SPEED_SLOW, "0.5x 慢速"),
            (cls.SPEED_NORMAL, "1x 正常"),
            (cls.SPEED_FAST, "2x 快速"),
            (cls.SPEED_VERY_FAST, "4x 极快"),
            (cls.SPEED_SKIP, "跳过"),
        ]

    def switch_board(self, board_id):
        """切换棋盘"""
        self.canvas.delete("all")

        if board_id == "permanent":
            self._generate_permanent_board()
        else:
            self._generate_limited_board()

        self._calc_canvas_size()
        self.canvas.config(width=self.canvas_w, height=self.canvas_h)

        self.piece_pos_idx = 0
        self.highlight_id = None
        self.dice_display_id = None
        self.dice_text_id = None

        self._render_full_board()


class RewardPopup(tk.Toplevel):
    """获得物品弹窗"""

    def __init__(self, parent, rewards, gift_result=None, pity_event=None):
        super().__init__(parent)
        self.title("获得物品")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(bg="#FFF")

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + (pw - 400) // 2
        y = py + (ph - 380) // 2
        self.geometry(f"+{x}+{y}")

        title_bar = tk.Frame(self, bg="#FF6B35", height=48)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="\u2728 获得物品 \u2728",
                  font=("Microsoft YaHei", 15, "bold"),
                  fg="#FFF", bg="#FF6B35").pack(expand=True)

        content = tk.Frame(self, bg="#FAFAFA")
        content.pack(fill=tk.BOTH, expand=True, padx=18, pady=12)

        if pity_event:
            msg = "变格触发!" if pity_event == "variant" else "硬保底!"
            tk.Label(content, text=f"\u26A0\uFE0F {msg}",
                      font=("Microsoft YaHei", 13, "bold"),
                      fg="#FF4500", bg="#FAFAFA").pack(pady=(0, 12))

        all_items = list(rewards)
        if gift_result:
            all_items.append(("gift", gift_result))

        for rtype, data in all_items:
            self._render_item_row(content, rtype, data)

        btn_area = tk.Frame(self, bg="#FFF")
        btn_area.pack(fill=tk.X, padx=18, pady=(0, 16))
        tk.Button(btn_area, text="确定", command=self.destroy,
                   font=("Microsoft YaHei", 12, "bold"), bg="#4A90D9", fg="white",
                   activebackground="#3A70B9", relief=tk.FLAT,
                   padx=28, pady=6, cursor="hand2").pack()

    def _render_item_row(self, parent, rtype, data):
        frame = tk.Frame(parent, bg="#F0F0F0", padx=14, pady=10)
        frame.pack(fill=tk.X, pady=4)

        name = data.get("name", "") if isinstance(data, dict) else str(data)
        is_dup = data.get("is_duplicate", False) if isinstance(data, dict) else False
        dup_c = data.get("dup_count", 0) if isinstance(data, dict) else 0

        style_map = {
            "s_character": ("#E53935", "[S]", "\u2605", True),
            "a_character": ("#AA00BB", "[A]", "\u2606", False),
            "a_disk": ("#1976D2", "[A盘]", "\u25A6", False),
            "b_disk": ("#757575", "[B盘]", "\u25A7", False),
            "dice": ("#388E3C", "", "\u2694", False),
            "gold_chip": ("#F57F17", "", "\u2726", False),
            "white_chip": ("#607D8B", "", "\u2727", False),
            "skin": ("#E91E63", "[皮肤]", "\u2728", False),
        }

        tag = f"gift_{data['type']}" if rtype == "gift" else rtype
        color, prefix, icon, is_bold = style_map.get(tag, ("#333", "", "\u2022", False))

        lbl_text = f"{icon} {prefix}" if prefix else icon
        tk.Label(frame, text=lbl_text,
                  font=("Microsoft YaHei", 11, "bold"),
                  fg=color, bg="#F0F0F0").pack(side=tk.LEFT)

        font_weight = "bold" if is_bold else "normal"
        font_size = 14 if is_bold else 12
        tk.Label(frame, text=name,
                  font=("Microsoft YaHei", font_size, font_weight),
                  fg=color, bg="#F0F0F0").pack(side=tk.LEFT, padx=12)

        if is_dup:
            parts = []
            if data.get("fragment"): parts.append(f"{data['fragment']}碎片")
            if data.get("extra_gold"): parts.append(f"{data['extra_gold']}金棋")
            if data.get("extra_white"): parts.append(f"{data['extra_white']}白棋")
            extra = ", ".join(parts) if parts else ""
            tk.Label(frame, text=f"x{dup_c} {extra}",
                      font=("Microsoft YaHei", 9),
                      fg="#999", bg="#F0F0F0").pack(side=tk.RIGHT)


class GachaSimulator:
    """抽卡模拟器主应用类"""

    def __init__(self):
        self.engine = GameEngine()
        self.root = tk.Tk()
        self.root.title("异环抽卡模拟器")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)

        self._show_disclaimer()
        self._build_ui()
        self._refresh_all()

    def _show_disclaimer(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("声明")
        dlg.geometry("520x420")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg="#FFF5E6")

        frame = tk.Frame(dlg, bg="#FFF5E6", padx=30, pady=24)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="关于本模拟器",
                  font=("Microsoft YaHei", 17, "bold"),
                  fg="#CC3300", bg="#FFF5E6").pack(pady=(0, 18))

        msg = (
            "本软件为 **非官方** 第三方模拟工具，"
            "供学习、研究和交流使用。\n\n"
            "- 本模拟器 **不等于** 原游戏，"
            "也 **不是** 原游戏官方或授权方开发的产品\n"
            "- 所有游戏数据、规则、图片属原游戏官方所有\n"
            "- 本模拟器不提供任何官方服务，与原游戏官方无关\n"
            "- 使用本工具即表示您同意以上条款\n\n"
            "请支持原游戏，合理使用模拟工具。"
        )
        tk.Label(frame, text=msg,
                  font=("Microsoft YaHei", 10),
                  fg="#444", bg="#FFF5E6",
                  justify=tk.LEFT,
                  wraplength=460).pack(pady=(0, 20))

        def on_ok():
            dlg.destroy()

        tk.Button(frame, text="我已知晓，开始使用",
                   command=on_ok,
                   font=("Microsoft YaHei", 11, "bold"),
                   bg="#4A90D9", fg="white",
                   activebackground="#3A70B9",
                   relief=tk.FLAT, padx=30, pady=8,
                   cursor="hand2").pack()

        dlg.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - 520) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - 420) // 2
        dlg.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        dlg.wait_window()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=6)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_outer = ttk.Frame(main_frame, width=220)
        left_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        left_outer.pack_propagate(False)

        left_canvas = tk.Canvas(left_outer, highlightthickness=0,
                                 bg="#f5f5f5")
        left_scrollbar = ttk.Scrollbar(left_outer, orient=tk.VERTICAL,
                                        command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_inner = ttk.Frame(left_canvas)
        left_canvas_window = left_canvas.create_window((0, 0),
                                                        window=left_inner,
                                                        anchor=tk.NW)

        def on_left_configure(event):
            left_canvas.itemconfig(left_canvas_window, width=event.width)

        def on_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_canvas.bind("<Configure>", on_left_configure)
        left_inner.bind("<Configure>", on_frame_configure)

        self._build_stats_panel(left_inner)
        self._build_resource_panel(left_inner)
        self._build_speed_panel(left_inner)
        self._build_board_selector(left_inner)
        self._build_operation_panel(left_inner)
        self._build_collection_panel(left_inner)

        right = ttk.Frame(main_frame)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_board_area(right)
        self._build_log_area(right)

        status = ttk.Frame(self.root)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(
            value="就绪 - 点击 [1抽] 或 [10抽] 开始"
        )
        ttk.Label(status, textvariable=self.status_var,
                   relief=tk.SUNKEN, anchor=tk.W, padding=(8, 4)).pack(fill=tk.X)

    def _build_stats_panel(self, parent):
        f = ttk.LabelFrame(parent, text="统计信息", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        self.lbl_total_rolls = ttk.Label(f, text="掷骰次数: 0",
                                          font=("Microsoft YaHei", 9))
        self.lbl_total_rolls.pack(anchor=tk.W, pady=1)

        self.lbl_pity = ttk.Label(f, text="S级保底: 0/90",
                                   font=("Microsoft YaHei", 9))
        self.lbl_pity.pack(anchor=tk.W, pady=1)

        self.lbl_gift = ttk.Label(f, text="集点赠礼: 0/10",
                                    font=("Microsoft YaHei", 9))
        self.lbl_gift.pack(anchor=tk.W, pady=1)

        self.lbl_mode = ttk.Label(f, text="当前: 基准棋盘",
                                    font=("Microsoft YaHei", 9))
        self.lbl_mode.pack(anchor=tk.W, pady=1)

    def _build_resource_panel(self, parent):
        f = ttk.LabelFrame(parent, text="资源", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        row0 = tk.Frame(f)
        row0.pack(fill=tk.X, pady=1)
        tk.Label(row0, text="红骰:", font=("Microsoft YaHei", 9),
                  width=5).pack(side=tk.LEFT)
        self.red_dice_var = tk.StringVar(value="")
        self.red_dice_entry = tk.Entry(row0, textvariable=self.red_dice_var,
                                         width=9, font=("Microsoft YaHei", 9))
        self.red_dice_entry.pack(side=tk.LEFT, padx=2)
        self.red_inf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row0, text="无限", variable=self.red_inf_var,
                        font=("Microsoft YaHei", 8),
                        command=self._on_dice_setting_change).pack(side=tk.LEFT)

        row1 = tk.Frame(f)
        row1.pack(fill=tk.X, pady=1)
        tk.Label(row1, text="蓝骰:", font=("Microsoft YaHei", 9),
                  width=5).pack(side=tk.LEFT)
        self.blue_dice_var = tk.StringVar(value="")
        self.blue_dice_entry = tk.Entry(row1, textvariable=self.blue_dice_var,
                                          width=9, font=("Microsoft YaHei", 9),
                                          state=tk.DISABLED)
        self.blue_dice_entry.pack(side=tk.LEFT, padx=2)
        self.blue_inf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text="无限(预留)",
                        variable=self.blue_inf_var,
                        font=("Microsoft YaHei", 8),
                        state=tk.DISABLED).pack(side=tk.LEFT)

        row2 = tk.Frame(f)
        row2.pack(fill=tk.X, pady=1)
        tk.Label(row2, text="环石:", font=("Microsoft YaHei", 9),
                  width=5).pack(side=tk.LEFT)
        self.ring_stone_var = tk.StringVar(value="无限")
        tk.Label(row2, textvariable=self.ring_stone_var,
                  font=("Microsoft YaHei", 9), fg="#E65100").pack(side=tk.LEFT)
        tk.Label(row2, text=" (160/骰)",
                  font=("Microsoft YaHei", 7), fg="#999").pack(side=tk.LEFT)

        # [已注释] 测试骰子功能（调试完成后可删除此段）
        # row_test = tk.Frame(f)
        # row_test.pack(fill=tk.X, pady=1)
        # tk.Label(row_test, text="测试骰子:", font=("Microsoft YaHei", 9),
        #           width=8).pack(side=tk.LEFT)
        # self.test_dice_var = tk.StringVar(value="")
        # self.test_dice_entry = tk.Entry(row_test, textvariable=self.test_dice_var,
        #                                  width=5, font=("Microsoft YaHei", 9))
        # self.test_dice_entry.pack(side=tk.LEFT, padx=2)
        # tk.Label(row_test, text="(空=随机, 1-6指定)",
        #           font=("Microsoft YaHei", 7), fg="#666").pack(side=tk.LEFT)

        self.lbl_gold_chips = ttk.Label(f, text="金棋: 0",
                                         font=("Microsoft YaHei", 9))
        self.lbl_gold_chips.pack(anchor=tk.W, pady=1)

        self.lbl_white_chips = ttk.Label(f, text="白棋: 0",
                                          font=("Microsoft YaHei", 9))
        self.lbl_white_chips.pack(anchor=tk.W, pady=1)

    def _build_speed_panel(self, parent):
        f = ttk.LabelFrame(parent, text="动画速度", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        self.speed_var = tk.StringVar(value="1x")
        speeds = AnimatedBoardCanvas.get_available_speeds()

        for val, text in speeds:
            rb = ttk.Radiobutton(f, text=text, variable=self.speed_var,
                                  value=val, command=self._on_speed_change)
            rb.pack(anchor=tk.W, pady=1)

    def _build_board_selector(self, parent):
        f = ttk.LabelFrame(parent, text="棋盘选择", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        boards = AnimatedBoardCanvas.get_available_boards()
        self.board_var = tk.StringVar(value="limited_xun")

        for board in boards:
            rb = ttk.Radiobutton(f, text=board["name"], variable=self.board_var,
                                  value=board["id"], command=self._on_board_change)
            rb.pack(anchor=tk.W, pady=1)

            desc_label = tk.Label(f, text=board["description"],
                                   font=("Microsoft YaHei", 8), fg="#666",
                                   bg="#F0F0F0")
            desc_label.pack(anchor=tk.W, padx=(18, 0))

    def _build_operation_panel(self, parent):
        f = ttk.LabelFrame(parent, text="操作", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        btn_font = ("Microsoft YaHei", 12, "bold")
        ttk.Button(f, text="? 1 抽", style="Big.TButton",
                    command=self._on_single_roll).pack(fill=tk.X, pady=3)
        ttk.Button(f, text="? 10 抽", style="Big.TButton",
                    command=self._on_ten_roll).pack(fill=tk.X, pady=3)
        ttk.Button(f, text="重置全部",
                    command=self._on_reset).pack(fill=tk.X, pady=3)

        style = ttk.Style()
        style.configure("Big.TButton", font=btn_font, padding=8)

    def _build_collection_panel(self, parent):
        f = ttk.LabelFrame(parent, text="已获得", padding=4)
        f.pack(fill=tk.BOTH, expand=True)

        nb = ttk.Notebook(f)
        nb.pack(fill=tk.BOTH, expand=True)

        cf = ttk.Frame(nb)
        nb.add(cf, text="角色")
        self.char_tree = ttk.Treeview(cf, columns=("c",), show="tree headings",
                                       height=6)
        self.char_tree.heading("#0", text="名称")
        self.char_tree.heading("c", text="数")
        self.char_tree.column("#0", width=130)
        self.char_tree.column("c", width=38)
        sc = ttk.Scrollbar(cf, orient=tk.VERTICAL, command=self.char_tree.yview)
        self.char_tree.configure(yscrollcommand=sc.set)
        self.char_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y)

        sf = ttk.Frame(nb)
        nb.add(sf, text="皮肤")
        self.skin_tree = ttk.Treeview(sf, columns=("c",), show="tree headings",
                                        height=6)
        self.skin_tree.heading("#0", text="类型")
        self.skin_tree.heading("c", text="数量")
        self.skin_tree.column("#0", width=80)
        self.skin_tree.column("c", width=60)
        ss = ttk.Scrollbar(sf, orient=tk.VERTICAL, command=self.skin_tree.yview)
        self.skin_tree.configure(yscrollcommand=ss.set)
        self.skin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ss.pack(side=tk.RIGHT, fill=tk.Y)

        df = ttk.Frame(nb)
        nb.add(df, text="弧盘")
        self.disk_tree = ttk.Treeview(df, columns=("c",), show="tree headings",
                                       height=6)
        self.disk_tree.heading("#0", text="名称")
        self.disk_tree.heading("c", text="数")
        self.disk_tree.column("#0", width=130)
        self.disk_tree.column("c", width=38)
        ds = ttk.Scrollbar(df, orient=tk.VERTICAL, command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=ds.set)
        self.disk_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ds.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_board_area(self, parent):
        f = ttk.LabelFrame(parent, text="棋盘", padding=4)
        f.pack(fill=tk.X, pady=(0, 4))
        self.board_canvas = AnimatedBoardCanvas(f, self.engine)
        self.board_canvas.speed_mode = self.speed_var

    def _build_log_area(self, parent):
        f = ttk.LabelFrame(parent, text="获得记录", padding=4)
        f.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            f, wrap=tk.WORD, font=("Consolas", 9),
            height=10, state=tk.DISABLED, bg="#FEFEFE", fg="#333"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        tag_configs = [
            ("s_char", "#CC0000", True),
            ("a_char", "#AA00BB", False),
            ("a_disk", "#1565C0", False),
            ("b_disk", "#666", False),
            ("dice", "#2E7D32", False),
            ("chip", "#E65100", False),
            ("pity", "#D32F2F", True),
            ("gift", "#E91E63", False),
            ("skin", "#E91E63", False),
            ("sleep", "#303F9F", False),
            ("normal", "#333", False),
            ("dup", "#999", False),
        ]
        for tag, fg, bold in tag_configs:
            kw = {"foreground": fg}
            if bold:
                kw["font"] = ("Consolas", 9, "bold")
            self.log_text.tag_configure(tag, **kw)

    def _on_speed_change(self):
        if hasattr(self, 'board_canvas') and hasattr(self.board_canvas, 'speed_mode'):
            self.board_canvas.speed_mode.set(self.speed_var.get())
            if hasattr(self.board_canvas, '_draw_speed_badge'):
                self.board_canvas.canvas.delete("speed_badge")
                self.board_canvas.canvas.delete("speed_label")
                self.board_canvas._draw_speed_badge()

    def _on_board_change(self):
        if not hasattr(self, 'board_canvas'):
            return

        new_board_id = self.board_var.get()

        board_info = next(
            (b for b in AnimatedBoardCanvas.get_available_boards() if b["id"] == new_board_id),
            None
        )
        if not board_info:
            return

        if messagebox.askyesno(
            "切换棋盘",
            f"确定切换到 [{board_info['name']}]?\\n"
            f"当前进度将重置。"
        ):
            self.board_canvas.switch_board(new_board_id)
            self.engine = GameEngine()
            self.board_canvas.engine = self.engine
            self._refresh_all()
            self.status_var.set(f"已切换到: {board_info['name']}")

    def _on_dice_setting_change(self):
        dm = self.engine.state.dice_manager
        is_inf = self.red_inf_var.get()
        dm.infinite_red = is_inf
        if is_inf:
            self.red_dice_entry.config(state=tk.DISABLED)
        else:
            self.red_dice_entry.config(state=tk.NORMAL)
            try:
                val = int(self.red_dice_var.get() or "0")
                dm.red_dice = max(0, val)
            except ValueError:
                dm.red_dice = 0
        self._refresh_all()

    def _on_single_roll(self):
        # 安全检查：如果动画状态卡住，强制重置
        if self.board_canvas.is_animating:
            print(f"[警告] _on_single_roll: 检测到is_animating=True，强制重置")
            self.board_canvas.is_animating = False

        dm = self.engine.state.dice_manager
        if not dm.infinite_red:
            try:
                val = int(self.red_dice_var.get() or "0")
                dm.red_dice = max(0, val)
            except ValueError:
                dm.red_dice = 0

            if not dm.infinite_ring:
                try:
                    rv = int(self.ring_stone_var.get() or "0")
                    dm.ring_stone = max(0, rv)
                except ValueError:
                    dm.ring_stone = 0

            success, consumed = dm.try_consume_for_roll(1)
            if not success:
                messagebox.showwarning("提示", "红骰和环石都不足！无法进行1抽")
                return

            self._refresh_all()

        global_pos = self.board_canvas.piece_pos_idx
        current_main = self.board_canvas.get_main_path_idx(global_pos)
        in_branch = self.board_canvas.is_in_branch_zone(global_pos)

        print(f"\n[掷骰前状态] global_pos={global_pos}, current_main={current_main}, in_branch={in_branch}")
        print(f"[掷骰前状态] engine.in_branch={self.engine.in_branch}, engine.branch_step={self.engine.branch_step}")

        # 显示当前位置的格子信息
        if global_pos < len(self.board_canvas.cell_names):
            print(f"[掷骰前状态] 当前格子名称={self.board_canvas.cell_names[global_pos]}")
            print(f"[掷骰前状态] 当前格子类型={self.board_canvas.cell_types[global_pos]}")

        # 预检测：是否在分支入口或已在分支内
        # 统一处理：进入分支 = 在分支内移动（都使用完整步数dv）
        is_already_in_branch = False  # 是否在分支内（包括刚进入）
        target_branch_key = None
        target_branch_data = None

        print(f"\n[预检测详情] in_branch={in_branch}, engine.in_branch={self.engine.in_branch}")
        print(f"[预检测详情] current_main={current_main}")

        if not in_branch and not self.engine.in_branch:
            # 情况1：在主路径上，检查是否要进入分支
            for bkey, bdata in self.board_canvas.branch_entries.items():
                entry_idx = bdata["entry_main_idx"]
                print(f"[预检测详情] 检查{bkey}: entry_main_idx={entry_idx}, current_main={current_main}, 匹配={current_main == entry_idx}")
                if current_main == entry_idx:
                    is_already_in_branch = True  # ✅ 标记为"将进入分支并移动"
                    target_branch_key = bkey
                    target_branch_data = bdata
                    print(f"\n[预检测] ✅ 当前位置{current_main}是{bkey}分支入口！将进入分支")
                    break
        elif in_branch or self.engine.in_branch:
            # 情况2：已在分支内，继续移动
            is_already_in_branch = True  # ✅ 关键修复：标记为在分支内！
            # 优先使用engine.in_branch（引擎记录的分支状态）
            # 如果engine.in_branch为None但in_branch=True（异常情况），则根据位置判断
            if self.engine.in_branch:
                target_branch_key = self.engine.in_branch
            elif in_branch:
                # engine状态已清除但位置仍在分支内：根据位置判断所属分支
                print(f"\n[预检测] ⚠️ 异常：engine.in_branch=None但位置{global_pos}仍在分支区域内")
                print(f"[预检测] ⚠️ 尝试根据位置判断所属分支...")
                target_branch_key = None
                for bkey, bdata in self.board_canvas.branch_entries.items():
                    b_start = bdata["branch_start"]
                    b_end = b_start + bdata["branch_len"] - 1
                    if b_start <= global_pos <= b_end:
                        target_branch_key = bkey
                        print(f"[预检测] ✅ 根据位置判断: 属于{bkey}分支（范围{b_start}-{b_end}）")
                        break

                if not target_branch_key:
                    print(f"[预检测] ❌ 无法判断所属分支，当作主路径处理")
                    is_already_in_branch = False  # 当作不在分支
                    target_branch_data = None
            else:
                target_branch_key = None

            if is_already_in_branch and target_branch_key:
                target_branch_data = self.board_canvas.branch_entries.get(target_branch_key, {})
                if not target_branch_data:
                    print(f"\n[警告] 找不到分支'{target_branch_key}'的配置数据！")
                    is_already_in_branch = False  # 安全降级：当作不在分支
                    target_branch_data = None
                else:
                    print(f"\n[预检测] 已在{target_branch_key}分支内，将正常移动")

        # 获取骰子点数
        # [已注释] 测试模式代码（调试完成后可删除）
        # test_dice_str = self.test_dice_var.get().strip()
        # if test_dice_str:
        #     try:
        #         dv = int(test_dice_str)
        #         if 1 <= dv <= 6:
        #             print(f"\n[测试模式] 使用指定骰子点数: {dv}")
        #         else:
        #             print(f"\n[测试模式] 指定值{dv}超出范围(1-6)，改为随机")
        #             dv = self.engine.roll_engine.roll_dice()
        #     except ValueError:
        #         print(f"\n[测试模式] 输入'{test_dice_str}'无效，改为随机")
        #         dv = self.engine.roll_engine.roll_dice()
        # else:
        dv = self.engine.roll_engine.roll_dice()

        # 计算目标位置（根据两种情况决定）
        # 安全检查：如果当前位置在分支区域内，强制使用分支逻辑
        current_in_branch_zone = self.board_canvas.is_in_branch_zone(global_pos)
        
        if is_already_in_branch:
            # 情况1：在分支内移动（包括刚从主路径进入）
            branch_start = target_branch_data["branch_start"]
            branch_end = target_branch_data["branch_start"] + target_branch_data["branch_len"] - 1

            # 判断是从主路径进入，还是已在分支内继续移动
            if global_pos < branch_start:
                # 从主路径进入分支：从分支起点开始走dv步
                # 修正：进入分支时，第一步应该到达branch_start，而不是branch_start+1
                # 所以target_global_pos = branch_start + dv - 1（dv=1时到达branch_start）
                start_pos = branch_start
                print(f"\n[分支进入] 从主路径{global_pos}进入{target_branch_key}分支")
                print(f"[分支进入] 从分支起点{start_pos}开始移动{dv}步")
            else:
                # 已在分支内：从当前位置继续走dv步
                start_pos = global_pos

            steps_to_exit = branch_end - start_pos  # 在分支内还能走的步数（不含跳转步）

            print(f"\n[分支移动详情] 起点={start_pos}, 分支范围={branch_start}-{branch_end}, 投掷={dv}点")
            print(f"[分支移动详情] 距离末尾还需{steps_to_exit}步（之后需要1步跳转）")

            if dv <= steps_to_exit:
                # 还在分支内移动，未超出
                # 修正：从主路径进入分支时，需要-1避免多走一格
                if global_pos < branch_start:
                    target_global_pos = start_pos + dv - 1
                else:
                    target_global_pos = start_pos + dv
                print(f"[分支移动] 在{target_branch_key}分支内移动: {start_pos} → {target_global_pos}")
            else:
                # 超出分支！先走到末尾，再跳转到出口（1步），然后继续在主路径上移动
                exit_idx = target_branch_data["exit_main_idx"]
                remaining_steps = dv - steps_to_exit - 1  # 减去分支内步数和跳转步
                target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)
                print(f"\n[分支离开] ✅ 超出{target_branch_key}分支范围！")
                print(f"[分支离开] 先走{steps_to_exit}步到末尾，跳转到出口{exit_idx}，再走{remaining_steps}步到达{target_global_pos}")
        elif current_in_branch_zone and not is_already_in_branch:
            # 情况1.5: 异常情况！位置在分支内但预检测失败
            # 强制使用分支离开逻辑（安全兜底）
            print(f"\n[警告-异常] 位置{global_pos}在分支区域内但is_already_in_branch=False！")
            print(f"[警告-异常] engine.in_branch={self.engine.in_branch}")
            
            # 尝试确定所属分支
            fallback_branch_key = None
            fallback_branch_data = None
            
            if self.engine.in_branch:
                fallback_branch_key = self.engine.in_branch
                fallback_branch_data = self.board_canvas.branch_entries.get(fallback_branch_key, {})
            
            if not fallback_branch_data:
                for bkey, bdata in self.board_canvas.branch_entries.items():
                    b_start = bdata["branch_start"]
                    b_end = b_start + bdata["branch_len"] - 1
                    if b_start <= global_pos <= b_end:
                        fallback_branch_key = bkey
                        fallback_branch_data = bdata
                        break
            
            if fallback_branch_data:
                branch_end = fallback_branch_data["branch_start"] + fallback_branch_data["branch_len"] - 1
                exit_idx = fallback_branch_data["exit_main_idx"]
                
                # 计算到末尾需要的步数
                steps_to_end = branch_end - global_pos + 1
                
                if dv <= steps_to_end:
                    # 还在分支内
                    target_global_pos = global_pos + dv
                    print(f"[警告-异常] 兜底处理: 在{fallback_branch_key}分支内移动 → {target_global_pos}")
                else:
                    # 离开分支
                    remaining_steps = dv - steps_to_end
                    target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)
                    print(f"[警告-异常] 兜底处理: 离开{fallback_branch_key}分支")
                    print(f"[警告-异常] 出口={exit_idx}, 剩余步数={remaining_steps}, 目标={target_global_pos}")
                
                # 更新状态变量供后续使用
                is_already_in_branch = True
                target_branch_key = fallback_branch_key
                target_branch_data = fallback_branch_data
            else:
                # 无法判断所属分支，降级为主路径移动（使用current_main而非global_pos）
                print(f"[警告-异常] 无法判断所属分支，降级为基于主路径索引的计算")
                main_path_idx = self.board_canvas.get_main_path_idx(global_pos)
                target_global_pos = self.board_canvas._cycle_pos(main_path_idx, dv)
                print(f"[警告-异常] 使用主路径索引{main_path_idx}计算, 目标={target_global_pos}")
        else:
            # 情况2：正常主路径移动
            target_global_pos = self.board_canvas._cycle_pos(global_pos, dv)

        # 使用目标位置的格子类型执行完整抽奖（只增加一次计数）
        target_cell_type = self.board_canvas.cell_types[target_global_pos] if target_global_pos < len(self.board_canvas.cell_types) else "apprentice_chest"
        target_cell_name = self.board_canvas.cell_names[target_global_pos] if target_global_pos < len(self.board_canvas.cell_names) else None
        print(f"\n[调试] 目标位置: 索引={target_global_pos}, 类型={target_cell_type}, 名称={target_cell_name}")

        # 确定分支状态（告诉引擎当前/目标是否在分支中）
        if is_already_in_branch:
            # 在分支内移动（包括刚进入）
            branch_start = target_branch_data["branch_start"]
            branch_end = branch_start + target_branch_data["branch_len"] - 1

            # 判断目标是否还在分支范围内 [branch_start, branch_end]
            if branch_start <= target_global_pos <= branch_end:
                # 还在分支内
                effective_is_in_branch = target_branch_key
                # 计算branch_step：从分支起点到目标的距离
                effective_branch_step = target_global_pos - branch_start
                print(f"[分支状态] 仍在{target_branch_key}分支内，step={effective_branch_step}")
            else:
                # 将要离开分支（目标在主路径上）
                # 使用特殊标记防止game_logic误触发enter事件
                effective_is_in_branch = target_branch_key
                effective_branch_step = -1  # 特殊值：表示将要离开分支
                print(f"[分支状态] 即将离开{target_branch_key}分支（目标={target_global_pos}, 分支范围={branch_start}-{branch_end}）")
        else:
            # 正常主路径
            effective_is_in_branch = self.engine.in_branch if in_branch else None
            effective_branch_step = self.engine.branch_step if in_branch else 0

        result = self.engine.execute_single_roll_with_target(
            current_pos_idx=current_main,
            current_cell_type=self.board_canvas.cell_types[global_pos],
            target_cell_type=target_cell_type,
            target_cell_name=target_cell_name,  # 传入目标格子的原始名称
            dice_value=dv,  # 使用已确定的骰子点数
            branch_entries=self.board_canvas.branch_entries,
            is_in_branch=effective_is_in_branch,
            branch_step=effective_branch_step,
        )

        ck = result["cell_type"]

        def done():
            # 注意：animate_roll()已经在动画过程中正确更新了piece_pos_idx
            # 这里只处理分支状态更新

            print(f"\n[done回调] branch_event={result.get('branch_event')}")
            print(f"[done回调] 当前piece_pos_idx={self.board_canvas.piece_pos_idx}")
            print(f"[done回调] is_already_in_branch={is_already_in_branch}")

            if is_already_in_branch:
                # 在分支内移动（包括刚进入）
                # 判断1: 仍在分支内（step >= 0 且 目标在分支范围内）
                if effective_is_in_branch and effective_branch_step >= 0:
                    # 还在分支内，更新branch_step
                    self.engine.in_branch = target_branch_key
                    self.engine.branch_step = effective_branch_step
                    print(f"\n[分支-继续] 在{target_branch_key}分支内，step={self.engine.branch_step}")
                # 判断2: 即将离开分支（特殊标记 step == -1 或 step < 0）
                elif effective_is_in_branch and effective_branch_step < 0:
                    # 即将离开分支（特殊标记），清除状态
                    self.engine.in_branch = None
                    self.engine.branch_step = 0
                    print(f"\n[分支-离开] 离开{target_branch_key}分支，已在主路径上继续移动")
                else:
                    # 安全兜底：如果effective_is_in_branch为None或其他异常情况，也清除状态
                    print(f"\n[分支-安全] 清除分支状态（effective_is_in_branch={effective_is_in_branch}, effective_branch_step={effective_branch_step}）")
                    self.engine.in_branch = None
                    self.engine.branch_step = 0
            elif result.get("branch_event") and result["branch_event"][0] == "enter" and not is_already_in_branch:
                # 只有当没有通过预检测处理分支时，才响应game_logic的分支进入事件
                # 如果已经通过is_already_in_branch处理了，就忽略这个事件（避免重复设置位置）
                bkey = result["branch_event"][1]
                bdata = result["branch_event"][2]
                self.engine.in_branch = bkey
                self.engine.branch_step = 0
                # 分支进入：跳转到分支起始位置
                print(f"\n[分支] 触发进入{bkey}分支，从主路径跳转到索引{bdata['branch_start']}")
                self.board_canvas.piece_pos_idx = bdata["branch_start"]
                print(f"[分支] ✅ piece_pos_idx已更新为={self.board_canvas.piece_pos_idx}")
            elif result.get("new_branch_state") and not is_already_in_branch:
                # 只有当没有通过预检测处理分支时，才响应game_logic的新分支状态
                # 避免预检测和game_logic双重设置导致的冲突
                self.engine.in_branch = result["new_branch_state"]
                self.engine.branch_step = result.get("new_branch_step", 0)
                print(f"\n[分支] 响应game_logic的新分支状态: {self.engine.in_branch}")
            else:
                # 正常情况：位置已在animate_roll中正确设置，无需重复计算
                # 但需要检查是否应该离开分支
                if self.engine.in_branch:
                    bdata = self.board_canvas.branch_entries.get(self.engine.in_branch, {})
                    if not bdata:
                        # 分支数据不存在，清除状态
                        print(f"\n[警告] engine.in_branch='{self.engine.in_branch}'但找不到对应配置，清除状态")
                        self.engine.in_branch = None
                        self.engine.branch_step = 0
                    else:
                        branch_end = bdata["branch_start"] + bdata["branch_len"] - 1
                        current_pos = self.board_canvas.piece_pos_idx
                        # 检查是否真的离开了分支
                        should_exit = (
                            current_pos > branch_end or
                            (not self.board_canvas.is_in_branch_zone(current_pos) and current_pos < 55)
                        )
                        if should_exit:
                            exit_idx = bdata["exit_main_idx"]
                            print(f"\n[分支] 检测到离开{self.engine.in_branch}分支")
                            print(f"[分支] 当前位置={current_pos}, 分支结束={branch_end}")
                            print(f"[分支] 返回主路径索引{exit_idx}")
                            # 只有当当前位置不是出口时才重置（避免重复设置）
                            if current_pos != exit_idx:
                                self.board_canvas.piece_pos_idx = exit_idx
                                print(f"[分支] ✅ 位置已修正为{exit_idx}")
                            self.engine.in_branch = None
                            self.engine.branch_step = 0

            self._show_popup(result)
            self._display_result(result)
            self._refresh_all()

        # 调用动画：根据情况决定是否强制目标位置
        if is_already_in_branch:
            # 分支内移动（包括刚进入或离开）→ 强制目标位置（使用完整步数dv）
            anim_target = target_global_pos

            # 判断是否离开分支，如果是则准备branch_exit_info
            branch_exit_info_for_anim = None
            if effective_is_in_branch and effective_branch_step < 0:
                # 即将离开分支：提供出口信息给动画
                branch_exit_info_for_anim = {
                    'branch_end': target_branch_data["branch_start"] + target_branch_data["branch_len"] - 1,
                    'exit_main_idx': target_branch_data["exit_main_idx"],
                    'branch_key': target_branch_key
                }
                print(f"[动画] 离开分支，提供出口信息: {branch_exit_info_for_anim}")
            else:
                print(f"[动画] 分支内移动到: {anim_target}, 步数={dv}")

            self.board_canvas.animate_roll(dv, ck, done, target_idx_override=anim_target,
                                         branch_exit_info=branch_exit_info_for_anim)
        else:
            # 正常主路径 → 不强制
            anim_target = None
            self.board_canvas.animate_roll(dv, ck, done, target_idx_override=anim_target)

    def _on_ten_roll(self):
        # 安全检查：如果动画状态卡住，强制重置
        if self.board_canvas.is_animating:
            print(f"[警告] _on_ten_roll: 检测到is_animating=True，强制重置")
            self.board_canvas.is_animating = False

        def run_n(idx):
            if idx >= 10:
                self.status_var.set(
                    f"完成10抽 | 总掷: {self.engine.state.total_rolls}")
                return

            dm = self.engine.state.dice_manager
            if not dm.infinite_red:
                try:
                    val = int(self.red_dice_var.get() or "0")
                    dm.red_dice = max(0, val)
                except ValueError:
                    dm.red_dice = 0

                if not dm.infinite_ring:
                    try:
                        rv = int(self.ring_stone_var.get() or "0")
                        dm.ring_stone = max(0, rv)
                    except ValueError:
                        dm.ring_stone = 0

                success, consumed = dm.try_consume_for_roll(1)
                if not success:
                    messagebox.showwarning("提示", f"红骰和环石都不足！已完成{idx}抽")
                    return

                self._refresh_all()

            global_pos = self.board_canvas.piece_pos_idx
            current_main = self.board_canvas.get_main_path_idx(global_pos)
            in_branch = self.board_canvas.is_in_branch_zone(global_pos)

            # 预检测：是否在分支入口或已在分支内（10连抽也需要统一处理）
            # 与单次投掷保持一致：进入分支 = 在分支内移动（都使用完整步数dv）
            is_already_in_branch = False  # 是否在分支内（包括刚进入）
            target_branch_key = None
            target_branch_data = None

            if not in_branch and not self.engine.in_branch:
                for bkey, bdata in self.board_canvas.branch_entries.items():
                    if current_main == bdata["entry_main_idx"]:
                        is_already_in_branch = True  # ✅ 标记为"将进入分支并移动"
                        target_branch_key = bkey
                        target_branch_data = bdata
                        break
            elif in_branch or self.engine.in_branch:
                # 与单次投掷保持一致：标记为在分支内
                is_already_in_branch = True  # ✅ 关键修复：与单次投掷一致
                # 优先使用engine.in_branch（引擎记录的分支状态）
                if self.engine.in_branch:
                    target_branch_key = self.engine.in_branch
                elif in_branch:
                    print(f"\n[预检测-10连] ⚠️ 异常：engine.in_branch=None但位置{global_pos}仍在分支区域内")
                    target_branch_key = None
                    for bkey, bdata in self.board_canvas.branch_entries.items():
                        b_start = bdata["branch_start"]
                        b_end = b_start + bdata["branch_len"] - 1
                        if b_start <= global_pos <= b_end:
                            target_branch_key = bkey
                            break

                    if not target_branch_key:
                        is_already_in_branch = False
                        target_branch_data = None
                else:
                    target_branch_key = None

                if is_already_in_branch and target_branch_key:
                    target_branch_data = self.board_canvas.branch_entries.get(target_branch_key, {})
                    if not target_branch_data:
                        is_already_in_branch = False
                        target_branch_data = None

            # 获取骰子点数
            # [已注释] 测试模式代码（调试完成后可删除）
            # test_dice_str = self.test_dice_var.get().strip()
            # if test_dice_str:
            #     try:
            #         dv = int(test_dice_str)
            #         if 1 <= dv <= 6:
            #             pass  # 使用指定值
            #         else:
            #             dv = self.engine.roll_engine.roll_dice()
            #     except ValueError:
            #         dv = self.engine.roll_engine.roll_dice()
            # else:
            dv = self.engine.roll_engine.roll_dice()

            # 计算目标位置（与单次投掷保持一致：使用完整步数）
            # 安全检查：如果当前位置在分支区域内，强制使用分支逻辑
            current_in_branch_zone_10 = self.board_canvas.is_in_branch_zone(global_pos)

            if is_already_in_branch:
                branch_start = target_branch_data["branch_start"]
                branch_end = target_branch_data["branch_start"] + target_branch_data["branch_len"] - 1

                if global_pos < branch_start:
                    start_pos = branch_start
                else:
                    start_pos = global_pos

                steps_to_exit = branch_end - start_pos  # 在分支内还能走的步数（不含跳转步）

                if dv <= steps_to_exit:
                    # 修正：从主路径进入分支时，需要-1避免多走一格（与单次投掷一致）
                    if global_pos < branch_start:
                        target_global_pos = start_pos + dv - 1
                    else:
                        target_global_pos = start_pos + dv
                    print(f"[分支移动-10连] 在{target_branch_key}分支内: {start_pos} → {target_global_pos}")
                else:
                    exit_idx = target_branch_data["exit_main_idx"]
                    remaining_steps = dv - steps_to_exit - 1  # 减去跳转步
                    target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)
                    print(f"[分支离开-10连] ✅ 离开{target_branch_key}, 出口={exit_idx}, 目标={target_global_pos}")
            elif current_in_branch_zone_10 and not is_already_in_branch:
                # 10连抽的安全兜底：与单次投掷保持一致
                print(f"\n[警告-异常-10连] 位置{global_pos}在分支区域内但is_already_in_branch=False")

                fallback_bkey_10 = None
                fallback_bdata_10 = None

                if self.engine.in_branch:
                    fallback_bkey_10 = self.engine.in_branch
                    fallback_bdata_10 = self.board_canvas.branch_entries.get(fallback_bkey_10, {})

                if not fallback_bdata_10:
                    for bkey, bdata in self.board_canvas.branch_entries.items():
                        b_start = bdata["branch_start"]
                        b_end = b_start + bdata["branch_len"] - 1
                        if b_start <= global_pos <= b_end:
                            fallback_bkey_10 = bkey
                            fallback_bdata_10 = bdata
                            break

                if fallback_bdata_10:
                    branch_end_10 = fallback_bdata_10["branch_start"] + fallback_bdata_10["branch_len"] - 1
                    exit_idx_10 = fallback_bdata_10["exit_main_idx"]
                    steps_to_end_10 = branch_end_10 - global_pos + 1

                    if dv <= steps_to_end_10:
                        target_global_pos = global_pos + dv
                        print(f"[警告-异常-10连] 兜底: 分支内移动 → {target_global_pos}")
                    else:
                        remaining_steps_10 = dv - steps_to_end_10
                        target_global_pos = self.board_canvas._cycle_pos(exit_idx_10, remaining_steps_10)
                        print(f"[警告-异常-10连] 兜底: 离开分支, 目标={target_global_pos}")

                    is_already_in_branch = True
                    target_branch_key = fallback_bkey_10
                    target_branch_data = fallback_bdata_10
                else:
                    main_path_idx_10 = self.board_canvas.get_main_path_idx(global_pos)
                    target_global_pos = self.board_canvas._cycle_pos(main_path_idx_10, dv)
                    print(f"[警告-异常-10连] 降级为主路径计算, 目标={target_global_pos}")
            else:
                target_global_pos = self.board_canvas._cycle_pos(global_pos, dv)
            target_cell_type = self.board_canvas.cell_types[target_global_pos] if target_global_pos < len(self.board_canvas.cell_types) else "apprentice_chest"
            target_cell_name = self.board_canvas.cell_names[target_global_pos] if target_global_pos < len(self.board_canvas.cell_names) else None

            # 确定分支状态（与单次投掷保持一致）
            if is_already_in_branch:
                branch_start = target_branch_data["branch_start"]
                branch_end = branch_start + target_branch_data["branch_len"] - 1

                # 判断目标是否还在分支范围内 [branch_start, branch_end]
                if branch_start <= target_global_pos <= branch_end:
                    effective_is_in_branch = target_branch_key
                    effective_branch_step = target_global_pos - branch_start
                else:
                    # 将要离开分支（目标在主路径上）
                    effective_is_in_branch = target_branch_key
                    effective_branch_step = -1  # 特殊值：表示将要离开分支
            else:
                # 正常主路径
                effective_is_in_branch = self.engine.in_branch if in_branch else None
                effective_branch_step = self.engine.branch_step if in_branch else 0

            # 使用目标格子类型执行完整抽奖（只增加一次计数）
            result = self.engine.execute_single_roll_with_target(
                current_pos_idx=current_main,
                current_cell_type=self.board_canvas.cell_types[global_pos],
                target_cell_type=target_cell_type,
                target_cell_name=target_cell_name,  # 传入目标格子的原始名称
                dice_value=dv,
                branch_entries=self.board_canvas.branch_entries,
                is_in_branch=effective_is_in_branch,
                branch_step=effective_branch_step,
            )

            ck = result["cell_type"]

            def after_one():
                # 注意：animate_roll()已经在动画过程中正确更新了piece_pos_idx
                # 这里只处理分支状态更新（与单次投掷保持一致）

                if is_already_in_branch:
                    # 在分支内移动（包括刚进入）
                    # 判断1: 仍在分支内（step >= 0 且 目标在分支范围内）
                    if effective_is_in_branch and effective_branch_step >= 0:
                        # 还在分支内，更新branch_step
                        self.engine.in_branch = target_branch_key
                        self.engine.branch_step = effective_branch_step
                        print(f"\n[分支-10连-继续] 在{target_branch_key}分支内，step={self.engine.branch_step}")
                    # 判断2: 即将离开分支（特殊标记 step < 0）
                    elif effective_is_in_branch and effective_branch_step < 0:
                        # 即将离开分支（特殊标记），清除状态
                        self.engine.in_branch = None
                        self.engine.branch_step = 0
                        print(f"\n[分支-10连-离开] 离开{target_branch_key}分支")
                    else:
                        # 安全兜底：清除状态
                        print(f"\n[分支-10连-安全] 清除分支状态")
                        self.engine.in_branch = None
                        self.engine.branch_step = 0
                elif result.get("branch_event") and result["branch_event"][0] == "enter" and not is_already_in_branch:
                    # 只有当没有通过预检测处理分支时，才响应game_logic的分支进入事件
                    bdata = result["branch_event"][2]
                    self.engine.in_branch = result["branch_event"][1]
                    print(f"\n[分支-10连] 触发进入分支，跳转到索引{bdata['branch_start']}")
                    self.board_canvas.piece_pos_idx = bdata["branch_start"]
                elif self.engine.in_branch:
                    bdata = self.board_canvas.branch_entries.get(self.engine.in_branch, {})
                    if not bdata:
                        print(f"\n[警告-10连] engine.in_branch='{self.engine.in_branch}'但找不到配置，清除")
                        self.engine.in_branch = None
                        self.engine.branch_step = 0
                    else:
                        branch_end = bdata["branch_start"] + bdata["branch_len"] - 1
                        current_pos = self.board_canvas.piece_pos_idx
                        should_exit = (
                            current_pos > branch_end or
                            (not self.board_canvas.is_in_branch_zone(current_pos) and current_pos < 55)
                        )
                        if should_exit:
                            exit_idx = bdata.get("exit_main_idx", 18)
                            print(f"\n[分支-10连] 检测到离开{self.engine.in_branch}分支")
                            print(f"[分支-10连] 当前={current_pos}, 分支结束={branch_end}")
                            if current_pos != exit_idx:
                                self.board_canvas.piece_pos_idx = exit_idx
                                print(f"[分支-10连] ✅ 位置修正为{exit_idx}")
                            self.engine.in_branch = None
                            self.engine.branch_step = 0
                # else: 正常情况，位置已在animate_roll中正确设置，无需修改

                self._display_result(result)
                self._refresh_all()
                self.root.after(50, lambda: run_n(idx + 1))

            # 调用动画：根据情况决定是否强制目标位置（10连抽与单次投掷保持一致）
            if is_already_in_branch:
                anim_target = target_global_pos

                # 判断是否离开分支，如果是则准备branch_exit_info（与单次投掷一致）
                branch_exit_info_for_anim_10 = None
                if effective_is_in_branch and effective_branch_step < 0:
                    branch_exit_info_for_anim_10 = {
                        'branch_end': target_branch_data["branch_start"] + target_branch_data["branch_len"] - 1,
                        'exit_main_idx': target_branch_data["exit_main_idx"],
                        'branch_key': target_branch_key
                    }

                self.board_canvas.animate_roll(dv, ck, after_one, target_idx_override=anim_target,
                                             branch_exit_info=branch_exit_info_for_anim_10)
            else:
                anim_target = None
                self.board_canvas.animate_roll(dv, ck, after_one, target_idx_override=anim_target)

        run_n(0)

    def _on_reset(self):
        if messagebox.askyesno(
            "确认",
            "确定重置所有数据?\n包括保底进度和收集记录。"
        ):
            self.engine = GameEngine()
            self.board_canvas.engine = self.engine
            self.board_canvas.reset_board()
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self._refresh_collection_trees()
            self._refresh_all()
            self.status_var.set("已重置")

    def _show_popup(self, result):
        rewards = [(r["type"], r) for r in result.get("rewards", [])]
        RewardPopup(self.root, rewards,
                     gift_result=result.get("gift_result"),
                     pity_event=result.get("pity_event"))

    def _display_result(self, result):
        self.log_text.config(state=tk.NORMAL)
        n = result["roll_number"]
        d = result["dice_value"]
        cn = result["cell_name"]
        self.log_text.insert(tk.END, f"[{n:>3d}] {d}点 -> {cn}\n", "normal")

        be = result.get("branch_event")
        if be:
            if be[0] == "enter":
                bname = be[2].get("name", be[1])
                self.log_text.insert(tk.END,
                    f"    >> 进入分支: {bname}! 继续掷骰 <<\n", "pity")
            elif be[0] == "s_got":
                self.log_text.insert(tk.END,
                    f"    >> 必定获得S级角色: 浔! <<\n", "s_char")

        for r in result.get("rewards", []):
            self._log_reward_item(r)

        pe = result.get("pity_event")
        if pe == "variant":
            self.log_text.insert(tk.END,
                "    ** 变格! S概率大幅提升 **\n", "pity")
        elif pe == "hard_pity":
            self.log_text.insert(tk.END, "    !! 硬保底 !!\n", "pity")

        g = result.get("gift_result")
        if g:
            t = "s_char" if g["type"] == "s_character" else "a_disk"
            self.log_text.insert(tk.END, f"    [赠礼] {g['name']}\n", t)
            if g.get("is_duplicate"):
                ex = []
                if g.get("fragment"): ex.append(f"{g['fragment']}碎")
                if g.get("extra_gold"): ex.append(f"{g['extra_gold']}金")
                if ex:
                    self.log_text.insert(tk.END,
                        f"              (重x{g['dup_count']} {', '.join(ex)})\n",
                        "dup")

        sp = result.get("sleep_pool_event")
        if sp and sp.get("started"):
            self.log_text.insert(tk.END, "    [沉眠] 追击!\n", "sleep")
            for cr in sp.get("chase_results", []):
                pp, gp, dd = cr["player_pos"], cr["guardian_pos"], cr["dice"]
                if cr["caught"]:
                    self.log_text.insert(tk.END,
                        f"              {dd}->P{pp}/G{gp} 追上!+30金\n", "chip")
                elif cr["failed"]:
                    self.log_text.insert(tk.END,
                        f"              {dd}->P{pp}/G{gp} 逃脱\n", "sleep")
                else:
                    self.log_text.insert(tk.END,
                        f"              {dd}->P{pp}/G{gp}\n", "normal")

        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_reward_item(self, r, indent="    "):
        type_map = {
            "s_character": ("s_char", "[S]"),
            "a_character": ("a_char", "[A]"),
            "a_disk": ("a_disk", "[A盘]"),
            "b_disk": ("b_disk", "[B盘]"),
            "skin": ("skin", "[皮肤]"),
            "dice": ("dice", ""),
            "gold_chip": ("chip", ""),
            "white_chip": ("chip", ""),
        }
        tag, prefix = type_map.get(r["type"], ("normal", ""))
        self.log_text.insert(tk.END, f"{indent}{prefix}{r.get('name','')}\n", tag)

        if r.get("is_duplicate") and r["type"] in ("s_character", "a_character",
                                                     "a_disk", "b_disk", "skin"):
            ex = []
            if r.get("fragment"): ex.append(f"{r['fragment']}碎")
            if r.get("extra_gold"): ex.append(f"{r['extra_gold']}金")
            if r.get("extra_white"): ex.append(f"{r['extra_white']}白")
            if ex:
                dc = r.get("dup_count", "?")
                self.log_text.insert(tk.END,
                    f"{indent}(x{dc} {', '.join(ex)})\n", "dup")

    def _refresh_all(self):
        s = self.engine.state
        pc = __import__("board_data").PITY_CONFIG["s_pity"]["hard_pity"]
        gc = __import__("board_data").PITY_CONFIG["gift_pity"]["interval"]

        self.lbl_total_rolls.config(text=f"掷骰: {s.total_rolls}")
        self.lbl_pity.config(text=f"S保底: {s.s_pity_counter}/{pc}")
        self.lbl_gift.config(text=f"赠礼: {s.gift_counter}/{gc}")

        md = "变格" if s.is_variant else "基准"
        self.lbl_mode.config(text=f"当前: {md}棋盘")

        dc = s.dice_manager.get_dice_count("red")
        if dc == float("inf"):
            self.red_inf_var.set(True)
            self.red_dice_entry.config(state=tk.DISABLED)
        else:
            self.red_inf_var.set(False)
            self.red_dice_entry.config(state=tk.NORMAL)
            self.red_dice_var.set(str(int(dc)))

        self.ring_stone_var.set("无限")
        rc = s.dice_manager.get_dice_count("ring")
        if rc != float("inf"):
            self.ring_stone_var.set(str(int(rc)))

        self.lbl_gold_chips.config(text=f"金棋: {s.gold_chips}")
        self.lbl_white_chips.config(text=f"白棋: {s.white_chips}")

        self._refresh_collection_trees()

    def _refresh_collection_trees(self):
        for item in self.char_tree.get_children():
            self.char_tree.delete(item)
        for item in self.skin_tree.get_children():
            self.skin_tree.delete(item)
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)

        from board_data import S_POOL_LIMITED, A_POOL_LIMITED, A_DISK_POOL, B_DISK_POOL, SKIN_SYSTEM, SKIN_CHARACTER

        for ch in S_POOL_LIMITED:
            c = self.engine.state.get_item_count("s_characters", ch["name"])
            self.char_tree.insert("", tk.END, text=f"{ch['name']} (S)", values=(c,))
        for ch in A_POOL_LIMITED:
            c = self.engine.state.get_item_count("a_characters", ch["name"])
            self.char_tree.insert("", tk.END, text=f"{ch['name']} (A)", values=(c,))

        skin_type_names = {
            "today_outfit": "穿搭",
            "vehicle_paint": "涂装",
            "glider_skin": "滑翔翼",
        }
        for stype_key, scfg in SKIN_SYSTEM.items():
            type_label = skin_type_names.get(stype_key, stype_key)
            total = 0
            for char_name, skin_full_name in scfg["skins"].items():
                c = self.engine.state.get_item_count("skins", skin_full_name)
                total += c
            if total > 0:
                self.skin_tree.insert("", tk.END, text=type_label,
                                         values=(f"{total}/{len(scfg['skins'])}",))

        for ad in A_DISK_POOL:
            c = self.engine.state.get_item_count("a_disks", ad)
            self.disk_tree.insert("", tk.END, text=f"{ad} (A)", values=(c,))
        for bd in B_DISK_POOL:
            c = self.engine.state.get_item_count("b_disks", bd)
            self.disk_tree.insert("", tk.END, text=f"{bd} (B)", values=(c,))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GachaSimulator()
    app.run()
