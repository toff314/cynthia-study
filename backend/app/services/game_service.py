"""益智游戏服务"""
import random
from typing import List, Dict, Any, Optional

# 从外部文件导入游戏数据
from ..data.game_data import (
    IDIOMS, WORDS, PARENT_CHILD_GAMES, 
    CHESS_INSTRUCTIONS, ITEMS_LIST
)

# 成语数据库 - 引用外部数据
GameIdioms = IDIOMS
GameWords = WORDS
GameParentChildGames = PARENT_CHILD_GAMES
GameChessInstructions = CHESS_INSTRUCTIONS
GameItemsList = ITEMS_LIST


class GameService:
    """游戏服务类"""

    # 从外部数据获取游戏配置
    IDIOMS = IDIOMS

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

        idioms = IDIOMS.get(difficulty, IDIOMS["normal"])
        
        # 尝试构建字谜网格
        words_data = []
        used_idioms = set()
        max_attempts = chain_length * 10
        attempts = 0
        
        while len(words_data) < chain_length and attempts < max_attempts:
            attempts += 1
            
            if words_data:
                found_match = False
                
                for _ in range(5):
                    target_word = random.choice(words_data)
                    target_chars = target_word['word']
                    target_pos = random.randint(0, len(target_chars) - 1)
                    target_char = target_chars[target_pos]
                    
                    matching_idioms = [idiom for idiom in idioms 
                                     if idiom not in used_idioms and target_char in idiom]
                    
                    if not matching_idioms:
                        continue
                        
                    idiom = random.choice(matching_idioms)
                    match_pos = idiom.index(target_char)
                    
                    target_direction = target_word.get('direction', 'horizontal')
                    new_direction = 'vertical' if target_direction == 'horizontal' else 'horizontal'
                    
                    if new_direction == 'vertical':
                        new_row = target_word['row'] - match_pos
                        new_col = target_word['col'] + target_pos
                    else:
                        new_row = target_word['row'] + target_pos
                        new_col = target_word['col'] - match_pos
                    
                    if new_row < 0 or new_col < 0:
                        continue
                    
                    can_place = True
                    for i, char in enumerate(idiom):
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
                            else:
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
                    remaining_idioms = [idiom for idiom in idioms if idiom not in used_idioms]
                    if not remaining_idioms:
                        break
                    idiom = random.choice(remaining_idioms)
                    used_idioms.add(idiom)
                    row = len(words_data) + 1
                    col = random.randint(0, 3)
                    words_data.append({
                        'word': idiom,
                        'row': row,
                        'col': col,
                        'direction': 'horizontal'
                    })
            else:
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
            position_letter_map = {}
            blank_positions_map = {}
            position_word_map = {}
            
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
            
            for word_data in words_data:
                word = word_data['word']
                word_len = len(word)
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                num_blanks = random.choice([1, 2]) if word_len >= 3 else min(1, word_len - 1)
                
                non_cross_positions = []
                for i in range(word_len):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if len(position_word_map.get(pos_key, [])) == 1:
                        non_cross_positions.append(i)
                
                if len(non_cross_positions) >= num_blanks:
                    blank_indices = random.sample(non_cross_positions, num_blanks)
                else:
                    blank_indices = random.sample(non_cross_positions, min(num_blanks, len(non_cross_positions)))
                
                blank_indices_set = set(blank_indices)
                
                for i, char in enumerate(word):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if i not in blank_indices_set:
                        if pos_key in position_letter_map:
                            if position_letter_map[pos_key] != char:
                                pass
                        else:
                            position_letter_map[pos_key] = char
                
                blank_positions_map[word_data['word']] = blank_indices
            
            # 根据chain_length映射到固定的网格大小
            size_mapping = {
                5: (6, 9),
                10: (8, 12),
                15: (10, 15),
                20: (12, 18)
            }
            if chain_length in size_mapping:
                fixed_cols, fixed_rows = size_mapping[chain_length]
            else:
                fixed_cols = 8
                fixed_rows = 12

            grid = [['' for _ in range(fixed_cols)] for _ in range(fixed_rows)]
            
            for pos_key, char in position_letter_map.items():
                grid_row, grid_col = pos_key
                
                if 0 <= grid_row < fixed_rows and 0 <= grid_col < fixed_cols:
                    grid[grid_row][grid_col] = char
        else:
            grid = [['']]
        
        # 处理成链格式
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
        if age_group == "low":
            difficulty = "easy"
        elif age_group == "mid":
            difficulty = "normal"
        elif age_group == "high":
            difficulty = "hard"

        words_by_category = WORDS.get(difficulty, WORDS["normal"])
        words = [word.capitalize() for word in words_by_category]
        
        words_data = []
        used_words = set()
        max_attempts = chain_length * 10
        attempts = 0
        
        while len(words_data) < chain_length and attempts < max_attempts:
            attempts += 1
            
            if words_data:
                found_match = False
                
                for _ in range(5):
                    target_word = random.choice(words_data)
                    target_word_str = target_word['word']
                    target_pos = random.randint(0, len(target_word_str) - 1)
                    target_char = target_word_str[target_pos]
                    
                    matching_words = [word for word in words 
                                    if word not in used_words and target_char in word]
                    
                    if not matching_words:
                        continue
                        
                    word = random.choice(matching_words)
                    match_pos = word.index(target_char)
                    
                    target_direction = target_word.get('direction', 'horizontal')
                    new_direction = 'vertical' if target_direction == 'horizontal' else 'horizontal'
                    
                    if new_direction == 'vertical':
                        new_row = target_word['row'] - match_pos
                        new_col = target_word['col'] + target_pos
                    else:
                        new_row = target_word['row'] + target_pos
                        new_col = target_word['col'] - match_pos
                    
                    if new_row < 0 or new_col < 0:
                        continue
                    
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
                            else:
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
                    remaining_words = [word for word in words if word not in used_words]
                    if not remaining_words:
                        break
                    word = random.choice(remaining_words)
                    used_words.add(word)
                    row = len(words_data) + 1
                    col = random.randint(0, 3)
                    words_data.append({
                        'word': word,
                        'row': row,
                        'col': col,
                        'direction': 'horizontal'
                    })
            else:
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
            position_letter_map = {}
            blank_positions_map = {}
            position_word_map = {}
            
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
            
            for word_data in words_data:
                word = word_data['word']
                word_len = len(word)
                row = word_data['row']
                col = word_data['col']
                direction = word_data['direction']
                
                num_blanks = random.choice([1, 2]) if word_len >= 3 else min(1, word_len - 1)
                
                non_cross_positions = []
                for i in range(word_len):
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if len(position_word_map.get(pos_key, [])) == 1:
                        non_cross_positions.append(i)
                
                if len(non_cross_positions) >= num_blanks:
                    blank_indices = random.sample(non_cross_positions, num_blanks)
                else:
                    blank_indices = random.sample(non_cross_positions, min(num_blanks, len(non_cross_positions)))
                
                blank_indices_set = set(blank_indices)
                
                for i, char in enumerate(word):
                    display_char = char.upper() if i == 0 else char.lower()
                    
                    if direction == 'horizontal':
                        pos_key = (row, col + i)
                    else:
                        pos_key = (row + i, col)
                    
                    if i not in blank_indices_set:
                        if pos_key in position_letter_map:
                            if position_letter_map[pos_key] != display_char:
                                pass
                        else:
                            position_letter_map[pos_key] = display_char
                
                blank_positions_map[word_data['word']] = blank_indices
            
            size_mapping = {
                5: (8, 12),
                10: (10, 15),
                15: (12, 18),
                20: (14, 21)
            }
            if chain_length in size_mapping:
                fixed_cols, fixed_rows = size_mapping[chain_length]
            else:
                fixed_cols = 10
                fixed_rows = 15

            grid = [['' for _ in range(fixed_cols)] for _ in range(fixed_rows)]
            
            for pos_key, letter in position_letter_map.items():
                grid_row, grid_col = pos_key
                
                if 0 <= grid_row < fixed_rows and 0 <= grid_col < fixed_cols:
                    grid[grid_row][grid_col] = letter
        else:
            grid = [['']]
        
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
        if size == 4:
            num_puzzles = 3
        elif size == 6:
            num_puzzles = 2
        else:
            num_puzzles = 1
        
        puzzles = []
        
        base_4x4 = [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [2, 1, 4, 3],
            [4, 3, 2, 1]
        ]
        
        base_6x6 = [
            [1, 2, 3, 4, 5, 6],
            [4, 5, 6, 1, 2, 3],
            [2, 3, 1, 5, 6, 4],
            [5, 6, 4, 2, 3, 1],
            [3, 1, 2, 6, 4, 5],
            [6, 4, 5, 3, 1, 2]
        ]
        
        base_9x9 = [
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
        
        for i in range(num_puzzles):
            if size == 4:
                empty_cells = 3 if difficulty == "easy" else 4
                solution = [[(num + i) % 4 + 1 for num in row] for row in base_4x4]
            elif size == 6:
                empty_cells = 12 if difficulty == "easy" else (15 if difficulty == "normal" else 18)
                solution = [[(num + i) % 6 + 1 for num in row] for row in base_6x6]
            else:
                empty_cells = 30 if difficulty == "easy" else (40 if difficulty == "normal" else 50)
                solution = [[(num % 9) + 1 for num in row] for row in base_9x9]
            
            grid = [row[:] for row in solution]
            positions = [(r, c) for r in range(size) for c in range(size)]
            for r, c in random.sample(positions, empty_cells):
                grid[r][c] = 0
            
            puzzles.append({
                "grid": grid,
                "solution": solution,
                "index": i + 1
            })
        
        return {
            "puzzles": puzzles,
            "size": size,
            "difficulty": difficulty,
            "count": num_puzzles
        }

    @staticmethod
    def generate_point24(difficulty: str = "normal", count: int = 1) -> Dict[str, Any]:
        """生成24点游戏
        
        Args:
            difficulty: 难度级别 (easy, normal, hard)
            count: 生成等式的数量
        """
        if difficulty == "easy":
            num_range = range(1, 6)
        elif difficulty == "hard":
            num_range = range(3, 10)
        else:
            num_range = range(1, 10)
        
        solvable_sets = [
            [1, 2, 3, 4], [2, 3, 4, 6], [1, 3, 4, 6],
            [2, 4, 6, 8], [3, 4, 6, 8], [1, 5, 5, 3]
        ]
        
        equations = []
        for _ in range(count):
            if difficulty != "hard" and random.random() < 0.5:
                numbers = random.choice(solvable_sets)
            else:
                numbers = [random.choice(num_range) for _ in range(4)]
            
            equations.append({
                "numbers": numbers,
                "target": 24
            })
        
        return {
            "equations": equations,
            "target": 24
        }

    @staticmethod
    def generate_chess(board_type: str, board_size: int = 8) -> Dict[str, Any]:
        """生成棋类游戏"""
        instructions = CHESS_INSTRUCTIONS.get(board_type, CHESS_INSTRUCTIONS["checkers"])
        
        grid = [[0 for _ in range(board_size)] for _ in range(board_size)]
        
        if board_type == "chess":
            grid[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
            grid[1] = ['p'] * board_size
            grid[-2] = ['P'] * board_size
            grid[-1] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        elif board_type == "checkers":
            for i in range(board_size):
                for j in range(board_size):
                    if (i + j) % 2 == 1:
                        if i < 3:
                            grid[i][j] = 1
                        elif i > board_size - 4:
                            grid[i][j] = 2
        elif board_type == "xiangqi":
            pass
        elif board_type == "go":
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
    def generate_parent_child_games(
        game_types: List[str], 
        card_count: int = 6
    ) -> Dict[str, Any]:
        """生成亲子类游戏
        
        Args:
            game_types: 游戏类型列表
            card_count: 生成卡片数量 (6, 8, 10)
        """
        cards = {}
        common_instructions = ""
        
        # 为每个游戏类型生成卡片
        for game_type in game_types:
            if game_type in PARENT_CHILD_GAMES:
                game_info = PARENT_CHILD_GAMES[game_type]
                common_instructions = game_info["instructions"]
                
                if game_type == "simon_says":
                    actions = game_info["actions"]
                    for i in range(min(card_count, len(actions))):
                        cards[f"卡片{i+1}"] = actions[i]
                
                elif game_type == "who_is_undercover":
                    word_pairs = game_info["word_pairs"]
                    for i in range(min(card_count, len(word_pairs))):
                        pair = word_pairs[i]
                        cards[f"卡片{i+1}"] = f"词语 A：{pair['a']}\n词语 B：{pair['b']}"
                
                elif game_type == "reverse_command":
                    commands = game_info["commands"]
                    for i in range(min(card_count, len(commands))):
                        cmd = commands[i]
                        # 生成相反指令（不使用反斜杠，使用换行）
                        reverse_map = {
                            "向前": "向后", "向后": "向前",
                            "左": "右", "右": "左",
                            "上": "下", "下": "上",
                            "举起": "放下", "睁开": "闭上", "站": "坐",
                            "举起右手": "放下左手", "举起左手": "放下右手",
                            "摸右耳朵": "摸左耳朵", "点头": "摇头",
                            "坐下": "站起来", "向左转": "向右转"
                        }
                        reverse_cmd = cmd
                        for k, v in reverse_map.items():
                            reverse_cmd = reverse_cmd.replace(k, v)
                        # 使用换行而不是反斜杠
                        cards[f"卡片{i+1}"] = f"指令：{cmd}\n反向：{reverse_cmd}"
                
                elif game_type == "number_game":
                    ranges = [(1, 100), (1, 50), (51, 100), (51, 150), (1, 200), (1, 30)]
                    for i in range(card_count):
                        min_num, max_num = ranges[i % len(ranges)]
                        target = random.randint(min_num, max_num)
                        cards[f"卡片{i+1}"] = f"范围：{min_num} - {max_num}\n目标数字：{target}"
                
                elif game_type == "gesture_game":
                    suggestions = game_info["suggestions"]
                    for i in range(min(card_count, len(suggestions))):
                        cards[f"卡片{i+1}"] = f"起始动作：{suggestions[i]}"
                
                elif game_type == "memory_game":
                    items_list = ITEMS_LIST
                    for i in range(card_count):
                        items = items_list[i % len(items_list)]
                        items_text = "、".join(items)
                        cards[f"卡片{i+1}"] = f"记忆物品：\n{items_text}"
                
                elif game_type == "blank_card":
                    # 空白卡片：全部生成空白卡片
                    for i in range(card_count):
                        cards[f"卡片{i+1}"] = ""  # 空白内容
        
        return {
            "cards": cards,
            "common_instructions": common_instructions,
            "total": len(cards)
        }

    @staticmethod
    def get_parent_child_game_types() -> List[Dict[str, Any]]:
        """获取亲子类游戏类型"""
        return [
            {"type": "simon_says", "name": "西蒙说", "icon": "🗣️"},
            {"type": "who_is_undercover", "name": "谁是卧底", "icon": "🕵️"},
            {"type": "reverse_command", "name": "反向指令", "icon": "↔️"},
            {"type": "number_game", "name": "数字炸弹", "icon": "💣"},
            {"type": "gesture_game", "name": "动作接龙", "icon": "🤸"},
            {"type": "memory_game", "name": "记忆大王", "icon": "🧠"},
            {"type": "blank_card", "name": "空白卡片", "icon": "📝"}
        ]

    @staticmethod
    def get_game_types_by_age_group(age_group: str) -> Dict[str, Any]:
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
        else:
            return {"title": "全部游戏", "games": []}

    @staticmethod
    def get_all_game_categories() -> List[Dict[str, Any]]:
        """获取所有游戏分类"""
        return [
            {"id": "low", "name": "低龄段", "description": "6-8岁", "icon": "👶"},
            {"id": "mid", "name": "中龄段", "description": "9-11岁", "icon": "🧒"},
            {"id": "high", "name": "高龄段", "description": "12岁以上", "icon": "🧑"},
            {"id": "chess", "name": "棋类游戏", "description": "各种棋盘", "icon": "♟️"},
            {"id": "parent_child", "name": "亲子类游戏", "description": "家庭互动", "icon": "👨‍👩‍👧‍👦"}
        ]

    @staticmethod
    def get_chess_types() -> List[Dict[str, Any]]:
        """获取棋类游戏类型"""
        return [
            {"type": "go", "name": "围棋", "icon": "⚫", "sizes": [9, 13, 19]},
            {"type": "chess", "name": "国际象棋", "icon": "♔"},
            {"type": "xiangqi", "name": "中国象棋", "icon": "♟"}
        ]

    @staticmethod
    def generate_chess_pieces(chess_type: str, board_size: int = 19) -> Dict[str, Any]:
        """生成棋子"""
        pieces = {}
        total_count = 0
        title = ""
        
        if chess_type == "go":
            total_positions = board_size * board_size
            half_count = total_positions // 2
            pieces["black"] = [{"id": i + 1, "type": "black"} for i in range(half_count)]
            pieces["white"] = [{"id": i + 1, "type": "white"} for i in range(half_count)]
            total_count = len(pieces["black"]) + len(pieces["white"])
            title = f"围棋棋子 ({board_size}×{board_size})"
            
        elif chess_type == "chess":
            white_pieces = []
            for i in range(8):
                white_pieces.append({"id": i + 1, "type": "pawn", "symbol": "♙", "name": "兵"})
            for i in range(2):
                white_pieces.append({"id": len(white_pieces) + 1, "type": "knight", "symbol": "♘", "name": "马"})
                white_pieces.append({"id": len(white_pieces) + 1, "type": "bishop", "symbol": "♗", "name": "象"})
            for i in range(2):
                white_pieces.append({"id": len(white_pieces) + 1, "type": "rook", "symbol": "♖", "name": "车"})
            white_pieces.append({"id": len(white_pieces) + 1, "type": "queen", "symbol": "♕", "name": "后"})
            white_pieces.append({"id": len(white_pieces) + 1, "type": "king", "symbol": "♔", "name": "王"})
            
            black_pieces = []
            for i in range(8):
                black_pieces.append({"id": i + 1, "type": "pawn", "symbol": "♟", "name": "兵"})
            for i in range(2):
                black_pieces.append({"id": len(black_pieces) + 1, "type": "knight", "symbol": "♞", "name": "马"})
                black_pieces.append({"id": len(black_pieces) + 1, "type": "bishop", "symbol": "♝", "name": "象"})
            for i in range(2):
                black_pieces.append({"id": len(black_pieces) + 1, "type": "rook", "symbol": "♜", "name": "车"})
            black_pieces.append({"id": len(black_pieces) + 1, "type": "queen", "symbol": "♛", "name": "后"})
            black_pieces.append({"id": len(black_pieces) + 1, "type": "king", "symbol": "♚", "name": "王"})
            
            pieces["white"] = white_pieces
            pieces["black"] = black_pieces
            total_count = len(pieces["white"]) + len(pieces["black"])
            title = "国际象棋棋子"
            
        elif chess_type == "xiangqi":
            red_pieces = []
            for i in range(5):
                red_pieces.append({"id": i + 1, "type": "soldier", "symbol": "兵", "name": "兵"})
            for i in range(2):
                red_pieces.append({"id": len(red_pieces) + 1, "type": "cannon", "symbol": "炮", "name": "炮"})
                red_pieces.append({"id": len(red_pieces) + 1, "type": "horse", "symbol": "马", "name": "马"})
                red_pieces.append({"id": len(red_pieces) + 1, "type": "chariot", "symbol": "车", "name": "车"})
                red_pieces.append({"id": len(red_pieces) + 1, "type": "elephant", "symbol": "相", "name": "相"})
                red_pieces.append({"id": len(red_pieces) + 1, "type": "advisor", "symbol": "仕", "name": "仕"})
            red_pieces.append({"id": len(red_pieces) + 1, "type": "general", "symbol": "帅", "name": "帅"})
            
            black_pieces = []
            for i in range(5):
                black_pieces.append({"id": i + 1, "type": "soldier", "symbol": "卒", "name": "卒"})
            for i in range(2):
                black_pieces.append({"id": len(black_pieces) + 1, "type": "cannon", "symbol": "炮", "name": "炮"})
                black_pieces.append({"id": len(black_pieces) + 1, "type": "horse", "symbol": "马", "name": "马"})
                black_pieces.append({"id": len(black_pieces) + 1, "type": "chariot", "symbol": "车", "name": "车"})
                black_pieces.append({"id": len(black_pieces) + 1, "type": "elephant", "symbol": "象", "name": "象"})
                black_pieces.append({"id": len(black_pieces) + 1, "type": "advisor", "symbol": "士", "name": "士"})
            black_pieces.append({"id": len(black_pieces) + 1, "type": "general", "symbol": "将", "name": "将"})
            
            pieces["red"] = red_pieces
            pieces["black"] = black_pieces
            total_count = len(pieces["red"]) + len(pieces["black"])
            title = "中国象棋棋子"
        
        return {
            "chess_type": chess_type,
            "board_size": board_size,
            "pieces": pieces,
            "title": title,
            "total_count": total_count
        }
