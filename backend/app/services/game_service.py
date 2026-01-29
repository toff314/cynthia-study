"""益智游戏服务"""
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.game import Game
from ..schemas.game import (
    IdiomChainGenerateRequest,
    WordChainGenerateRequest,
    SudokuGenerateRequest,
    Point24GenerateRequest,
    ChessGenerateRequest,
    ParentChildGenerateRequest
)


class GameService:
    """游戏服务类"""

    # 成语数据库 - 按难度分类
    IDIOMS = {
        "easy": [
            # 低龄段（初级）
            "一心一意", "人山人海", "四面八方", "五颜六色", "七上八下",
            "不可思议", "不约而同", "千里迢迢", "画蛇添足", "守株待兔",
            "亡羊补牢", "掩耳盗铃", "井底之蛙", "狐假虎威", "刻舟求剑",
            "自相矛盾", "拔苗助长", "坐井观天", "杯弓蛇影", "对牛弹琴",
            "马到成功", "龙飞凤舞", "虎头虎脑", "牛气冲天", "羊入虎口",
            "猴年马月", "鸡飞狗跳", "狗急跳墙", "猪朋狗友", "鼠目寸光",
            "春暖花开", "夏日炎炎", "秋高气爽", "冬雪纷飞", "风和日丽",
            "月明星稀", "星罗棋布", "云开雾散", "雨过天晴", "电闪雷鸣",
            "花好月圆", "草长莺飞", "树大根深", "水滴石穿", "山清水秀",
        ],
        "normal": [
            # 中龄段（中级）
            "画龙点睛", "胸有成竹", "熟能生巧", "三心二意", "九牛一毛",
            "千军万马", "万里长征", "顶天立地", "惊天动地", "气吞山河",
            "风雨同舟", "同舟共济", "众志成城", "团结一心", "齐心协力",
            "勤能补拙", "笨鸟先飞", "铁杵成针", "水滴石穿", "积少成多",
            "聚沙成塔", "集腋成裘", "循序渐进", "温故知新", "学而不厌",
            "诲人不倦", "教学相长", "三人行必有我师", "举一反三", "触类旁通",
            "知无不言", "言无不尽", "言而有信", "言行一致", "心口如一",
            "表里如一", "光明正大", "光明磊落", "大公无私", "公而忘私",
            "艰苦朴素", "勤俭节约", "吃苦耐劳", "任劳任怨", "百折不挠",
        ],
        "hard": [
            # 高龄段（高级）
            "卧薪尝胆", "破釜沉舟", "背水一战", "一鼓作气", "哀兵必胜",
            "运筹帷幄", "决胜千里", "知己知彼", "百战不殆", "兵不厌诈",
            "声东击西", "调虎离山", "瓮中捉鳖", "关门打狗", "围魏救赵",
            "顺手牵羊", "打草惊蛇", "抛砖引玉", "欲擒故纵", "借刀杀人",
            "金蝉脱壳", "暗度陈仓", "偷梁换柱", "指桑骂槐", "假痴不癫",
            "上屋抽梯", "树上开花", "反客为主", "美人计", "空城计",
            "反间计", "苦肉计", "连环计", "走为上计", "三十六计",
            "朝秦暮楚", "朝令夕改", "朝三暮四", "阳奉阴违", "口蜜腹剑",
            "笑里藏刀", "明争暗斗", "勾心斗角", "尔虞我诈", "明枪暗箭",
        ]
    }

    # 单词数据库 - 按难度分类
    WORDS = {
        "easy": [
            # 低龄段（初级）
            "cat", "dog", "apple", "book", "pen", "desk", "chair", "ball",
            "red", "blue", "green", "yellow", "bird", "fish", "frog", "duck",
            "milk", "cake", "rice", "egg", "bread", "water", "juice", "tea",
            "sun", "moon", "star", "cloud", "rain", "snow", "wind", "day",
            "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "big", "small", "long", "short", "hot", "cold",
            "happy", "sad", "good", "bad", "yes", "no", "open", "close",
            "go", "come", "run", "walk", "jump", "swim", "fly", "sing",
        ],
        "normal": [
            # 中龄段（中级）
            "rainbow", "butterfly", "elephant", "dinosaur", "computer", "library",
            "school", "hospital", "restaurant", "supermarket", "beautiful", "wonderful",
            "exciting", "interesting", "delicious", "important", "different", "together",
            "morning", "afternoon", "evening", "weekend", "holiday", "birthday",
            "family", "friend", "teacher", "student", "doctor", "nurse", "police",
            "garden", "park", " playground", "cinema", "museum", "theatre",
            "music", "dance", "paint", "draw", "read", "write", "study", "learn",
            "breakfast", "lunch", "dinner", "snack", "vegetable", "fruit", "meat",
        ],
        "hard": [
            # 高龄段（高级）
            "adventure", "discovery", "technology", "environment", "communication",
            "celebration", "achievement", "development", "improvement", "encouragement",
            "understand", "remember", "imagination", "creativity", "opportunity",
            "challenge", "responsibility", "community", "friendship", "leadership",
            "knowledge", "experience", "confidence", "determination", "perseverance",
            "excellent", "fantastic", "magnificent", "extraordinary", "remarkable",
            "intelligent", "wonderful", "beautiful", "successful", "wonderfully",
            "yesterday", "tomorrow", "everywhere", "everything", "everyone",
            "somebody", "something", "everything", "nothing", "anything",
        ]
    }

    # 亲子类游戏模板
    PARENT_CHILD_GAMES = {
        "simon_says": {
            "title": "西蒙说",
            "instructions": "游戏规则：1. 主持人说'西蒙说'开头，大家要跟着做动作；2. 如果没有'西蒙说'开头，大家就不能做；3. 做错的人淘汰；4. 坚持到最后的人获胜！",
            "actions": [
                "拍三下手", "摸一下鼻子", "跺左脚", "举双手", "转身一圈",
                "拍右肩膀", "摸左耳朵", "点点头", "眨眨眼", "笑一下"
            ]
        },
        "who_is_undercover": {
            "title": "谁是卧底",
            "instructions": "游戏规则：1. 所有人抽取词语，大多数是词语A，少数是词语B（卧底）；2. 每人轮流描述自己的词语（不能直接说出）；3. 描述后投票淘汰一人；4. 卧底淘汰则平民获胜，平民只剩两人则卧底获胜！",
            "word_pairs": [
                {"a": "牛奶", "b": "豆浆"},
                {"a": "铅笔", "b": "毛笔"},
                {"a": "手机", "b": "电话"},
                {"a": "苹果", "b": "梨"},
                {"a": "老虎", "b": "狮子"}
            ]
        },
        "reverse_command": {
            "title": "反向指令",
            "instructions": "游戏规则：1. 主持人发出指令；2. 大家要做相反的动作；3. 向前变向后，向上变向下，变左变右；4. 反应慢或做错的人淘汰！",
            "commands": [
                "向前走一步", "举起右手", "向左转", "睁开眼睛", "站起来",
                "摸右耳朵", "点头", "举起左手", "坐下", "向右转"
            ]
        },
        "number_game": {
            "title": "数字炸弹",
            "instructions": "游戏规则：1. 主持人心中想一个1-100的数字；2. 大家轮流猜数字；3. 主持人提示猜大了或猜小了；4. 猜到数字的人'爆炸'淘汰；5. 范围越小越刺激！",
            "examples": ["目标：42", "猜测范围：1-100"]
        },
        "gesture_game": {
            "title": "动作接龙",
            "instructions": "游戏规则：1. 第一个人做一个动作；2. 第二个人重复第一个人的动作，再加上一个新动作；3. 第三个人重复前两个人的动作，再加新动作；4.以此类推，忘记或做错的人淘汰！",
            "suggestions": [
                "拍手", "转圈", "摸头", "扭腰", "踢腿", "蹲下"
            ]
        },
        "memory_game": {
            "title": "记忆大王",
            "instructions": "游戏规则：1. 主持人说出一系列物品；2. 每人轮流重复并添加新物品；3. 必须按顺序说出所有之前的物品；4. 忘记或说错的人淘汰！",
            "examples": ["苹果，香蕉，橘子，香蕉，香蕉香蕉"]
        }
    }

    # 棋类游戏说明
    CHESS_INSTRUCTIONS = {
        "chess": {
            "title": "国际象棋",
            "instructions": "国际象棋是一种双人对弈的棋类游戏。\n\n棋盘：8×8的方格，黑白相间。\n\n棋子：\n- 王（King）：横竖斜均可移动，每次一格\n- 后（Queen）：横竖斜均可移动，格数不限\n- 车（Rook）：横竖移动，格数不限\n- 象（Bishop）：斜着移动，格数不限\n- 马（Knight）：走'日'字形\n- 兵（Pawn）：只能向前走，第一步可走两格\n\n目标：将死对方的王！"
        },
        "checkers": {
            "title": "国际跳棋",
            "instructions": "国际跳棋是一种简单有趣的棋类游戏。\n\n棋盘：8×8的方格，只能用深色格子。\n\n规则：\n- 棋子只能在深色格子上斜向移动\n- 普通棋子只能向前移动一格\n- 可以跳过对方棋子吃子\n- 到达对方底线后升为'王'\n- '王'可以向前后斜向移动\n\n目标：吃光对方所有棋子，或让对方无路可走！"
        },
        "xiangqi": {
            "title": "中国象棋",
            "instructions": "中国象棋是中国传统的棋类游戏。\n\n规则：\n- 帅/将：只在九宫内移动，横竖一格\n- 仕/士：九宫内斜走一格\n- 相/象：斜走两格，不能过河\n- 车：横竖直线走，格数不限\n- 马：走'日'字，可被蹩马腿\n- 炮：与车相同，但吃子需隔一个子\n- 兵/卒：只能向前，过河后可横走\n\n目标：将死对方的帅/将！"
        },
        "go": {
            "title": "围棋",
            "instructions": "围棋是中国古老的棋类游戏。\n\n棋盘：19×19的交叉点（初学者可用9×9或13×13）\n\n规则：\n- 黑白双方轮流下子\n- 棋子下在交叉点上\n- 下子后有气的子才能存活\n- 无气的子被提掉\n- 打劫时不能立即回头吃\n\n目标：占据更多的地盘（棋盘上的空点）！"
        }
    }

    @staticmethod
    def generate_idiom_chain(age_group: str, difficulty: str = "normal",
                           chain_length: int = 10, blank_ratio: float = 0.3) -> Dict[str, Any]:
        """生成成语接龙字谜游戏"""
        # 根据年龄段确定难度
        if age_group == "low":
            difficulty = "easy"
        elif age_group == "mid":
            difficulty = "normal"
        elif age_group == "high":
            difficulty = "hard"

        idioms = GameService.IDIOMS.get(difficulty, GameService.IDIOMS["normal"])
        
        # 尝试构建字谜网格
        # 策略：选择成语，让它们在字与字之间重叠
        words_data = []
        used_idioms = set()
        
        # 尝试生成的最大次数
        max_attempts = chain_length * 10
        attempts = 0
        
        while len(words_data) < chain_length and attempts < max_attempts:
            attempts += 1
            
            # 如果已有词，找一个可以重叠的位置
            if words_data:
                found_match = False
                
                # 尝试多次寻找交叉点，提高重叠率
                for _ in range(5):  # 增加尝试次数
                    # 随机选择一个已放置的词
                    target_word = random.choice(words_data)
                    target_chars = target_word['word']
                    
                    # 随机选择已放置词中的一个位置
                    target_pos = random.randint(0, len(target_chars) - 1)
                    target_char = target_chars[target_pos]
                    
                    # 寻找包含该字且未使用的成语
                    matching_idioms = [idiom for idiom in idioms 
                                     if idiom not in used_idioms and target_char in idiom]
                    
                    if not matching_idioms:
                        continue
                        
                    idiom = random.choice(matching_idioms)
                    match_pos = idiom.index(target_char)
                    
                    # 决定是横放还是竖放
                    target_direction = target_word.get('direction', 'horizontal')
                    new_direction = 'vertical' if target_direction == 'horizontal' else 'horizontal'
                    
                    # 计算新词的起始位置
                    if new_direction == 'vertical':
                        # 竖放：(row, col) = (target_row - match_pos, target_col)
                        new_row = target_word['row'] - match_pos
                        new_col = target_word['col'] + target_pos
                    else:
                        # 横放：(row, col) = (target_row + target_pos, target_col - match_pos)
                        new_row = target_word['row'] + target_pos
                        new_col = target_word['col'] - match_pos
                    
                    # 检查位置是否有效
                    if new_row < 0 or new_col < 0:
                        continue
                    
                    # 检查是否与现有词冲突
                    can_place = True
                    for i, char in enumerate(idiom):
                        if new_direction == 'vertical':
                            check_row = new_row + i
                            check_col = new_col
                        else:
                            check_row = new_row
                            check_col = new_col + i
                        
                        # 检查这个位置是否已被占用
                        for w in words_data:
                            if w['direction'] == 'horizontal':
                                if check_row == w['row']:
                                    if w['col'] <= check_col < w['col'] + len(w['word']):
                                        if w['word'][check_col - w['col']] != char:
                                            can_place = False
                                            break
                            else:  # vertical
                                if check_col == w['col']:
                                    if w['row'] <= check_row < w['row'] + len(w['word']):
                                        if w['word'][check_row - w['row']] != char:
                                            can_place = False
                                            break
                            if not can_place:
                                break
                        
                        if not can_place:
                            break
                    
                    if can_place:
                        # 可以放置，添加到列表
                        used_idioms.add(idiom)
                        words_data.append({
                            'word': idiom,
                            'row': new_row,
                            'col': new_col,
                            'direction': new_direction
                        })
                        found_match = True
                        break
                
                if not found_match:
                    # 无法找到匹配，选择一个新的成语横向放置，减小行距
                    remaining_idioms = [idiom for idiom in idioms if idiom not in used_idioms]
                    if not remaining_idioms:
                        break
                    idiom = random.choice(remaining_idioms)
                    used_idioms.add(idiom)
                    
                    # 放在新行，减小行距从 *2 改为 +1
                    row = len(words_data) + 1
                    col = random.randint(0, 3)
                    
                    words_data.append({
                        'word': idiom,
                        'row': row,
                        'col': col,
                        'direction': 'horizontal'
                    })
            else:
                # 第一个词，直接横向放置
                idiom = random.choice(idioms)
                used_idioms.add(idiom)
                words_data.append({
                    'word': idiom,
                    'row': 0,
                    'col': 0,
                    'direction': 'horizontal'
                })
        
        # 构建网格表示并挖空
        if words_data:
            max_row = max(w['row'] + (len(w['word']) if w['direction'] == 'vertical' else 1) for w in words_data)
            max_col = max(w['col'] + (len(w['word']) if w['direction'] == 'horizontal' else 1) for w in words_data)
            
            # 为了防止负坐标，计算偏移量
            min_row = min(w['row'] for w in words_data)
            min_col = min(w['col'] for w in words_data)
            
            # 计算每个词挖空的位置（在交叉点除外）
            blank_positions_map = {}  # 记录每个词需要挖空的位置
            position_word_map = {}    # 记录每个位置属于哪些词（用于检测交叉点）
            
            # 先统计每个位置被多少个词使用
            for word_data in words_data:
                word = word_data['word']
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                for i, char in enumerate(word):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if pos_key not in position_word_map:
                        position_word_map[pos_key] = []
                    position_word_map[pos_key].append(word_data['word'])
            
            # 为每个词确定挖空位置（避开交叉点）
            for word_data in words_data:
                word = word_data['word']
                word_len = len(word)
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                # 随机选择1-2个位置挖空
                num_blanks = random.choice([1, 2]) if word_len >= 3 else min(1, word_len - 1)
                
                # 找出非交叉点的位置
                non_cross_positions = []
                for i in range(word_len):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    # 检查是否是交叉点（被多个词使用）
                    if len(position_word_map.get(pos_key, [])) == 1:
                        non_cross_positions.append(i)
                
                # 从非交叉点中随机选择挖空位置
                if len(non_cross_positions) >= num_blanks:
                    blank_indices = random.sample(non_cross_positions, num_blanks)
                else:
                    # 如果非交叉点不足，则只在可用位置挖空
                    blank_indices = random.sample(non_cross_positions, min(num_blanks, len(non_cross_positions)))
                
                blank_positions_map[word_data['word']] = blank_indices
            
            # 生成网格（带挖空）
            grid = [['' for _ in range(max_col - min_col + 3)] for _ in range(max_row - min_row + 3)]
            
            # 放置所有词（在交叉点显示字符，在挖空位置不显示）
            for word_data in words_data:
                word = word_data['word']
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                blank_indices = blank_positions_map.get(word, [])
                
                for i, char in enumerate(word):
                    # 计算网格中的实际坐标（调整偏移）
                    if direction == 'horizontal':
                        grid_row = row - min_row
                        grid_col = col + i - min_col
                    else:
                        grid_row = row + i - min_row
                        grid_col = col - min_col
                    
                    # 检查是否被挖空
                    if i in blank_indices:
                        # 这个位置被挖空，留空
                        if grid[grid_row][grid_col] == '':
                            grid[grid_row][grid_col] = ''  # 挖空
                    else:
                        # 这个位置不挖空，显示字符
                        if grid[grid_row][grid_col] == '':
                            grid[grid_row][grid_col] = char
                        # 如果交叉点已经有字符，保持原样（它们应该相同）
        else:
            grid = [['']]
        
        # 为每个词记录其实际位置（调整坐标系）
        for word_data in words_data:
            word_data['row'] = word_data['row'] - min_row
            word_data['col'] = word_data['col'] - min_col
        
        # 处理成链格式（用于提示答案）
        chain = []
        for word_data in words_data:
            chars = list(word_data['word'])
            blank_indices = blank_positions_map.get(word_data['word'], [])
            blanks = [i in blank_indices for i in range(len(chars))]
            
            chain.append({
                "word": word_data['word'],
                "chars": chars,
                "blanks": blanks,
                "row": word_data['row'],
                "col": word_data['col'],
                "direction": word_data['direction']
            })
        
        return {
            "grid": grid,
            "chain": chain,
            "difficulty": difficulty,
            "chain_length": len(words_data)
        }

    @staticmethod
    def generate_word_chain(age_group: str, difficulty: str = "normal",
                           chain_length: int = 10, blank_ratio: float = 0.3) -> Dict[str, Any]:
        """生成英语单词接龙字谜游戏"""
        # 根据年龄段确定难度
        if age_group == "low":
            difficulty = "easy"
        elif age_group == "mid":
            difficulty = "normal"
        elif age_group == "high":
            difficulty = "hard"

        words = GameService.WORDS.get(difficulty, GameService.WORDS["normal"])
        
        # 尝试构建字谜网格
        words_data = []
        used_words = set()
        
        # 尝试生成的最大次数
        max_attempts = chain_length * 10
        attempts = 0
        
        while len(words_data) < chain_length and attempts < max_attempts:
            attempts += 1
            
            # 如果已有词，找一个可以重叠的位置
            if words_data:
                found_match = False
                
                # 尝试多次寻找交叉点，提高重叠率
                for _ in range(5):  # 增加尝试次数
                    # 随机选择一个已放置的词
                    target_word = random.choice(words_data)
                    target_word_str = target_word['word']
                    
                    # 随机选择已放置词中的一个位置
                    target_pos = random.randint(0, len(target_word_str) - 1)
                    target_char = target_word_str[target_pos]
                    
                    # 寻找包含该字母且未使用的单词
                    matching_words = [word for word in words 
                                    if word not in used_words and target_char in word]
                    
                    if not matching_words:
                        continue
                        
                    word = random.choice(matching_words)
                    match_pos = word.index(target_char)
                    
                    # 决定是横放还是竖放
                    target_direction = target_word.get('direction', 'horizontal')
                    new_direction = 'vertical' if target_direction == 'horizontal' else 'horizontal'
                    
                    # 计算新词的起始位置
                    if new_direction == 'vertical':
                        new_row = target_word['row'] - match_pos
                        new_col = target_word['col'] + target_pos
                    else:
                        new_row = target_word['row'] + target_pos
                        new_col = target_word['col'] - match_pos
                    
                    # 检查位置是否有效
                    if new_row < 0 or new_col < 0:
                        continue
                    
                    # 检查是否与现有词冲突
                    can_place = True
                    for i, char in enumerate(word):
                        if new_direction == 'vertical':
                            check_row = new_row + i
                            check_col = new_col
                        else:
                            check_row = new_row
                            check_col = new_col + i
                        
                        for w in words_data:
                            if w['direction'] == 'horizontal':
                                if check_row == w['row']:
                                    if w['col'] <= check_col < w['col'] + len(w['word']):
                                        if w['word'][check_col - w['col']] != char:
                                            can_place = False
                                            break
                            else:  # vertical
                                if check_col == w['col']:
                                    if w['row'] <= check_row < w['row'] + len(w['word']):
                                        if w['word'][check_row - w['row']] != char:
                                            can_place = False
                                            break
                            if not can_place:
                                break
                        
                        if not can_place:
                            break
                    
                    if can_place:
                        used_words.add(word)
                        words_data.append({
                            'word': word,
                            'row': new_row,
                            'col': new_col,
                            'direction': new_direction
                        })
                        found_match = True
                        break
                
                if not found_match:
                    # 无法找到匹配，选择一个新的单词横向放置，减小行距
                    remaining_words = [word for word in words if word not in used_words]
                    if not remaining_words:
                        break
                    word = random.choice(remaining_words)
                    used_words.add(word)
                    
                    # 减小行距从 *2 改为 +1
                    row = len(words_data) + 1
                    col = random.randint(0, 3)
                    
                    words_data.append({
                        'word': word,
                        'row': row,
                        'col': col,
                        'direction': 'horizontal'
                    })
            else:
                # 第一个词，直接横向放置
                word = random.choice(words)
                used_words.add(word)
                words_data.append({
                    'word': word,
                    'row': 0,
                    'col': 0,
                    'direction': 'horizontal'
                })
        
        # 构建网格表示并挖空
        if words_data:
            max_row = max(w['row'] + (len(w['word']) if w['direction'] == 'vertical' else 1) for w in words_data)
            max_col = max(w['col'] + (len(w['word']) if w['direction'] == 'horizontal' else 1) for w in words_data)
            
            # 为了防止负坐标，计算偏移量
            min_row = min(w['row'] for w in words_data)
            min_col = min(w['col'] for w in words_data)
            
            # 计算每个词挖空的位置（在交叉点除外）
            blank_positions_map = {}  # 记录每个词需要挖空的位置
            position_word_map = {}    # 记录每个位置属于哪些词（用于检测交叉点）
            
            # 先统计每个位置被多少个词使用
            for word_data in words_data:
                word = word_data['word']
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                for i, char in enumerate(word):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if pos_key not in position_word_map:
                        position_word_map[pos_key] = []
                    position_word_map[pos_key].append(word_data['word'])
            
            # 为每个词确定挖空位置（避开交叉点）
            for word_data in words_data:
                word = word_data['word']
                word_len = len(word)
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                # 随机选择1-2个位置挖空
                num_blanks = random.choice([1, 2]) if word_len >= 3 else min(1, word_len - 1)
                
                # 找出非交叉点的位置
                non_cross_positions = []
                for i in range(word_len):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    # 检查是否是交叉点（被多个词使用）
                    if len(position_word_map.get(pos_key, [])) == 1:
                        non_cross_positions.append(i)
                
                # 从非交叉点中随机选择挖空位置
                if len(non_cross_positions) >= num_blanks:
                    blank_indices = random.sample(non_cross_positions, num_blanks)
                else:
                    # 如果非交叉点不足，则只在可用位置挖空
                    blank_indices = random.sample(non_cross_positions, min(num_blanks, len(non_cross_positions)))
                
                blank_positions_map[word_data['word']] = blank_indices
            
            # 生成网格（带挖空）
            grid = [['' for _ in range(max_col - min_col + 3)] for _ in range(max_row - min_row + 3)]
            
            # 放置所有词（在交叉点显示字符，在挖空位置不显示）
            for word_data in words_data:
                word = word_data['word']
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                blank_indices = blank_positions_map.get(word, [])
                
                for i, char in enumerate(word):
                    # 计算网格中的实际坐标（调整偏移）
                    if direction == 'horizontal':
                        grid_row = row - min_row
                        grid_col = col + i - min_col
                    else:
                        grid_row = row + i - min_row
                        grid_col = col - min_col
                    
                    # 检查是否被挖空
                    if i in blank_indices:
                        # 这个位置被挖空，留空
                        if grid[grid_row][grid_col] == '':
                            grid[grid_row][grid_col] = ''  # 挖空
                    else:
                        # 这个位置不挖空，显示字符
                        if grid[grid_row][grid_col] == '':
                            grid[grid_row][grid_col] = char.upper()
                        # 如果交叉点已经有字符，保持原样（它们应该相同）
        else:
            grid = [['']]
        
        # 为每个词记录其实际位置（调整坐标系）
        for word_data in words_data:
            word_data['row'] = word_data['row'] - min_row
            word_data['col'] = word_data['col'] - min_col
        
        # 处理成链格式
        chain = []
        for word_data in words_data:
            letters = list(word_data['word'])
            blank_indices = blank_positions_map.get(word_data['word'], [])
            blanks = [i in blank_indices for i in range(len(letters))]
            
            chain.append({
                "word": word_data['word'],
                "letters": letters,
                "blanks": blanks,
                "row": word_data['row'],
                "col": word_data['col'],
                "direction": word_data['direction']
            })
        
        return {
            "grid": grid,
            "chain": chain,
            "difficulty": difficulty,
            "chain_length": len(words_data)
        }

    @staticmethod
    def generate_sudoku(size: int = 9, difficulty: str = "normal") -> Dict[str, Any]:
        """生成数独游戏"""
        # 根据大小调整难度
        if size == 4:
            empty_cells = 3 if difficulty == "easy" else 4
        elif size == 6:
            empty_cells = 12 if difficulty == "easy" else (15 if difficulty == "normal" else 18)
        else:  # size == 9
            empty_cells = 30 if difficulty == "easy" else (40 if difficulty == "normal" else 50)
        
        # 简化版：使用预定义的有效数独模板
        if size == 4:
            solution = [
                [1, 2, 3, 4],
                [3, 4, 1, 2],
                [2, 1, 4, 3],
                [4, 3, 2, 1]
            ]
        elif size == 6:
            # 6x6数独：2行3列的2x3宫格
            solution = [
                [1, 2, 3, 4, 5, 6],
                [4, 5, 6, 1, 2, 3],
                [2, 3, 1, 5, 6, 4],
                [5, 6, 4, 2, 3, 1],
                [3, 1, 2, 6, 4, 5],
                [6, 4, 5, 3, 1, 2]
            ]
        else:  # 9x9
            solution = [
                [5, 3, 4, 6, 7, 8, 9, 1, 2],
                [6, 7, 2, 1, 9, 5, 3, 4, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 5, 9, 7, 6, 1, 4, 2, 3],
                [4, 2, 6, 8, 5, 3, 7, 9, 1],
                [7, 1, 3, 9, 2, 4, 8, 5, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9]
            ]
        
        # 创建网格并挖空
        grid = [row[:] for row in solution]
        positions = [(i, j) for i in range(size) for j in range(size)]
        for i, j in random.sample(positions, empty_cells):
            grid[i][j] = 0
        
        return {
            "grid": grid,
            "solution": solution,
            "size": size,
            "difficulty": difficulty
        }

    @staticmethod
    def generate_point24(difficulty: str = "normal") -> Dict[str, Any]:
        """生成24点游戏"""
        # 根据难度选择数字范围
        if difficulty == "easy":
            num_range = range(1, 7)
        elif difficulty == "hard":
            num_range = range(3, 10)
        else:  # normal
            num_range = range(1, 10)
        
        # 随机选择4个数字
        numbers = [random.choice(num_range) for _ in range(4)]
        
        # 简单检查是否可能有解（这里简化处理，实际应该检查）
        # 预定义一些可解的组合作为示例
        solvable_sets = [
            [1, 2, 3, 4],  # (1+2+3)*4 = 24
            [2, 3, 4, 6],  # 2*3*4 = 24
            [1, 3, 4, 6],  # (1+3)*6 = 24
            [2, 4, 6, 8],  # 2*4+8+8 = 24 (简化)
            [3, 4, 6, 8],  # (3+6-3)*4 = 24
        ]
        
        if difficulty != "hard" and random.random() < 0.5:
            numbers = random.choice(solvable_sets)
        
        # 生成可能的解答示例
        solutions = []
        if sum(numbers) == 24:
            solutions.append(f"{numbers[0]}+{numbers[1]}+{numbers[2]}+{numbers[3]}=24")
        
        return {
            "numbers": numbers,
            "target": 24,
            "solutions": solutions
        }

    @staticmethod
    def generate_chess(board_type: str, board_size: int = 8) -> Dict[str, Any]:
        """生成棋类游戏"""
        instructions = GameService.CHESS_INSTRUCTIONS.get(board_type, GameService.CHESS_INSTRUCTIONS["checkers"])
        
        # 生成空棋盘网格
        grid = [[0 for _ in range(board_size)] for _ in range(board_size)]
        
        # 根据棋盘类型初始化棋子
        if board_type == "chess":
            # 国际象棋简化标记：白棋为大写，黑棋为小写
            # R=车, N=马, B=象, Q=后, K=王, P=兵
            grid[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
            grid[1] = ['p'] * board_size
            grid[-2] = ['P'] * board_size
            grid[-1] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        elif board_type == "checkers":
            # 跳棋：黑棋=1，白棋=2
            for i in range(board_size):
                for j in range(board_size):
                    if (i + j) % 2 == 1:
                        if i < 3:
                            grid[i][j] = 1  # 黑棋
                        elif i > board_size - 4:
                            grid[i][j] = 2  # 白棋
        elif board_type == "xiangqi":
            # 中国象棋：需要特殊棋盘，这里简化为空网格
            pass
        elif board_type == "go":
            # 围棋：空棋盘，有星位点
            star_points = []
            if board_size == 19:
                star_points = [(3, 3), (3, 9), (3, 15),
                              (9, 3), (9, 9), (9, 15),
                              (15, 3), (15, 9), (15, 15)]
            elif board_size == 13:
                star_points = [(3, 3), (3, 6), (3, 9),
                              (6, 3), (6, 6), (6, 9),
                              (9, 3), (9, 6), (9, 9)]
            elif board_size == 9:
                star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
            return {
                "board_type": board_type,
                "board_size": board_size,
                "grid": grid,
                "star_points": star_points,
                "title": instructions["title"],
                "instructions": instructions["instructions"]
            }
        
        return {
            "board_type": board_type,
            "board_size": board_size,
            "grid": grid,
            "title": instructions["title"],
            "instructions": instructions["instructions"]
        }

    @staticmethod
    def generate_parent_child_games(game_types: List[str]) -> Dict[str, Any]:
        """生成亲子类游戏 - 为每个游戏生成6张使用卡片"""
        cards = {}
        common_instructions = ""
        
        # 物品类数据库
        items_list = [
            ["苹果", "香蕉", "橘子", "葡萄", "西瓜", "桃子"],
            ["桌子", "椅子", "沙发", "床", "衣柜", "书柜"],
            ["铅笔", "橡皮", "尺子", "剪刀", "胶水", "笔记本"],
            ["小狗", "小猫", "小鸟", "小鱼", "小兔", "小鸭"],
            ["红色", "蓝色", "绿色", "黄色", "紫色", "粉色"],
            ["汽车", "公交车", "自行车", "火车", "飞机", "轮船"]
        ]
        
        # 为每个游戏类型生成6张卡片
        for game_type in game_types:
            if game_type in GameService.PARENT_CHILD_GAMES:
                game_info = GameService.PARENT_CHILD_GAMES[game_type]
                
                # 设置统一的游戏规则
                common_instructions = game_info["instructions"]
                
                if game_type == "simon_says":
                    # 西蒙说：生成6张动作卡片
                    actions = game_info["actions"]
                    for i in range(min(6, len(actions))):
                        cards[f"卡片{i+1}"] = actions[i]
                
                elif game_type == "who_is_undercover":
                    # 谁是卧底：生成6张词语对卡片
                    word_pairs = game_info["word_pairs"]
                    for i in range(min(6, len(word_pairs))):
                        pair = word_pairs[i]
                        cards[f"卡片{i+1}"] = f"词语 A：{pair['a']} / 词语 B：{pair['b']}"
                
                elif game_type == "reverse_command":
                    # 反向指令：生成6张指令卡片
                    commands = game_info["commands"]
                    for i in range(min(6, len(commands))):
                        cmd = commands[i]
                        # 生成相反指令
                        reverse_map = {
                            "向前": "向后", "向后": "向前",
                            "左": "右", "右": "左",
                            "上": "下", "下": "上",
                            "举起": "放下", "睁": "闭", "站": "坐"
                        }
                        reverse_cmd = cmd
                        for k, v in reverse_map.items():
                            reverse_cmd = reverse_cmd.replace(k, v)
                        cards[f"卡片{i+1}"] = f"指令：{cmd} / 反向：{reverse_cmd}"
                
                elif game_type == "number_game":
                    # 数字炸弹：生成6张不同范围的游戏卡片
                    ranges = [(1, 100), (1, 50), (51, 100), (1, 200), (51, 150), (1, 30)]
                    for i, (min_num, max_num) in enumerate(ranges):
                        target = random.randint(min_num, max_num)
                        cards[f"卡片{i+1}"] = f"范围：{min_num} - {max_num} / 目标数字：{target}"
                
                elif game_type == "gesture_game":
                    # 动作接龙：生成6张起始动作卡片
                    suggestions = game_info["suggestions"]
                    for i in range(min(6, len(suggestions))):
                        cards[f"卡片{i+1}"] = f"起始动作：{suggestions[i]}"
                
                elif game_type == "memory_game":
                    # 记忆大王：生成6张物品列表卡片
                    for i in range(min(6, len(items_list))):
                        items = items_list[i]
                        items_text = "、".join(items)
                        cards[f"卡片{i+1}"] = f"记忆物品：{items_text}"
        
        return {
            "cards": cards,
            "common_instructions": common_instructions,
            "total": len(cards)
        }

    @staticmethod
    def get_game_types_by_age_group(age_group: str) -> Dict[str, List[str]]:
        """根据年龄段获取游戏类型"""
        if age_group == "low":
            return {
                "title": "低龄段游戏（6-8岁）",
                "games": [
                    {"type": "idiom_chain", "name": "成语接龙（初级）", "icon": "📝"},
                    {"type": "word_chain", "name": "英语单词接龙（初级）", "icon": "🔤"},
                    {"type": "sudoku", "name": "四宫格数独", "icon": "🔢"}
                ]
            }
        elif age_group == "mid":
            return {
                "title": "中龄段游戏（9-11岁）",
                "games": [
                    {"type": "idiom_chain", "name": "成语接龙（中级）", "icon": "📝"},
                    {"type": "word_chain", "name": "英语单词接龙（中级）", "icon": "🔤"},
                    {"type": "sudoku", "name": "六宫格数独", "icon": "🔢"}
                ]
            }
        elif age_group == "high":
            return {
                "title": "高龄段游戏（12岁以上）",
                "games": [
                    {"type": "idiom_chain", "name": "成语接龙（高级）", "icon": "📝"},
                    {"type": "word_chain", "name": "英语单词接龙（高级）", "icon": "🔤"},
                    {"type": "sudoku", "name": "九宫格数独", "icon": "🔢"},
                    {"type": "point24", "name": "24点", "icon": "➕"}
                ]
            }
        else:  # all
            return {
                "title": "全部游戏",
                "games": []
            }

    @staticmethod
    def get_all_game_categories() -> List[Dict[str, Any]]:
        """获取所有游戏分类"""
        return [
            {
                "id": "low",
                "name": "低龄段",
                "description": "6-8岁",
                "icon": "👶"
            },
            {
                "id": "mid",
                "name": "中龄段",
                "description": "9-11岁",
                "icon": "🧒"
            },
            {
                "id": "high",
                "name": "高龄段",
                "description": "12岁以上",
                "icon": "🧑"
            },
            {
                "id": "chess",
                "name": "棋类游戏",
                "description": "各种棋盘",
                "icon": "♟️"
            },
            {
                "id": "parent_child",
                "name": "亲子类游戏",
                "description": "家庭互动",
                "icon": "👨‍👩‍👧‍👦"
            }
        ]

    @staticmethod
    def get_chess_types() -> List[Dict[str, Any]]:
        """获取棋类游戏类型（仅围棋）"""
        return [
            {"type": "go", "name": "围棋", "icon": "⚫", "sizes": [9, 13, 19]}
        ]

    @staticmethod
    def get_parent_child_game_types() -> List[Dict[str, Any]]:
        """获取亲子类游戏类型"""
        return [
            {"type": "simon_says", "name": "西蒙说", "icon": "🗣️"},
            {"type": "who_is_undercover", "name": "谁是卧底", "icon": "🕵️"},
            {"type": "reverse_command", "name": "反向指令", "icon": "�"},
            {"type": "number_game", "name": "数字炸弹", "icon": "�"},
            {"type": "gesture_game", "name": "动作接龙", "icon": "🤸"},
            {"type": "memory_game", "name": "记忆大王", "icon": "🧠"}
        ]

    @staticmethod
    def create_game(db: Session, game_data: dict) -> Game:
        """创建游戏记录"""
        game = Game(**game_data)
        db.add(game)
        db.commit()
        db.refresh(game)
        return game

    @staticmethod
    def get_games_by_type(db: Session, game_type: str, age_group: str = None) -> List[Game]:
        """根据类型和年龄段获取游戏列表"""
        query = db.query(Game).filter(Game.game_type == game_type)
        if age_group:
            query = query.filter(Game.age_group == age_group)
        return query.order_by(Game.created_at.desc()).limit(50).all()
