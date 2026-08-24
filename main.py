# -*- coding: utf-8 -*-

"""
抽卡模拟器主程序 - GUI界面（Tkinter）
包含动画棋盘、骰子滚动、棋子移动、落格高亮、获得弹窗、皮肤系统
版本: v1.2.1 - 全新渲染引擎 + 多棋盘架构 + 5档速度控制
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from game_logic import GameEngine, SLEEP_POOL_CONFIG
from board_data import get_variant_transforms


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
        # [V0.4.3修改] 变格后的S级同行（必定获得S级角色，方形样式）
        "companion_s": {
            "color": "#FF8A65", "border": "#E64A19", "text": "#fff",
            "shape": "round_rect", "icon": "\u2665", "short_name": "S级",
            "desc": "变格-于此同行 (必得S级)",
            "gradient_top": "#FFAB91", "gradient_bottom": "#FF5722"
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
        # [V0.3新增] 失纬棋盒（常驻棋盘独有，给金色棋子）
        "lost_treasure_box": {
            "color": "#FFD700", "border": "#B8860B", "text": "#5D4037",
            "shape": "diamond", "icon": "\u2728", "short_name": "失纬",
            "desc": "失纬棋盒 (金棋)",
            "gradient_top": "#FFF176", "gradient_bottom": "#FBC02D"
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
        "companion_s": "\u2665",  # [V0.4.2新增] 变格S级同行
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
        "companion_s": "S级",  # [V0.4.2新增] 变格S级同行
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
        self.is_variant = False  # [V0.4.3修复] 初始化变格状态标志

        if board_config:
            self._load_board_config(board_config)
        else:
            # [V1.3.0修复] 无外部配置时，使用引擎当前棋盘ID，不再硬编码浔
            default_board_id = getattr(self.engine.gacha, 'board_id', 'limited_nanally')
            self._generate_limited_board(default_board_id)

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
        self._is_updating = False  # [V0.4.2新增] 防止重复渲染标志
        self._render_count = 0  # [V0.4.3新增] 渲染计数器（用于诊断重叠）
        self._last_render_time = 0  # [V0.4.3新增] 上次渲染时间戳
        self._render_full_board()

    def _on_canvas_resize(self, event):
        """画布大小改变时重新计算并渲染

        [V0.4.2修复] 添加_is_updating标志，防止自定义起点期间重复渲染导致棋盘叠加
        [V0.4.3优化] 精简日志
        """
        # [V0.4.2核心修复] 如果正在更新中（如自定义起点），跳过resize渲染
        if getattr(self, '_is_updating', False):
            return  # 静默跳过，不输出日志

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

    def _generate_limited_board(self, board_id="limited_xun"):
        """生成限定棋盘布局（V0.4.2重构 - 使用插件化架构）

        [V0.4.2核心修改] 现在使用 boards/ 插件化架构，而非旧的 board_data.py 硬编码

        核心思路：
        1. 从 boards 包获取棋盘实例（自动注册机制）
        2. 调用 generate_layout() 获取完整布局数据
        3. 坐标数据直接来自棋盘插件，确保与变格配置一致

        参数:
            board_id: 棋盘ID（如 "limited_xun", "limited_requiem"）
        """
        # [V0.4.2重构] 使用插件化架构替代旧版 board_data.py
        try:
            from boards import get_board as boards_get_board
            board = boards_get_board(board_id)
            print(f"[V0.4.2-DEBUG] 成功加载棋盘插件: {board.display_name} (ID: {board.board_id})")
        except Exception as e:
            print(f"[错误] 无法从boards包加载棋盘 {board_id}: {e}")
            print(f"[回退] 使用默认棋盘（娜娜莉）")
            from boards import get_board as boards_get_board
            board = boards_get_board("limited_nanally")

        # 设置基本信息
        self.board_name = board.display_name
        self.board_type = board.board_type
        self.current_board_id = board_id
        self.board_id = board_id  # [V0.4.2新增] 保存board_id供后续使用

        # [关键修复] 重置cell_size为默认值
        self.cell_size = 32
        cs = self.cell_size

        # [V0.4.2核心] 调用插件的 generate_layout() 方法
        cell_positions, cell_types, cell_names, branch_entries = board.generate_layout()

        print("=" * 80)
        print(f"开始生成限定棋盘布局（V0.4.2插件化架构）")
        print(f"棋盘: {self.board_name} (ID: {board_id})")
        print(f"坐标数量: {len(cell_positions)}, 类型数量: {len(cell_types)}, 名称数量: {len(cell_names)}")
        print("=" * 80)

        # 构建屏幕坐标（将逻辑坐标转换为画布坐标）
        self.cell_positions = []
        self.cell_types = []
        self.cell_names = []

        for idx, ((row, col), ctype, cname) in enumerate(zip(cell_positions, cell_types, cell_names)):
            # 计算屏幕坐标
            x = col * cs + cs // 2
            y = row * cs
            self.cell_positions.append((x, y))
            self.cell_types.append(ctype)
            self.cell_names.append(cname)

            if idx < 55 or idx % 10 == 0:  # 只打印部分日志避免刷屏
                print(f"  [{idx:2d}] ({row:2d},{col:2d}) {cname} -> ({x}, {y}) [{ctype}]")

        # 计算分支信息
        self.total_cells = len(self.cell_types)
        self.main_path_len = 55  # 主路径固定55格（0-54）

        b1_start = 55  # 分支1起始索引
        b1_count = len(branch_entries.get("B1", {}).get("branch_cells", []))
        b2_start = b1_start + b1_count  # 分支2起始索引
        b2_count = len(branch_entries.get("B2", {}).get("branch_cells", []))

        print(f"\n[布局统计] 主路径: {self.main_path_len}格, 分支1: {b1_count}格, 分支2: {b2_count}格, 总计: {self.total_cells}格")

        # 创建格子编号映射数组
        self.cell_numbers = list(range(55))  # 主路径: 0-54
        self.cell_numbers.extend([f"B1-{i}" for i in range(b1_count)])  # 分支1
        self.cell_numbers.extend([f"B2-{i}" for i in range(b2_count)])  # 分支2

        # [V0.4.2修复] 使用插件提供的分支配置，确保与布局数据一致
        s_char_name = ""
        s_pool = board.get_s_pool()
        if s_pool:
            s_char_name = s_pool[0].get("name", "") if isinstance(s_pool[0], dict) else str(s_pool[0])

        b1_config = branch_entries.get("B1", {})
        b2_config = branch_entries.get("B2", {})

        self.branch_entries = {
            "s_character": {
                "name": f"S级角色区({s_char_name})",
                "entry_main_idx": b1_config.get("start_main_idx", 16),
                "skip_main_idx": b1_config.get("start_main_idx", 16) + 1,
                "exit_main_idx": b1_config.get("rejoin_main_idx", 18),
                "branch_start": b1_start,
                "branch_len": b1_count,
                "s_pos_in_branch": 0,
            },
            "skin_surprise": {
                "name": "皮肤惊喜区",
                "entry_main_idx": b2_config.get("start_main_idx", 43),
                "skip_main_idx": b2_config.get("start_main_idx", 43) + 1,
                "exit_main_idx": b2_config.get("rejoin_main_idx", 45),
                "branch_start": b2_start,
                "branch_len": b2_count,
            },
        }

        # 保存分支配置供其他方法使用
        self._plugin_branch_entries = branch_entries  # [V0.4.2新增]

        print(f"\n[棋盘信息] 当前加载: {self.board_name} (ID: {board_id})")
        print(f"[棋盘信息] S级角色: {s_char_name}")
        # 获取同行角色信息
        companions = board.get_companions()
        if companions:
            companion_names = [v for v in companions.values() if isinstance(v, str)]
            print(f"[棋盘信息] 同行角色: {companion_names}")

    def _generate_permanent_board(self):
        """生成常驻棋盘布局（使用board_data硬编码数据）"""
        # [V0.3-强制标记] 如果看到这行说明是最新版本
        print("\n" + "#" * 80)
        print("### [V0.3-最新版本] _generate_permanent_board() 被调用 ###")
        print("### 如果没看到这行，说明运行的是旧版代码！ ###")
        print("#" * 80 + "\n")

        # [V0.3-GUI弹窗] 强制显示版本信息
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "V0.3版本确认",
                "您正在运行最新版本的 _generate_permanent_board()\n\n"
                "如果看到此弹窗，说明代码已更新。\n"
                "点击确定继续..."
            )
            root.destroy()
        except Exception as e:
            print(f"[警告] 无法显示弹窗: {e}")

        import board_data

        try:
            config = board_data.get_board_config("permanent_default")
        except Exception as e:
            print(f"[错误] 无法获取常驻棋盘配置: {e}")
            return

        self.board_name = config["display_name"]
        self.board_type = config["board_type"]
        self.current_board_id = "permanent_default"

        # [关键修复] 重置cell_size为默认值
        self.cell_size = 32
        cs = self.cell_size

        companions = config.get("companions", {})
        s_character_names = config.get("s_character_names", [])

        def build_type_mapping():
            """动态构建类型映射表（支持常驻棋盘特殊格子）"""
            T = {
                "起点": "start",
                "学徒宝箱": "apprentice_chest",
                "勇者宝箱": "brave_chest",
                "迷迭棋盒（30个白色棋子）": "mist_box",
                "迷迭棋盒（50个白色棋子）": "mist_box",
                "失纬棋盒（4个金色棋子）": "lost_treasure_box",
                "失纬棋盒（16个金色棋子）": "lost_treasure_box",
                "弧光盲盒+沉眠池": "arcade_blind",
                "弧光盲盒": "arcade_blind",
                "再来一次+沉眠池": "roll_again",
                "多重惊喜": "multi_surprise",
            }

            # [V0.3修复] 添加常驻棋盘特殊同行标记的直接映射
            # 布局数据中使用中文描述，而companions配置中使用特殊标记
            T["于此同行（随机A级）"] = "companion"
            T["于此同行（随机S级）"] = "companion"

            for cell_idx, char_name in companions.items():
                cell_name = f"于此同行（{char_name}）"
                T[cell_name] = "companion"

            return T

        T = build_type_mapping()

        # [V0.3调试] 打印关键映射项
        print(f"\n[调试] 类型映射表大小: {len(T)}")
        test_keys = ["于此同行（随机A级）", "于此同行（随机S级）", "失纬棋盒（4个金色棋子）", "失纬棋盒（16个金色棋子）"]
        for key in test_keys:
            if key in T:
                print(f"  ✓ '{key}' → '{T[key]}'")
            else:
                print(f"  ✗ '{key}' 未找到!")
                # 检查是否有相似的key
                for t_key in T.keys():
                    if "同行" in t_key or "失纬" in t_key or "失玮" in t_key:
                        print(f"    相似: '{t_key}'")

        layout_data = config.get("layout")
        if not layout_data:
            print(f"[警告] 常驻棋盘没有布局数据")
            layout_data = board_data.get_permanent_board_layout()

        main_path_raw = layout_data["main_path"]
        branch1_raw = layout_data["branch1"]
        branch2_raw = layout_data["branch2"]

        print("=" * 80)
        print("开始生成常驻棋盘布局（基于board_data.py硬编码数据）")
        print(f"主路径: {len(main_path_raw)}格, 分支1: {len(branch1_raw)}格, 分支2: {len(branch2_raw)}格")
        print("=" * 80)

        # 构建最终数据
        self.cell_positions = []
        self.cell_types = []
        self.cell_names = []

        def append_parsed_data(data_list, label="路径"):
            """辅助函数：添加已解析的数据"""
            count = 0
            for row, col, name, idx in data_list:
                x = col * cs + cs // 2
                y = row * cs
                self.cell_positions.append((x, y))

                # [V0.3-最终修复] 使用关键词匹配替代精确字符串匹配
                # 解决可能的编码/缓存导致的字符不匹配问题
                mapped_type = None

                if "起点" in name:
                    mapped_type = "start"
                elif "同行" in name:          # 包含"于此同行"的所有变体
                    mapped_type = "companion"
                elif "失纬" in name or "失玮" in name:  # 兼容两种写法
                    mapped_type = "lost_treasure_box"
                elif "勇者宝箱" in name:
                    mapped_type = "brave_chest"
                elif "学徒宝箱" in name:
                    mapped_type = "apprentice_chest"
                elif "迷迭棋盒" in name:
                    mapped_type = "mist_box"
                elif "弧光盲盒" in name:
                    mapped_type = "arcade_blind"
                elif "再来一次" in name:
                    mapped_type = "roll_again"
                elif "多重惊喜" in name:
                    mapped_type = "multi_surprise"
                elif "今日穿搭" in name:
                    mapped_type = "today_outfit"
                elif "改装时刻" in name:
                    mapped_type = "vehicle_paint"
                elif "风向标" in name:
                    mapped_type = "glider_skin"
                else:
                    # 兜底
                    mapped_type = "apprentice_chest"
                    print(f"[警告-{label}] 格子{idx} '{name}' 使用默认类型")

                self.cell_types.append(mapped_type)
                self.cell_names.append(name)
                count += 1
            return count

        main_count = append_parsed_data(main_path_raw, "主路径")
        self.main_path_len = len(self.cell_types)
        b1_start = len(self.cell_types)
        b1_count = append_parsed_data(branch1_raw, "分支1")
        b2_start = len(self.cell_types)
        b2_count = append_parsed_data(branch2_raw, "分支2")

        self.total_cells = len(self.cell_types)

        # 创建格子编号映射数组
        self.cell_numbers = []
        for item in main_path_raw:
            self.cell_numbers.append(item[3])
        for i, item in enumerate(branch1_raw):
            self.cell_numbers.append(f"B1-{i}")
        for i, item in enumerate(branch2_raw):
            self.cell_numbers.append(f"B2-{i}")

        print(f"\n[常驻棋盘] 主路径: {main_count}格, 分支1: {b1_count}格, 分支2: {b2_count}格")
        print(f"[常驻棋盘] S级角色池: {s_character_names}")
        print(f"[常驻棋盘] 同行角色: {list(companions.values())}")

        # 分支元数据配置
        self.branch_entries = {
            "s_character": {
                "name": f"S级角色区(随机S级)",
                "entry_main_idx": 16,
                "skip_main_idx": 17,
                "exit_main_idx": 18,
                "branch_start": b1_start,
                "branch_len": b1_count,
                "s_pos_in_branch": 0,
            },
            "skin_surprise": {
                "name": "宝箱区(多重惊喜)",
                "entry_main_idx": 43,
                "skip_main_idx": 44,
                "exit_main_idx": 45,
                "branch_start": b2_start,
                "branch_len": b2_count,
            },
        }

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
        """绘制所有格子 - 增强版 v4.3（支持变格显示）

        [V0.4.2修复] 在绘制前先清除所有旧格子，避免叠加
        [V0.4.3优化] 精简日志，只保留关键诊断信息
        """
        import time

        # [V0.4.3新增] 绘制计数器和时间戳
        if not hasattr(self, '_draw_count'):
            self._draw_count = 0
            self._last_draw_time = 0

        self._draw_count += 1
        current_time = time.time()
        time_since_last = current_time - self._last_draw_time if self._last_draw_time > 0 else 0
        self._last_draw_time = current_time

        print(f"[_draw_grid_cells] #{self._draw_count} (距上次{time_since_last:.2f}s)")

        # [V0.4.2核心修复] 清除所有旧的格子图形（避免叠加）
        if hasattr(self, 'canvas') and self.canvas:
            before_count = len(self.canvas.find_all())
            # [V0.4.3核心修复] 使用delete("all")彻底清除
            self.canvas.delete("all")
            after_count = len(self.canvas.find_all())

            # [V0.4.3关键日志] 只在图形数量异常时输出（>0说明有残留）
            if after_count > 0:
                print(f"[_draw_grid_cells] 警告: delete('all')后仍有{after_count}个图形残留")

        half = self.cell_size // 2 - 2

        # [V0.4.2新增] 获取变格变换配置
        variant_transforms = get_variant_transforms(self.board_id)
        is_variant = getattr(self, 'is_variant', False)

        for idx, (cx, cy) in enumerate(self.cell_positions):
            cell_key = self.cell_types[idx]

            # [V0.4.2新增] 变格状态检测：替换格子类型和名称
            display_name = None
            if is_variant and variant_transforms:
                # 尝试通过索引查找（主路径用数字）
                cell_idx_key = idx
                # 也尝试分支格式（如 B1-0, B2-2 等）
                cell_branch_key = None
                if hasattr(self, 'cell_keys') and idx < len(self.cell_keys):
                    cell_branch_key = self.cell_keys[idx]

                transform = None
                for key in [cell_idx_key, cell_branch_key]:
                    if key is not None and key in variant_transforms:
                        transform = variant_transforms[key]
                        break

                if transform:
                    old_key = cell_key
                    cell_key = transform["variant"]
                    display_name = transform["variant_name"]

            style = self.CELL_STYLES.get(cell_key, self.CELL_STYLES["mist_box"])

            px, py = self._ox(cx), self._oy(cy)
            x1, y1 = px - half, py - half
            x2, y2 = px + half, py + half

            is_special = cell_key in ("companion", "multi_surprise")
            is_branch_point = self._is_branch_related(idx)
            is_variant_cell = display_name is not None  # [V0.4.2新增] 变格格子标记

            shadow_off = 3
            self.canvas.create_rectangle(
                x1 + shadow_off, y1 + shadow_off,
                x2 + shadow_off, y2 + shadow_off,
                fill="#aaa", outline="", tags=f"shadow_{idx}"
            )

            # [V0.4.3修改] 边框颜色：变格格子使用深橙色边框（与companion_s样式一致）
            if is_variant_cell:
                border_col = "#E64A19"  # 深橙红色（变格专用）
                border_wid = 3
            elif is_special:
                border_col = "#FFD700"
                border_wid = 3
            elif is_branch_point:
                border_col = "#E65100"
                border_wid = 2
            else:
                border_col = style["border"]
                border_wid = 2

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

            if cell_key == "companion" or cell_key == "companion_s":
                # [V0.4.2修复] 变格S级同行也显示心形图标（于此同行）
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
                # [V0.4.2修改] 变格格子显示变格名称，否则显示默认简称
                if display_name:
                    # 提取变格名称的关键部分（去掉"变"字后的前2个字符）
                    if "学徒宝箱变" in display_name:
                        short_display = "学变"
                    elif "勇者宝箱变" in display_name:
                        short_display = "勇变"
                    else:
                        short_display = display_name[:2]
                else:
                    short_name = style["short_name"]
                    short_display = short_name[:2]

                name_font = ("Microsoft YaHei", max(6, min(8, self.cell_size // 5)), "bold")
                # [V0.4.2新增] 变格格子使用橙色文字
                text_color_variant = "#FF6B00" if is_variant_cell else text_color
                self.canvas.create_text(
                    px, icon_y,
                    text=short_display, font=name_font,
                    fill=text_color_variant, tags=f"text_{idx}"
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

        # [V0.4.3已移除] 变格渲染完成汇总

    def _draw_player_piece(self):
        """绘制玩家棋子"""
        # [V0.4.3已移除详细诊断日志] _draw_player_piece正常执行
        for pid in self.piece_ids:
            self.canvas.delete(pid)
        self.piece_ids = []

        if not self.cell_positions or self.piece_pos_idx >= len(self.cell_positions):
            # [V0.4.3已移除] 警告日志
            return

        cx, cy = self.cell_positions[self.piece_pos_idx]
            # [V0.4.3已移除] 绘制位置诊断
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

        short_name = self.board_name
        if "限定棋盘(" in self.board_name or "限定棋盘（" in self.board_name:
            import re
            match = re.search(r'[（(](.+?)[)）]', self.board_name)
            if match:
                short_name = match.group(1)

        title_text = f"{icon} {short_name}" if icon else short_name

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
        """渲染棋盘（V0.4.3简洁版）"""
        # 清除并重绘
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.delete("all")

        if not self.cell_positions:
            return

        # [V0.4.3核心修复] 获取变格变换配置（v5.0版本必须在此处处理）
        variant_transforms = get_variant_transforms(self.board_id)
        is_variant = getattr(self, 'is_variant', False)

        # [V0.4.3已移除] 变格状态诊断日志

        cs = self.cell_size
        half = cs // 2

        for idx, (pos, cell_type) in enumerate(zip(self.cell_positions, self.cell_types)):
            x, y = pos
            ox = x + self.offset_x
            oy = y + self.offset_y

            # [V0.4.3新增] v5版本变格检测：替换格子类型
            display_name = None
            actual_cell_type = cell_type  # 默认使用原始类型

            if is_variant and variant_transforms:
                # 尝试多种key格式匹配（数字索引 + 分支标识符）
                candidate_keys = [idx]
                if 55 <= idx <= 63:
                    candidate_keys.append(f"B1-{idx - 55}")
                elif 64 <= idx <= 72:
                    candidate_keys.append(f"B2-{idx - 64}")

                for key in candidate_keys:
                    if key in variant_transforms:
                        transform = variant_transforms[key]
                        actual_cell_type = transform["variant"]
                        display_name = transform["variant_name"]
                        if idx < 20:  # 变格格子静默处理，不输出日志
                            pass
                        break

            # [V0.4.3已移除] 逐格渲染诊断日志

            style = self.CELL_STYLES.get(actual_cell_type, self.CELL_STYLES["apprentice_chest"])
            color = style["color"]
            # [V0.4.3新增] 变格格子边框颜色
            border = style["border"]
            border_wid = 2
            if display_name is not None:
                border = "#E64A19"  # 深橙红色（变格专用）
                border_wid = 3

            x1, y1 = ox - half + 2, oy - half + 2
            x2, y2 = ox + half - 2, oy + half - 2

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color, outline=border, width=border_wid,
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
                # [V0.5.5修复] 分支格子显示本地编号（B1-0 ~ B1-8、B2-0 ~ B2-8），
                # 主路径仍显示数字索引，避免分支2在变格/常态下都显示成全局序号。
                if hasattr(self, 'cell_numbers') and idx < len(self.cell_numbers):
                    num_text = str(self.cell_numbers[idx])
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

        # 棋盘名称文字 - 只显示角色名
        import re
        board_short = self.board_name
        if "限定棋盘(" in self.board_name or "限定棋盘（" in self.board_name:
            match = re.search(r'[（(](.+?)[)）]', self.board_name)
            if match:
                board_short = match.group(1)
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
            print(f"[animate_roll] [警告] is_animating已是True，动画被跳过!")
            print(f"[animate_roll] piece_pos_idx={self.piece_pos_idx}, 可能导致卡死")
            return
        self.is_animating = True

        # [V0.4.3已移除] animate_roll内部参数日志

        # 使用强制目标位置或自动计算
        if target_idx_override is not None:
            target_idx = target_idx_override
            current_in_branch = (self.piece_pos_idx >= 55)  # 当前是否在分支内
            is_leaving_branch = (current_in_branch and target_idx < 55 and branch_exit_info)

            if target_idx >= 55:
                # 目标在分支内：使用完整的骰子点数
                steps = dice_value
            elif is_leaving_branch:
                # 从分支离开到主路径：两段式移动
                steps = dice_value
            else:
                # 目标在主路径上：使用骰子点数作为步数
                steps = dice_value
        else:
            target_idx = self._cycle_pos(self.piece_pos_idx, dice_value)
            steps = dice_value

        # [V0.4.3已移除] 详细走棋日志输出

        # 动画参数
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

                        # 仅在段1最后一步处理跳转
                        if i == steps_in_branch_to_exit - 1 and temp_idx >= branch_end_local:
                            pass  # 到达分支末尾，下步跳转
                    elif i == steps_in_branch_to_exit:
                        # 关键一步：跳转到出口（段1结束，段2开始）
                        temp_idx = exit_main_local
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
        """
        获取可用棋盘列表（动态从board_data.py读取）
        
        扩展方式：
        1. 当前模式：在board_data.py的BOARDS_REGISTRY中添加配置
        2. 未来模式：在boards/目录下新建文件夹，放入对应资源文件
        
        返回:
            棋盘信息列表，每个元素包含：
            - id: 棋盘ID（如 "limited_xun"）
            - name: 显示名称
            - type: 棋盘类型（"limited"/"permanent"）
            - description: 描述信息
        """
        try:
            import board_data
            
            dynamic_boards = []
            
            for board_id in board_data.get_available_boards():
                try:
                    config = board_data.get_board_config(board_id)
                    
                    dynamic_boards.append({
                        "id": board_id,
                        "name": config["display_name"],
                        "type": config["board_type"],
                        "description": cls._generate_board_description(config),
                        # [新增] 是否可用（用于UI禁用未开放的棋盘）
                        "enabled": config.get("enabled", True),  # 默认可用
                    })
                except Exception as e:
                    print(f"[警告] 无法加载棋盘 {board_id}: {e}")
                    continue
            
            if not dynamic_boards:
                print("[警告] 未找到任何棋盘配置，使用默认配置")
                return cls._get_default_boards()
            
            return dynamic_boards
            
        except ImportError:
            print("[警告] 无法导入board_data模块，使用默认配置")
            return cls._get_default_boards()
        except Exception as e:
            print(f"[错误] 读取棋盘配置失败: {e}")
            return cls._get_default_boards()
    
    @classmethod
    def _generate_board_description(cls, config):
        """根据棋盘配置生成描述信息"""
        parts = []
        
        board_type = config.get("board_type", "")
        if board_type == "limited":
            s_char = config.get("s_character_name", "")
            if s_char:
                parts.append(f"S级角色: {s_char}")
            parts.append("含限定角色和皮肤分支")
        elif board_type == "permanent":
            parts.append("常驻奖励棋盘")
        
        a_pool_main = config.get("a_pool_main_names", [])
        if a_pool_main:
            parts.append(f"A级主池: {', '.join(a_pool_main[:3])}{'...' if len(a_pool_main) > 3 else ''}")
        
        return " | ".join(parts) if parts else "基础奖励棋盘"
    
    @classmethod
    def _get_default_boards(cls):
        """默认棋盘配置（当无法从board_data.py读取时使用）"""
        return [
            {
                "id": "limited_nanally",
                "name": "限定棋盘（娜娜莉）",
                "type": "limited",
                "description": "限时角色娜娜莉专属棋盘，含S级角色和皮肤分支",
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
        """切换棋盘（动态版本 - 支持多棋盘切换）
        
        参数:
            board_id: 目标棋盘ID（如 "limited_xun", "limited_requiem"）
        
        [关键] 第三层防护：最终安全检查，确保不会切换到未开放的棋盘
        """
        # [关键] 第三层防护：最终安全检查（即使前两层都被绕过）
        try:
            import board_data
            config = board_data.get_board_config(board_id)
            
            # 检查是否启用
            if not config.get("enabled", True):
                print(f"[错误] 尝试切换到未开放的棋盘: {board_id}，操作被阻止")
                
                # 不执行任何切换操作
                return False
                
        except Exception as e:
            print(f"[警告] 检查棋盘状态失败: {e}，允许继续（向后兼容）")
        
        self.canvas.delete("all")

        if board_id == "permanent":
            self._generate_permanent_board()
        else:
            self._generate_limited_board(board_id)

        # 重新计算画布尺寸（基于新棋盘的坐标数据）
        self._calc_canvas_size()
        
        # [关键] 检查当前窗口大小，如果窗口已最大化或较大，则触发自适应调整
        # 这确保切换棋盘后，如果之前窗口被放大过，新棋盘也能正确自适应
        if hasattr(self, 'canvas') and self.canvas:
            current_w = self.canvas.winfo_width()
            current_h = self.canvas.winfo_height()
            
            if current_w > 100 and current_h > 100:
                # 保存当前窗口大小作为目标尺寸
                self.target_canvas_w = current_w
                self.target_canvas_h = current_h
                
                # 触发自适应计算（根据实际窗口大小调整cell_size）
                self._calc_adaptive_size()
        
        # 应用最终计算的画布尺寸
        self.canvas.config(width=self.canvas_w, height=self.canvas_h)

        # 重置游戏状态
        self.piece_pos_idx = 0
        self.highlight_id = None
        self.dice_display_id = None
        self.dice_text_id = None

        # [V0.4.2新增] 同步变格状态到棋盘画布（用于渲染变格格子）
        if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
            self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
            self.board_canvas.board_id = board_id  # 确保board_id正确传递

        # 重新渲染整个棋盘
        self._render_full_board()

        # [V0.3新增] 常驻棋盘隐藏皮肤标签页（无装扮礼遇系统）
        try:
            import board_data
            config = board_data.get_board_config(board_id)
            board_type = config.get("board_type", "limited")

            if hasattr(self, 'collection_notebook'):
                if board_type == "permanent":
                    # 常驻棋盘：隐藏"皮肤"标签页
                    tabs = self.collection_notebook.tabs()
                    for tab in tabs:
                        if self.collection_notebook.tab(tab, "text") == "皮肤":
                            self.collection_notebook.hide(tab)
                            break
                else:
                    # 限定棋盘：显示所有标签页（包括皮肤）
                    tabs = self.collection_notebook.tabs()
                    for tab in tabs:
                        self.collection_notebook.add(tab)
        except Exception as e:
            print(f"[警告] 更新皮肤标签页可见性失败: {e}")


class RechargeDialog(tk.Toplevel):
    """充值弹窗：选择套餐并支付人民币购买环石"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("充值购买环石")
        self.geometry("360x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + (pw - 360) // 2
        y = py + (ph - 420) // 2
        self.geometry(f"+{x}+{y}")

        from board_data import get_all_recharge_packs

        content = tk.Frame(self, bg="#FAFAFA")
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(content, text="选择充值套餐", font=("Microsoft YaHei", 13, "bold"),
                 bg="#FAFAFA", fg="#333").pack(anchor=tk.W, pady=(0, 8))

        dm = app.engine.state.dice_manager
        total_label = tk.Label(content, text=f"累计充值: {dm.total_recharged_rmb:.2f} 元",
                               font=("Microsoft YaHei", 10), bg="#FAFAFA", fg="#1976D2")
        total_label.pack(anchor=tk.W, pady=(0, 10))

        packs = get_all_recharge_packs()
        if not packs:
            tk.Label(content, text="未找到充值套餐配置\n请检查 充值信息.csv 文件",
                     font=("Microsoft YaHei", 10), bg="#FAFAFA", fg="#999").pack(expand=True)
            tk.Button(content, text="关闭", command=self.destroy, font=("Microsoft YaHei", 11),
                      bg="#E0E0E0", relief=tk.FLAT, padx=20, pady=5).pack(pady=12)
            return

        container = tk.Frame(content, bg="#FAFAFA")
        container.pack(fill=tk.BOTH, expand=True)

        def do_recharge(pack):
            rmb = pack["rmb_price"]
            stones = pack["total_stones"]
            # [V0.5.4修复] 充值前先把UI输入框中的骰子/环石数值同步到DiceManager，
            # 避免玩家输入后未触发同步就直接充值，导致刷新时把输入框清零。
            app._sync_dice_inputs_to_manager(dm)
            print(f"[充值调试-前] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone} "
                  f"无限红={dm.infinite_red} 无限蓝={dm.infinite_blue}")
            if dm.recharge(rmb, stones):
                print(f"[充值调试-recharge后] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone}")
                app.total_rmb_var.set(f"{dm.total_recharged_rmb:.2f}")
                app.ring_stone_var.set(str(dm.ring_stone))
                print(f"[充值调试-刷新前] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone}")
                app._refresh_all()
                print(f"[充值调试-刷新后] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone}")
                messagebox.showinfo("充值成功",
                    f"支付 {rmb:.0f} 元\n获得 {stones} 环石\n当前环石: {dm.ring_stone}", parent=self)
                self.destroy()
            else:
                messagebox.showerror("充值失败", "充值处理失败，请重试", parent=self)

        for pack in packs:
            # [V0.5.2修复] 按钮只显示基础充值数量，加赠单独标注在旁
            text = f"{pack['rmb_price']:.0f}元  →  {pack['ring_stones']}环石"
            if pack["bonus_stones"] > 0:
                text += f"  (+{pack['bonus_stones']}环石)"

            tk.Button(container, text=text, font=("Microsoft YaHei", 11),
                      bg="#FFF", activebackground="#FFF3E0",
                      relief=tk.RIDGE, bd=1, cursor="hand2",
                      command=lambda p=pack: do_recharge(p)).pack(fill=tk.X, pady=4, ipady=6)

        tk.Button(content, text="关闭", command=self.destroy,
                  font=("Microsoft YaHei", 11), bg="#E0E0E0", relief=tk.FLAT,
                  padx=20, pady=5).pack(pady=(12, 0))


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
        # [修复] 传递默认棋盘ID，确保初始奖励池正确
        self.engine = GameEngine("limited_nanally")
        print(f"[main.__init__] 初始引擎: gacha.board_type={self.engine.gacha.board_type}, gacha.board_id={self.engine.gacha.board_id}")
        self.root = tk.Tk()
        self.root.title("异环抽卡模拟器 v1.2.1")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)

        # [保护性措施] 抽卡状态管理
        self.is_rolling = False  # 是否正在进行抽卡（单次或十连）
        self.btn_roll_single = None  # 单次抽卡按钮引用
        self.btn_roll_ten = None  # 十连抽按钮引用

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

        # [V0.4.1新增] 数字输入验证：只允许输入0-9（必须在root创建后调用）
        vcmd = (self.root.register(self._validate_number_input), "%P")

        row0 = tk.Frame(f)
        row0.pack(fill=tk.X, pady=1)
        tk.Label(row0, text="红骰:", font=("Microsoft YaHei", 9),
                  width=5).pack(side=tk.LEFT)
        self.red_dice_var = tk.StringVar(value="")
        self.red_dice_entry = tk.Entry(row0, textvariable=self.red_dice_var,
                                         width=9, font=("Microsoft YaHei", 9),
                                         validate="key", validatecommand=vcmd)
        self.red_dice_entry.pack(side=tk.LEFT, padx=2)
        # [V0.5.4修复] 输入框失去焦点或回车时自动同步到DiceManager，避免未同步导致刷新清零
        self.red_dice_entry.bind("<FocusOut>", self._on_dice_entry_commit)
        self.red_dice_entry.bind("<Return>", self._on_dice_entry_commit)
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
                                          validate="key", validatecommand=vcmd)
        self.blue_dice_entry.pack(side=tk.LEFT, padx=2)
        # [V0.5.4修复] 输入框失去焦点或回车时自动同步到DiceManager，避免未同步导致刷新清零
        self.blue_dice_entry.bind("<FocusOut>", self._on_dice_entry_commit)
        self.blue_dice_entry.bind("<Return>", self._on_dice_entry_commit)
        self.blue_inf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text="无限",
                        variable=self.blue_inf_var,
                        font=("Microsoft YaHei", 8),
                        command=self._on_dice_setting_change).pack(side=tk.LEFT)

        row2 = tk.Frame(f)
        row2.pack(fill=tk.X, pady=1)
        tk.Label(row2, text="环石:", font=("Microsoft YaHei", 9),
                  width=5).pack(side=tk.LEFT)
        self.ring_stone_var = tk.StringVar(value="0")
        self.ring_stone_entry = tk.Entry(row2, textvariable=self.ring_stone_var,
                                           width=9, font=("Microsoft YaHei", 9),
                                           validate="key", validatecommand=vcmd)
        self.ring_stone_entry.pack(side=tk.LEFT, padx=2)
        # [V0.5.4修复] 输入框失去焦点或回车时自动同步到DiceManager，避免未同步导致刷新清零
        self.ring_stone_entry.bind("<FocusOut>", self._on_dice_entry_commit)
        self.ring_stone_entry.bind("<Return>", self._on_dice_entry_commit)
        tk.Label(row2, text=" (160/骰)",
                  font=("Microsoft YaHei", 7), fg="#999").pack(side=tk.LEFT)

        # 累计充值金额显示 + 充值按钮
        self._rmb_frame = tk.Frame(f)
        self._rmb_frame.pack(fill=tk.X, pady=1)

        tk.Label(self._rmb_frame, text="累计充值:", font=("Microsoft YaHei", 9),
                  width=7).pack(side=tk.LEFT)
        self.total_rmb_var = tk.StringVar(value="0.00")
        tk.Label(self._rmb_frame, textvariable=self.total_rmb_var,
                  font=("Microsoft YaHei", 9), fg="#1976D2").pack(side=tk.LEFT)
        tk.Label(self._rmb_frame, text=" 元",
                  font=("Microsoft YaHei", 9), fg="#1976D2").pack(side=tk.LEFT)

        # 充值按钮
        self.btn_recharge = ttk.Button(
            self._rmb_frame,
            text="充值",
            command=self._on_recharge_click,
            width=6
        )
        self.btn_recharge.pack(side=tk.RIGHT, padx=(5, 0))

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

        # [优化] 使用Combobox替代Radiobutton，支持更多棋盘且节省空间
        # 按类型分组显示（限定棋盘 / 常驻棋盘）
        board_values = []
        board_display = []  # 用于Combobox显示的文本
        self._board_enabled_status = {}  # [新增] 记录每个选项的可用状态

        for board in boards:
            board_values.append(board["id"])
            # 添加类型前缀便于识别
            type_prefix = "★" if board["type"] == "limited" else "♥"
            
            # [新增] 根据是否可用添加标记
            is_enabled = board.get("enabled", True)
            if not is_enabled:
                display_text = f"{type_prefix} {board['name']}（暂未开放）"
            else:
                display_text = f"{type_prefix} {board['name']}"
            
            board_display.append(display_text)
            
            # [新增] 记录每个选项的可用状态
            self._board_enabled_status[display_text] = is_enabled

        # [修复] 初始值应该使用显示文本，而不是board_id
        # 优先选择第一个可用的限定棋盘
        default_board_id = "limited_nanally"
        if default_board_id in board_values:
            default_index = board_values.index(default_board_id)
        else:
            # 如果默认棋盘不存在，找第一个可用的棋盘
            default_index = next(
                (i for i, b in enumerate(boards) if b.get("enabled", True)),
                0
            )
        self.board_var = tk.StringVar(value=board_display[default_index])

        # 创建下拉框
        self.board_combo = ttk.Combobox(
            f,
            textvariable=self.board_var,
            values=board_display,
            state="readonly",
            font=("Microsoft YaHei", 9),
            width=20,
        )
        self.board_combo.pack(fill=tk.X, pady=(0, 4))
        
        # 存储board_id到显示文本的映射
        self._board_id_to_display = dict(zip(board_values, board_display))
        self._display_to_board_id = dict(zip(board_display, board_values))
        self._board_info_cache = {b["id"]: b for b in boards}

        # 绑定选择事件
        self.board_combo.bind("<<ComboboxSelected>>", self._on_board_combo_change)

        # 当前棋盘描述标签
        self.board_desc_var = tk.StringVar(value=self._get_board_description("limited_nanally"))
        desc_label = tk.Label(
            f,
            textvariable=self.board_desc_var,
            font=("Microsoft YaHei", 8),
            fg="#666",
            bg="#F0F0F0",
            wraplength=180,  # 自动换行
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, fill=tk.X)

    def _get_board_description(self, board_id):
        """获取棋盘描述信息"""
        board_info = self._board_info_cache.get(board_id)
        if not board_info:
            return "未知棋盘"
        return board_info.get("description", "")

    def _on_board_combo_change(self, event=None):
        """Combobox选择变化时的处理"""
        selected_display = self.board_var.get()
        
        # [关键] 第一层防护：检查是否选择了不可用的棋盘
        if hasattr(self, '_board_enabled_status'):
            is_enabled = self._board_enabled_status.get(selected_display, True)
            if not is_enabled:
                # [强制] 阻止切换到未开放的棋盘
                # 使用 warning 级别提示（比 info 更醒目）
                messagebox.showwarning(
                    "功能暂未开放",
                    f"\n「{selected_display}」\n\n"
                    f"该棋盘暂未开放，请等待官方发布相关信息。\n"
                    f"当前仍使用原有棋盘。\n"
                )
                
                # [关键] 强制恢复到上一个有效选择（不依赖事件循环）
                current_board_id = getattr(self.board_canvas, 'current_board_id', 'limited_xun')
                current_display = self._board_id_to_display.get(current_board_id)
                if current_display and current_display != selected_display:
                    self.board_var.set(current_display)
                
                # [重要] 阻止所有后续操作
                return False  # 返回False表示被阻止
        
        new_board_id = self._display_to_board_id.get(selected_display)

        if new_board_id and new_board_id != getattr(self.board_canvas, 'current_board_id', None):
            # 更新描述
            self.board_desc_var.set(self._get_board_description(new_board_id))
            
            # 调用原有的切换逻辑
            self._on_board_change()
            
        return True  # 正常执行

    def _build_operation_panel(self, parent):
        f = ttk.LabelFrame(parent, text="操作", padding=6)
        f.pack(fill=tk.X, pady=(0, 4))

        btn_font = ("Microsoft YaHei", 12, "bold")
        self.btn_roll_single = ttk.Button(f, text="? 1 抽", style="Big.TButton",
                    command=self._on_single_roll)
        self.btn_roll_single.pack(fill=tk.X, pady=3)
        self.btn_roll_ten = ttk.Button(f, text="? 10 抽", style="Big.TButton",
                    command=self._on_ten_roll)
        self.btn_roll_ten.pack(fill=tk.X, pady=3)
        ttk.Button(f, text="重置全部",
                    command=self._on_reset).pack(fill=tk.X, pady=3)

        style = ttk.Style()
        style.configure("Big.TButton", font=btn_font, padding=8)

    def _build_collection_panel(self, parent):
        f = ttk.LabelFrame(parent, text="已获得", padding=4)
        f.pack(fill=tk.BOTH, expand=True)

        nb = ttk.Notebook(f)
        nb.pack(fill=tk.BOTH, expand=True)
        self.collection_notebook = nb  # [V0.3新增] 保存引用，用于常驻棋盘隐藏皮肤标签页

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

    # ===== 氪金系统UI回调 =====

    def _on_recharge_click(self):
        """充值按钮点击事件处理 - 打开充值弹窗"""
        RechargeDialog(self.root, self)

    def _enable_recharge_system(self):
        """启用氪金系统UI（充值按钮和累计充值显示）"""
        self._rmb_frame.pack(fill=tk.X, pady=1)
        self.btn_recharge.config(state=tk.NORMAL)
        print("[系统] 氪金系统已启用")

    def _disable_recharge_system(self):
        """禁用氪金系统UI"""
        self._rmb_frame.pack_forget()
        self.btn_recharge.config(state=tk.DISABLED)
        print("[系统] 氪金系统已禁用")

    def _lock_roll_buttons(self):
        """[保护性措施] 锁定抽卡按钮，防止重复点击"""
        self.is_rolling = True
        if self.btn_roll_single:
            self.btn_roll_single.config(state=tk.DISABLED)
        if self.btn_roll_ten:
            self.btn_roll_ten.config(state=tk.DISABLED)
        print(f"[保护性措施] 抽卡按钮已锁定")

    def _unlock_roll_buttons(self):
        """[保护性措施] 解锁抽卡按钮"""
        self.is_rolling = False
        if self.btn_roll_single:
            self.btn_roll_single.config(state=tk.NORMAL)
        if self.btn_roll_ten:
            self.btn_roll_ten.config(state=tk.NORMAL)
        print(f"[保护性措施] 抽卡按钮已解锁")

    def _handle_hard_pity_result(self, result):
        """
        [V0.4.2新增] 处理硬保底结果（不移动棋子，直接显示奖励）

        参数:
            result: execute_hard_pity()返回的结果字典
        """

        # 1. 解锁按钮
        self._unlock_roll_buttons()

        # [V0.4.3修复] 先获取rewards，再使用（修复UnboundLocalError）
        rewards = result.get("rewards", [])

        # 2. 显示奖励弹窗
        if rewards:
            reward_text = "【89抽硬保底】\n\n"
            for r in rewards:
                if r["type"] == "s_character":
                    dup_mark = " (重复)" if r.get("is_duplicate") else ""
                    reward_text += f"S级角色: {r['name']}{dup_mark}\n"
                    if r.get("extra_white", 0) > 0:
                        reward_text += f"  +{r['extra_white']}白色棋子\n"
                    if r.get("extra_gold", 0) > 0:
                        reward_text += f"  +{r['extra_gold']}金色棋子\n"

            messagebox.showinfo("硬保底奖励", reward_text)
        else:
            pass  # 没有奖励数据

        # 3. 记录日志
        self.log_text.insert(tk.END, f"[系统] 89抽硬保底触发！获得S级角色\n", "highlight")
        for r in rewards:
            if r["type"] == "s_character":
                dup_str = "(重复)" if r.get("is_duplicate") else ""
                self.log_text.insert(
                    tk.END,
                    f"  -> S级角色: {r['name']} {dup_str}\n",
                    "s_character" if not r.get("is_duplicate") else "duplicate"
                )

        # [V0.4.3修复] 同步更新棋盘变格状态（垫刀数清零 → 关闭变格显示）
        if hasattr(self, 'board_canvas') and self.board_canvas:
            old_variant = getattr(self.board_canvas, 'is_variant', False)
            self.board_canvas.is_variant = self.engine.state.is_variant  # 从引擎同步
            if old_variant and not self.board_canvas.is_variant:
                print(f"[硬保底-UI处理] 棋盘变格状态已关闭: True -> False (将重绘)")
                # 重新渲染棋盘以更新变格显示
                self.board_canvas._render_full_board()

        # 4. 更新统计显示
        self._refresh_all()

        # 5. 滚动日志到底部
        self.log_text.see(tk.END)

    def _stop_rolling_if_needed(self):
        """
        [保护性措施] 如果正在抽卡，停止并提示用户

        返回:
            bool: 是否成功停止（False表示用户取消操作）
        """
        if not self.is_rolling:
            return True  # 没有在抽卡，可以直接执行

        print(f"[保护性措施] 检测到正在抽卡，准备停止...")

        # 停止动画
        if hasattr(self, 'board_canvas') and self.board_canvas:
            self.board_canvas.is_animating = False

        # 解锁按钮
        self._unlock_roll_buttons()

        # 提示用户
        result = messagebox.askyesno(
            "抽卡进行中",
            "当前正在进行抽卡操作。\n\n"
            "是否强制停止并继续当前操作？\n"
            "(注意：当前抽卡进度将丢失)"
        )

        if result:
            print(f"[保护性措施] 用户确认停止抽卡")
            return True
        else:
            print(f"[保护性措施] 用户取消操作")
            # 重新锁定（因为实际上没有停止）
            self._lock_roll_buttons()
            return False

    def _on_board_change(self):
        """切换棋盘的确认逻辑"""
        # [保护性措施] 检查是否正在抽卡
        if not self._stop_rolling_if_needed():
            return  # 用户取消操作

        if not hasattr(self, 'board_canvas'):
            return

        # [修复] 从Combobox显示文本转换为board_id
        selected_display = self.board_var.get()
        
        # [关键] 第二层防护：硬性阻断未开放的棋盘（即使绕过第一层）
        if hasattr(self, '_board_enabled_status'):
            is_enabled = self._board_enabled_status.get(selected_display, True)
            if not is_enabled:
                messagebox.showerror(
                    "操作被阻止",
                    f"\n无法切换到「{selected_display}」\n\n"
                    f"原因：该棋盘暂未开放\n"
                    f"请选择其他可用棋盘。\n"
                )
                
                # 强制恢复到默认棋盘
                default_display = self._board_id_to_display.get("limited_nanally")
                if default_display:
                    self.board_var.set(default_display)
                
                return  # 硬性终止
        
        new_board_id = self._display_to_board_id.get(selected_display, selected_display)

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
            # [V0.4.1修复] 先同步textbox中的骰子数量到dice_manager（避免保存时读到旧值）
            self._on_dice_setting_change()

            # [V0.4.1修复] 保存当前骰子数量（切换棋盘不应影响骰子）
            # [V0.5.2修复] 同时保存累计充值/消费数据
            old_dm = self.engine.state.dice_manager
            saved_dice = {
                "red": old_dm.red_dice,
                "blue": old_dm.blue_dice,
                "ring": old_dm.ring_stone,
                "inf_red": old_dm.infinite_red,
                "inf_blue": old_dm.infinite_blue,
                "inf_ring": old_dm.infinite_ring,
                "total_recharged_rmb": old_dm.total_recharged_rmb,
                "total_consumed_ring_stones": old_dm.total_consumed_ring_stones,
                "recharge_history": list(old_dm.recharge_history),
            }
            # [V0.4.1调试-已验证] print(f"[switch_board] 保存骰子: 红={saved_dice['red']}, 蓝={saved_dice['blue']}, "
            #       f"环石={saved_dice['ring']}, 无限红={saved_dice['inf_red']}, 无限蓝={saved_dice['inf_blue']}")

            self.board_canvas.switch_board(new_board_id)
            # [修复] 传递当前棋盘ID给GameEngine，确保奖励池正确加载
            self.engine = GameEngine(new_board_id)
            self.board_canvas.engine = self.engine

            # [V0.4.1修复] 恢复骰子数量
            # [V0.5.2修复] 同时恢复累计充值/消费数据
            new_dm = self.engine.state.dice_manager
            new_dm.red_dice = saved_dice["red"]
            new_dm.blue_dice = saved_dice["blue"]
            new_dm.ring_stone = saved_dice["ring"]
            new_dm.infinite_red = saved_dice["inf_red"]
            new_dm.infinite_blue = saved_dice["inf_blue"]
            new_dm.infinite_ring = saved_dice["inf_ring"]
            new_dm.total_recharged_rmb = saved_dice["total_recharged_rmb"]
            new_dm.total_consumed_ring_stones = saved_dice["total_consumed_ring_stones"]
            new_dm.recharge_history = saved_dice["recharge_history"]

            # [V0.4.1调试-已验证] 验证恢复结果
            # print(f"[switch_board] 恢复后验证: 红={new_dm.red_dice}, 蓝={new_dm.blue_dice}, "
            #       f"环石={new_dm.ring_stone}, 无限红={new_dm.infinite_red}, 无限蓝={new_dm.infinite_blue}")
            # print(f"[switch_board] 切换后: gacha.board_type={self.engine.gacha.board_type}, board_id={new_board_id}")
            self._refresh_all()
            self.status_var.set(f"已切换到: {board_info['name']}")
        else:
            # [V0.5.4修复] 用户取消切换时，恢复下拉框和描述到当前实际棋盘
            # 避免界面显示新棋盘但底层仍是旧棋盘，导致视觉/逻辑不一致
            current_board_id = getattr(self.board_canvas, 'current_board_id', 'limited_xun')
            current_display = self._board_id_to_display.get(current_board_id)
            if current_display:
                self.board_var.set(current_display)
            self.board_desc_var.set(self._get_board_description(current_board_id))

    def _validate_number_input(self, new_value):
        """[V0.4.1新增] 验证输入是否为纯数字（允许空字符串）"""
        if new_value == "":
            return True  # 允许清空
        return new_value.isdigit()  # 只允许0-9

    def _on_dice_entry_commit(self, event=None):
        """[V0.5.4新增] 骰子/环石输入框失去焦点或按回车时，自动同步到DiceManager"""
        self._sync_dice_inputs_to_manager()
        self._refresh_all()

    def _sync_dice_inputs_to_manager(self, dm=None):
        """[V0.5.2新增] 将UI输入框中的骰子/环石数值同步到DiceManager"""
        if dm is None:
            dm = self.engine.state.dice_manager

        print(f"[_sync_dice_inputs_to_manager-入口] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone} "
              f"red_var='{self.red_dice_var.get()}' blue_var='{self.blue_dice_var.get()}' ring_var='{self.ring_stone_var.get()}'")

        is_inf = self.red_inf_var.get()
        dm.infinite_red = is_inf
        if is_inf:
            self.red_dice_entry.config(state=tk.DISABLED)
        else:
            self.red_dice_entry.config(state=tk.NORMAL)

        # [V0.5.3修复] 始终同步输入框数值到DiceManager，仅在空值时用DiceManager回填。
        # 无限模式只控制是否扣减，不应导致玩家输入的骰子数量丢失。
        raw = self.red_dice_var.get().strip()
        if raw == "":
            self.red_dice_var.set(str(dm.red_dice))
        else:
            try:
                dm.red_dice = max(0, int(raw))
            except ValueError:
                dm.red_dice = 0

        is_blue_inf = self.blue_inf_var.get()
        dm.infinite_blue = is_blue_inf
        if is_blue_inf:
            self.blue_dice_entry.config(state=tk.DISABLED)
        else:
            self.blue_dice_entry.config(state=tk.NORMAL)

        # [V0.5.3修复] 蓝骰与红骰保持一致：无限模式不扣减，但保留输入数量
        raw = self.blue_dice_var.get().strip()
        if raw == "":
            self.blue_dice_var.set(str(dm.blue_dice))
        else:
            try:
                dm.blue_dice = max(0, int(raw))
            except ValueError:
                dm.blue_dice = 0

        # [V0.5新增] 环石输入同步（关闭无限模式，采用输入值）
        dm.infinite_ring = False
        raw = self.ring_stone_var.get().strip()
        if raw == "":
            self.ring_stone_var.set(str(dm.ring_stone))
        else:
            try:
                dm.ring_stone = max(0, int(raw))
            except ValueError:
                dm.ring_stone = 0

        print(f"[_sync_dice_inputs_to_manager-出口] 红={dm.red_dice} 蓝={dm.blue_dice} 环石={dm.ring_stone}")

    def _on_dice_setting_change(self):
        self._sync_dice_inputs_to_manager()
        self._refresh_all()

    def _on_single_roll(self):
        # [V0.4.3已移除详细入口日志]
        try:
            self._on_single_roll_impl()
        except Exception as e:
            print(f"\n[错误-致命] _on_single_roll发生未捕获异常: {e}")
            import traceback
            traceback.print_exc()
            # 确保解锁按钮，避免程序卡死
            try:
                self._unlock_roll_buttons()
                self.board_canvas.is_animating = False
            except:
                pass

    def _on_single_roll_impl(self):
        # [保护性措施] 检查是否正在抽卡
        if self.is_rolling:
            print(f"[保护性措施] 单次抽卡被忽略：正在进行中的抽卡")
            return

        # [保护性措施] 锁定按钮
        self._lock_roll_buttons()

        # 安全检查：如果动画状态卡住，强制重置
        if self.board_canvas.is_animating:
            print(f"[警告] _on_single_roll: 检测到is_animating=True，强制重置")
            self.board_canvas.is_animating = False

        dm = self.engine.state.dice_manager

        # [V0.3新增] 根据当前棋盘类型决定使用哪种骰子
        current_board_id = getattr(self.board_canvas, 'current_board_id', 'limited_xun')
        try:
            import board_data
            board_config = board_data.get_board_config(current_board_id)
            board_type = board_config.get("board_type", "limited")
        except Exception:
            board_type = "limited"

        # 常驻棋盘使用蓝色骰子，限定棋盘使用红色骰子
        dice_type_to_use = "blue" if board_type == "permanent" else "red"

        # [V0.5.2] 统一同步输入框数值
        self._sync_dice_inputs_to_manager(dm)

        success, consumed = dm.try_consume_for_roll(1, dice_type=dice_type_to_use)
        # [V0.4.3已移除] 骰子消耗日志
        if not success:
            dice_name = "蓝骰" if dice_type_to_use == "blue" else "红骰"
            messagebox.showwarning("提示", f"{dice_name}和环石都不足！无法进行1抽")
            self._unlock_roll_buttons()  # [V0.4.3修复] 必须解锁按钮，否则后续无法操作
            return

        self._refresh_all()

        global_pos = self.board_canvas.piece_pos_idx
        current_main = self.board_canvas.get_main_path_idx(global_pos)
        in_branch = self.board_canvas.is_in_branch_zone(global_pos)

        # [V0.4.3已移除] 掷骰前详细状态诊断（8行）

        # 显示当前位置的格子信息
        if global_pos < len(self.board_canvas.cell_names):
            pass  # 格子信息静默处理

        # 预检测：是否在分支入口或已在分支内
        # 统一处理：进入分支 = 在分支内移动（都使用完整步数dv）
        is_already_in_branch = False  # 是否在分支内（包括刚进入）
        target_branch_key = None
        target_branch_data = None

        # [V0.4.3已移除] 预检测详细日志

        if not in_branch and not self.engine.in_branch:
            # 情况1：在主路径上，检查是否要进入分支
            for bkey, bdata in self.board_canvas.branch_entries.items():
                entry_idx = bdata["entry_main_idx"]
                if current_main == entry_idx:
                    is_already_in_branch = True  # 标记为"将进入分支并移动"
                    target_branch_key = bkey
                    target_branch_data = bdata
                    break
        elif in_branch or self.engine.in_branch:
            # 情况2：已在分支内，继续移动
            is_already_in_branch = True
            if self.engine.in_branch:
                target_branch_key = self.engine.in_branch
            elif in_branch:
                # engine状态已清除但位置仍在分支内：根据位置判断所属分支
                target_branch_key = None
                for bkey, bdata in self.board_canvas.branch_entries.items():
                    b_start = bdata["branch_start"]
                    b_end = b_start + bdata["branch_len"] - 1
                    if b_start <= global_pos <= b_end:
                        target_branch_key = bkey
                        break

                if not target_branch_key:
                    is_already_in_branch = False  # 当作不在分支
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
            else:
                # 已在分支内：从当前位置继续走dv步
                start_pos = global_pos

            steps_to_exit = branch_end - start_pos  # 在分支内还能走的步数（不含跳转步）

            # [V0.4.3已移除] 分支移动详细日志

            if dv <= steps_to_exit:
                # 还在分支内移动，未超出
                # 修正：从主路径进入分支时，需要-1避免多走一格
                if global_pos < branch_start:
                    target_global_pos = start_pos + dv - 1
                else:
                    target_global_pos = start_pos + dv
            else:
                # 超出分支！先走到末尾，再跳转到出口（1步），然后继续在主路径上移动
                exit_idx = target_branch_data["exit_main_idx"]
                remaining_steps = dv - steps_to_exit - 1  # 减去分支内步数和跳转步
                target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)
        elif current_in_branch_zone and not is_already_in_branch:
            # 情况1.5: 异常情况！位置在分支内但预检测失败
            # 强制使用分支离开逻辑（安全兜底）

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

                steps_to_end = branch_end - global_pos + 1

                if dv <= steps_to_end:
                    target_global_pos = global_pos + dv
                else:
                    remaining_steps = dv - steps_to_end
                    target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)

                is_already_in_branch = True
                target_branch_key = fallback_branch_key
                target_branch_data = fallback_branch_data
            else:
                main_path_idx = self.board_canvas.get_main_path_idx(global_pos)
                target_global_pos = self.board_canvas._cycle_pos(main_path_idx, dv)
        else:
            # 情况2：正常主路径移动
            target_global_pos = self.board_canvas._cycle_pos(global_pos, dv)

        # 使用目标位置的格子类型执行完整抽奖（只增加一次计数）
        target_cell_type = self.board_canvas.cell_types[target_global_pos] if target_global_pos < len(self.board_canvas.cell_types) else "apprentice_chest"
        target_cell_name = self.board_canvas.cell_names[target_global_pos] if target_global_pos < len(self.board_canvas.cell_names) else None

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

        # [V0.4.2新增] 硬保底检测：89抽后触发，不移动棋子直接获得S级
        if self.engine.state.s_pity_counter >= 89:
            # 硬保底触发
            result = self.engine.execute_hard_pity(
                current_pos_idx=current_main,
                current_cell_type=self.board_canvas.cell_types[global_pos],
                branch_entries=self.board_canvas.branch_entries,
                is_in_branch=effective_is_in_branch,
                branch_step=effective_branch_step,
            )

            # 硬保底特殊处理：直接显示结果，不执行动画
            self._handle_hard_pity_result(result)
            return  # 提前返回，不执行后续的正常流程

        result = self.engine.execute_single_roll_with_target(
            current_pos_idx=current_main,
            current_cell_type=self.board_canvas.cell_types[global_pos],
            target_pos_idx=target_global_pos,  # [V0.4.3修复] 传入目标位置用于变格检测
            target_cell_type=target_cell_type,
            target_cell_name=target_cell_name,  # 传入目标格子的原始名称
            dice_value=dv,  # 使用已确定的骰子点数
            branch_entries=self.board_canvas.branch_entries,
            is_in_branch=effective_is_in_branch,
            branch_step=effective_branch_step,
        )

        ck = result["cell_type"]

        # [V0.5.4修复] 抽奖逻辑可能已触发变格，动画开始前同步到棋盘画布
        # 使用 result["was_variant"] 作为本次投掷的变格状态（获得S级后 engine.state.is_variant 会被重置）
        if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
            old_variant = getattr(self.board_canvas, 'is_variant', False)
            new_variant = result.get("was_variant", getattr(self.engine.state, 'is_variant', False))
            self.board_canvas.is_variant = new_variant
            if old_variant != self.board_canvas.is_variant:
                print(f"[变格-动画前同步] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                self.board_canvas._render_full_board()

        # [V0.4.3已移除] 单抽准备动画日志

        def done():
            # 处理分支状态更新

            if is_already_in_branch:
                # 在分支内移动（包括刚进入）
                # 判断1: 仍在分支内（step >= 0 且 目标在分支范围内）
                if effective_is_in_branch and effective_branch_step >= 0:
                    # 还在分支内，更新branch_step
                    self.engine.in_branch = target_branch_key
                    self.engine.branch_step = effective_branch_step
                # [V0.4.3已移除] 分支状态日志
            elif effective_is_in_branch and effective_branch_step < 0:
                # 即将离开分支，清除状态
                self.engine.in_branch = None
                self.engine.branch_step = 0
            elif result.get("branch_event") and result["branch_event"][0] == "enter" and not is_already_in_branch:
                # 响应game_logic的分支进入事件
                bkey = result["branch_event"][1]
                bdata = result["branch_event"][2]
                self.engine.in_branch = bkey
                self.engine.branch_step = 0
                # 分支进入：跳转到分支起始位置
                self.board_canvas.piece_pos_idx = bdata["branch_start"]
            elif result.get("new_branch_state") and not is_already_in_branch:
                # 响应game_logic的新分支状态（避免预检测和game_logic双重设置冲突）
                self.engine.in_branch = result["new_branch_state"]
                self.engine.branch_step = result.get("new_branch_step", 0)
            else:
                # 正常情况：位置已在animate_roll中正确设置
                # 检查是否应该离开分支
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
                            # 只有当当前位置不是出口时才重置
                            if current_pos != exit_idx:
                                self.board_canvas.piece_pos_idx = exit_idx
                            self.engine.in_branch = None
                            self.engine.branch_step = 0

            self._show_popup(result)
            self._display_result(result)

            # [V0.4.3新增] 同步变格状态并重绘棋盘（S级结算后is_variant可能已重置为False）
            if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                old_variant = getattr(self.board_canvas, 'is_variant', False)
                self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
                if old_variant != self.board_canvas.is_variant:
                    print(f"[变格-恢复] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                    self.board_canvas._render_full_board()

            self._refresh_all()

            # [保护性措施] 单次抽卡完成，解锁按钮
            self._unlock_roll_buttons()

        # [V0.3-修复] 先启动动画，再在done回调中处理弹窗和UI更新

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
            else:
                pass  # 分支内移动

            self.board_canvas.animate_roll(dv, ck, done, target_idx_override=anim_target,
                                         branch_exit_info=branch_exit_info_for_anim)
        else:
            # 正常主路径 -> 不强制
            anim_target = None
            self.board_canvas.animate_roll(dv, ck, done, target_idx_override=anim_target)

    def _on_ten_roll(self):
        # [保护性措施] 检查是否正在抽卡
        if self.is_rolling:
            print(f"[保护性措施] 十连抽被忽略：正在进行中的抽卡")
            return

        # [保护性措施] 锁定按钮
        self._lock_roll_buttons()

        # 安全检查：如果动画状态卡住，强制重置
        if self.board_canvas.is_animating:
            print(f"[警告] _on_ten_roll: 检测到is_animating=True，强制重置")
            self.board_canvas.is_animating = False

        # [V0.5.2] 十连前先判断资源是否够投满10次
        dm = self.engine.state.dice_manager
        current_board_id = getattr(self.board_canvas, 'current_board_id', 'limited_xun')
        try:
            import board_data
            board_config = board_data.get_board_config(current_board_id)
            board_type = board_config.get("board_type", "limited")
        except Exception:
            board_type = "limited"
        dice_type_to_use = "blue" if board_type == "permanent" else "red"

        # 同步输入框数值到 dice_manager
        self._sync_dice_inputs_to_manager(dm)

        dice_available = dm.get_dice_count(dice_type_to_use)
        ring_available = dm.get_dice_count("ring")
        if dice_available != float("inf") and ring_available != float("inf"):
            total_available = int(dice_available) + int(ring_available)
            if total_available < 10:
                dice_name = "蓝骰" if dice_type_to_use == "blue" else "红骰"
                messagebox.showwarning(
                    "资源不足",
                    f"当前资源不足以进行10连抽\n"
                    f"{dice_name}可用: {int(dice_available)}抽\n"
                    f"环石可用: {int(ring_available)}抽\n"
                    f"共需: 10抽"
                )
                self._unlock_roll_buttons()
                return

        # [调试-10连] 记录十连抽开始时的状态
        start_total_rolls = self.engine.state.total_rolls
        start_s_pity = self.engine.state.s_pity_counter
        start_gift = self.engine.state.gift_counter
        # [V0.3-已注释] 十连抽调试日志（需要时可取消）
        # print(f"\n[调试-10连-开始] ===== 十连抽开始 =====")
        # print(f"[调试-10连-开始] 初始状态: total_rolls={start_total_rolls}, s_pity={start_s_pity}, gift={start_gift}")

        def run_n(idx):
            # [V0.3-已注释] run_n调用日志（需要时可取消）
            # print(f"\n[调试-run_n] ========== run_n({idx}) 被调用 ==========")
            # print(f"[调试-run_n] 当前状态: total_rolls={self.engine.state.total_rolls}, s_pity={self.engine.state.s_pity_counter}, gift={self.engine.state.gift_counter}")

            # [保护性措施] 检查是否被强制停止
            if not self.is_rolling:
                # print(f"[保护性措施] 十连抽被强制停止于第{idx}次 (已完成{idx}/10次)")
                self.status_var.set(f"已停止 | 已完成{idx}抽 | 总掷: {self.engine.state.total_rolls}")
                self._unlock_roll_buttons()
                return

            try:
                if idx >= 10:
                    # [调试-10连] 记录十连抽结束时的状态
                    end_total_rolls = self.engine.state.total_rolls
                    end_s_pity = self.engine.state.s_pity_counter
                    end_gift = self.engine.state.gift_counter
                    actual_rolls = end_total_rolls - start_total_rolls
                    actual_s_pity = end_s_pity - start_s_pity
                    actual_gift = end_gift - start_gift

                    # [V0.3-已注释] 十连抽结束日志（需要时可取消）
                    # print(f"\n[调试-10连-结束] ===== 十连抽结束 =====")
                    # print(f"[调试-10连-结束] 最终状态: total_rolls={end_total_rolls}, s_pity={end_s_pity}, gift={end_gift}")
                    # print(f"[调试-10连-结束] 实际增加: rolls=+{actual_rolls}(期望+10), s_pity=+{actual_s_pity}, gift=+{actual_gift}")

                    if actual_rolls != 10:
                        print(f"[调试-10连-错误] [!] 投掷次数异常! 实际={actual_rolls}, 期望=10")  # 保留关键错误提示

                    self.status_var.set(
                        f"完成10抽 | 总掷: {self.engine.state.total_rolls}")

                    # [V0.4.3新增] 10连抽结束后同步变格状态并重绘棋盘
                    if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                        old_variant = getattr(self.board_canvas, 'is_variant', False)
                        self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
                        if old_variant != self.board_canvas.is_variant:
                            print(f"[变格-恢复-10连] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                            self.board_canvas._render_full_board()

                    # [保护性措施] 十连抽完成，解锁按钮
                    self._unlock_roll_buttons()

                    return

                dm = self.engine.state.dice_manager

                # [V0.5.2] 统一同步输入框数值
                self._sync_dice_inputs_to_manager(dm)

                success, consumed = dm.try_consume_for_roll(1, dice_type=dice_type_to_use)
                if not success:
                    dice_name = "蓝骰" if dice_type_to_use == "blue" else "红骰"
                    messagebox.showwarning("提示", f"{dice_name}和环石都不足！已完成{idx}抽")
                    return

                self._refresh_all()

                global_pos = self.board_canvas.piece_pos_idx
                current_main = self.board_canvas.get_main_path_idx(global_pos)
                in_branch = self.board_canvas.is_in_branch_zone(global_pos)

                # [V0.3-已注释] 状态一致性检查日志（需要时可取消）
                # print(f"[10连-状态] global_pos={global_pos}, current_main={current_main}, in_branch_zone={in_branch}")
                # print(f"[10连-状态] engine.in_branch={self.engine.in_branch}, engine.branch_step={self.engine.branch_step}")
                # print(f"[10连-状态] board.is_animating={self.board_canvas.is_animating}")

                # [安全检查] 验证global_pos有效性
                total_cells = len(self.board_canvas.cell_positions)
                if global_pos < 0 or global_pos >= total_cells:
                    print(f"[错误-严重] global_pos={global_pos} 超出范围[0, {total_cards})！强制修正为0")
                    global_pos = 0
                    self.board_canvas.piece_pos_idx = 0

                # 预检测：是否在分支入口或已在分支内（10连抽也需要统一处理）
                # 与单次投掷保持一致：进入分支 = 在分支内移动（都使用完整步数dv）
                is_already_in_branch = False  # 是否在分支内（包括刚进入）
                target_branch_key = None
                target_branch_data = None

                if not in_branch and not self.engine.in_branch:
                    for bkey, bdata in self.board_canvas.branch_entries.items():
                        if current_main == bdata["entry_main_idx"]:
                            is_already_in_branch = True  # [OK] 标记为"将进入分支并移动"
                            target_branch_key = bkey
                            target_branch_data = bdata
                            break
                elif in_branch or self.engine.in_branch:
                    # 与单次投掷保持一致：标记为在分支内
                    is_already_in_branch = True  # [OK] 关键修复：与单次投掷一致
                    # 优先使用engine.in_branch（引擎记录的分支状态）
                    if self.engine.in_branch:
                        target_branch_key = self.engine.in_branch
                    elif in_branch:
                        print(f"\n[预检测-10连] [!] 异常：engine.in_branch=None但位置{global_pos}仍在分支区域内")
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
                            print(f"[错误] 找不到分支配置: {target_branch_key}，清除分支状态")
                            is_already_in_branch = False
                            target_branch_data = None
                            target_branch_key = None
                            self.engine.in_branch = None
                            self.engine.branch_step = 0

                # 获取骰子点数
                dv = self.engine.roll_engine.roll_dice()
                # [V0.4.3已移除] 10连投掷点数日志

                    # 计算目标位置（与单次投掷保持一致：使用完整步数）
                current_in_branch_zone_10 = self.board_canvas.is_in_branch_zone(global_pos)

                if is_already_in_branch and target_branch_data:
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
                        # 分支内移动
                        pass
                    else:
                        exit_idx = target_branch_data["exit_main_idx"]
                        remaining_steps = dv - steps_to_exit - 1  # 减去跳转步
                        target_global_pos = self.board_canvas._cycle_pos(exit_idx, remaining_steps)
                        # 离开分支
                        pass
                elif current_in_branch_zone_10 and not is_already_in_branch:
                    # 10连抽的安全兜底：与单次投掷保持一致

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
                        else:
                            remaining_steps_10 = dv - steps_to_end_10
                            target_global_pos = self.board_canvas._cycle_pos(exit_idx_10, remaining_steps_10)

                        is_already_in_branch = True
                        target_branch_key = fallback_bkey_10
                        target_branch_data = fallback_bdata_10
                    else:
                        main_path_idx_10 = self.board_canvas.get_main_path_idx(global_pos)
                        target_global_pos = self.board_canvas._cycle_pos(main_path_idx_10, dv)
                else:
                    target_global_pos = self.board_canvas._cycle_pos(global_pos, dv)

                # [安全检查] 验证target_global_pos有效性
                if target_global_pos < 0 or target_global_pos >= total_cells:
                    print(f"[错误-严重] target_global_pos={target_global_pos} 超出范围[0, {total_cells})！强制使用循环逻辑修正")
                    target_global_pos = self.board_canvas._cycle_pos(global_pos, dv)
                    if target_global_pos < 0 or target_global_pos >= total_cells:
                        print(f"[错误-致命] 无法修正target_global_pos，强制设为0")
                        target_global_pos = 0

                # [V0.3-已注释] 10连抽目标/执行日志（需要时可取消）
                # print(f"[10连-目标] 最终位置: {target_global_pos}")

                target_cell_type = self.board_canvas.cell_types[target_global_pos] if target_global_pos < len(self.board_canvas.cell_types) else "apprentice_chest"
                target_cell_name = self.board_canvas.cell_names[target_global_pos] if target_global_pos < len(self.board_canvas.cell_names) else None

                # [调试-10连] 记录执行前的状态
                # print(f"[调试-10连-前] 第{idx+1}次执行前: total_rolls={self.engine.state.total_rolls}, s_pity={self.engine.state.s_pity_counter}, gift={self.engine.state.gift_counter}")

                # 确定分支状态（与单次投掷保持一致）
                if is_already_in_branch and target_branch_data:
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

                # [V0.4.2新增] 硬保底检测：89抽后触发（10连抽也适用）
                if self.engine.state.s_pity_counter >= 89:
                    # 调用硬保底结算（不移动棋子）
                    result = self.engine.execute_hard_pity(
                        current_pos_idx=current_main,
                        current_cell_type=self.board_canvas.cell_types[global_pos],
                        branch_entries=self.board_canvas.branch_entries,
                        is_in_branch=effective_is_in_branch,
                        branch_step=effective_branch_step,
                    )

                    # 10连抽中触发硬保底：记录结果但不立即显示弹窗
                    hard_pity_rewards = result.get("rewards", [])

                    # 同步更新棋盘变格状态（硬保底后垫刀清零 -> 关闭变格）
                    if hasattr(self, 'board_canvas') and self.board_canvas:
                        self.board_canvas.is_variant = self.engine.state.is_variant

                    # 记录日志（不显示弹窗）
                    self.log_text.insert(tk.END, f"[系统] 89抽硬保底触发！获得S级角色\n", "highlight")
                    for r in hard_pity_rewards:
                        if r["type"] == "s_character":
                            dup_str = "(重复)" if r.get("is_duplicate") else ""
                            self.log_text.insert(
                                tk.END,
                                f"  -> S级角色: {r['name']} {dup_str}\n",
                                "s_character" if not r.get("is_duplicate") else "duplicate"
                            )
                    self.log_text.see(tk.END)

                    # [V0.4.3核心修复] 构建特殊result标记这是硬保底
                    result = {
                        "roll_number": result["roll_number"],
                        "dice_value": 0,
                        "cell_type": "hard_pity",
                        "cell_name": "硬保底",
                        "rewards": hard_pity_rewards,
                        "pity_event": "hard_pity_89",
                        "is_hard_pity": True,
                        "new_position_idx": current_main,  # 不移动
                    }

                    # [V0.4.3核心修复] 使用continue跳过execute_single_roll_with_target，
                    # 避免多执行一次投掷（否则会变成11抽）
                    ck = result["cell_type"]  # 设置ck供后续动画逻辑使用

                    def after_one_hard_pity():
                        """[V0.4.3新增] 硬保底的after_one回调：不移动棋子"""
                        try:
                            self._display_result(result)

                            # [V0.5.3修复] 硬保底后同步变格状态并重绘棋盘
                            # 硬保底会重置垫刀并关闭变格，确保棋盘显示恢复基准状态
                            if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                                old_variant = getattr(self.board_canvas, 'is_variant', False)
                                self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
                                if old_variant != self.board_canvas.is_variant:
                                    print(f"[变格-硬保底] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                                    self.board_canvas._render_full_board()

                            self._refresh_all()
                            self.root.after(50, lambda: run_n(idx + 1))
                        except Exception as e:
                            print(f"[错误-致命] 硬保底after_one回调失败: {e}")
                            import traceback
                            traceback.print_exc()
                            self.root.after(100, lambda: run_n(idx + 1))

                    # 硬保底不移动棋子，直接调用after_one
                    self.root.after(300, after_one_hard_pity)
                    return  # ✅ [V0.4.3修复] 跳过后续的execute_single_roll_with_target（避免多执行1次）

                # 使用目标格子类型执行完整抽奖（只增加一次计数）
                result = self.engine.execute_single_roll_with_target(
                    current_pos_idx=current_main,
                    current_cell_type=self.board_canvas.cell_types[global_pos],
                    target_pos_idx=target_global_pos,  # [V0.4.3修复] 传入目标位置用于变格检测
                    target_cell_type=target_cell_type,
                    target_cell_name=target_cell_name,  # 传入目标格子的原始名称
                    dice_value=dv,
                    branch_entries=self.board_canvas.branch_entries,
                    is_in_branch=effective_is_in_branch,
                    branch_step=effective_branch_step,
                )

                ck = result["cell_type"]

                # [V0.5.4修复] 十连抽每抽开始前同步变格状态到棋盘画布
                # 使用 result["was_variant"] 保留本次投掷的真实变格状态（获得S级后 engine.state.is_variant 会被重置）
                if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                    old_variant = getattr(self.board_canvas, 'is_variant', False)
                    new_variant = result.get("was_variant", getattr(self.engine.state, 'is_variant', False))
                    self.board_canvas.is_variant = new_variant
                    if old_variant != self.board_canvas.is_variant:
                        print(f"[变格-10连抽同步] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                        self.board_canvas._render_full_board()

                def after_one():
                    try:
                        # 注意：animate_roll()已经在动画过程中正确更新了piece_pos_idx
                        # 这里只处理分支状态更新（与单次投掷保持一致）

                        if is_already_in_branch and target_branch_data:
                            # 在分支内移动（包括刚进入）
                            # 判断1: 仍在分支内（step >= 0 且 目标在分支范围内）
                            if effective_is_in_branch and effective_branch_step >= 0:
                                # 还在分支内，更新branch_step
                                self.engine.in_branch = target_branch_key
                                self.engine.branch_step = effective_branch_step
                            # 判断2: 即将离开分支（特殊标记 step < 0）
                            elif effective_is_in_branch and effective_branch_step < 0:
                                # 即将离开分支，清除状态
                                self.engine.in_branch = None
                                self.engine.branch_step = 0
                            else:
                                # 安全兜底：清除状态
                                self.engine.in_branch = None
                                self.engine.branch_step = 0
                        elif result.get("branch_event") and result["branch_event"][0] == "enter" and not is_already_in_branch:
                            # 响应game_logic的分支进入事件
                            bdata = result["branch_event"][2]
                            self.engine.in_branch = result["branch_event"][1]
                            self.board_canvas.piece_pos_idx = bdata["branch_start"]
                        elif self.engine.in_branch:
                            bdata = self.board_canvas.branch_entries.get(self.engine.in_branch, {})
                            if not bdata:
                                # 分支配置不存在，清除状态
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
                                    if current_pos != exit_idx:
                                        self.board_canvas.piece_pos_idx = exit_idx
                                    self.engine.in_branch = None
                                    self.engine.branch_step = 0
                        # else: 正常情况，位置已在animate_roll中正确设置

                        self._display_result(result)

                        # [V0.5.3修复] 10连抽过程中同步变格状态并重绘棋盘
                        # 确保第70抽触发变格后，后续投掷的棋盘显示实时更新
                        if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                            old_variant = getattr(self.board_canvas, 'is_variant', False)
                            self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
                            if old_variant != self.board_canvas.is_variant:
                                print(f"[变格-10连抽] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                                self.board_canvas._render_full_board()

                        self._refresh_all()
                        self.root.after(50, lambda: run_n(idx + 1))
                    except Exception as e:
                        print(f"\n[错误-致命] after_one回调执行失败: {e}")
                        import traceback
                        traceback.print_exc()
                        # 尝试继续下一次投掷
                        try:
                            self._display_result(result)

                            # [V0.5.3修复] 异常恢复路径也同步变格状态并重绘棋盘
                            if hasattr(self, 'board_canvas') and hasattr(self, 'engine'):
                                old_variant = getattr(self.board_canvas, 'is_variant', False)
                                self.board_canvas.is_variant = getattr(self.engine.state, 'is_variant', False)
                                if old_variant != self.board_canvas.is_variant:
                                    print(f"[变格-10连抽-恢复] is_variant: {old_variant} -> {self.board_canvas.is_variant}, 触发棋盘重绘")
                                    self.board_canvas._render_full_board()

                            self._refresh_all()
                            self.root.after(100, lambda: run_n(idx + 1))
                        except Exception as e2:
                            # 恢复失败，跳过本次并继续
                            pass
                            self.root.after(200, lambda: run_n(idx + 1))

                # 调用动画：根据情况决定是否强制目标位置（10连抽与单次投掷保持一致）
                if is_already_in_branch and target_branch_data:
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

            except Exception as e:
                print(f"\n{'!'*80}")
                print(f"[错误-致命] 10连抽第{idx+1}次发生异常！！！")
                print(f"[错误信息] {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                # [调试-10连] 记录异常发生时的状态
                print(f"[调试-10连-异常] 异常时状态: total_rolls={self.engine.state.total_rolls}, s_pity={self.engine.state.s_pity_counter}, gift={self.engine.state.gift_counter}")
                print(f"{'!'*80}\n")

                # 尝试恢复并继续下一次投掷
                try:
                    # 重置可能卡住的动画状态
                    if hasattr(self, 'board_canvas') and self.board_canvas:
                        self.board_canvas.is_animating = False

                    # 强制刷新界面
                    self._refresh_all()

                    # 延迟后继续下一次（给系统时间恢复）
                    self.root.after(300, lambda: run_n(idx + 1))
                    print(f"[恢复] 已尝试恢复，将在300ms后继续第{idx+2}次投掷\n")
                except Exception as recovery_err:
                    print(f"[错误-致命] 恢复失败: {recovery_err}")
                    print(f"[错误-致命] 10连抽已中断，已完成{idx}/10次")
                    self.status_var.set(f"10连抽中断于第{idx+1}次 | 总掷: {self.engine.state.total_rolls}")

                    # [保护性措施] 十连抽异常中断，解锁按钮
                    self._unlock_roll_buttons()

        run_n(0)

    def _on_reset(self):
        # [保护性措施] 检查是否正在抽卡
        if not self._stop_rolling_if_needed():
            return  # 用户取消操作

        # [V0.4] 显示重置选项弹窗（完全重置 / 自定义起点）
        self._show_reset_options()

    def _show_reset_options(self):
        """显示重置选项弹窗：完全重置 或 自定义起点"""
        dialog = tk.Toplevel(self.root)
        dialog.title("重置选项")
        dialog.geometry("420x250")  # [修复] 增加高度以显示按钮
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 420) // 2
        y = (dialog.winfo_screenheight() - 250) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="选择操作方式：", font=("", 11)).pack(anchor=tk.W, pady=(0, 10))

        # 选项变量
        choice_var = tk.StringVar(value="full")

        # 选项1: 完全重置
        f1 = ttk.Frame(frame)
        f1.pack(fill=tk.X, pady=5)
        rb1 = ttk.Radiobutton(f1, text="完全重置", variable=choice_var, value="full")
        rb1.pack(anchor=tk.W)
        ttk.Label(f1, text="  （回起点[0] + 清空所有计数器）", font=("", 9), foreground="gray").pack(anchor=tk.W)

        # 选项2: 自定义起点
        f2 = ttk.Frame(frame)
        f2.pack(fill=tk.X, pady=5)
        rb2 = ttk.Radiobutton(f2, text="自定义起点位置", variable=choice_var, value="custom")
        rb2.pack(anchor=tk.W)
        ttk.Label(f2, text="  （选择1-54或分支位置，清空计数器）", font=("", 9), foreground="gray").pack(anchor=tk.W)

        # 提示信息
        ttk.Label(frame, text="\n注意: 两种方式都不影响骰子数量", font=("", 9), foreground="blue").pack(anchor=tk.W)

        def on_confirm():
            choice = choice_var.get()
            dialog.destroy()

            if choice == "full":
                self._do_full_reset()
            elif choice == "custom":
                self._show_position_selector()

        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_frame, text="确定", command=on_confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

    def _do_full_reset(self):
        """执行完全重置（回起点+清空所有计数器）"""
        if messagebox.askyesno(
            "确认完全重置",
            "确定要完全重置吗？\n\n将执行以下操作:\n"
            "- 棋子回到起点[0]\n"
            "- 清空保底/赠礼等所有计数器\n"
            "- 关闭追击状态\n"
            "- 清空奖励记录\n\n"
            "骰子数量不会受到影响。"
        ):
            current_board = getattr(self.board_canvas, 'current_board_id', 'limited_xun')
            self.engine = GameEngine(current_board)
            self.board_canvas.engine = self.engine
            # [V0.4.3修复] 同步重置变格状态并重绘棋盘
            self.board_canvas.is_variant = False
            self.board_canvas.reset_board()
            self.board_canvas._render_full_board()
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self._refresh_collection_trees()
            self._refresh_all()
            self.status_var.set("已完全重置")
            print("[重置] 已执行完全重置，棋子回到起点[0]")

    def _show_position_selector(self):
        """显示位置选择器弹窗（输入编号+查询面板）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("自定义起点位置")
        dialog.geometry("550x680")  # [修复] 增加高度以容纳新增的赠礼输入框和按钮
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 550) // 2
        y = (dialog.winfo_screenheight() - 680) // 2
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(main_frame, text="设置起点位置", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入或选择位置", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行：目标位置
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X)

        ttk.Label(entry_frame, text="目标位置:").pack(side=tk.LEFT)
        pos_var = tk.StringVar()
        entry = ttk.Entry(entry_frame, textvariable=pos_var, width=15)
        entry.pack(side=tk.LEFT, padx=(5, 10))

        selected_info = ttk.Label(entry_frame, text="[未选择]", foreground="gray")
        selected_info.pack(side=tk.LEFT)

        # [V0.4] 第二行：垫刀数（可选）
        pity_frame = ttk.Frame(input_frame)
        pity_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(pity_frame, text="垫刀数(可选):").pack(side=tk.LEFT)
        pity_var = tk.StringVar()
        pity_entry = ttk.Entry(pity_frame, textvariable=pity_var, width=10)
        pity_entry.pack(side=tk.LEFT, padx=(5, 10))

        pity_hint = ttk.Label(pity_frame, text="已抽次数(0-89), >=70自动变格", font=("", 8), foreground="gray")
        pity_hint.pack(side=tk.LEFT)

        # [V0.4] 第三行：赠礼计数器（可选）
        gift_frame = ttk.Frame(input_frame)
        gift_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(gift_frame, text="赠礼计数(可选):").pack(side=tk.LEFT)
        gift_var = tk.StringVar()
        gift_entry = ttk.Entry(gift_frame, textvariable=gift_var, width=10)
        gift_entry.pack(side=tk.LEFT, padx=(5, 10))

        gift_hint = ttk.Label(gift_frame, text="当前集点进度(0-9), >=10触发赠礼", font=("", 8), foreground="gray")
        gift_hint.pack(side=tk.LEFT)

        # 有效范围提示
        ttk.Label(input_frame, text="有效范围: 1-54, B1-0~B1-8, B2-0~B2-8  |  注: 起点[0]请使用'完全重置'",
                   font=("", 9), foreground="blue").pack(anchor=tk.W, pady=(5, 0))

        # 快速选择区域
        quick_frame = ttk.LabelFrame(main_frame, text="快速选择常用位置", padding=5)
        quick_frame.pack(fill=tk.X, pady=(0, 10))

        quick_btns = ttk.Frame(quick_frame)
        quick_btns.pack(fill=tk.X)

        # 常用位置按钮（限定棋盘专用）
        quick_positions = [
            ("16-欧皇路口", "16"),
            ("43-皮肤路口", "43"),
        ]
        for text, val in quick_positions:
            btn = ttk.Button(quick_btns, text=text, width=14,
                             command=lambda v=val: pos_var.set(v))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # 位置参考面板（可双向滚动）
        ref_label = ttk.LabelFrame(main_frame, text="位置参考（点击填入）", padding=5)
        ref_label.pack(fill=tk.BOTH, expand=True)

        # 创建Canvas和双向Scrollbar实现滚动
        canvas_container = tk.Canvas(ref_label, highlightthickness=0)

        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(ref_label, orient=tk.VERTICAL, command=canvas_container.yview)
        # [V0.4] 新增横向滚动条
        h_scrollbar = ttk.Scrollbar(ref_label, orient=tk.HORIZONTAL, command=canvas_container.xview)

        scrollable_frame = ttk.Frame(canvas_container)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
        )

        canvas_container.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas_container.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # [V0.4修复] 使用局部绑定替代bind_all，避免弹窗关闭后访问已销毁组件
        def on_mousewheel(event):
            try:
                canvas_container.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass  # 弹窗已关闭，忽略

        def on_shift_mousewheel(event):
            try:
                canvas_container.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass  # 弹窗已关闭，忽略

        # 绑定到canvas_container自身（非全局）
        canvas_container.bind("<MouseWheel>", on_mousewheel)
        canvas_container.bind("<Shift-MouseWheel>", on_shift_mousewheel)

        # [V0.4] 布局：右侧纵向滚动条，底部横向滚动条
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 填充格子数据
        self._populate_cell_buttons(scrollable_frame, pos_var, selected_info)

        # 绑定输入框变化事件
        def on_entry_change(*args):
            val = pos_var.get().strip()
            if val:
                cell_name = self._get_cell_name_by_pos(val)
                if cell_name:
                    selected_info.config(text=f"[已选择: {cell_name}]", foreground="green")
                else:
                    selected_info.config(text=f"[无效输入]", foreground="red")
            else:
                selected_info.config(text="[未选择]", foreground="gray")

        pos_var.trace_add("write", on_entry_change)

        # 确认和取消按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        def on_confirm():
            val = pos_var.get().strip()
            if not val:
                messagebox.showwarning("提示", "请输入或选择一个目标位置")
                return

            # 验证位置有效性
            if not self._validate_position(val):
                messagebox.showerror("错误", f"无效的位置编号: {val}\n\n有效范围:\n- 主路径: 0-54\n- 分支1: B1-0 ~ B1-8\n- 分支2: B2-0 ~ B2-8")
                return

            # [V0.4] 获取垫刀数和赠礼计数
            pity_input = pity_var.get().strip()
            gift_input = gift_var.get().strip()

            dialog.destroy()
            self._set_custom_start_position(val, pity_input, gift_input)

        def on_cancel():
            dialog.destroy()
            # [V0.4修复] 不再需要手动解绑，使用局部绑定自动随弹窗销毁

        ttk.Button(btn_frame, text="确定", command=on_confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

    def _populate_cell_buttons(self, parent, pos_var, info_label):
        """填充格子按钮到滚动面板"""
        # 获取当前棋盘的格子数据
        cell_names = getattr(self.board_canvas, 'cell_names', [])
        cell_types = getattr(self.board_canvas, 'cell_types', [])

        if not cell_names:
            ttk.Label(parent, text="无法获取棋盘数据", foreground="red").pack(pady=20)
            return

        # 分组显示
        sections = {
            "主路径 (0-54)": range(0, 55),  # [V0.4.2修复] 包含起点0
            "分支1-S级区 (B1-0 ~ B1-8)": [f"B1-{i}" for i in range(9)],
            "分支2-皮肤区 (B2-0 ~ B2-8)": [f"B2-{i}" for i in range(9)],  # 分支2有9格
        }

        for section_name, indices in sections.items():
            # 可折叠的分组标题
            section_frame = ttk.LabelFrame(parent, text=section_name, padding=3)
            section_frame.pack(fill=tk.X, pady=2, padx=2)

            btn_row = ttk.Frame(section_frame)
            btn_row.pack(fill=tk.X)

            count = 0
            for idx in indices:
                # 获取格子名称
                name = ""
                if isinstance(idx, int):
                    if idx < len(cell_names):
                        name = cell_names[idx]
                        # 缩短名称显示
                        short_name = name[:6] + ".." if len(name) > 8 else name
                        display_text = f"{idx}:{short_name}"
                else:
                    # 分支格子
                    branch_idx = None
                    if idx.startswith("B1-"):
                        branch_idx = 55 + int(idx.split("-")[1])
                    elif idx.startswith("B2-"):
                        branch_idx = 64 + int(idx.split("-")[1])
                    if branch_idx and branch_idx < len(cell_names):
                        name = cell_names[branch_idx]
                        short_name = name[:6] + ".." if len(name) > 8 else name
                        display_text = f"{idx}:{short_name}"
                    else:
                        display_text = str(idx)

                # 创建按钮
                btn = ttk.Button(btn_row, text=display_text, width=12,
                                 command=lambda v=str(idx): pos_var.set(v))
                btn.pack(side=tk.LEFT, padx=1, pady=1)
                count += 1

                # 每6个换行
                if count % 6 == 0:
                    btn_row = ttk.Frame(section_frame)
                    btn_row.pack(fill=tk.X)

    def _validate_position(self, pos_str):
        """验证位置编号是否有效"""
        pos_str = str(pos_str).strip().upper()

        # 检查主路径范围（[V0.4.2修复] 允许0即起点）
        if pos_str.isdigit():
            num = int(pos_str)
            return 0 <= num <= 54  # [V0.4.2修复] 原来是1-54，改为0-54

        # 检查分支格式
        if pos_str.startswith("B1-"):
            try:
                idx = int(pos_str.split("-")[1])
                return 0 <= idx <= 8  # 分支1有9格（B1-0 ~ B1-8）
            except ValueError:
                return False

        if pos_str.startswith("B2-"):
            try:
                idx = int(pos_str.split("-")[1])
                return 0 <= idx <= 8  # 分支2有9格（B2-0 ~ B2-8）
            except ValueError:
                return False

        return False

    def _get_cell_name_by_pos(self, pos_str):
        """根据位置获取格子名称"""
        cell_names = getattr(self.board_canvas, 'cell_names', [])
        if not cell_names:
            return None

        pos_str = str(pos_str).strip().upper()

        try:
            if pos_str.startswith("B1-"):
                idx = 55 + int(pos_str.split("-")[1])
            elif pos_str.startswith("B2-"):
                idx = 64 + int(pos_str.split("-")[1])
            else:
                idx = int(pos_str)

            if 0 <= idx < len(cell_names):
                return cell_names[idx]
        except (ValueError, IndexError):
            pass

        return None

    def _set_custom_start_position(self, target_pos, pity_input="", gift_input=""):
        """执行自定义起点设置

        Args:
            target_pos: 目标位置（如 "22", "B1-0"）
            pity_input: 垫刀数输入（可选，默认为0）
            gift_input: 赠礼计数器输入（可选，默认为0）
        """
        print(f"\n{'='*60}")
        print(f"[自定义起点-DEBUG] ===== 函数入口 =====")

        # [V0.4.2核心修复] 设置更新标志，防止resize事件触发重复渲染
        if hasattr(self, 'board_canvas'):
            self.board_canvas._is_updating = True
            print(f"[自定义起点-DEBUG] 已设置 _is_updating=True (防止重复渲染)")

        print(f"[自定义起点-DEBUG] target_pos原始值='{target_pos}'")
        target_pos = str(target_pos).strip().upper()
        print(f"[自定义起点-DEBUG] target_pos处理后='{target_pos}'")

        cell_name = self._get_cell_name_by_pos(target_pos)
        print(f"[自定义起点-DEBUG] 格子名称={cell_name}")

        # [V0.4] 解析并验证垫刀数
        try:
            pity_count = int(pity_input.strip()) if pity_input.strip() else 0
        except ValueError:
            messagebox.showerror("错误", f"请输入有效的垫刀数(0-89)\n输入内容: {pity_input}")
            return

        if pity_count < 0 or pity_count >= 90:
            messagebox.showerror(
                "错误",
                f"垫刀数范围为0-89\n当前值: {pity_count}\n\n"
                f">=90已达到硬保底，请使用'完全重置'选项"
            )
            return

        if pity_count > 0:
            print(f"[自定义起点] 垫刀数: {pity_count}")

        # [V0.4] 解析并验证赠礼计数
        try:
            gift_count = int(gift_input.strip()) if gift_input.strip() else 0
        except ValueError:
            messagebox.showerror("错误", f"请输入有效的赠礼计数(0-9)\n输入内容: {gift_input}")
            return

        if gift_count < 0 or gift_count >= 10:
            messagebox.showerror(
                "错误",
                f"赠礼计数范围为0-9\n当前值: {gift_count}\n\n"
                f">=10应触发赠礼，请使用完全重置后重新开始"
            )
            return

        if gift_count > 0:
            print(f"[自定义起点] 赠礼计数: {gift_count}")

        # 第一步：强制关闭当前追击状态（必须！）
        was_in_chase = self.engine.in_chase
        self.engine.in_chase = False
        self.engine.chase_rounds_left = 0
        if was_in_chase:
            print(f"[自定义起点] 已强制关闭当前追击状态")

        # [V0.4修复] 保存当前骰子数量（自定义起点不应影响骰子）
        # [V0.4.1修复] 先同步textbox中的骰子数量到dice_manager
        self._on_dice_setting_change()
        dm = self.engine.state.dice_manager
        saved_red = dm.red_dice
        saved_blue = dm.blue_dice
        saved_ring = dm.ring_stone
        saved_inf_red = dm.infinite_red
        saved_inf_blue = dm.infinite_blue
        saved_inf_ring = dm.infinite_ring
        print(f"[自定义起点] 保存骰子: 红={saved_red}, 蓝={saved_blue}, 环石={saved_ring}")

        # 第二步：设置计数器（使用用户输入值而非全部清零）
        self.engine.state.total_rolls = 0

        # [V0.4] 设置垫刀数到保底计数器（而非清零）
        self.engine.state.s_pity_counter = pity_count

        # [V0.4] 设置赠礼计数器（而非清零）
        self.engine.state.gift_counter = gift_count

        # [V0.4] 检查是否进入变格状态（注意：属性名是 is_variant 不是 is_variated）
        print(f"\n[自定义起点-DEBUG] ===== 变格状态设置 =====")
        print(f"[自定义起点-DEBUG] pity_count={pity_count}, 阈值=70")
        if pity_count >= 70:
            self.engine.state.is_variant = True  # [V0.4修复] 正确的属性名
            print(f"[自定义起点-DEBUG] 已设置 engine.state.is_variant = True")
        else:
            self.engine.state.is_variant = False
            print(f"[自定义起点-DEBUG] 已设置 engine.state.is_variant = False")

        # [V0.4.2新增] 同步变格状态到棋盘画布
        # 注意：不在这里调用 _draw_grid_cells()，统一在位置更新后刷新显示
        if hasattr(self, 'board_canvas'):
            print(f"[自定义起点-DEBUG] 同步前 board_canvas.is_variant={getattr(self.board_canvas, 'is_varient', 'N/A')}")
            self.board_canvas.is_variant = self.engine.state.is_variant
            print(f"[自定义起点-DEBUG] 同步后 board_canvas.is_variant={self.board_canvas.is_variant}")

        # [V0.4] 清除白色/金色棋子数量
        old_white = self.engine.state.white_chips
        old_gold = self.engine.state.gold_chips
        self.engine.state.white_chips = 0
        self.engine.state.gold_chips = 0

        # [V0.4] 清空奖池收集记录（S/A角色、A/B盘、皮肤）
        self.engine.state.collection = {
            "s_characters": {},
            "a_characters": {},
            "a_disks": {},
            "b_disks": {},
            "skins": {},
        }
        self.engine.state.skin_claimed = {stype: False for stype in ["daily", "weekly", "monthly", "seasonal", "event"]}

        print(f"[自定义起点] 已设置计数器: s_pity={pity_count}, gift={gift_count}, total_rolls=0")
        if old_white > 0 or old_gold > 0:
            print(f"[自定义起点] 已清除棋子: 白色={old_white}, 金色={old_gold}")
        print(f"[自定义起点] 已清空奖池收集记录")

        # 第三步：解析目标位置并更新
        print(f"\n[自定义起点-DEBUG] ===== 位置解析与更新 =====")
        global_pos = self._parse_target_to_global_index(target_pos)
        print(f"[自定义起点-DEBUG] _parse_target_to_global_index('{target_pos}') 返回: {global_pos}")
        if global_pos is None:
            print(f"[自定义起点] 错误: 无法解析位置 {target_pos}")
            return

        # 更新棋子位置
        old_pos = self.board_canvas.piece_pos_idx
        print(f"[自定义起点-DEBUG] 更新前 piece_pos_idx={old_pos}")
        self.board_canvas.piece_pos_idx = global_pos
        print(f"[自定义起点-DEBUG] 更新后 piece_pos_idx={self.board_canvas.piece_pos_idx}")

        # 更新引擎状态
        if global_pos >= 55 and global_pos <= 63:
            # 分支1（9格：55-63）
            self.engine.in_branch = "branch1"
            self.engine.branch_step = global_pos - 55
            # 计算对应的主路径位置（分支1从16号进入）
            self.engine.current_main = 16
        elif global_pos >= 64 and global_pos <= 72:
            # 分支2（9格：64-72）[V0.4.2修正] 确认CSV和board_data.py均为9格
            self.engine.in_branch = "branch2"
            self.engine.branch_step = global_pos - 64
            # 计算对应的主路径位置（分支2从43号进入）
            self.engine.current_main = 43
        else:
            # 主路径
            self.engine.in_branch = None
            self.engine.branch_step = 0
            self.engine.current_main = global_pos

        print(f"[自定义起点] 位置更新: {old_pos} -> {global_pos} ({cell_name})")
        print(f"[自定义起点] 引擎状态: current_main={self.engine.current_main}, in_branch={self.engine.in_branch}")

        # 第四步：检查目标是否为沉眠池格子 → 特殊处理
        cell_type = ""
        if global_pos < len(self.board_canvas.cell_types):
            cell_type = self.board_canvas.cell_types[global_pos]

        is_sleep_pool = ("沉眠池" in (cell_name or "")) or (cell_type == "arcade_blind" and "沉眠池" in (cell_name or ""))

        if is_sleep_pool:
            # 沉眠池特殊处理：重新初始化追击状态
            self.engine.sleep_pool.start_chase()  # [V0.4修复] 必须调用start_chase()设置sleep_pool内部状态(active, guardian_pos等)
            self.engine.in_chase = True
            self.engine.chase_rounds_left = SLEEP_POOL_CONFIG["max_chase_rounds"]
            print(f"[自定义起点] 目标是沉眠池格子！已重新初始化追击（剩余{self.engine.chase_rounds_left}轮）")
        else:
            print(f"[自定义起点] 目标不是沉眠池，追击保持关闭")

        # 第五步：刷新显示（不触发任何奖励结算）
        # [V0.4.3核心修复] 统一使用 _render_full_board() 而不是 _draw_grid_cells()
        # 原因：_draw_grid_cells 只绘制格子和棋子（缺少背景、边框、图例）
        #       后续 _on_canvas_resize 会触发 _render_full_board 绘制完整棋盘
        #       两者交替执行会导致"两层棋盘重叠"的视觉效果！
        print(f"[自定义起点] 刷新显示: piece_pos={self.board_canvas.piece_pos_idx} (使用完整渲染)")
        self.board_canvas._render_full_board()  # ✅ 统一使用完整渲染，避免和resize冲突
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[系统] 自定义起点: 移动到 [{target_pos}] {cell_name}\n", "normal")
        if pity_count > 0 or gift_count > 0:
            info_parts = []
            if pity_count > 0:
                variant_text = " [变格]" if pity_count >= 70 else ""
                info_parts.append(f"垫刀:{pity_count}{variant_text}")
            if gift_count > 0:
                info_parts.append(f"赠礼:{gift_count}")
            self.log_text.insert(tk.END, f"[系统] 设置: {', '.join(info_parts)}\n", "normal")
        if is_sleep_pool:
            self.log_text.insert(tk.END, f"[系统] 已触发沉眠池追击模式\n", "pity")
        self.log_text.config(state=tk.DISABLED)

        # [V0.4修复] 恢复骰子数量（必须在_refresh_all之前，否则UI会显示错误值）
        dm.red_dice = saved_red
        dm.blue_dice = saved_blue
        dm.ring_stone = saved_ring
        dm.infinite_red = saved_inf_red
        dm.infinite_blue = saved_inf_blue
        dm.infinite_ring = saved_inf_ring
        print(f"[自定义起点] 恢复骰子: 红={saved_red}, 蓝={saved_blue}, 环石={saved_ring}")

        self._refresh_all()

        # 更新状态栏
        status_text = f"自定义起点: {cell_name}"
        status_parts = []
        if pity_count > 0:
            status_parts.append(f"垫刀:{pity_count}")
        if gift_count > 0:
            status_parts.append(f"赠礼:{gift_count}")
        if status_parts:
            status_text += f" | {', '.join(status_parts)}"
        self.status_var.set(status_text)

        # [V0.4.2核心修复] 清除更新标志，恢复正常resize响应
        if hasattr(self, 'board_canvas'):
            self.board_canvas._is_updating = False
            print(f"[自定义起点-DEBUG] 已清除 _is_updating=False (恢复正常渲染)")

        print(f"[自定义起点] 设置完成!")

    def _parse_target_to_global_index(self, target_pos):
        """将目标位置字符串转换为全局索引"""
        print(f"[_parse_target-DEBUG] 入口: target_pos='{target_pos}'")
        target_pos = str(target_pos).strip().upper()
        print(f"[_parse_target-DEBUG] 处理后: target_pos='{target_pos}'")

        try:
            if target_pos.startswith("B1-"):
                branch_idx = int(target_pos.split("-")[1])
                if 0 <= branch_idx <= 8:
                    result = 55 + branch_idx
                    print(f"[_parse_target-DEBUG] 分支1: branch_idx={branch_idx}, 返回={result}")
                    return result
                else:
                    print(f"[_parse_target-DEBUG] 分支1越界: branch_idx={branch_idx}")
            elif target_pos.startswith("B2-"):
                branch_idx = int(target_pos.split("-")[1])
                if 0 <= branch_idx <= 8:  # [V0.4.2修正] 分支2有9格（64-72）
                    result = 64 + branch_idx
                    print(f"[_parse_target-DEBUG] 分支2: branch_idx={branch_idx}, 返回={result}")
                    return result
                else:
                    print(f"[_parse_target-DEBUG] 分支2越界: branch_idx={branch_idx}")
            else:
                num = int(target_pos)
                # [V0.4.2修复] 允许索引0（起点），范围改为0-54
                if 0 <= num <= 54:
                    print(f"[_parse_target-DEBUG] 主路径: num={num}, 返回={num}")
                    return num
                else:
                    print(f"[_parse_target-DEBUG] 主路径越界: num={num}")
        except ValueError as e:
            print(f"[_parse_target-DEBUG] 解析错误: {e}")

        print(f"[_parse_target-DEBUG] 返回None")
        return None

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
                s_char_name = "未知S级角色"
                try:
                    import board_data as bd
                    config = bd.get_board_config(self.engine.current_board_id)
                    s_char_name = config.get("s_character_name", "未知S级角色")
                except Exception as e:
                    print(f"[警告] 获取S级角色名失败: {e}")
                self.log_text.insert(tk.END,
                    f"    >> 必定获得S级角色: {s_char_name}! <<\n", "s_char")

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
            rounds_total = sp.get("rounds_total", 3)
            chase_results = sp.get("chase_results", [])
            in_progress = sp.get("in_progress", False)
            
            if not chase_results:
                # [V0.3] 首次进入追击：显示初始化信息
                self.log_text.insert(tk.END, 
                    f"    [沉眠] 追击开始! 守护者逃离{sp.get('guardian_start', 9)}格, 剩余{rounds_total}次机会\n", "sleep")
                # 提示用户需要继续投掷
                self.log_text.insert(tk.END, 
                    f"    [沉眠] 请继续投掷追击守护者...\n", "normal")
            else:
                # 显示每轮追击结果
                for cr in chase_results:
                    pp, gp, dd = cr["player_pos"], cr["guardian_pos"], cr["dice"]
                    current_round = rounds_total - self.engine.chase_rounds_left
                    
                    if cr["caught"]:
                        self.log_text.insert(tk.END,
                            f"    [沉眠-第{current_round}轮] {dd}点 -> 玩家{pp}/守护者{gp} -> 追上!+{SLEEP_POOL_CONFIG['success_reward_gold']}金\n", "chip")
                    elif cr["failed"]:
                        self.log_text.insert(tk.END,
                            f"    [沉眠-第{current_round}轮] {dd}点 -> 玩家{pp}/守护者{gp} -> 逃脱!\n", "sleep")
                    else:
                        remaining = self.engine.chase_rounds_left
                        self.log_text.insert(tk.END,
                            f"    [沉眠-第{current_round}轮] {dd}点 -> 玩家{pp}/守护者{gp} (剩余{remaining}轮)\n", "normal")
                        
                        if in_progress:
                            self.log_text.insert(tk.END,
                                f"    [沉眠] 继续投掷追击...\n", "normal")

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

        print(f"[_refresh_all-入口] 红={s.dice_manager.red_dice} 蓝={s.dice_manager.blue_dice} 环石={s.dice_manager.ring_stone}")

        self.lbl_total_rolls.config(text=f"掷骰: {s.total_rolls}")
        self.lbl_pity.config(text=f"S保底: {s.s_pity_counter}/{pc}")
        self.lbl_gift.config(text=f"赠礼: {s.gift_counter}/{gc}")

        md = "变格" if s.is_variant else "基准"
        self.lbl_mode.config(text=f"当前: {md}棋盘")

        # [V0.5.3修复] 同步变格状态到棋盘画布，确保十连抽过程中棋盘显示实时更新
        if hasattr(self, 'board_canvas') and self.board_canvas:
            self.board_canvas.is_variant = s.is_variant

        dc = s.dice_manager.get_dice_count("red")
        if dc == float("inf"):
            # [V0.5.4修复] 先回填数值再设置无限勾选，避免Checkbutton的command触发同步时读到旧值
            self.red_dice_var.set(str(int(s.dice_manager.red_dice)))
            self.red_dice_entry.config(state=tk.DISABLED)
            self.red_inf_var.set(True)
        else:
            self.red_dice_var.set(str(int(dc)))
            self.red_dice_entry.config(state=tk.NORMAL)
            self.red_inf_var.set(False)

        # [V0.5.2修复] 直接显示环石原值，get_dice_count("ring") 已换算为可用抽数
        self.ring_stone_var.set(str(int(s.dice_manager.ring_stone)))

        # [V0.3新增] 蓝色骰子显示同步
        bc = s.dice_manager.get_dice_count("blue")
        if bc == float("inf"):
            # [V0.5.4修复] 先回填数值再设置无限勾选，避免Checkbutton的command触发同步时读到旧值
            self.blue_dice_var.set(str(int(s.dice_manager.blue_dice)))
            self.blue_dice_entry.config(state=tk.DISABLED)
            self.blue_inf_var.set(True)
        else:
            self.blue_dice_var.set(str(int(bc)))
            self.blue_dice_entry.config(state=tk.NORMAL)
            self.blue_inf_var.set(False)

        # [V0.5] 更新累计充值金额显示
        if hasattr(self, 'total_rmb_var') and hasattr(s.dice_manager, 'total_recharged_rmb'):
            self.total_rmb_var.set(f"{s.dice_manager.total_recharged_rmb:.2f}")

        print(f"[_refresh_all-出口] 红={s.dice_manager.red_dice} 蓝={s.dice_manager.blue_dice} 环石={s.dice_manager.ring_stone}")

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

        # [修复] 使用动态接口获取当前棋盘的奖励配置
        from board_data import (
            get_s_pool, get_a_pool, get_skin_system,
            A_DISK_POOL, B_DISK_POOL  # 弧盘池（全局共享）
        )
        current_board = getattr(self.board_canvas, 'current_board_id', 'limited_xun')

        s_pool = get_s_pool(current_board)
        a_pool = get_a_pool(current_board)
        skin_system = get_skin_system(current_board)

        for ch in s_pool:
            c = self.engine.state.get_item_count("s_characters", ch["name"])
            self.char_tree.insert("", tk.END, text=f"{ch['name']} (S)", values=(c,))
        for ch in a_pool:
            c = self.engine.state.get_item_count("a_characters", ch["name"])
            self.char_tree.insert("", tk.END, text=f"{ch['name']} (A)", values=(c,))

        skin_type_names = {
            "today_outfit": "穿搭",
            "vehicle_paint": "涂装",
            "glider_skin": "滑翔翼",
        }
        for stype_key, scfg in skin_system.items():
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
