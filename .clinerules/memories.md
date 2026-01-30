# Educational Game Domain
- 开发儿童益智游戏平台，游戏需支持按年龄分级（低中高龄）和打印离线使用，旨在减少屏幕时间保护视力。

# Game Mechanics
- 成语及英语单词接龙游戏需遵循字/字母重叠规则，采用横竖交叉的网格布局，非纯横向排列，且支持自定义生成数量。
- 亲子类游戏需生成至少6张游戏卡牌，且卡牌题目选项必须限定为单选形式。
- 记忆类游戏需生成6张卡片，且每张卡片的内容应包含6个具体物品。
- Sudoku games: 4-grid generates 3 horizontal items, 6-grid generates 2 horizontal items; for printing, grids must fit one page (smaller), hide bottom text, and pagination for reference answers.

# UI/UX
- 成语接龙和单词接龙游戏中，隐藏的字或字母必须显示边框以保持布局结构可见。
- 游戏棋盘格子的高宽比应严格设置为1.414:1，以适配打印需求。
- Puzzle游戏中4宫格和6宫格的小格子应填满大格子宽度，不留空白间距。
- 围棋棋盘宽度至少占页面三分之二；打印时隐藏规则说明，背景黄色调需更淡。
- Cells in Idiom and English Word Solitaire games should have equal width and height (square shape).
- PuzzleGames.vue中的UI标签文字（如“生成数量”、“棋盘大小”）颜色需与背景形成高对比度以确保清晰可见。

# Code Style
- 将 frontend/src/views 目录下 Vue 文件内联样式拆分为独立文件以提高代码可维护性。
