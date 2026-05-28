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
)


class DiceManager:
    """骰子管理器 - 管理红色/蓝色骰子与环石的消耗与获取"""

    def __init__(self):
        self.red_dice = 999999
        self.blue_dice = 0
        self.ring_stone = 0
        self.infinite_red = True
        self.infinite_blue = False
        self.infinite_ring = True

    def get_dice_count(self, dice_type="red"):
        """获取指定类型骰子数量"""
        if dice_type == "red":
            return self.red_dice if not self.infinite_red else float("inf")
        elif dice_type == "blue":
            return self.blue_dice if not self.infinite_blue else float("inf")
        elif dice_type == "ring":
            return self.ring_stone if not self.infinite_ring else float("inf")
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
            if self.ring_stone >= count:
                self.ring_stone -= count
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
            ring_count = self.ring_stone if not self.infinite_ring else float("inf")
            if ring_count >= needed:
                return True

        return False

    def try_consume_for_roll(self, count=1):
        """
        尝试消耗进行抽取
        优先级: 红骰 > 环石
        返回 (success, consumed_type)
        """
        if self.consume_dice(count, "red"):
            return True, "red"

        if self.consume_dice(count, "ring"):
            return True, "ring"

        return False, None


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
        """增加S级保底计数，检查是否触发变格"""
        self.s_pity_counter += 1
        pity_cfg = PITY_CONFIG["s_pity"]
        if self.s_pity_counter >= pity_cfg["variant_threshold"] and not self.is_variant:
            self.is_variant = True
            return "variant"
        if self.s_pity_counter >= pity_cfg["hard_pity"]:
            return "hard_pity"
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

    def __init__(self, state):
        self.state = state

    def gacha_s_character(self):
        """
        S级角色抽签判定
        返回: (是否获得, 角色名, 获得原因)
        """
        pity_cfg = PITY_CONFIG["s_pity"]

        # 硬保底判定
        if self.state.s_pity_counter >= pity_cfg["hard_pity"] - 1:
            char_name = S_POOL_LIMITED[0]["name"]
            self.state.reset_s_pity()
            return True, char_name, "硬保底"

        # 变格/基准概率判定
        base_rate = pity_cfg["base_rate_variant"] if self.state.is_variant else pity_cfg["base_rate_normal"]
        if random.random() < base_rate:
            char_name = S_POOL_LIMITED[0]["name"]
            self.state.reset_s_pity()
            return True, char_name, "变格" if self.state.is_variant else "常规"

        return False, None, None

    def gacha_a_character_from_gift(self):
        """集点赠礼中的A级角色抽取（仅从非gift_only的角色中抽取）"""
        eligible = [c for c in A_POOL_LIMITED if not c["gift_only"]]
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
        """
        cell = CELL_TYPES["companion"]
        sub_rates = cell["sub_rates"]
        r = random.random()
        if r < sub_rates["s_character"]:
            s_companions = [c for c in COMPANIONS_LIMITED if c["rank"] == "S"]
            companion = random.choice(s_companions)
            return companion["name"], "S"
        else:
            a_companions = [c for c in COMPANIONS_LIMITED if c["rank"] == "A"]
            companion = random.choice(a_companions)
            return companion["name"], "A"

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
        """
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

    def __init__(self):
        self.state = GameState()
        self.gacha = GachaEngine(self.state)
        self.sleep_pool = SleepPoolEngine()
        self.roll_engine = RollEngine()
        # 分支状态追踪
        self.in_branch = None       # 当前所在分支: "s_character" / "skin_surprise" / None
        self.branch_step = 0        # 在分支内的步数(0-based)

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
                    print(f"[game_logic] ✅ 触发分支进入: {bkey} (current_pos={current_pos_idx})")
                    break

        # S级角色分支特殊处理：必定获得（无需额外掷骰）
        # "于此同行"到达后直接获得S级角色
        if is_in_branch == "s_character" and ck == "companion":
            result["branch_event"] = ("s_got",)  # 标记已获得S级角色

        # 5. 根据格子类型执行效果（使用概率暗箱）
        rewards = []
        dice_gained = 0

        if ck == "apprentice_chest":
            rewards = self._resolve_apprentice_chest_darkbox()
        elif ck == "brave_chest":
            rewards = self._resolve_brave_chest_darkbox()
        elif ck == "companion":
            rewards = self._resolve_companion_darkbox(cell_name=cell_name)  # 传入格子名称
        elif ck == "mist_box":
            rewards = self._resolve_mist_box(cell_name=cell_name)  # 传入格子名称
        elif ck in ("arcade_blind",):
            rewards, sp_event = self._resolve_arcade_blind_sleep()
            result["sleep_pool_event"] = sp_event
        elif ck == "roll_again":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 1)
            self.state.dice_manager.add_dice(dice_gained, "red")
            rewards.append({"type": "dice", "name": f"+{dice_gained}红色骰子"})
        elif ck == "multi_surprise":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 5)
            self.state.dice_manager.add_dice(dice_gained, "red")
            rewards.append({"type": "dice", "name": f"+{dice_gained}红色骰子"})
        elif ck in SKIN_TYPE_KEYS:
            rewards = self._resolve_skin_cell_darkbox(ck)

        result["rewards"] = rewards + claim_rewards
        result["dice_gained"] = dice_gained
        result["skin_claims"] = claim_rewards

        # 6. S级保底计数 + 判定（暗箱：保底独立于格子类型）
        pity_event = self.state.increment_s_pity()
        result["pity_event"] = pity_event

        has_s_in_rewards = any(r.get("type") == "s_character" for r in rewards)
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

        # 8. 记录历史
        self.state.roll_history.append(result)

        return result

    def execute_single_roll_with_target(self, current_pos_idx=0, current_cell_type=None,
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

        self.state.total_rolls += 1

        claim_rewards = self._check_skin_claims()

        # 使用目标位置的格子类型作为落格类型
        ck = target_cell_type or "apprentice_chest"
        cell_info = CELL_TYPES.get(ck)
        if not cell_info:
            ck = "apprentice_chest"
            cell_info = CELL_TYPES[ck]

        result["cell_type"] = ck
        result["cell_name"] = cell_info.get("name", ck)

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
                    print(f"[分支检测] ✅ 触发进入{bkey}分支！")
                    break
            else:
                print(f"[分支检测] ❌ 未匹配任何分支入口")

        # S级角色分支特殊处理：必定获得（无需额外掷骰）
        if is_in_branch == "s_character" and ck == "companion":
            result["branch_event"] = ("s_got",)  # 标记已获得S级角色

        # 根据目标格子类型执行效果
        rewards = []
        dice_gained = 0

        if ck == "apprentice_chest":
            rewards = self._resolve_apprentice_chest_darkbox()
        elif ck == "brave_chest":
            rewards = self._resolve_brave_chest_darkbox()
        elif ck == "companion":
            rewards = self._resolve_companion_darkbox(cell_name=target_cell_name)  # 传入目标格子名称
        elif ck == "mist_box":
            rewards = self._resolve_mist_box(cell_name=target_cell_name)  # 传入目标格子名称
        elif ck in ("arcade_blind",):
            rewards, sp_event = self._resolve_arcade_blind_sleep()
            result["sleep_pool_event"] = sp_event
        elif ck == "roll_again":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 1)
            self.state.dice_manager.add_dice(dice_gained, "red")
            rewards.append({"type": "dice", "name": f"+{dice_gained}红色骰子"})
        elif ck == "multi_surprise":
            dice_gained = CELL_TYPES[ck].get("dice_reward", 5)
            self.state.dice_manager.add_dice(dice_gained, "red")
            rewards.append({"type": "dice", "name": f"+{dice_gained}红色骰子"})
        elif ck in SKIN_TYPE_KEYS:
            rewards = self._resolve_skin_cell_darkbox(ck)

        result["rewards"] = rewards + claim_rewards
        result["dice_gained"] = dice_gained
        result["skin_claims"] = claim_rewards

        pity_event = self.state.increment_s_pity()
        result["pity_event"] = pity_event

        has_s_in_rewards = any(r.get("type") == "s_character" for r in rewards)
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

        self.state.roll_history.append(result)

        return result

    def _check_skin_claims(self):
        """
        皮肤累计领取检查
        当 total_rolls 达到 claim_threshold 时，自动发放对应皮肤
        返回: 领取的皮肤奖励列表
        """
        claim_rewards = []
        for stype_key in SKIN_TYPE_KEYS:
            if self.state.skin_claimed.get(stype_key, False):
                continue
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

    def _resolve_sleep_pool(self):
        """沉眠池结算"""
        self.sleep_pool.start_chase()
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
        大类: 低级奖励（B级弧盘为主，小概率A级弧盘）
        严格遵循官方概率，不直接出S级（S仅通过保底系统产出）
        """
        rewards = []
        r = random.random()

        if r < 0.06:
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

        return rewards

    def _resolve_brave_chest_darkbox(self):
        """
        勇者宝箱 - 概率暗箱版
        大类: 中级奖励（B级弧盘+金棋，较大概率A级弧盘）
        
        变格机制(70抽后):
        - 变格状态下勇者宝箱大部分概率出限定S级角色
        - 常规状态: S级2%, A级13%, B级85%
        - 变格状态: S级60%, A级20%, B级20%
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
            if r < 0.02:
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
            elif r < 0.15:
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

        rewards.append({"type": "gold_chip", "name": f"+{cell.get('extra_gold', 16)}金色棋子"})
        return rewards

    def _resolve_companion_darkbox(self, cell_name=None):
        """
        于此同行 - 根据格子名称确定角色（修复版）
        规则：必定获得当前格子内所示角色

        参数:
            cell_name: 格子的完整名称，如"于此同行（海月）"
                      如果为None，则随机抽取（兼容旧代码）
        """
        # 同行角色映射表
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
                self.state.reset_s_pity()
                print(f"[同行] S级角色{char_name}已获得，重置S级保底计数器")
        else:
            # 兼容旧逻辑：随机抽取
            pity_cfg = PITY_CONFIG["s_pity"]
            base_rate = pity_cfg["base_rate_variant"] if self.state.is_variant else pity_cfg["base_rate_normal"]

            if random.random() < base_rate or self.state.s_pity_counter >= pity_cfg["hard_pity"] - 1:
                char_name, rank = self.gacha.gacha_companion()
                if rank == "S":
                    self.state.reset_s_pity()
                print(f"\n[同行-随机] 抽取到{rank}级角色: {char_name}")
            else:
                a_companions = [c for c in COMPANIONS_LIMITED if c["rank"] == "A"]
                char_name = random.choice(a_companions)["name"]
                rank = "A"
                print(f"\n[同行-随机] 抽取到A级角色: {char_name}")

        collection_key = "s_characters" if rank == "S" else "a_characters"
        item_type = "s_character" if rank == "S" else "a_character"

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

    def _resolve_arcade_blind_sleep(self):
        """弧光盲盒+沉眠池组合结算"""
        rewards = self._resolve_arcade_blind()
        sp_event = None
        if random.random() < 0.3:
            _, sp_event = self._resolve_sleep_pool()
            rewards.extend(_[0] if _ else [] for _ in [sp_event])
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
        """
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
