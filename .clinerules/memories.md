# Educational Game Domain
- 开发儿童益智游戏平台，游戏需支持按年龄分级（低中高龄）和打印离线使用，旨在减少屏幕时间保护视力。

# Game Mechanics
- 成语及英语单词接龙游戏需遵循字/字母重叠规则，采用横竖交叉的网格布局，非纯横向排列，且支持自定义生成数量。
- 亲子类游戏生成的卡牌数量需严格匹配用户选择的参数（如8张或10张），而非固定生成6张，题目选项仍需限定为单选。
- 记忆类游戏需生成6张卡片，且每张卡片的内容应包含6个具体物品。
- Sudoku games: 4-grid generates 3 horizontal items, 6-grid generates 2 horizontal items; for printing, grids must fit one page (smaller), hide bottom text, and pagination for reference answers.
- 棋类游戏需支持生成全套棋子，围棋数量按棋盘大小计算（半黑半白），国际象棋及象棋需包含所有标准棋子。
- Blank card generation should be treated as a distinct game category (similar to Memory King), not a simple option.
- 24点游戏需生成6个等式，采用每列一个式子的布局，数字与答案在同一行显示，且需增加数字之间的间距。

# UI/UX
- 成语接龙和单词接龙游戏中，隐藏的字或字母必须显示边框以保持布局结构可见。
- 游戏棋盘格子的高宽比应严格设置为1.414:1，以适配打印需求。
- Puzzle游戏中4宫格和6宫格的小格子应填满大格子宽度，不留空白间距。
- Go board width must be at least 2/3 of the page; in print mode, hide rule descriptions, remaining piece count text (e.g., 'remaining black pieces'), and use a lighter yellow background.
- Cells in Idiom and English Word Solitaire games should have equal width and height (square shape).
- PuzzleGames.vue中的UI标签文字（如“生成数量”、“棋盘大小”）颜色需与背景形成高对比度以确保清晰可见。
- 棋牌类及非棋牌类游戏规则样式需保持一致，且在打印模式下统一隐藏。
- PuzzleGames.vue 组件中的棋盘规则说明在打印模式下必须保持隐藏状态。
- Chess game pieces should be rendered at double their original size.
- Go game pieces should not display text labels on them.
- International chess black pieces should not be pure black; styling must be adjusted (e.g., using dark grey) to ensure internal patterns are visible.
- 所有棋类游戏棋子的边框需设计为虚线样式，以便于用户打印后进行手工剪裁。
- 在PuzzleGames.vue中，数字炸弹游戏和反向指令必须使用不同的图标进行区分，避免混淆。
- Card game styles should be simplified to avoid overly fancy or decorative designs.
- 亲子类游戏（如西蒙说）的生成按钮需置于各自游戏标题下方（类成语接龙风格），按钮样式为白框、选中显示勾选、隐藏统计文字；生成数量控件置于大类标题下方。
- 亲子类游戏生成的卡牌文字需加粗加黑加大，且需美化卡片边框样式。
- International Chess (8x8) and Chinese Chess (9x10) boards require larger grid cells and wider spacing between pieces.
- Board games (Go 13x13, 9x9, 19x19) must display complete grid lines including both horizontal and vertical lines, and maintain proper layout to avoid excessive row generation or page overflow.

# Code Style
- 将 frontend/src/views 目录下 Vue 文件内联样式拆分为独立文件以提高代码可维护性。
