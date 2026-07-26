# -*- coding: utf-8 -*-

"""
游戏逻辑引擎模块
包含 GameState、DiceManager、RollEngine、GachaEngine、SleepPoolEngine 等核心类
"""

import random
from board_data import (
    S_POOL_LIMITED, A_POOL_LIMITED,
    A_DISK_POOL, B_DISK_POOL,
    COMPANIONS_LIMITED, CELL_TYPES, CELL_RATE_BOUNDS,
    PITY_CONFIG, DUPLICATE_RULES, SLEEP_POOL_CONFIG,
    MIST_BOX_WHITE_CHIPS, SKIN_SYSTEM, SKIN_TYPE_KEYS, SKIN_CHARACTER,
    get_s_pool, get_a_pool, get_skin_character, get_skin_system, get_companions_list,
    get_board_rules,  # [新增] 动态规则接口
    get_board_config,  # [V0.4.1修复] 获取棋盘完整配置（含board_type）
    get_variant_transforms,  # [V0.4.2新增] 获取变格变换配置
)

# ============================================================
# [安全措施] 调试模式开关（发布版本必须设置为 False）
# ============================================================
DEBUG_MODE = False  # [!] 发布版本：False | 开发版本：True

def _write_debug_log(message):
    """
    [安全措施] 条件性日志写入函数

    仅在 DEBUG_MODE=True 时写入日志文件，发布版本完全禁用

    参数:
        message (str): 要写入的日志消息
    """
    if not DEBUG_MODE:
        return  # 发布版本：直接返回，不写文件

    try:
        import os
        _debug_log_path = os.path.join(os.path.dirname(__file__), "gacha_debug.log")
        import time as _time
        with open(_debug_log_path, "a", encoding="utf-8") as _f:
            _f.write(message + "\n")
    except Exception:
        pass  # 日志写入失败不影响主逻辑


class DiceManager:
    """骰子管理器 - 管理红色/蓝色骰子与环石的消耗与获取
    
    [扩展] 支持氪金系统（Phase 4 预留）
    - 环石作为氪金货币
    - 支持人民币充值购买环石
    - 支持有限模式（环石用完无法抽取）
    """

    def __init__(self):
        # ===== 基础资源 =====
        # [V0.5.3修复] 红骰初始为0；无限模式下只表示不扣减，不代表实际持有数量
        self.red_dice = 0
        self.blue_dice = 0
        self.ring_stone = 0

        # ===== 无限模式开关（当前默认开启）=====
        self.infinite_red = True
        self.infinite_blue = True   # [V0.3修复] 常驻棋盘默认无限蓝骰
        self.infinite_ring = True  # [关键] 关闭后启用真实消耗模式
        
        # ===== 氪金系统字段 =====
        # 累计充值金额（用于统计）
        self.total_recharged_rmb = 0.0
        
        # 累计消费环石数量（用于统计）
        self.total_consumed_ring_stones = 0
        
        # 充值历史记录（可选，用于审计）
        # 格式: [{"rmb": 6.0, "ring_stones": 60, "timestamp": "..."}, ...]
        self.recharge_history = []

    def get_dice_count(self, dice_type="red"):
        """获取指定类型骰子数量"""
        if dice_type == "red":
            return self.red_dice if not self.infinite_red else float("inf")
        elif dice_type == "blue":
            return self.blue_dice if not self.infinite_blue else float("inf")
        elif dice_type == "ring":
            # 环石按 160:1 换算为可用抽数
            return self.ring_stone // 160 if not self.infinite_ring else float("inf")
        return 0

    def consume_dice(self, count, dice_type="red"):
        """消耗骰子/环石，返回是否成功"""
        if dice_type == "red":
            if self.infinite_red:
                return True
            if self.red_dice >= count:
                self.red_dice -= count
                return True
            return False
        elif dice_type == "blue":
            if self.infinite_blue:
                return True
            if self.blue_dice >= count:
                self.blue_dice -= count
                return True
            return False
        elif dice_type == "ring":
            if self.infinite_ring:
                return True
            # 环石按 160:1 换算为骰子消耗
            stone_cost = count * 160
            if self.ring_stone >= stone_cost:
                self.ring_stone -= stone_cost
                return True
            return False
        return False

    def add_dice(self, count, dice_type="red"):
        """增加骰子/环石"""
        if dice_type == "red":
            self.red_dice += count
        elif dice_type == "blue":
            self.blue_dice += count
        elif dice_type == "ring":
            self.ring_stone += count

    def can_afford_roll(self, roll_mode="single", dice_type="red"):
        """判断是否能进行抽卡（优先使用指定类型，红骰不足时可用环石）"""
        needed = 1 if roll_mode == "single" else 10

        if dice_type == "red" and self.infinite_red:
            return True

        current = self.get_dice_count(dice_type)
        if current >= needed:
            return True

        if dice_type == "red" and not self.infinite_ring:
            # 环石按 160:1 换算为可用抽数
            ring_count = self.ring_stone // 160 if not self.infinite_ring else float("inf")
            if ring_count >= needed:
                return True

        return False

    def try_consume_for_roll(self, count=1, dice_type="red"):
        """
        尝试消耗进行抽取
        优先级: 指定类型骰子 > 红骰(备用) > 环石
        返回 (success, consumed_type)

        [V0.3新增] 支持蓝色骰子（常驻棋盘使用）
            - 当dice_type="blue"时，优先消耗蓝骰
            - 蓝骰不足时回退到红骰或环石

        [扩展] 当 infinite_ring=False 时，环石不足会返回失败
        """
        # [V0.3-调试] 记录消耗前的状态
        print(f"[try_consume] 请求: count={count}, type={dice_type}, 当前蓝骰={self.blue_dice}, 红骰={self.red_dice}, 环石={self.ring_stone}")

        # 优先使用指定类型的骰子（不跨类型回退）
        if dice_type == "blue":
            if self.consume_dice(count, "blue"):
                print(f"[try_consume] 结果: 消耗蓝骰成功, 剩余={self.blue_dice}")
                return True, "blue"
            # [V0.3修复] 蓝骰不足时不回退到红骰，直接使用环石
            # 之前bug: 跨类型回退导致常驻棋盘扣除红骰
        elif dice_type == "red":
            if self.consume_dice(count, "red"):
                print(f"[try_consume] 结果: 消耗红骰成功, 剩余={self.red_dice}")
                return True, "red"

        # 最后尝试环石（统一备用资源，160环石=1抽）
        if self.consume_dice(count, "ring"):
            if not self.infinite_ring:
                # 累计消耗环石数（实际扣除的环石）
                self.total_consumed_ring_stones += count * 160
            print(f"[try_consume] 结果: 消耗环石成功")
            return True, "ring"

        print(f"[try_consume] 结果: 消耗失败! 所有资源不足")
        return False, None

    # ===== [新增] 氪金系统方法（Phase 4 预留）=====
    
    def recharge(self, rmb_amount, ring_stones_received):
        """
        模拟充值 - 使用人民币购买环石
        
        参数:
            rmb_amount: 充值的人民币金额（元）
            ring_stones_received: 获得的环石数量
        
        返回:
            bool: 是否成功
        
        使用示例：
            >>> dice_manager.recharge(6.0, 60)   # 充值6元，获得60环石
            >>> dice_manager.recharge(30.0, 320) # 充值30元，获得320环石（可能有额外奖励）
        
        注意：
            - 此方法会自动更新余额和累计统计
            - 充值记录会被保存到历史中（用于审计）
        """
        if rmb_amount <= 0 or ring_stones_received <= 0:
            print(f"[错误] 充值金额必须大于0: RMB={rmb_amount}, 环石={ring_stones_received}")
            return False
        
        # 增加环石
        self.ring_stone += ring_stones_received
        
        # 更新累计充值金额
        self.total_recharged_rmb += rmb_amount
        
        # 记录充值历史
        from datetime import datetime
        recharge_record = {
            "rmb": rmb_amount,
            "ring_stones": ring_stones_received,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.recharge_history.append(recharge_record)
        
        print(f"[充值成功] 支付{rmb_amount}元，获得{ring_stones_received}环石，当前环石余额:{self.ring_stone}")
        
        return True
    
    def get_recharge_statistics(self):
        """
        获取充值统计数据
        
        返回:
            dict: 包含以下字段
            - total_rmb: 累计充值金额（元）
            - total_ring_stones_from_recharge: 通过充值获得的环石总数
            - recharge_count: 充值次数
            - current_ring_stone_balance: 当前环石余额
            - total_consumed_ring_stones: 累计消费环石数
        
        使用示例：
            >>> stats = dice_manager.get_recharge_statistics()
            >>> print(f"总充值: {stats['total_rmb']}元")
            >>> print(f"总消费环石: {stats['total_consumed_ring_stones']}")
        """
        total_ring_from_recharge = sum(record["ring_stones"] for record in self.recharge_history)
        
        return {
            "total_rmb": round(self.total_recharged_rmb, 2),
            "total_ring_stones_from_recharge": total_ring_from_recharge,
            "recharge_count": len(self.recharge_history),
            "current_ring_stone_balance": self.ring_stone,
            "total_consumed_ring_stones": self.total_consumed_ring_stones,
        }
    
    def can_afford_with_current_resources(self, rolls_needed, price_per_roll=160):
        """
        检查当前资源是否足够进行指定次数的抽取（有限模式）
        
        参数:
            rolls_needed: 需要抽取的次数
            price_per_roll: 单抽价格（默认160环石）
        
        返回:
            dict: {
                "can_afford": bool,           # 是否能负担
                "dice_available": int,       # 可用骰子数
                "ring_stone_needed": int,     # 还需要多少环石
                "rmb_needed_to_recharge": float,  # 需要充多少钱才能抽完
                "shortfall_reason": str       # 不足原因（如果能负担则为空）
            }
        
        使用示例：
            >>> result = dice_manager.can_afford_with_current_resources(10)
            >>> if not result["can_afford"]:
            ...     print(f"还需要充值 {result['rmb_needed_to_recharge']} 元")
        """
        # 计算可用资源（红骰优先，环石按 160:1 折算为抽数）
        available_dice = self.get_dice_count("red")
        if available_dice == float("inf"):
            available_dice = 999999  # 无限模式视为很多
        
        # 计算还需要多少次抽取
        remaining_rolls = max(0, rolls_needed - min(available_dice, rolls_needed))
        
        # 计算需要的环石
        ring_stone_needed = remaining_rolls * price_per_roll
        
        # 检查环石是否足够（get_dice_count("ring") 已返回可用抽数，需再乘 160 得到环石数）
        current_ring = self.get_dice_count("ring")
        if current_ring == float("inf"):
            can_afford = True
            shortfall_reason = ""
        elif current_ring * 160 >= ring_stone_needed:
            can_afford = True
            shortfall_reason = ""
        else:
            can_afford = False
            shortfall = ring_stone_needed - current_ring * 160
            shortfall_reason = f"环石不足：需要{ring_stone_needed}，当前有{current_ring * 160}"
            
            # 估算需要充值多少钱（按充值信息.csv 默认 1元=10环石）
            estimated_rmb_needed = shortfall / 10.0
            
            return {
                "can_afford": False,
                "dice_available": int(available_dice) if available_dice != 999999 else -1,
                "ring_stone_needed": ring_stone_needed,
                "rmb_needed_to_recharge": round(estimated_rmb_needed, 2),
                "shortfall_reason": shortfall_reason,
            }
        
        return {
            "can_afford": can_afford,
            "dice_available": int(available_dice) if available_dice != 999999 else -1,
            "ring_stone_needed": ring_stone_needed,
            "rmb_needed_to_recharge": 0.0,
            "shortfall_reason": shortfall_reason,
        }


class GameState:
    """游戏状态管理器 - 管理所有游戏运行时状态"""

    def __init__(self):
        self.dice_manager = DiceManager()
        self.total_rolls = 0
        self.s_pity_counter = 0
        self.gift_counter = 0
        self.is_variant = False
        self.gold_chips = 0
        self.white_chips = 0
        self.collection = {
            "s_characters": {},
            "a_characters": {},
            "a_disks": {},
            "b_disks": {},
            "skins": {},
        }
        self.sleep_pool_active = False
        self.roll_history = []
        # 皮肤累计领取记录: {skin_type_key: bool} 记录是否已通过累计次数领取
        self.skin_claimed = {stype: False for stype in SKIN_TYPE_KEYS}

    def reset(self):
        """重置所有游戏状态"""
        self.__init__()

    def add_to_collection(self, item_type, item_name):
        """将获得物品加入收集记录，返回是否为重复及重复次数"""
        col = self.collection[item_type]
        if item_name in col:
            col[item_name] += 1
            return True, col[item_name]
        else:
            col[item_name] = 1
            return False, 1

    def get_item_count(self, item_type, item_name):
        """获取物品已获得次数"""
        return self.collection.get(item_type, {}).get(item_name, 0)

    def increment_s_pity(self):
        """增加S级保底计数，检查是否触发变格或硬保底"""
        pity_cfg = PITY_CONFIG["s_pity"]

        # [V0.5.5修复] 变格状态不再在本次投掷中立即生效，
        # 而是等到本次结算后再启用，供下一次投掷使用。
        # 这样第70抽本身仍按常规格子结算，第71抽起才应用变格格子变换。
        self.s_pity_counter += 1
        if self.s_pity_counter >= pity_cfg["hard_pity"]:
            return "hard_pity"
        if self.s_pity_counter >= pity_cfg["variant_threshold"]:
            return "variant"
        return None

    def reset_s_pity(self):
        """获得S级角色后重置保底计数和变格状态"""
        self.s_pity_counter = 0
        self.is_variant = False

    def check_gift(self):
        """检查集点赠礼，每10次触发一次"""
        cfg = PITY_CONFIG["gift_pity"]
        self.gift_counter += 1
        if self.gift_counter >= cfg["interval"]:
            self.gift_counter = 0
            return True
        return False


class RollEngine:
    """掷骰与落格引擎"""

    @staticmethod
    def roll_dice():
        """掷骰子，返回1~6的点数"""
        return random.randint(1, 6)

    @staticmethod
    def determine_cell_type():
        """根据概率分布决定落入哪种格子类型"""
        r = random.random()
        for cell_key, start, end in CELL_RATE_BOUNDS:
            if start <= r < end:
                return cell_key
        return list(CELL_TYPES.keys())[-1]


class GachaEngine:
    """抽卡判定引擎 - 处理S级/A级/B级/弧盘/皮肤的抽签判定"""

    def __init__(self, state, board_id="limited_xun"):
        self.state = state
        self.board_id = board_id
        # 加载当前棋盘的动态奖励配置
        self._load_board_rewards(board_id)

    def _load_board_rewards(self, board_id):
        """
        加载指定棋盘的奖励池数据和规则配置
        
        参数:
            board_id: 棋盘ID（如 "limited_xun", "limited_requiem", "limited_caerus"）
        
        说明：
            - 从board_data动态接口获取当前棋盘的奖励配置和概率规则
            - 支持运行时切换棋盘（调用此方法重新加载即可）
            - [关键] 每个棋盘可以有完全独立的概率配置！
        """
        self.board_id = board_id
        # [V0.3新增] 记录棋盘类型（用于UI显示差异）
        try:
            board_config = get_board_config(board_id)
            self.board_type = board_config.get("board_type", "limited")
            print(f"[GachaEngine] 初始化棋盘: {board_id}, board_type={self.board_type}")
        except Exception as e:
            self.board_type = "limited"
            print(f"[GachaEngine] 初始化棋盘失败: {board_id}, 使用默认board_type=limited, 错误={e}")
        # 动态加载S级/A级角色池
        self.s_pool = get_s_pool(board_id)
        self.a_pool = get_a_pool(board_id)
        # 动态加载同行角色列表
        self.companions_list = get_companions_list(board_id)
        # 动态加载皮肤系统
        self.skin_char = get_skin_character(board_id)
        self.skin_system = get_skin_system(board_id)
        
        # [新增] 动态加载完整规则配置（支持每个棋盘独立概率！）
        self.rules = get_board_rules(board_id)

    def switch_board(self, new_board_id):
        """
        切换到新棋盘（重新加载所有奖励池）
        
        参数:
            new_board_id: 新的棋盘ID
        
        使用场景：
            - 用户在界面切换浔/安魂曲棋盘时
            - 需要立即更新所有抽卡判定逻辑
        """
        if new_board_id != self.board_id:
            print(f"[系统] 切换棋盘: {self.board_id} -> {new_board_id}")
            self._load_board_rewards(new_board_id)

    def gacha_s_character(self):
        """
        S级角色抽签判定
        返回: (是否获得, 角色名, 获得原因)

        [关键修复] 使用动态加载的规则，支持每个棋盘独立概率配置
        例如：浔棋盘 S级概率 1.87%，常驻棋盘 6个S级均分1.86%

        [V0.3新增] 支持多S角色池（常驻棋盘6个S级角色随机抽取）
        """
        # [修复] 优先使用动态规则，回退到全局默认
        if hasattr(self, 'rules') and 's_pity_hard' in self.rules:
            rules = self.rules
            pity_variant_threshold = rules.get("s_pity_variant_threshold", 70)
            pity_hard = rules.get("s_pity_hard", 90)
            base_rate_variant = rules.get("s_base_rate_variant", 0.1959)
            base_rate_normal = rules.get("s_base_rate_normal", 0.0099)
        else:
            # 回退到全局配置（向后兼容）
            pity_cfg = PITY_CONFIG["s_pity"]
            pity_variant_threshold = pity_cfg.get("variant_threshold", 70)
            pity_hard = pity_cfg.get("hard_pity", 90)
            base_rate_variant = pity_cfg.get("base_rate_variant", 0.1959)
            base_rate_normal = pity_cfg.get("base_rate_normal", 0.0099)

        # 硬保底判定
        if self.state.s_pity_counter >= pity_hard - 1:
            # 多S角色池：随机选择一个（常驻棋盘6选1，限定棋盘只有1个所以必选中）
            char_name = random.choice([c["name"] for c in self.s_pool])
            self.state.reset_s_pity()
            return True, char_name, "硬保底"

        # 变格/基准概率判定
        base_rate = base_rate_variant if self.state.is_variant else base_rate_normal
        if random.random() < base_rate:
            # 多S角色池：随机选择一个
            char_name = random.choice([c["name"] for c in self.s_pool])
            self.state.reset_s_pity()
            return True, char_name, "变格" if self.state.is_variant else "常规"

        return False, None, None

    def gacha_a_character_from_gift(self):
        """集点赠礼中的A级角色抽取（仅从非gift_only的角色中抽取）"""
        eligible = [c for c in self.a_pool if not c["gift_only"]]
        total_rate = sum(c["rate"] for c in eligible)
        r = random.random() * total_rate
        cumulative = 0.0
        for char in eligible:
            cumulative += char["rate"]
            if r < cumulative:
                return char["name"]
        return eligible[-1]["name"]

    def gacha_a_disk(self):
        """随机获得一个A级弧盘"""
        return random.choice(A_DISK_POOL)

    def gacha_b_disk(self):
        """随机获得一个B级弧盘"""
        return random.choice(B_DISK_POOL)

    def gacha_companion(self):
        """
        于此同行格子判定
        返回: (角色名, 品阶)

        [V0.3新增] 支持常驻棋盘的随机同行机制：
        - 随机S级：从S级池中随机选1个
        - 随机A级：从A级主池中随机选1个
        """
        cell = CELL_TYPES["companion"]
        sub_rates = cell["sub_rates"]
        r = random.random()

        if r < sub_rates["s_character"]:
            s_companions = [c for c in self.companions_list if c["rank"] == "S"]
            if not s_companions:
                return "未知S级", "S"
            companion = random.choice(s_companions)
            char_name = companion["name"]

            # 常驻棋盘：处理"随机S级"标记
            if char_name == "随机S级" and self.s_pool:
                char_name = random.choice([c["name"] for c in self.s_pool])

            return char_name, "S"
        else:
            a_companions = [c for c in self.companions_list if c["rank"] == "A"]
            if not a_companions:
                return "未知A级", "A"
            companion = random.choice(a_companions)
            char_name = companion["name"]

            # 常驻棋盘：处理"随机A级"标记
            if char_name == "随机A级" and self.a_pool:
                char_name = random.choice([c["name"] for c in self.a_pool])

            return char_name, "A"

    def gacha_gift(self):
        """
        集点赠礼判定
        返回: (类型, 名称) 或 None
        """
        cfg = PITY_CONFIG["gift_pity"]
        r = random.random()
        if r < cfg["a_character_rate"]:
            name = self.gacha_a_character_from_gift()
            return ("a_character", name)
        else:
            name = self.gacha_a_disk()
            return ("a_disk", name)

    def calculate_duplicate_reward(self, item_type, item_name, count):
        """
        计算重复获得补偿
        参数:
            item_type: 物品类型 (s_character / a_character / a_disk / b_disk)
            item_name: 物品名称
            count: 当前总获得次数（含本次）
        返回: 补偿字典 {fragment, gold_chip, white_chip}
        """
        reward = {"fragment": 0, "gold_chip": 0, "white_chip": 0}
        rules = DUPLICATE_RULES.get(item_type, {})

        if item_type in ("s_character", "a_character"):
            if 2 <= count <= 7:
                rule = rules.get("range_2_7", {})
                reward["fragment"] = rule.get("fragment", 0)
                reward["gold_chip"] = rule.get("gold_chip", 0)
            elif count >= 8:
                rule = rules.get("range_8_plus", {})
                reward["gold_chip"] = rule.get("gold_chip", 0)
        elif item_type == "a_disk":
            reward["gold_chip"] = rules.get("extra_gold_chip", 0)
        elif item_type == "b_disk":
            reward["white_chip"] = rules.get("extra_white_chip", 0)

        return reward

    def gacha_skin(self, skin_type_key):
        """
        装扮礼遇皮肤抽取（落格触发）
        参数: skin_type_key - 皮肤类型key (today_outfit / vehicle_paint / glider_skin)
        返回: (皮肤完整名称, 皮肤类型key)
        
        [关键修复] 使用动态加载的skin_system，确保不同棋盘获得对应角色的皮肤
        """
        # 优先使用动态皮肤系统，如果不存在则回退到全局默认
        if hasattr(self, 'skin_system') and skin_type_key in self.skin_system:
            cfg = self.skin_system[skin_type_key]
        else:
            cfg = SKIN_SYSTEM[skin_type_key]
        
        skins_dict = cfg["skins"]
        char_name = random.choice(list(skins_dict.keys()))
        skin_full_name = skins_dict[char_name]
        return skin_full_name, skin_type_key


class SleepPoolEngine:
    """沉眠池追击引擎"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置追击状态"""
        self.active = False
        self.guardian_pos = 0
        self.player_pos = 0
        self.rounds_left = SLEEP_POOL_CONFIG["max_chase_rounds"]

    def start_chase(self):
        """开始追击事件"""
        self.active = True
        self.guardian_pos = SLEEP_POOL_CONFIG["guardian_flee_distance"]
        self.player_pos = 0
        self.rounds_left = SLEEP_POOL_CONFIG["max_chase_rounds"]

    def chase_round(self, dice_value):
        """
        执行一轮追击
        参数: dice_value 玩家掷出的骰子点数
        返回: (是否追上, 是否失败, 剩余回合, 守护者位置, 玩家位置)
        """
        if not self.active:
            return False, False, 0, 0, 0

        self.player_pos += dice_value
        self.guardian_pos += SLEEP_POOL_CONFIG["guardian_speed"]
        self.rounds_left -= 1

        caught = self.player_pos >= self.guardian_pos
        failed = self.rounds_left <= 0 and not caught

        if caught or failed:
            self.active = False

        return caught, failed, self.rounds_left, self.guardian_pos, self.player_pos


class GameEngine:
    """
    游戏主引擎 - 整合所有子系统，提供完整的单次掷骰流程
    新版: 使用固定棋盘布局 + 分支机制 + 概率暗箱
    """

    def __init__(self, board_id="limited_xun"):
        self.state = GameState()
        self.gacha = GachaEngine(self.state, board_id)
        self.sleep_pool = SleepPoolEngine()
        self.roll_engine = RollEngine()
        # 分支状态追踪
        self.in_branch = None       # 当前所在分支: "s_character" / "skin_surprise" / None
        self.branch_step = 0        # 在分支内的步数(0-based)
        # [V0.3新增] 追击状态追踪（分回合手动投掷）
        self.in_chase = False       # 是否处于沉眠池追击模式
        self.chase_rounds_left = 0  # 剩余追击回合数
        self.chase_player_pos = 0   # 追击中玩家位置
        self.chase_guardian_pos = 0 # 追击中守护者位置
        self.current_board_id = board_id

    def switch_board(self, new_board_id):
        """
        切换到新棋盘（更新所有子系统的奖励配置）
        
        参数:
            new_board_id: 新的棋盘ID
        
        说明：
            - 调用GachaEngine.switch_board()更新奖励池
            - 更新当前棋盘ID记录
        """
        if new_board_id != self.current_board_id:
            print(f"[GameEngine] 切换棋盘: {self.current_board_id} -> {new_board_id}")
            self.gacha.switch_board(new_board_id)
            self.current_board_id = new_board_id

    def execute_single_roll(self, current_pos_idx=0, cell_type=None, cell_name=None,
                            branch_entries=None, is_in_branch=None,
                            branch_step=0):
        """
        执行单次完整掷骰流程（新版：支持固定棋盘+分支）

        参数:
            current_pos_idx: 当前棋子位置索引
            cell_type: 当前落格的类型（从固定棋盘获取）
            cell_name: 当前落格的原始名称（如"于此同行（海月）"，用于同行格子确定具体角色）
            branch_entries: 分支元数据字典（从BoardCanvas获取）
            is_in_branch: 当前是否在分支内
            branch_step: 在分支内的步数

        返回: 结果字典，包含本次所有信息
        """
        result = {
            "roll_number": self.state.total_rolls + 1,
            "dice_value": 0,
            "cell_type": None,
            "cell_name": None,
            "rewards": [],
            "pity_event": None,
            "gift_result": None,
            "sleep_pool_event": None,
            "dice_gained": 0,
            "branch_event": None,     # 分支事件: enter/exit/extra_roll_s/None
            "new_position_idx": current_pos_idx,  # 更新后的位置
            "new_branch_state": is_in_branch,
            "new_branch_step": branch_step,
        }

        # 1. 掷骰子
        dice_value = self.roll_engine.roll_dice()
        result["dice_value"] = dice_value
        self.state.total_rolls += 1

        # 1.5 皮肤累计领取检查
        claim_rewards = self._check_skin_claims()

        # 2. 确定落格类型（使用固定棋盘传入的类型，或概率暗箱）
        if cell_type:
            ck = cell_type
        else:
            ck = self.roll_engine.determine_cell_type()

        # [V0.3新增] 根据实际格子名称修正类型（常驻棋盘的失纬棋盒等特殊格子）
        if cell_name and "失纬棋盒" in str(cell_name):
            ck = "lost_treasure_box"

        cell_info = CELL_TYPES.get(ck)
        if not cell_info:
            ck = "apprentice_chest"
            cell_info = CELL_TYPES[ck]

        result["cell_type"] = ck
        result["cell_name"] = cell_info.get("name", ck)

        # 3. 检测分支入口/出口
        # 防御性检查：只有当参数标记不在分支中 且 引擎当前也不在分支中时，才触发进入
        if branch_entries and not is_in_branch and not self.in_branch:
            for bkey, bdata in branch_entries.items():
                if current_pos_idx == bdata["entry_main_idx"]:
                    # 正好落在分支入口！触发分支进入
                    result["branch_event"] = ("enter", bkey, bdata)
                    self.in_branch = bkey
                    self.branch_step = 0
                    result["new_branch_state"] = bkey
                    result["new_branch_step"] = 0
                    print(f"[game_logic] [OK] 触发分支进入: {bkey} (current_pos={current_pos_idx})")
                    break

        # S级角色分支特殊处理：必定获得（无需额外掷骰）
        # "于此同行"到达后直接获得S级角色
        if is_in_branch == "s_character" and ck == "companion":
            result["branch_event"] = ("s_got",)  # 标记已获得S级角色

        # 5. 根据格子类型执行效果（使用概率暗箱）
        rewards = []
        dice_gained = 0

        # [V0.4.2新增] 变格类型特殊处理
        if ck == "companion_s":
            # 勇者宝箱变 → 必定获得S级角色（100%）
            rewards = self._resolve_variant_brave_chest_s()
        elif ck == "apprentice_chest":
            rewards = self._resolve_apprentice_chest_darkbox()
        elif ck == "brave_chest":
            rewards = self._resolve_brave_chest_darkbox()
        elif ck == "companion":
            rewards = self._resolve_companion_darkbox(cell_name=cell_name)  # 传入格子名称
        elif ck == "mist_box":
            rewards = self._resolve_mist_box(cell_name=cell_name)  # 传入格子名称
        elif ck == "lost_treasure_box":
            rewards = self._resolve_lost_treasure_box(cell_name=cell_name)  # 失纬棋盒（常驻独有）
        elif ck in ("arcade_blind",):
            # [V0.3修复] 根据格子名称区分：弧光盲盒(单独) vs 弧光盲盒+沉眠池(组合)
            if cell_name and "沉眠池" in str(cell_name):
                # 组合格子：触发追击
                rewards, sp_event = self._resolve_arcade_blind_sleep()
                result["sleep_pool_event"] = sp_event
            else:
                # 单独格子：只获得弧光盲盒奖励
                rewards = self._resolve_arcade_blind()
        elif ck == "roll_again":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 1)
            # [V0.3新增] 常驻棋盘用蓝色骰子，限定棋盘用红色骰子
            dice_color = "blue" if self.gacha.board_type == "permanent" else "red"
            dice_color_cn = "蓝色" if dice_color == "blue" else "红色"
            print(f"[骰子奖励-再来一次] board_type={self.gacha.board_type}, 颜色={dice_color}, 数量={dice_gained}")
            self.state.dice_manager.add_dice(dice_gained, dice_color)
            rewards.append({"type": "dice", "name": f"+{dice_gained}{dice_color_cn}骰子"})
        elif ck == "multi_surprise":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 5)
            # [V0.3新增] 常驻棋盘用蓝色骰子，限定棋盘用红色骰子
            dice_color = "blue" if self.gacha.board_type == "permanent" else "red"
            dice_color_cn = "蓝色" if dice_color == "blue" else "红色"
            # [V0.4.1调试-已验证] print(f"[骰子奖励-多重惊喜] board_type={self.gacha.board_type}, 颜色={dice_color}, 数量={dice_gained}")
            self.state.dice_manager.add_dice(dice_gained, dice_color)
            rewards.append({"type": "dice", "name": f"+{dice_gained}{dice_color_cn}骰子"})
        elif ck in SKIN_TYPE_KEYS:
            rewards = self._resolve_skin_cell_darkbox(ck)

        result["rewards"] = rewards + claim_rewards
        result["dice_gained"] = dice_gained
        result["skin_claims"] = claim_rewards

        # 6. S级保底计数 + 判定（暗箱：保底独立于格子类型）
        # [修复] 总是执行increment_s_pity()确保计数正确
        has_s_in_rewards = any(r.get("type") == "s_character" for r in rewards)

        pity_event = self.state.increment_s_pity()
        result["pity_event"] = pity_event

        # [修复] 如果获得了S级角色，重置保底计数器
        if has_s_in_rewards:
            self.state.reset_s_pity()
            result["pity_event"] = None
            pity_event = None

        if pity_event in ("variant", "hard_pity") and not has_s_in_rewards:
            got_s, s_name, reason = self.gacha.gacha_s_character()
            if got_s:
                is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
                dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
                self.state.gold_chips += dup_reward.get("gold_chip", 0)
                reward_entry = {
                    "type": "s_character",
                    "name": s_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "reason": reason,
                    "fragment": dup_reward.get("fragment", 0),
                    "extra_gold": dup_reward.get("gold_chip", 0),
                }
                rewards.append(reward_entry)
                result["rewards"] = rewards

        # 7. 集点赠礼检查
        gift_result = None

        # [V0.3-已注释] 终极调试-gift日志（需要时可取消）
        print(f"[终极调试-gift前] gift_counter={self.state.gift_counter}")

        if self.state.check_gift():
            # [V0.3-已注释] 终极调试-gift触发日志（需要时可取消）
            print(f"[终极调试-gift触发] gift_counter重置为{self.state.gift_counter}")

            gift_item = self.gacha.gacha_gift()
            gift_type, gift_name = gift_item
            is_dup, dup_count = self.state.add_to_collection(
                {"a_character": "a_characters", "a_disk": "a_disks"}[gift_type],
                gift_name
            )
            dup_reward = self.gacha.calculate_duplicate_reward(gift_type, gift_name, dup_count)
            self.state.gold_chips += dup_reward.get("gold_chip", 0)
            gift_result = {
                "type": gift_type,
                "name": gift_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "fragment": dup_reward.get("fragment", 0),
                "extra_gold": dup_reward.get("gold_chip", 0),
            }
        result["gift_result"] = gift_result

        # 8. 记录历史
        self.state.roll_history.append(result)

        return result

    def execute_single_roll_with_target(self, current_pos_idx=0, current_cell_type=None,
                                        target_pos_idx=None,  # [V0.4.3修复] 目标位置索引（用于变格检测）
                                        target_cell_type=None, target_cell_name=None,
                                        dice_value=None,
                                        branch_entries=None, is_in_branch=None,
                                        branch_step=0):
        """
        使用指定目标格子类型执行单次掷骰（修复版）

        与 execute_single_roll 的区别：
        - 使用传入的 dice_value，不重新掷骰
        - 使用 target_cell_type 作为落格类型（来自可视化棋盘）
        - 保留分支检测、奖励计算等完整逻辑

        参数:
            current_pos_idx: 当前位置索引
            current_cell_type: 当前位置的格子类型（用于分支检测）
            target_cell_type: 目标位置的格子类型（用于抽奖）
            target_cell_name: 目标位置的原始名称（如"于此同行（海月）"，用于同行格子确定角色）
            dice_value: 已确定的骰子点数
            branch_entries: 分支元数据
            is_in_branch: 是否在分支内
            branch_step: 分支内步数
        """
        result = {
            "roll_number": self.state.total_rolls + 1,
            "dice_value": dice_value if dice_value else 1,
            "cell_type": target_cell_type or "apprentice_chest",
            "cell_name": None,
            "rewards": [],
            "pity_event": None,
            "gift_result": None,
            "sleep_pool_event": None,
            "dice_gained": 0,
            "branch_event": None,
            "new_position_idx": current_pos_idx,
            "new_branch_state": is_in_branch,
            "new_branch_step": branch_step,
        }

        # [终极调试] 记录函数入口状态
        import time as _time
        _entry_time = _time.time()

        # [文件日志] 写入调试文件（仅DEBUG_MODE=True时生效）
        _write_debug_log(f"[{_entry_time:.3f}] [入口] roll={result['roll_number']} total_rolls={self.state.total_rolls} s_pity={self.state.s_pity_counter} gift={self.state.gift_counter}")

        # [V0.3-已注释] 终极调试-入口日志（需要时可取消）
        print(f"[终极调试-入口] [{_entry_time:.3f}] roll_number={result['roll_number']}, 执行前: total_rolls={self.state.total_rolls}, s_pity={self.state.s_pity_counter}, gift={self.state.gift_counter}")
        # [V0.4.1调试-已验证] print(f"[终极调试-入口] gacha.board_id={self.gacha.board_id}, gacha.board_type={self.gacha.board_type}")

        self.state.total_rolls += 1

        # [V0.5.5修复] S级保底计数在格子结算前更新，但变格状态不立即生效。
        # 第70抽仍按当前变格状态（通常为False）结算，结算后再启用变格；
        # 第71抽起 is_variant 为 True，才应用变格格子变换。
        pity_event = self.state.increment_s_pity()
        result["pity_event"] = pity_event

        # [V0.5.4/V0.5.5修复] 记录本次投掷实际使用的变格状态（结算前的状态），
        # 供UI在动画期间正确渲染变格格子。获得S级角色后 is_variant 会被重置。
        result["was_variant"] = self.state.is_variant

        # [V0.3-已注释] 终极调试-total_rolls+1日志（需要时可取消）
        print(f"[终极调试-total_rolls+1] [{_time.time():.3f}] total_rolls={self.state.total_rolls}")

        # [文件日志-步骤1]
        _write_debug_log(f"[{_time.time():.3f}] [步骤1-total_rolls+1] roll={result['roll_number']} total_rolls={self.state.total_rolls}")

        # [V0.3-FINAL] 追击模式：不再拦截正常结算，而是作为附加内容
        # 追击是投掷的额外奖励，不影响正常的棋子移动和格子结算
        # 追击状态将在正常结算完成后处理（见函数末尾）

        # [关键修复] 已在_resolve_arcade_blind_sleep中处理异常
        claim_rewards = self._check_skin_claims()

        # [文件日志-步骤2]
        _write_debug_log(f"[{_time.time():.3f}] [步骤2-skin_claims] roll={result['roll_number']}")

        # 使用目标位置的格子类型作为落格类型
        ck = target_cell_type or "apprentice_chest"

        # [V0.4.2修复] 变格状态检测：应用变格变换（与显示层_draw_grid_cells保持一致）
        # [V0.4.3核心修复] 使用目标位置(target_pos_idx)而非当前位置(current_pos_idx)进行变格检测
        variant_check_pos = target_pos_idx if target_pos_idx is not None else current_pos_idx
        print(f"[变格检测] ===== 开始检测位置{variant_check_pos}的变格状态 ===== (current={current_pos_idx}, target={target_pos_idx})")
        print(f"[变格检测] self.state.is_variant={self.state.is_variant}")
        print(f"[变格检测] self.state.s_pity_counter={getattr(self.state, 's_pity_counter', 'N/A')}")
        if self.state.is_variant:
            print(f"[变格检测] is_variant=True, 开始查找变格变换")
            try:
                # [V0.4.3修复] 使用current_board_id（GameEngine属性），而不是board_id（GachaEngine属性）
                board_id_for_variant = getattr(self, 'board_id', None) or getattr(self, 'current_board_id', 'limited_xun')
                variant_transforms = get_variant_transforms(board_id_for_variant)
                print(f"[变格检测] board_id={board_id_for_variant}, transforms数量={len(variant_transforms) if variant_transforms else 0}")

                # [V0.4.3新增] 列出所有变换配置的keys
                if variant_transforms:
                    transform_keys = list(variant_transforms.keys())
                    print(f"[变格检测] 所有变换keys: {transform_keys}")

                if variant_transforms:
                    # [V0.4.3核心修复] 同时尝试数字索引和分支标识符
                    # 主路径: 0-54 (直接用数字)
                    # 分支B1: 55-63 (对应 B1-0 ~ B1-8)
                    # 分支B2: 64-72 (对应 B2-0 ~ B2-8)
                    cell_idx_key = variant_check_pos
                    print(f"[变格检测] 查找key={cell_idx_key}(类型:{type(cell_idx_key)}), target_cell_type原始={target_cell_type}")

                    # 构建候选keys列表：先尝试原始key，再尝试分支标识符
                    candidate_keys = [cell_idx_key]

                    # [V0.4.3新增] 分支索引到标识符的映射
                    if isinstance(cell_idx_key, int):
                        if 55 <= cell_idx_key <= 63:
                            branch_id = cell_idx_key - 55
                            candidate_keys.append(f"B1-{branch_id}")
                            print(f"[变格检测] 检测到分支1位置{cell_idx_key}, 添加候选key: B1-{branch_id}")
                        elif 64 <= cell_idx_key <= 72:
                            branch_id = cell_idx_key - 64
                            candidate_keys.append(f"B2-{branch_id}")
                            print(f"[变格检测] 检测到分支2位置{cell_idx_key}, 添加候选key: B2-{branch_id}")

                    # 遍历所有候选key查找变换
                    transform = None
                    for key in candidate_keys:
                        if key in variant_transforms:
                            transform = variant_transforms[key]
                            print(f"[变格检测] 使用匹配key={key}找到变换")
                            break

                    if transform:
                        original_ck = ck
                        ck = transform["variant"]  # 使用变格后的类型
                        print(f"[变格检测] ✅ 位置{cell_idx_key}(key={cell_idx_key}): {original_ck} -> {ck} ({transform['variant_name']})")
                    else:
                        print(f"[变格检测] ❌ 位置{cell_idx_key}无变格变换 (target_cell_type={target_cell_type}, 候选keys={candidate_keys})")
            except Exception as e:
                import traceback
                print(f"[警告] 变格检测失败: {e}")
                traceback.print_exc()
        else:
            print(f"[变格检测] is_variant=False, 跳过变格变换 (垫刀数可能<70)")

        # [V0.3新增] 根据实际格子名称修正类型（常驻棋盘的失纬棋盒等特殊格子）
        if target_cell_name and "失纬棋盒" in str(target_cell_name):
            ck = "lost_treasure_box"

        cell_info = CELL_TYPES.get(ck)
        if not cell_info:
            ck = "apprentice_chest"
            cell_info = CELL_TYPES[ck]

        result["cell_type"] = ck
        result["cell_name"] = cell_info.get("name", ck)

        # [文件日志-步骤3]
        _write_debug_log(f"[{_time.time():.3f}] [步骤3-cell_type] roll={result['roll_number']} cell_type={ck}")

        # 检测分支入口（基于当前位置）
        # 防御性检查：只有当参数标记不在分支中 且 引擎当前也不在分支中时，才触发进入
        if branch_entries and not is_in_branch and not self.in_branch:
            print(f"\n[分支检测] 当前位置={current_pos_idx}, 是否在分支={is_in_branch}")
            for bkey, bdata in branch_entries.items():
                print(f"[分支检测] 检查{bkey}: 入口={bdata['entry_main_idx']}, 匹配={current_pos_idx == bdata['entry_main_idx']}")
                if current_pos_idx == bdata["entry_main_idx"]:
                    result["branch_event"] = ("enter", bkey, bdata)
                    self.in_branch = bkey
                    self.branch_step = 0
                    result["new_branch_state"] = bkey
                    result["new_branch_step"] = 0
                    print(f"[分支检测] [OK] 触发进入{bkey}分支！")
                    break
            else:
                print(f"[分支检测] [X] 未匹配任何分支入口")

        # S级角色分支特殊处理：必定获得（无需额外掷骰）
        if is_in_branch == "s_character" and ck == "companion":
            result["branch_event"] = ("s_got",)  # 标记已获得S级角色

        # 根据目标格子类型执行效果
        rewards = []
        dice_gained = 0

        # [V0.4.3新增] 奖励分支诊断日志
        print(f"[奖励检测] ===== 开始计算奖励 =====")
        print(f"[奖励检测] ck={ck}, target_cell_name={target_cell_name}, 位置={variant_check_pos}")

        # [V0.4.2新增] 变格类型特殊处理
        if ck == "companion_s":
            # 勇者宝箱变 → 必定获得S级角色（100%）
            print(f"[奖励检测] ✅ 走变格路径: companion_s (必定S级角色)")
            rewards = self._resolve_variant_brave_chest_s()
            print(f"[奖励检测] 变格奖励数: {len(rewards) if rewards else 0}")
            if rewards:
                for r in rewards:
                    print(f"[奖励检测]   奖励: {r}")
        elif ck == "apprentice_chest":
            print(f"[奖励检测] 走普通路径: apprentice_chest (学徒宝箱)")
            rewards = self._resolve_apprentice_chest_darkbox()
        elif ck == "brave_chest":
            print(f"[奖励检测] 走普通路径: brave_chest (勇者宝箱) ⚠️ 如果该位置应该变格则说明变格失败！")
            rewards = self._resolve_brave_chest_darkbox()
        elif ck == "companion":
            # [V0.3-已修复] 同行诊断日志（已注释，需要时可取消）
            # try:
            #     with open("_companion_debug.log", "a", encoding="utf-8") as f:
            #         f.write(f"[{__import__('time').time():.3f}] [companion处理]\n")
            #         f.write(f"  ck={ck}, target_cell_name={repr(target_cell_name)}\n")
            #         f.write(f"  in_chase={self.in_chase}\n")
            #         f.write("-" * 50 + "\n")
            # except Exception as e:
            #     print(f"[诊断-文件写入失败] {e}")
            rewards = self._resolve_companion_darkbox(cell_name=target_cell_name)  # 传入目标格子名称
            # try:
            #     with open("_companion_debug.log", "a", encoding="utf-8") as f:
            #         f.write(f"[{__import__('time').time():.3f}] [companion结果]\n")
            #         f.write(f"  rewards长度={len(rewards) if rewards else 0}\n")
            #         if rewards:
            #             f.write(f"  rewards[0]={rewards[0]}\n")
            #         f.write("-" * 50 + "\n")
            # except Exception as e:
            #     print(f"[诊断-文件写入失败] {e}")
        elif ck == "mist_box":
            rewards = self._resolve_mist_box(cell_name=target_cell_name)  # 传入目标格子名称
        elif ck == "lost_treasure_box":
            rewards = self._resolve_lost_treasure_box(cell_name=target_cell_name)  # 失纬棋盒（常驻独有）
        elif ck in ("arcade_blind",):
            # [V0.3修复] 根据格子名称区分：弧光盲盒(单独) vs 弧光盲盒+沉眠池(组合)
            if target_cell_name and "沉眠池" in str(target_cell_name):
                # 组合格子：触发追击
                rewards, sp_event = self._resolve_arcade_blind_sleep()
                result["sleep_pool_event"] = sp_event
            else:
                # 单独格子：只获得弧光盲盒奖励
                rewards = self._resolve_arcade_blind()
        elif ck == "roll_again":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 1)
            # [V0.3新增] 常驻棋盘用蓝色骰子，限定棋盘用红色骰子
            dice_color = "blue" if self.gacha.board_type == "permanent" else "red"
            dice_color_cn = "蓝色" if dice_color == "blue" else "红色"
            print(f"[骰子奖励-再来一次] board_type={self.gacha.board_type}, 颜色={dice_color}, 数量={dice_gained}")
            self.state.dice_manager.add_dice(dice_gained, dice_color)
            rewards.append({"type": "dice", "name": f"+{dice_gained}{dice_color_cn}骰子"})
        elif ck == "multi_surprise":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 5)
            # [V0.3新增] 常驻棋盘用蓝色骰子，限定棋盘用红色骰子
            dice_color = "blue" if self.gacha.board_type == "permanent" else "red"
            dice_color_cn = "蓝色" if dice_color == "blue" else "红色"
            # [V0.4.1调试-已验证] print(f"[骰子奖励-多重惊喜] board_type={self.gacha.board_type}, 颜色={dice_color}, 数量={dice_gained}")
            self.state.dice_manager.add_dice(dice_gained, dice_color)
            rewards.append({"type": "dice", "name": f"+{dice_gained}{dice_color_cn}骰子"})
        elif ck in SKIN_TYPE_KEYS:
            rewards = self._resolve_skin_cell_darkbox(ck)

        result["rewards"] = rewards + claim_rewards
        result["dice_gained"] = dice_gained
        result["skin_claims"] = claim_rewards

        # [V0.3-已注释] 保底/奖励调试日志（需要时可取消）
        # _write_debug_log(f"[{_time.time():.3f}] [步骤4-rewards] roll={result['roll_number']} rewards={len(rewards)}")
        # has_s_in_rewards_final = any(r.get("type") == "s_character" for r in rewards)
        # print(f"[终极调试-奖励后] 奖励数={len(rewards)}, 有S级={has_s_in_rewards_final}, s_pity={self.state.s_pity_counter}")
        # print(f"[调试-保底] increment_s_pity前: total_rolls={self.state.total_rolls}, s_pity_counter={self.state.s_pity_counter}")
        # _write_debug_log(f"[{_time.time():.3f}] [步骤5-increment_s_pity前] roll={result['roll_number']} s_pity={self.state.s_pity_counter}")

        # [修复] 检查是否需要重置保底（如果获得了S级角色）
        has_s_in_rewards = any(r.get("type") == "s_character" for r in rewards)

        if has_s_in_rewards:
            # 本次已获得S级角色，重置保底计数器
            # 注意：可能已经重置过（如"于此同行"），但重复重置是安全的
            # print(f"[调试-保底] 获得S级角色，重置保底 (当前s_pity={self.state.s_pity_counter} -> 0)")
            self.state.reset_s_pity()
            # 清除pity_event，避免触发额外的硬保底逻辑
            result["pity_event"] = None
            pity_event = None
        else:
            pass  # print(f"[调试-保底] 正常增加s_pity (当前s_pity={self.state.s_pity_counter})")

        # [V0.5.5修复] 本次投掷未获得S级角色，且保底计数达到变格阈值时，
        # 在结算后启用变格状态，供下一次投掷使用。
        if not has_s_in_rewards and self.state.s_pity_counter >= PITY_CONFIG["s_pity"]["variant_threshold"]:
            self.state.is_variant = True

        # [V0.3-已注释] increment_s_pity后调试日志（需要时可取消）
        # print(f"[调试-保底] increment_s_pity后: total_rolls={self.state.total_rolls}, s_pity_counter={self.state.s_pity_counter}, event={pity_event}")

        has_s_in_rewards = any(r.get("type") == "s_character" for r in rewards)
        if pity_event == "hard_pity" and not has_s_in_rewards:
            # [V0.3-已注释] 硬保底调试日志（需要时可取消）
            # print(f"[硬保底调试] 触发{pity_event}! 执行前: s_pity={self.state.s_pity_counter}, 已有S级={has_s_in_rewards}")

            got_s, s_name, reason = self.gacha.gacha_s_character()

            # print(f"[硬保底调试] gacha_s_character后: s_pity={self.state.s_pity_counter}, got_s={got_s}, name={s_name}")

            if got_s:
                is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
                dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
                self.state.gold_chips += dup_reward.get("gold_chip", 0)
                reward_entry = {
                    "type": "s_character",
                    "name": s_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "reason": reason,
                    "fragment": dup_reward.get("fragment", 0),
                    "extra_gold": dup_reward.get("gold_chip", 0),
                }
                rewards.append(reward_entry)
                result["rewards"] = rewards
                # print(f"[硬保底调试] 最终: s_pity={self.state.s_pity_counter}, rewards含S级=True")

        gift_result = None
        if self.state.check_gift():
            gift_item = self.gacha.gacha_gift()
            gift_type, gift_name = gift_item
            is_dup, dup_count = self.state.add_to_collection(
                {"a_character": "a_characters", "a_disk": "a_disks"}[gift_type],
                gift_name
            )
            dup_reward = self.gacha.calculate_duplicate_reward(gift_type, gift_name, dup_count)
            self.state.gold_chips += dup_reward.get("gold_chip", 0)
            gift_result = {
                "type": gift_type,
                "name": gift_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "fragment": dup_reward.get("fragment", 0),
                "extra_gold": dup_reward.get("gold_chip", 0),
            }
        result["gift_result"] = gift_result

        # [V0.3-FINAL] 追击模式：作为投掷的附加内容
        # 追击不影响正常结算，每次投掷自动附带一轮追击（如果处于追击模式）
        if self.in_chase:
            print(f"\n[追击-附加] 第{SLEEP_POOL_CONFIG['max_chase_rounds'] - self.chase_rounds_left + 1}轮追击（附加在正常投掷后）")
            chase_rewards, chase_event = self._execute_chase_round(dice_value)  # [V0.3-FIX] 修正函数名

            # 将追击奖励追加到正常奖励中
            if chase_rewards:
                result["rewards"].extend(chase_rewards)

            # 记录追击事件（用于UI显示）
            result["sleep_pool_event"] = chase_event

            # 检查追击是否结束
            if chase_event and not chase_event.get("in_progress", False):
                print(f"[追击-附加] 追击结束!")
                self.in_chase = False
            else:
                print(f"[追击-附加] 追击继续，剩余{self.chase_rounds_left}轮")

        # [终极调试-出口] 记录函数返回前的完整状态
        _exit_time = _time.time()
        _duration = _exit_time - _entry_time

        # [文件日志] 写入调试文件（仅DEBUG_MODE=True时生效）
        _write_debug_log(f"[{_exit_time:.3f}] (+{_duration:.3f}s) [出口] roll={result['roll_number']} total_rolls={self.state.total_rolls} s_pity={self.state.s_pity_counter} gift={self.state.gift_counter} pity_event={result.get('pity_event')} has_gift={gift_result is not None}")

        # [V0.3-已注释] 终极调试-出口日志（需要时可取消）
        print(f"[终极调试-出口] [{_exit_time:.3f}] (+{_duration:.3f}s) roll_number={result['roll_number']}, 最终: total_rolls={self.state.total_rolls}, s_pity={self.state.s_pity_counter}, gift={self.state.gift_counter}, pity_event={result.get('pity_event')}, has_gift={gift_result is not None}")

        self.state.roll_history.append(result)

        return result

    def _check_skin_claims(self):
        """
        皮肤累计领取检查
        当 total_rolls 达到 claim_threshold 时，自动发放对应皮肤
        返回: 领取的皮肤奖励列表
        
        [关键修复] 使用动态加载的skin_system，确保不同棋盘领取对应角色的皮肤
        """
        claim_rewards = []
        
        # [修复] 优先使用动态皮肤系统的keys，回退到全局默认
        skin_type_keys = list(self.gacha.skin_system.keys()) if hasattr(self.gacha, 'skin_system') else SKIN_TYPE_KEYS
        
        for stype_key in skin_type_keys:
            if self.state.skin_claimed.get(stype_key, False):
                continue
            
            # [修复] 优先使用动态皮肤配置
            if hasattr(self.gacha, 'skin_system') and stype_key in self.gacha.skin_system:
                cfg = self.gacha.skin_system[stype_key]
            else:
                cfg = SKIN_SYSTEM[stype_key]
            
            threshold = cfg["claim_threshold"]
            if self.state.total_rolls >= threshold:
                self.state.skin_claimed[stype_key] = True
                skin_full_name = list(cfg["skins"].values())[0]
                is_dup, dup_count = self.state.add_to_collection("skins", skin_full_name)
                dup_gold = 0
                if is_dup:
                    rule_key = f"skin_{stype_key}"
                    rule = DUPLICATE_RULES.get(rule_key, {})
                    dup_gold = rule.get("gold_chip", 0)
                    self.state.gold_chips += dup_gold
                claim_rewards.append({
                    "type": "skin",
                    "name": skin_full_name,
                    "skin_type": stype_key,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "extra_gold": dup_gold,
                    "reason": f"累计{threshold}次领取",
                })
        return claim_rewards

    def _resolve_apprentice_chest(self):
        """学徒宝箱结算"""
        rewards = []

        got_s, s_name, reason = self.gacha.gacha_s_character()
        if got_s:
            is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
            dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
            self.state.gold_chips += dup_reward.get("gold_chip", 0)
            rewards.append({
                "type": "s_character",
                "name": s_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "reason": reason,
                "fragment": dup_reward.get("fragment", 0),
                "extra_gold": dup_reward.get("gold_chip", 0),
            })
        else:
            disk_name = self.gacha.gacha_b_disk()
            is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
            dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
            self.state.white_chips += dup_reward.get("white_chip", 0)
            rewards.append({
                "type": "b_disk",
                "name": disk_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "extra_white": dup_reward.get("white_chip", 0),
            })

        return rewards

    def _resolve_brave_chest(self):
        """勇者宝箱结算"""
        cell = CELL_TYPES["brave_chest"]
        rewards = []
        self.state.gold_chips += cell.get("extra_gold", 0)

        got_s, s_name, reason = self.gacha.gacha_s_character()
        if got_s:
            is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
            dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
            self.state.gold_chips += dup_reward.get("gold_chip", 0)
            rewards.append({
                "type": "s_character",
                "name": s_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "reason": reason,
                "fragment": dup_reward.get("fragment", 0),
                "extra_gold": dup_reward.get("gold_chip", 0) + cell.get("extra_gold", 0),
            })
        else:
            disk_name = self.gacha.gacha_b_disk()
            is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
            dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
            self.state.white_chips += dup_reward.get("white_chip", 0)
            rewards.append({
                "type": "b_disk",
                "name": disk_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "extra_white": dup_reward.get("white_chip", 0),
            })
            rewards.append({"type": "gold_chip", "name": f"+{cell['extra_gold']}金色棋子"})

        return rewards

    def _resolve_companion(self):
        """于此同行结算"""
        char_name, rank = self.gacha.gacha_companion()
        if rank == "S":
            collection_key = "s_characters"
            item_type = "s_character"
        else:
            collection_key = "a_characters"
            item_type = "a_character"

        is_dup, dup_count = self.state.add_to_collection(collection_key, char_name)
        dup_reward = self.gacha.calculate_duplicate_reward(item_type, char_name, dup_count)
        self.state.gold_chips += dup_reward.get("gold_chip", 0)

        return [{
            "type": item_type,
            "name": char_name,
            "rank": rank,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "reason": "于此同行",
            "fragment": dup_reward.get("fragment", 0),
            "extra_gold": dup_reward.get("gold_chip", 0),
        }]

    def _resolve_mist_box(self, cell_name=None):
        """
        迷迭棋盒结算 - 根据格子名称确定数量（修复版）

        规则：根据CSV中的名称确定固定数量
        - "迷迭棋盒（30个白色棋子）" → 30个
        - "迷迭棋盒（50个白色棋子）" → 50个

        参数:
            cell_name: 格子的完整名称，如"迷迭棋盒（30个白色棋子）"
                      如果为None，则随机抽取（兼容旧代码）
        """
        import re

        if cell_name:
            # 从名称中提取数量
            match = re.search(r'（(\d+)个白色棋子）', cell_name)
            if match:
                chips = int(match.group(1))
                print(f"\n[迷迭棋盒] 格子'{cell_name}' → 固定获得{chips}个白色棋子")
            else:
                # 无法解析时使用默认值
                chips = 30
                print(f"\n[迷迭棋盒] 无法从名称'{cell_name}'解析数量，默认{chips}个")
        else:
            # 兼容旧逻辑：随机抽取
            chips = random.choice(MIST_BOX_WHITE_CHIPS)
            print(f"\n[迷迭棋盒-随机] 随机获得{chips}个白色棋子")

        self.state.white_chips += chips
        return [{"type": "white_chip", "name": f"+{chips}白色棋子"}]

    def _resolve_lost_treasure_box(self, cell_name=None):
        """
        失纬棋盒结算（常驻棋盘独有）

        规则：根据格子名称确定金色棋子数量
        - "失纬棋盒（4个金色棋子）" → 4个
        - "失纬棋盒（16个金色棋子）" → 16个

        与迷迭棋盒的区别：
        - 迷迭棋盒 → 白色棋子
        - 失纬棋盒 → 金色棋子

        参数:
            cell_name: 格子的完整名称，如"失纬棋盒（16个金色棋子）"
        """
        import re

        if cell_name:
            match = re.search(r'（(\d+)个金色棋子）', cell_name)
            if match:
                chips = int(match.group(1))
                print(f"\n[失纬棋盒] 格子'{cell_name}' → 固定获得{chips}个金色棋子")
            else:
                chips = 16  # 默认值
                print(f"\n[失纬棋盒] 无法从名称'{cell_name}'解析数量，默认{chips}个")
        else:
            chips = 16
            print(f"\n[失纬棋盒-默认] 获得{chips}个金色棋子")

        self.state.gold_chips += chips
        return [{"type": "gold_chip", "name": f"+{chips}金色棋子"}]

    def _resolve_arcade_blind(self):
        """弧光盲盒结算"""
        disk_name = self.gacha.gacha_a_disk()
        is_dup, dup_count = self.state.add_to_collection("a_disks", disk_name)
        dup_reward = self.gacha.calculate_duplicate_reward("a_disk", disk_name, dup_count)
        self.state.gold_chips += dup_reward.get("gold_chip", 0)

        return [{
            "type": "a_disk",
            "name": disk_name,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "extra_gold": dup_reward.get("gold_chip", 0),
        }]

    def _resolve_skin_cell(self, skin_type_key):
        """装扮礼遇皮肤格子结算（落格触发）"""
        skin_full_name, stype = self.gacha.gacha_skin(skin_type_key)
        is_dup, dup_count = self.state.add_to_collection("skins", skin_full_name)

        dup_gold = 0
        if is_dup:
            rule_key = f"skin_{skin_type_key}"
            rule = DUPLICATE_RULES.get(rule_key, {})
            dup_gold = rule.get("gold_chip", 0)
            self.state.gold_chips += dup_gold

        return [{
            "type": "skin",
            "name": skin_full_name,
            "skin_type": skin_type_key,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "extra_gold": dup_gold,
        }]

    def _start_sleep_pool(self):
        """
        初始化沉眠池追击（进入追击模式）
        
        [V0.3修复] 分回合手动投掷：只初始化状态，不自动执行追击
        后续每次投掷调用 _execute_chase_round() 执行一轮
        """
        self.sleep_pool.start_chase()
        # 同步状态到GameEngine（用于UI显示）
        self.in_chase = True
        self.chase_rounds_left = SLEEP_POOL_CONFIG["max_chase_rounds"]
        self.chase_player_pos = 0
        self.chase_guardian_pos = SLEEP_POOL_CONFIG["guardian_flee_distance"]
        
        print(f"\n[追击] === 追击开始 ===")
        print(f"[追击] 守护者初始位置: {self.chase_guardian_pos}格")
        print(f"[追击] 剩余回合: {self.chase_rounds_left}")
        
        # 返回初始化事件信息（用于UI显示"追击开始"）
        return {
            "started": True,
            "guardian_start": SLEEP_POOL_CONFIG["guardian_flee_distance"],
            "rounds_total": SLEEP_POOL_CONFIG["max_chase_rounds"],
            "chase_results": [],
            "success": False,
            "in_progress": True,  # 标记追击进行中
        }

    def _execute_chase_round(self, dice_value):
        """
        执行一轮追击（分回合投掷）
        
        参数:
            dice_value: 本次掷骰的点数
            
        返回:
            (rewards, event_info): 奖励列表和本轮追击结果
        """
        if not self.in_chase or self.chase_rounds_left <= 0:
            return [], None
        
        # 执行一轮追击
        caught, failed, rounds_left, g_pos, p_pos = self.sleep_pool.chase_round(dice_value)
        
        # 同步状态
        self.chase_rounds_left = rounds_left
        self.chase_player_pos = p_pos
        self.chase_guardian_pos = g_pos
        
        round_result = {
            "dice": dice_value,
            "player_pos": p_pos,
            "guardian_pos": g_pos,
            "caught": caught,
            "failed": failed,
        }
        
        print(f"\n[追击-第{SLEEP_POOL_CONFIG['max_chase_rounds'] - rounds_left}轮]")
        print(f"[追击] 骰子={dice_value}, 玩家位置={p_pos}, 守护者位置={g_pos}")
        
        # 构建事件信息
        event_info = {
            "started": True,
            "guardian_start": SLEEP_POOL_CONFIG["guardian_flee_distance"],
            "rounds_total": SLEEP_POOL_CONFIG["max_chase_rounds"],
            "chase_results": [round_result],
            "success": False,
            "in_progress": not (caught or failed),  # 追击是否继续
        }
        
        rewards = [{"type": "white_chip", "name": "进入沉眠池"}]
        
        if caught:
            # 追上守护者！
            event_info["success"] = True
            self.state.gold_chips += SLEEP_POOL_CONFIG["success_reward_gold"]
            rewards.append({"type": "gold_chip", "name": f"+{SLEEP_POOL_CONFIG['success_reward_gold']}金色棋子"})
            self._end_chase()
            print(f"[追击] 成功追上！获得{SLEEP_POOL_CONFIG['success_reward_gold']}金色棋子")
        elif failed:
            # 追击失败（回合用尽）
            self._end_chase()
            print(f"[追击] 追击失败！守护者逃脱")
        else:
            # 追击继续
            print(f"[追击] 剩余{rounds_left}轮，继续追击...")
        
        return rewards, event_info
    
    def _end_chase(self):
        """结束追击模式"""
        self.in_chase = False
        self.sleep_pool.active = False
        print(f"[追击] === 追击结束 ===")

    def _resolve_sleep_pool(self):
        """
        沉眠池结算（兼容旧接口 - 自动完成全部追击）
        
        [V0.3废弃] 此方法保留用于向后兼容，新代码应使用 _start_sleep_pool + _execute_chase_round
        """
        event_info = {
            "started": True,
            "guardian_start": SLEEP_POOL_CONFIG["guardian_flee_distance"],
            "rounds_total": SLEEP_POOL_CONFIG["max_chase_rounds"],
            "chase_results": [],
            "success": False,
        }

        for _ in range(SLEEP_POOL_CONFIG["max_chase_rounds"]):
            dice_val = self.roll_engine.roll_dice()
            caught, failed, rounds_left, g_pos, p_pos = self.sleep_pool.chase_round(dice_val)
            round_result = {
                "dice": dice_val,
                "player_pos": p_pos,
                "guardian_pos": g_pos,
                "caught": caught,
                "failed": failed,
            }
            event_info["chase_results"].append(round_result)

            if caught:
                event_info["success"] = True
                self.state.gold_chips += SLEEP_POOL_CONFIG["success_reward_gold"]
                break
            if failed:
                break

        rewards = [{"type": "white_chip", "name": "进入沉眠池"}]
        if event_info["success"]:
            rewards.append({"type": "gold_chip", "name": f"+{SLEEP_POOL_CONFIG['success_reward_gold']}金色棋子"})

        return rewards, event_info

    # ==================== 概率暗箱版本（格子定大类 + 官方概率） ====================

    def _resolve_apprentice_chest_darkbox(self):
        """
        学徒宝箱 - 概率暗箱版
        遵循官方规则：S级0.2%，B级99.8%
        """
        rewards = []
        r = random.random()

        if r < 0.002:
            got_s, s_name, reason = self.gacha.gacha_s_character()
            if got_s:
                is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
                dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
                self.state.gold_chips += dup_reward.get("gold_chip", 0)
                rewards.append({
                    "type": "s_character",
                    "name": s_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "reason": reason,
                    "fragment": dup_reward.get("fragment", 0),
                    "extra_gold": dup_reward.get("gold_chip", 0),
                })
            else:
                disk_name = self.gacha.gacha_b_disk()
                is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
                dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
                self.state.white_chips += dup_reward.get("white_chip", 0)
                rewards.append({
                    "type": "b_disk",
                    "name": disk_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "extra_white": dup_reward.get("white_chip", 0),
                })
        else:
            disk_name = self.gacha.gacha_b_disk()
            is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
            dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
            self.state.white_chips += dup_reward.get("white_chip", 0)
            rewards.append({
                "type": "b_disk",
                "name": disk_name,
                "is_duplicate": is_dup,
                "dup_count": dup_count,
                "extra_white": dup_reward.get("white_chip", 0),
            })

        return rewards

    def _resolve_brave_chest_darkbox(self):
        """
        勇者宝箱 - 概率暗箱版
        遵循官方规则：
        - 常规状态: S级3%, B级97%
        - 变格状态: S级60%, A级20%, B级20%
        必定额外获得2个金色棋子
        """
        cell = CELL_TYPES["brave_chest"]
        rewards = []
        self.state.gold_chips += cell.get("extra_gold", 0)

        r = random.random()

        if self.state.is_variant:
            if r < 0.60:
                got_s, s_name, reason = self.gacha.gacha_s_character()
                if got_s:
                    is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
                    dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
                    self.state.gold_chips += dup_reward.get("gold_chip", 0)
                    rewards.append({
                        "type": "s_character",
                        "name": s_name,
                        "is_duplicate": is_dup,
                        "dup_count": dup_count,
                        "reason": f"{reason}(变格)",
                        "fragment": dup_reward.get("fragment", 0),
                        "extra_gold": dup_reward.get("gold_chip", 0),
                    })
                else:
                    disk_name = self.gacha.gacha_b_disk()
                    is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
                    dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
                    self.state.white_chips += dup_reward.get("white_chip", 0)
                    rewards.append({
                        "type": "b_disk",
                        "name": disk_name,
                        "is_duplicate": is_dup,
                        "dup_count": dup_count,
                        "extra_white": dup_reward.get("white_chip", 0),
                    })
            elif r < 0.80:
                disk_name = self.gacha.gacha_a_disk()
                is_dup, dup_count = self.state.add_to_collection("a_disks", disk_name)
                dup_reward = self.gacha.calculate_duplicate_reward("a_disk", disk_name, dup_count)
                self.state.gold_chips += dup_reward.get("gold_chip", 0)
                rewards.append({
                    "type": "a_disk",
                    "name": disk_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "extra_gold": dup_reward.get("gold_chip", 0),
                })
            else:
                disk_name = self.gacha.gacha_b_disk()
                is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
                dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
                self.state.white_chips += dup_reward.get("white_chip", 0)
                rewards.append({
                    "type": "b_disk",
                    "name": disk_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "extra_white": dup_reward.get("white_chip", 0),
                })
        else:
            if r < 0.03:
                got_s, s_name, reason = self.gacha.gacha_s_character()
                if got_s:
                    is_dup, dup_count = self.state.add_to_collection("s_characters", s_name)
                    dup_reward = self.gacha.calculate_duplicate_reward("s_character", s_name, dup_count)
                    self.state.gold_chips += dup_reward.get("gold_chip", 0)
                    rewards.append({
                        "type": "s_character",
                        "name": s_name,
                        "is_duplicate": is_dup,
                        "dup_count": dup_count,
                        "reason": reason,
                        "fragment": dup_reward.get("fragment", 0),
                        "extra_gold": dup_reward.get("gold_chip", 0),
                    })
                else:
                    disk_name = self.gacha.gacha_b_disk()
                    is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
                    dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
                    self.state.white_chips += dup_reward.get("white_chip", 0)
                    rewards.append({
                        "type": "b_disk",
                        "name": disk_name,
                        "is_duplicate": is_dup,
                        "dup_count": dup_count,
                        "extra_white": dup_reward.get("white_chip", 0),
                    })
            else:
                disk_name = self.gacha.gacha_b_disk()
                is_dup, dup_count = self.state.add_to_collection("b_disks", disk_name)
                dup_reward = self.gacha.calculate_duplicate_reward("b_disk", disk_name, dup_count)
                self.state.white_chips += dup_reward.get("white_chip", 0)
                rewards.append({
                    "type": "b_disk",
                    "name": disk_name,
                    "is_duplicate": is_dup,
                    "dup_count": dup_count,
                    "extra_white": dup_reward.get("white_chip", 0),
                })

        rewards.append({"type": "gold_chip", "name": f"+{cell.get('extra_gold', 16)}金色棋子"})
        return rewards

    def _resolve_variant_brave_chest_s(self):
        """
        [V0.4.2新增] 勇者宝箱变结算 - 必定获得S级角色（100%）

        变格规则：
        - 原始类型：勇者宝箱（brave_chest）
        - 变格后：S级于此同行（companion_s）
        - 概率：必定获得S级角色（100%），不使用概率暗箱

        返回: 奖励列表
        """
        print(f"\n[变格-勇者宝箱变] === 必定获得S级角色 (100%) ===")

        # [V0.4.3修复] 使用current_board_id（GameEngine属性），而不是board_id（GachaEngine属性）
        board_id_for_s_pool = getattr(self, 'board_id', None) or getattr(self, 'current_board_id', 'limited_xun')

        # 获取当前棋盘的S级奖池
        s_pool = get_s_pool(board_id_for_s_pool)
        if not s_pool:
            # 兜底：使用默认限定池
            s_pool = S_POOL_LIMITED

        # [V0.4.3修复] s_pool是list[dict]格式，用["name"]提取角色名
        # 格式: [{"name": "浔", "rate": 0.0187, "limited": True}, ...]
        chosen = random.choice(s_pool)
        char_name = chosen.get("name", "未知S级") if isinstance(chosen, dict) else str(chosen)

        # 加入收集记录
        is_dup, dup_count = self.state.add_to_collection("s_characters", char_name)

        # 计算重复奖励
        dup_reward = self.gacha.calculate_duplicate_reward("s_character", char_name, dup_count)
        self.state.white_chips += dup_reward.get("white_chip", 0)
        self.state.gold_chips += dup_reward.get("gold_chip", 0)

        rewards = [{
            "type": "s_character",
            "name": char_name,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "extra_white": dup_reward.get("white_chip", 0),
            "extra_gold": dup_reward.get("gold_chip", 0),
            "variant_type": "brave_chest_variant",  # 标记为变格类型
        }]

        print(f"[变格-勇者宝箱变] 获得S级角色: {char_name} (重复={is_dup}, 第{dup_count}次)")
        return rewards

    def execute_hard_pity(self, current_pos_idx=0, current_cell_type=None,
                          branch_entries=None, is_in_branch=None, branch_step=0):
        """
        [V0.4.2新增] 执行硬保底结算（89抽后触发）

        硬保底规则：
        - 触发条件：s_pity_counter >= 89
        - 行为：正常消耗骰子，但不移动棋子，直接获得S级角色
        - 奖励：必定获得S级角色（100%）
        - 保底计数器：重置为0

        参数:
            current_pos_idx: 当前位置索引（不移动，仅记录）
            current_cell_type: 当前格子类型（不使用，保留接口一致性）
            branch_entries: 分支元数据（不使用）
            is_in_branch: 是否在分支内（不改变）
            branch_step: 分支步数（不改变）

        返回: 结果字典（与execute_single_roll格式一致）
        """
        print(f"\n[硬保底] === 89抽硬保底触发 ===")
        print(f"[硬保底] 当前垫刀数: {self.state.s_pity_counter}")

        result = {
            "roll_number": self.state.total_rolls + 1,
            "dice_value": 0,  # 硬保底不掷骰子
            "cell_type": "hard_pity",  # 特殊类型标记
            "cell_name": "硬保底",
            "rewards": [],
            "pity_event": "hard_pity_89",  # 标记硬保底事件
            "gift_result": None,
            "sleep_pool_event": None,
            "dice_gained": 0,
            "branch_event": None,
            "new_position_idx": current_pos_idx,  # 不移动
            "new_branch_state": is_in_branch,
            "new_branch_step": branch_step,
            "is_hard_pity": True,  # 标记为硬保底（UI用于判断是否移动棋子）
        }

        # 增加总投掷次数
        self.state.total_rolls += 1

        # 获取当前棋盘的S级奖池
        # [V0.4.3修复] 使用current_board_id（GameEngine属性），而不是board_id（GachaEngine属性）
        board_id_for_s_pool = getattr(self, 'board_id', None) or getattr(self, 'current_board_id', 'limited_xun')
        print(f"[硬保底-DEBUG] board_id_for_s_pool={board_id_for_s_pool}")
        print(f"[硬保底-DEBUG] 调用 get_s_pool({board_id_for_s_pool})...")

        s_pool = get_s_pool(board_id_for_s_pool)
        print(f"[硬保底-DEBUG] get_s_pool返回类型={type(s_pool)}, 长度={len(s_pool) if s_pool else 0}")
        if s_pool:
            print(f"[硬保底-DEBUG] s_pool[0]={s_pool[0]}")

        if not s_pool:
            print(f"[硬保底-DEBUG] s_pool为空，使用S_POOL_LIMITED备用")
            s_pool = S_POOL_LIMITED

        # 随机抽取一个S级角色
        # [V0.4.3修复] s_pool是list格式 [{"name":..., "rate":...}]，不是dict
        try:
            s_character_data = random.choice(s_pool)
            char_name = s_character_data["name"]
            print(f"[硬保底] 抽取S级角色: {char_name}")
        except Exception as e:
            print(f"[硬保底-错误] 抽取S级角色失败: {e}, type(s_pool)={type(s_pool)}")
            char_name = "浔"  # 默认值
            print(f"[硬保底-错误] 使用默认角色: {char_name}")

        # 加入收集记录
        is_dup, dup_count = self.state.add_to_collection("s_characters", char_name)

        # 计算重复奖励
        dup_reward = self.gacha.calculate_duplicate_reward("s_character", char_name, dup_count)
        self.state.white_chips += dup_reward.get("white_chip", 0)
        self.state.gold_chips += dup_reward.get("gold_chip", 0)

        result["rewards"] = [{
            "type": "s_character",
            "name": char_name,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "extra_white": dup_reward.get("white_chip", 0),
            "extra_gold": dup_reward.get("gold_chip", 0),
            "pity_type": "hard_pity_89",  # 标记为硬保底获得
        }]

        # 重置垫刀计数器和变格状态（两者联动）
        old_pity = self.state.s_pity_counter
        self.state.s_pity_counter = 0
        # [V0.4.3修复] 硬保底后必须同步关闭变格模式（否则棋盘显示不变）
        self.state.is_variant = False

        print(f"[硬保底] 获得S级角色: {char_name} (重复={is_dup}, 第{dup_count}次)")
        print(f"[硬保底] 垫刀计数器重置: {old_pity} -> 0, 变格模式已关闭")

        # 添加到历史记录
        self.state.roll_history.append(result)

        return result

    def _resolve_companion_darkbox(self, cell_name=None):
        """
        于此同行 - 根据格子名称确定角色（修复版）
        规则：必定获得当前格子内所示角色

        参数:
            cell_name: 格子的完整名称，如"于此同行（海月）"
                      如果为None，则随机抽取（兼容旧代码）

        [关键修复] 动态生成同行角色映射表，确保不同棋盘使用正确的角色
        """
        # [V0.3-版本标记] 确认加载的是最新代码
        print(f"\n[同行-版本] === V0.3-FIX3 已加载 (排除特殊标记) ===")

        # [修复] 动态生成同行角色映射表，基于当前棋盘的companions_list
        # [V0.3-关键修复] 排除特殊标记(__RANDOM_S__/__)，让它们走随机抽取逻辑
        if hasattr(self.gacha, 'companions_list') and self.gacha.companions_list:
            companion_map = {}
            for comp in self.gacha.companions_list:
                char_name = comp["name"]
                rank = comp["rank"]
                # [V0.3-修复] 跳过特殊标记，不加入companion_map
                if char_name in ("随机S级", "随机A级", "__RANDOM_S__", "__RANDOM_A__"):
                    continue
                # 格子名称格式："于此同行（角色名）"
                map_key = f"于此同行（{char_name}）"
                companion_map[map_key] = (char_name, rank)
        else:
            # 回退到默认配置
            companion_map = {
                "于此同行（浔）": ("浔", "S"),
                "于此同行（海月）": ("海月", "A"),
                "于此同行（翳）": ("翳", "A"),
                "于此同行（哈尼娅）": ("哈尼娅", "A"),
            }

        if cell_name and cell_name in companion_map:
            # 根据格子名称确定角色
            char_name, rank = companion_map[cell_name]
            print(f"\n[同行] 格子'{cell_name}' → 必定获得{rank}级角色: {char_name}")
            # S级角色必定获得，需要重置保底
            if rank == "S":
                # print(f"[同行-调试] reset_s_pity前: s_pity_counter={self.state.s_pity_counter}")
                self.state.reset_s_pity()
                # print(f"[同行-调试] reset_s_pity后: s_pity_counter={self.state.s_pity_counter}")
                print(f"[同行] S级角色{char_name}已获得，重置S级保底计数器")
        elif cell_name:
            # [V0.3-已注释] 同行详细调试日志（需要时可取消）
            # print(f"\n[同行-调试] cell_name='{cell_name}'")
            # print(f"[同行-调试] hasattr(s_pool)={hasattr(self.gacha, 's_pool')}, s_pool长度={len(self.gacha.s_pool) if hasattr(self.gacha, 's_pool') and self.gacha.s_pool else 0}")
            # print(f"[同行-调试] hasattr(a_pool)={hasattr(self.gacha, 'a_pool')}, a_pool长度={len(self.gacha.a_pool) if hasattr(self.gacha, 'a_pool') and self.gacha.a_pool else 0}")

            # [V0.3修复] 处理常驻棋盘的随机同行标记
            # 布局数据使用中文描述"于此同行（随机S级）"，而companions使用特殊标记"__RANDOM_S__"
            if "随机S级" in cell_name or "__RANDOM_S__" in cell_name:
                # 随机S级：从当前棋盘的S级角色池中抽取
                if hasattr(self.gacha, 's_pool') and self.gacha.s_pool:
                    choice = random.choice(self.gacha.s_pool)
                    # [V0.3-关键修复] 兼容两种格式：字典{"name":"xx"} 或 字符串"xx"
                    char_name = choice["name"] if isinstance(choice, dict) else str(choice)
                    rank = "S"
                    print(f"\n[同行-随机S] 格子'{cell_name}' → 随机获得S级角色: {char_name}")
                    # print(f"[同行-调试-S] s_pool类型={type(choice).__name__}, 选择结果={repr(choice)}")
                    self.state.reset_s_pity()
                    # print(f"[同行-随机S] S级角色{char_name}已获得，重置S级保底计数器")
                else:
                    # 回退：使用固定列表（常驻棋盘6个S级角色）
                    char_name = random.choice(["罗夏", "玛薇", "深蓝", "芙露德莉斯", "琴诺", "珂莱塔"])
                    rank = "S"
                    print(f"\n[同行-随机S] 格子'{cell_name}' → 随机获得S级角色: {char_name} (回退模式)")
                    self.state.reset_s_pity()
            elif "随机A级" in cell_name or "__RANDOM_A__" in cell_name:
                # 随机A级：从当前棋盘的A级角色池中抽取
                if hasattr(self.gacha, 'a_pool') and self.gacha.a_pool:
                    print(f"[同行-随机A调试] a_pool长度={len(self.gacha.a_pool)}, 内容={[c['name'] if isinstance(c, dict) else c for c in self.gacha.a_pool]}")
                    choice = random.choice(self.gacha.a_pool)
                    # [V0.3-关键修复] 兼容两种格式：字典{"name":"xx"} 或 字符串"xx"
                    char_name = choice["name"] if isinstance(choice, dict) else str(choice)
                    rank = "A"
                    print(f"\n[同行-随机A] 格子'{cell_name}' → 随机获得A级角色: {char_name}")
                    # print(f"[同行-调试-A] a_pool类型={type(choice).__name__}, 选择结果={repr(choice)}")
                    # print(f"[同行-调试-A] a_pool内容: {self.gacha.a_pool}")
                else:
                    # 回退：使用固定列表
                    char_name = random.choice(["安卡希雅", "炽", "里", "莱特", "游隼"])
                    rank = "A"
                    print(f"\n[同行-随机A] 格子'{cell_name}' → 随机获得A级角色: {char_name} (回退模式)")
            else:
                # 完全未识别的同行格子，走概率抽取
                char_name, rank = self._fallback_random_companion()
                print(f"\n[同行-未知] 格子'{cell_name}' 未识别，概率抽取: {rank}级 {char_name}")
        else:
            # 兼容旧逻辑：随机抽取（cell_name为None时）
            # [修复] 使用动态规则
            if hasattr(self.gacha, 'rules') and 's_pity_hard' in self.gacha.rules:
                rules = self.gacha.rules
                base_rate_variant = rules.get("s_base_rate_variant", 0.1959)
                base_rate_normal = rules.get("s_base_rate_normal", 0.0099)
                pity_hard = rules.get("s_pity_hard", 90)
            else:
                pity_cfg = PITY_CONFIG["s_pity"]
                base_rate_variant = pity_cfg.get("base_rate_variant", 0.1959)
                base_rate_normal = pity_cfg.get("base_rate_normal", 0.0099)
                pity_hard = pity_cfg.get("hard_pity", 90)
            
            base_rate = base_rate_variant if self.state.is_variant else base_rate_normal

            if random.random() < base_rate or self.state.s_pity_counter >= pity_hard - 1:
                char_name, rank = self.gacha.gacha_companion()
                if rank == "S":
                    self.state.reset_s_pity()
                print(f"\n[同行-随机] 抽取到{rank}级角色: {char_name}")
            else:
                # [修复] 使用动态加载的同行角色列表
                if hasattr(self.gacha, 'companions_list') and self.gacha.companions_list:
                    a_companions = [c for c in self.gacha.companions_list if c["rank"] == "A"]
                else:
                    a_companions = [c for c in COMPANIONS_LIMITED if c["rank"] == "A"]
                
                char_name = random.choice(a_companions)["name"]
                rank = "A"
                print(f"\n[同行-随机] 抽取到A级角色: {char_name}")

        collection_key = "s_characters" if rank == "S" else "a_characters"
        item_type = "s_character" if rank == "S" else "a_character"

        # [V0.3-已注释] 同行结果文件诊断（需要时可取消）
        # try:
        #     with open("_companion_debug.log", "a", encoding="utf-8") as f:
        #         f.write(f"[{__import__('time').time():.3f}] [同行-结果]\n")
        #         f.write(f"  char_name={repr(char_name)}, rank={rank}\n")
        #         f.write(f"  item_type={item_type}, collection_key={collection_key}\n")
        #         f.write(f"  cell_name_for_reason={repr(cell_name)}\n")
        #         f.write("-" * 50 + "\n")
        # except Exception as e:
        #     print(f"[诊断-文件写入失败] {e}")

        is_dup, dup_count = self.state.add_to_collection(collection_key, char_name)
        dup_reward = self.gacha.calculate_duplicate_reward(item_type, char_name, dup_count)
        self.state.gold_chips += dup_reward.get("gold_chip", 0)

        return [{
            "type": item_type,
            "name": char_name,
            "rank": rank,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "reason": f"于此同行({cell_name or '随机'})",
            "fragment": dup_reward.get("fragment", 0),
            "extra_gold": dup_reward.get("gold_chip", 0),
        }]

    def _fallback_random_companion(self):
        """回退方法：当同行格子无法识别时，使用概率抽取"""
        if hasattr(self.gacha, 'rules') and 's_pity_hard' in self.gacha.rules:
            rules = self.gacha.rules
            base_rate_variant = rules.get("s_base_rate_variant", 0.1959)
            base_rate_normal = rules.get("s_base_rate_normal", 0.0099)
            pity_hard = rules.get("s_pity_hard", 90)
        else:
            pity_cfg = PITY_CONFIG["s_pity"]
            base_rate_variant = pity_cfg.get("base_rate_variant", 0.1959)
            base_rate_normal = pity_cfg.get("base_rate_normal", 0.0099)
            pity_hard = pity_cfg.get("hard_pity", 90)

        base_rate = base_rate_variant if self.state.is_variant else base_rate_normal

        if random.random() < base_rate or self.state.s_pity_counter >= pity_hard - 1:
            char_name, rank = self.gacha.gacha_companion()
            if rank == "S":
                self.state.reset_s_pity()
            print(f"\n[同行-随机] 抽取到{rank}级角色: {char_name}")
        else:
            # 使用动态加载的同行角色列表
            if hasattr(self.gacha, 'companions_list') and self.gacha.companions_list:
                a_companions = [c for c in self.gacha.companions_list if c["rank"] == "A"]
            else:
                a_companions = [c for c in COMPANIONS_LIMITED if c["rank"] == "A"]

            char_name = random.choice(a_companions)["name"]
            rank = "A"
            print(f"\n[同行-随机] 抽取到A级角色: {char_name}")

        return char_name, rank

    def _resolve_arcade_blind_sleep(self):
        """
        弧光盲盒+沉眠池组合结算
        
        [V0.3修复] 分回合手动投掷：
        1. 获得弧光盲盒奖励
        2. 初始化追击状态（不自动执行追击）
        3. 后续每次投掷调用 _execute_chase_round() 执行一轮
        """
        rewards = self._resolve_arcade_blind()
        
        # [V0.3修复] 只初始化追击，不自动完成
        sp_event = self._start_sleep_pool()
        
        return rewards, sp_event

    def _resolve_skin_cell_darkbox(self, skin_type_key):
        """
        装扮礼遇皮肤 - 固定奖励版（符合规则说明）

        规则说明明确指出：
        - 风向标："必定获得滑翔翼皮肤"
        - 今日穿搭："必定获得角色时装"
        - 改装时刻："必定获得载具涂装"

        所有皮肤格子一旦到达，必定获得对应皮肤（100%确定）
        "进入概率"是落格概率（由暗箱/骰子系统控制），不影响奖励内容

        参数:
            skin_type_key: 皮肤类型key (glider_skin/today_outfit/vehicle_paint)
        
        [关键修复] 使用动态加载的skin_system，确保不同棋盘获得对应角色的皮肤
        """
        # [修复] 优先使用动态皮肤配置
        if hasattr(self.gacha, 'skin_system') and skin_type_key in self.gacha.skin_system:
            cfg = self.gacha.skin_system[skin_type_key]
        else:
            cfg = SKIN_SYSTEM[skin_type_key]

        # 所有皮肤格子都必定获得对应皮肤
        print(f"\n[皮肤-{cfg['name']}] 必定获得{cfg['name']}")

        skin_full_name, stype = self.gacha.gacha_skin(skin_type_key)
        is_dup, dup_count = self.state.add_to_collection("skins", skin_full_name)

        rule_key = f"skin_{skin_type_key}"
        rule = DUPLICATE_RULES.get(rule_key, {})
        dup_gold = rule.get("gold_chip", 0) if is_dup else 0
        self.state.gold_chips += dup_gold

        return [{
            "type": "skin",
            "name": skin_full_name,
            "skin_type": skin_type_key,
            "is_duplicate": is_dup,
            "dup_count": dup_count,
            "extra_gold": dup_gold,
            "reason": f"{cfg['name']}-必定获得",
        }]
