"""益智游戏服务"""
import random
from typing import List, Dict, Any, Optional

# 从外部文件导入游戏数据
from ..data.game_data import (
    IDIOMS, WORDS, PARENT_CHILD_GAMES, 
    CHESS_INSTRUCTIONS, ITEMS_LIST,
    SUDOKU_TEMPLATES, SUDOKU_EMPTY_CELLS,
    POINT24_SOLVABLE_SETS, CHESS_PIECES, XIANGQI_PIECES,
    GO_STAR_POINTS, CHAIN_GRID_SIZES,
    POINT24_NUM_RANGES, NUMBER_GAME_RANGES
)

# 成语数据库 - 引用外部数据
GameIdioms = IDIOMS
GameWords = WORDS
GameParentChildGames = PARENT_CHILD_GAMES
GameChessInstructions = CHESS_INSTRUCTIONS
GameSudokuTemplates = SUDOKU_TEMPLATES
GameSudokuEmptyCells = SUDOKU_EMPTY_CELLS
GamePoint24Sets = POINT24_SOLVABLE_SETS
GameChessPieces = CHESS_PIECES
GameGoStarPoints = GO_STAR_POINTS
GameChainGridSizes = CHAIN_GRID_SIZES


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
            
            # 使用外部数据中的网格大小映射
            size_mapping = CHAIN_GRID_SIZES.get("idiom", {})
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
            
            # 使用外部数据中的网格大小映射
            size_mapping = CHAIN_GRID_SIZES.get("word", {})
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
    def generate_sudoku(size: int = 9, difficulty: str = "normal",
                       count: Optional[int] = None) -> Dict[str, Any]:
        """生成数独游戏
        
        Args:
            size: 网格大小 (4/6/9)
            difficulty: 难度级别 (easy/normal/hard)
            count: 生成数量，默认4宫格4个、6宫格2个、9宫格1个
        """
        if count is not None:
            num_puzzles = count
        elif size == 9:
            num_puzzles = 1
        else:
            num_puzzles = 2
        
        puzzles = []
        
        # 使用外部数据中的模板
        base_4x4 = SUDOKU_TEMPLATES.get("4x4", [])
        base_6x6 = SUDOKU_TEMPLATES.get("6x6", [])
        base_9x9 = SUDOKU_TEMPLATES.get("9x9", [])
        
        # 使用外部数据中的空格数配置
        empty_cells_config = SUDOKU_EMPTY_CELLS
        
        for i in range(num_puzzles):
            if size == 4:
                size_key = "4x4"
                empty_cells = empty_cells_config[size_key].get(difficulty, 4)
                solution = [[(num + i) % 4 + 1 for num in row] for row in base_4x4]
            elif size == 6:
                size_key = "6x6"
                empty_cells = empty_cells_config[size_key].get(difficulty, 15)
                solution = [[(num + i) % 6 + 1 for num in row] for row in base_6x6]
            else:
                size_key = "9x9"
                empty_cells = empty_cells_config[size_key].get(difficulty, 40)
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
        # 使用外部数据中的24点可解集合
        num_ranges = POINT24_NUM_RANGES
        num_range = num_ranges.get(difficulty, range(1, 10))
        solvable_sets = POINT24_SOLVABLE_SETS
        
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
        
        grid = []
        river_pos = -1  # 楚河汉界位置（仅用于中国象棋）
        rows = 0
        cols = 0
        
        # 根据棋类类型生成棋盘
        if board_type == "chess":
            # 国际象棋：8x8黑白相间方格
            rows = 8
            cols = 8
            grid = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    # 黑白相间：(i + j) 为偶数是白格(0)，奇数是黑格(1)
                    row.append(0 if (i + j) % 2 == 0 else 1)
                grid.append(row)
            
        elif board_type == "checkers":
            # 国际跳棋：board_size x board_size
            rows = board_size
            cols = board_size
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    if (i + j) % 2 == 1:
                        if i < 3:
                            grid[i][j] = 1
                        elif i > rows - 4:
                            grid[i][j] = 2
                            
        elif board_type == "xiangqi":
            # 中国象棋：8列9行，第5行（索引4）为楚河汉界（合并为一格）
            rows = 9
            cols = 8
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            # 第5行（索引4）设为特殊值-1，表示楚河汉界（需要合并）
            grid[4] = [-1] * cols  # 用-1标记楚河汉界行
            river_pos = 5  # 楚河汉界在第5行之后（索引4和5之间）
            
        elif board_type == "go":
            # 围棋：board_size x board_size 方格
            rows = board_size
            cols = board_size
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            star_points = GO_STAR_POINTS.get(board_size, [])
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
            "board_size": cols,  # 棋盘列数
            "rows": rows,  # 棋盘行数
            "grid": grid,
            "river_pos": river_pos,  # 楚河汉界位置（仅中国象棋使用）
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
                    # 随机选择动作
                    selected_actions = random.sample(actions, min(card_count, len(actions)))
                    # 如果卡片数量超过动作列表，则循环随机添加
                    while len(selected_actions) < card_count:
                        selected_actions.extend(random.sample(actions, min(card_count - len(selected_actions), len(actions))))
                    for i in range(card_count):
                        cards[f"卡片{i+1}"] = selected_actions[i]
               
                elif game_type == "who_is_undercover":
                    word_pairs = game_info["word_pairs"]
                    # 随机选择词语对
                    selected_pairs = random.sample(word_pairs, min(card_count, len(word_pairs)))
                    # 如果卡片数量超过词语对列表，则循环随机添加
                    while len(selected_pairs) < card_count:
                        selected_pairs.extend(random.sample(word_pairs, min(card_count - len(selected_pairs), len(word_pairs))))
                    for i in range(card_count):
                        pair = selected_pairs[i]
                        cards[f"卡片{i+1}"] = f"词语 A：{pair['a']}\n词语 B：{pair['b']}"
               
                elif game_type == "reverse_command":
                    command_pairs = game_info["command_pairs"]
                    # 随机选择指令对
                    selected_pairs = random.sample(command_pairs, min(card_count, len(command_pairs)))
                    # 如果卡片数量超过指令对列表，则循环随机添加
                    while len(selected_pairs) < card_count:
                        selected_pairs.extend(random.sample(command_pairs, min(card_count - len(selected_pairs), len(command_pairs))))
                    for i in range(card_count):
                        pair = selected_pairs[i]
                        cards[f"卡片{i+1}"] = f"指令：{pair['original']}\n反向：{pair['reverse']}"
               
                elif game_type == "number_game":
                    # 使用外部数据中的数字范围配置
                    ranges = NUMBER_GAME_RANGES
                    for i in range(card_count):
                        min_num, max_num = ranges[i % len(ranges)]
                        target = random.randint(min_num, max_num)
                        cards[f"卡片{i+1}"] = f"范围：{min_num} - {max_num}\n目标数字：{target}"
               
                elif game_type == "gesture_game":
                    suggestions = game_info["suggestions"]
                    # 随机选择建议
                    selected_suggestions = random.sample(suggestions, min(card_count, len(suggestions)))
                    # 如果卡片数量超过建议列表，则循环随机添加
                    while len(selected_suggestions) < card_count:
                        selected_suggestions.extend(random.sample(suggestions, min(card_count - len(selected_suggestions), len(suggestions))))
                    for i in range(card_count):
                        suggestion = selected_suggestions[i]
                        cards[f"卡片{i+1}"] = f"起始动作：{suggestion}"
                
                elif game_type == "memory_game":
                    items_list = ITEMS_LIST
                    # 随机选择物品组
                    selected_items = random.sample(items_list, min(card_count, len(items_list)))
                    # 如果卡片数量超过物品组列表，则循环随机添加
                    while len(selected_items) < card_count:
                        selected_items.extend(random.sample(items_list, min(card_count - len(selected_items), len(items_list))))
                    for i in range(card_count):
                        items = selected_items[i]
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
            # 使用外部数据中的国际象棋棋子定义
            pieces = CHESS_PIECES.copy()
            total_count = len(pieces["white"]) + len(pieces["black"])
            title = "国际象棋棋子"
            
        elif chess_type == "xiangqi":
            # 使用外部数据中的中国象棋棋子定义
            pieces = XIANGQI_PIECES.copy()
            total_count = len(pieces["red"]) + len(pieces["black"])
            title = "中国象棋棋子"
        
        return {
            "chess_type": chess_type,
            "board_size": board_size,
            "pieces": pieces,
            "title": title,
            "total_count": total_count
        }
