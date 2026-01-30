<template>
  <div class="puzzle-games">
    <div class="header">
      <h1>🎮 益智游戏中心 🎮</h1>
      <p>远离电子产品，保护眼睛，在纸上快乐学习</p>
      <router-link to="/" class="back-link">← 返回首页</router-link>
    </div>

    <!-- 分类选择 -->
    <div class="section">
      <h2>选择游戏分类</h2>
      <div class="categories-grid">
        <div
          v-for="category in categories"
          :key="category.id"
          :class="['category-card', { active: selectedCategory === category.id }]"
          @click="selectCategory(category.id)"
        >
          <span class="category-icon">{{ category.icon }}</span>
          <div class="category-info">
            <h3>{{ category.name }}</h3>
            <p>{{ category.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 年龄段游戏选择 -->
    <div v-if="selectedCategory && ['low', 'mid', 'high'].includes(selectedCategory)" class="section">
      <h2>{{ getAgeTitle() }}</h2>
      
      <!-- 生成数量选择 -->
      <div class="count-selector">
        <span class="count-label">生成数量：</span>
        <button
          v-for="count in [5, 10, 15, 20]"
          :key="count"
          :class="['count-btn', { active: selectedCount === count }]"
          @click="selectedCount = count"
        >
          {{ count }}个
        </button>
      </div>
      
      <div class="games-grid">
        <div
          v-for="game in currentGames"
          :key="game.type"
          class="game-card"
        >
          <span class="game-icon">{{ game.icon }}</span>
          <h3>{{ game.name }}</h3>
          <button class="play-btn" @click="generateGame(game, selectedCategory)">
            生成游戏
          </button>
        </div>
      </div>
    </div>

    <!-- 棋类游戏选择 -->
    <div v-if="selectedCategory === 'chess'" class="section">
      <h2>♟️ 棋类游戏</h2>
      <div class="games-grid">
        <div
          v-for="chess in chessTypes"
          :key="chess.type"
          class="game-card"
        >
          <span class="game-icon">{{ chess.icon }}</span>
          <h3>{{ chess.name }}</h3>
          <div v-if="chess.sizes" class="size-selector">
            <span>棋盘大小：</span>
            <button
              v-for="size in chess.sizes"
              :key="size"
              :class="['size-btn', { active: selectedChessSize === size }]"
              @click="selectedChessSize = size"
            >
              {{ size }}×{{ size }}
            </button>
          </div>
          <div class="chess-actions">
            <button class="play-btn" @click="handleGenerateChess(chess)">
              生成棋盘
            </button>
            <button class="play-btn secondary" @click="handleGenerateChessPieces(chess)">
              生成棋子
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 亲子类游戏选择 -->
    <div v-if="selectedCategory === 'parent_child'" class="section">
      <h2>👨‍👩‍👧‍👦 亲子类游戏 - 单选一个游戏类型</h2>
      <div class="games-grid">
        <div
          v-for="game in parentChildTypes"
          :key="game.type"
          :class="['game-card', { selected: selectedParentGame === game.type }]"
          @click="selectParentGame(game.type)"
        >
          <span class="game-icon">{{ game.icon }}</span>
          <h3>{{ game.name }}</h3>
          <span class="check-mark" v-if="selectedParentGame === game.type">✓</span>
        </div>
      </div>
      <button class="generate-btn" @click="handleGenerateParentChild">
        生成游戏卡片 (至少6张)
      </button>
    </div>

    <!-- 游戏预览区域 -->
    <div v-if="gameContent" class="game-preview section">
      <div class="preview-header">
        <h2>{{ gameTitle }}</h2>
        <div class="preview-actions">
          <button class="action-btn" @click="regenerateGame">
            🔄 重新生成
          </button>
          <button class="action-btn primary" @click="printGame">
            🖨️ 打印
          </button>
        </div>
      </div>

      <!-- 成语接龙/单词接龙字谜网格 -->
      <div v-if="gameContent.grid && gameContent.chain" class="word-puzzle-game">
        <!-- 统一的游戏规则 -->
        <div class="common-rules">
          <h3>📋 游戏规则</h3>
          <div class="rules-content">
            <p><strong>难度：</strong>{{ gameContent.difficulty }}</p>
            <p><strong>数量：</strong>{{ gameContent.chain_length }}个词</p>
            <p><strong>游戏说明：</strong>字/字母在交叉点重叠，找出所有隐藏的成语/单词</p>
            <p><strong>玩法：</strong>根据给定的字谜网格，找到所有隐藏的成语或单词。每个词都通过字或字母的重叠与其他词连接，形成交叉的接龙结构。</p>
          </div>
        </div>
        
        <!-- 字谜网格 -->
        <div class="puzzle-grid">
          <div
            v-for="(row, rowIndex) in gameContent.grid"
            :key="rowIndex"
            class="puzzle-row"
          >
            <div
              v-for="(cell, cellIndex) in row"
              :key="cellIndex"
              :class="getPuzzleCellClass(rowIndex, cellIndex, cell)"
            >
              {{ cell }}
            </div>
          </div>
        </div>
        
        <!-- 答案提示 -->
        <div class="answer-hint">
          <button class="toggle-answer-btn" @click="showChainAnswer = !showChainAnswer">
            {{ showChainAnswer ? '隐藏答案' : '查看答案' }}
          </button>
          <div v-if="showChainAnswer" class="answer-list">
            <h4>隐藏的词语：</h4>
            <ul>
              <li v-for="(item, index) in gameContent.chain" :key="index">
                <strong>{{ item.word }}</strong>
                <span class="position-hint">
                  ({{ item.direction === 'horizontal' ? '横' : '竖' }}: 第{{ (item.row ?? 0) + 1 }}行, 第{{ (item.col ?? 0) + 1 }}列)
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 数独（支持多个谜题并排） -->
      <div v-if="gameContent.puzzles && gameContent.size" class="sudoku-container">
        <!-- 统一的游戏规则 -->
        <div class="common-rules">
          <h3>📋 游戏规则</h3>
          <div class="rules-content">
            <p><strong>大小：</strong>{{ gameContent.size }}×{{ gameContent.size }}</p>
            <p><strong>难度：</strong>{{ gameContent.difficulty }}</p>
            <p><strong>数量：</strong>{{ gameContent.count }}个（答案在下方）</p>
            <p><strong>游戏说明：</strong>在空格中填入1-{{ gameContent.size }}的数字，使每行、每列以及每个宫内的数字都不重复。{{ gameContent.size === 4 ? '4宫格：2×2的宫格' : gameContent.size === 6 ? '6宫格：2×3的宫格' : '9宫格：3×3的宫格' }}</p>
          </div>
        </div>
        
        <!-- 谜题区域（并排排列） -->
        <div class="puzzles-row">
          <div 
            v-for="(puzzle, puzzleIndex) in gameContent.puzzles" 
            :key="puzzleIndex"
            class="puzzle-item"
          >
            <div class="puzzle-number" v-if="(gameContent.count ?? 0) > 1">#{{ puzzleIndex + 1 }}</div>
              <div class="sudoku-board" :class="`size-${gameContent.size} small`">
                <div
                  v-for="(row, rowIndex) in puzzle.grid"
                  :key="rowIndex"
                  class="sudoku-row"
                >
                  <div
                    v-for="(cell, cellIndex) in row"
                    :key="cellIndex"
                    :class="['sudoku-cell', {
                      'border-thick-right': shouldHaveThickBorder(Number(gameContent.size), cellIndex, 'right'),
                      'border-thick-bottom': shouldHaveThickBorder(Number(gameContent.size), rowIndex, 'bottom')
                    }]"
                  >
                    {{ typeof cell === 'number' && cell > 0 ? cell : '' }}
                  </div>
                </div>
              </div>
          </div>
        </div>
        
        <!-- 答案区域 -->
        <div v-if="showSolution" class="answers-section">
          <h4 style="text-align: center;">参考答案</h4>
          <div class="puzzles-row">
            <div 
              v-for="(puzzle, puzzleIndex) in gameContent.puzzles" 
              :key="`answer-${puzzleIndex}`"
              class="puzzle-item"
            >
              <div class="puzzle-number" v-if="(gameContent.count ?? 0) > 1">#{{ puzzleIndex + 1 }}</div>
              <div class="sudoku-board" :class="`size-${gameContent.size} small`">
                <div
                  v-for="(row, rowIndex) in puzzle.solution"
                  :key="`sol-${puzzleIndex}-${rowIndex}`"
                  class="sudoku-row"
                >
                  <div
                    v-for="(cell, cellIndex) in row"
                    :key="`sol-${puzzleIndex}-${rowIndex}-${cellIndex}`"
                    :class="['sudoku-cell', {
                      'border-thick-right': shouldHaveThickBorder(Number(gameContent.size!), cellIndex, 'right'),
                      'border-thick-bottom': shouldHaveThickBorder(Number(gameContent.size!), rowIndex, 'bottom')
                    }]"
                  >
                    {{ cell }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button class="toggle-solution-btn" @click="showSolution = !showSolution">
          {{ showSolution ? '隐藏答案' : '显示答案' }}
        </button>
      </div>

      <!-- 24点 -->
      <div v-if="gameContent.numbers" class="point24-game">
        <!-- 统一的游戏规则 -->
        <div class="common-rules">
          <h3>📋 游戏规则</h3>
          <div class="rules-content">
            <p><strong>目标：</strong>将四个数字通过运算得到结果 24</p>
            <p><strong>运算符：</strong>使用加（+）、减（-）、乘（×）、除（÷）和括号</p>
            <p><strong>规则：</strong>每个数字必须使用一次且只能使用一次</p>
            <p v-if="gameContent.solutions && gameContent.solutions.length > 0"><strong>提示示例：</strong>{{ gameContent.solutions[0] }}</p>
          </div>
        </div>
        
        <div class="numbers-container">
          <div class="numbers-display">
            <div v-for="(num, index) in gameContent.numbers" :key="index" class="number-card">
              {{ num }}
            </div>
          </div>
          <div class="target-display">
            = {{ gameContent.target }}
          </div>
        </div>
      </div>

      <!-- 棋类棋盘 -->
      <div v-if="gameContent.board_type" class="chess-game">
        <!-- 统一的游戏规则 -->
        <div class="common-rules">
          <h3>📋 游戏规则</h3>
          <div class="rules-content">{{ gameContent.instructions }}</div>
        </div>
        <div class="chess-board" :class="`size-${gameContent.board_size}`">
          <div
            v-for="(row, rowIndex) in gameContent.grid"
            :key="rowIndex"
            class="chess-row"
          >
            <div
              v-for="(cell, cellIndex) in row"
              :key="cellIndex"
              :class="['chess-cell', { 'has-star': hasStarPoint(rowIndex, cellIndex) }]"
            >
            <span v-if="hasStarPoint(rowIndex, cellIndex)" class="star-point">●</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 棋类棋子 -->
      <div v-if="gameContent.chess_type && gameContent.pieces" class="chess-pieces">
        <div class="pieces-header">
          <h3>{{ gameContent.title }}</h3>
          <p class="pieces-info">共生成 {{ gameContent.total_count }} 个棋子</p>
        </div>
        
        <div class="pieces-container">
          <!-- 围棋棋子 -->
          <div v-if="gameContent.chess_type === 'go'" class="go-pieces">
            <div class="piece-group">
              <h4>黑棋 ({{ (gameContent.pieces as any).black?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).black?.slice(0, 50)" 
                  :key="'black-'+index"
                  class="go-piece black"
                ></div>
              </div>
              <p v-if="(gameContent.pieces as any).black?.length > 50" class="more-pieces">... 还有 {{ (gameContent.pieces as any).black.length - 50 }} 个黑棋</p>
            </div>
            <div class="piece-group">
              <h4>白棋 ({{ (gameContent.pieces as any).white?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).white?.slice(0, 50)" 
                  :key="'white-'+index"
                  class="go-piece white"
                ></div>
              </div>
              <p v-if="(gameContent.pieces as any).white?.length > 50" class="more-pieces">... 还有 {{ (gameContent.pieces as any).white.length - 50 }} 个白棋</p>
            </div>
          </div>

          <!-- 国际象棋棋子 -->
          <div v-if="gameContent.chess_type === 'chess'" class="chess-model-pieces">
            <div class="piece-group">
              <h4>白棋 ({{ (gameContent.pieces as any).white?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).white" 
                  :key="'white-'+index"
                  class="chess-model-piece white"
                  :title="piece.name"
                >
                  {{ piece.symbol }}
                </div>
              </div>
            </div>
            <div class="piece-group">
              <h4>黑棋 ({{ (gameContent.pieces as any).black?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).black" 
                  :key="'black-'+index"
                  class="chess-model-piece black"
                  :title="piece.name"
                >
                  {{ piece.symbol }}
                </div>
              </div>
            </div>
          </div>

          <!-- 中国象棋棋子 -->
          <div v-if="gameContent.chess_type === 'xiangqi'" class="xiangqi-pieces">
            <div class="piece-group">
              <h4>红棋 ({{ (gameContent.pieces as any).red?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).red" 
                  :key="'red-'+index"
                  class="xiangqi-piece red"
                  :title="piece.name"
                >
                  {{ piece.symbol }}
                </div>
              </div>
            </div>
            <div class="piece-group">
              <h4>黑棋 ({{ (gameContent.pieces as any).black?.length || 0 }})</h4>
              <div class="piece-grid">
                <div 
                  v-for="(piece, index) in (gameContent.pieces as any).black" 
                  :key="'black-'+index"
                  class="xiangqi-piece black"
                  :title="piece.name"
                >
                  {{ piece.symbol }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 亲子类游戏卡片 -->
      <div v-if="gameContent.cards && typeof gameContent.cards === 'object'" class="parent-child-game">
        <!-- 统一的游戏规则 -->
        <div class="common-rules">
          <h3>📋 游戏规则</h3>
          <div class="rules-content">{{ (gameContent as any).common_instructions }}</div>
        </div>
        
        <!-- 卡片信息 -->
        <div class="cards-info">
          <p>共生成 {{ gameContent.total }} 张游戏卡片</p>
        </div>
        
        <!-- 卡片网格 -->
        <div class="cards-grid">
          <div 
            v-for="(entry, index) in Object.entries((gameContent as any).cards)" 
            :key="index" 
            class="game-card-item"
          >
            <div class="card-number">{{ index + 1 }}</div>
            <div class="card-content">{{ entry[1] }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import {
  getGameCategories,
  getGamesByAgeGroup,
  getChessTypes,
  getParentChildTypes,
  generateIdiomChain,
  generateWordChain,
  generateSudoku,
  generatePoint24 as generatePoint24Api,
  generateChess as generateChessApi,
  generateChessPieces as generateChessPiecesApi,
  generateParentChildGames as generateParentChildGamesApi,
  type GameCategory,
  type GameType,
  type GameState
} from '@/api/games'
import './PuzzleGames.css'

// 状态管理
const categories = ref<GameCategory[]>([])
const selectedCategory = ref<string>('')
const selectedCount = ref<number>(10)
const selectedChessSize = ref<number>(19)
const selectedParentGame = ref<string>('simon_says')
const currentGames = ref<GameType[]>([])
const chessTypes = ref<GameType[]>([])
const parentChildTypes = ref<GameType[]>([])
const gameContent = ref<GameState | null>(null)
const gameTitle = ref<string>('')
const showSolution = ref(false)
const showChainAnswer = ref(false)
const lastGameParams = ref<any>(null)

// 获取分类
onMounted(async () => {
  try {
    const cats = await getGameCategories()
    categories.value = cats.data.categories
  } catch (error) {
    console.error('获取分类失败:', error)
  }
})

// 选择分类
const selectCategory = async (categoryId: string) => {
  selectedCategory.value = categoryId
  gameContent.value = null

  if (['low', 'mid', 'high'].includes(categoryId)) {
    const result = await getGamesByAgeGroup(categoryId)
    currentGames.value = result.data.games
  } else if (categoryId === 'chess') {
    const result = await getChessTypes()
    chessTypes.value = result.data.chess_types
  } else if (categoryId === 'parent_child') {
    const result = await getParentChildTypes()
    parentChildTypes.value = result.data.game_types
  }
}

// 选择亲子游戏（单选模式）
const selectParentGame = (gameType: string) => {
  selectedParentGame.value = gameType
}

// 获取年龄段标题
const getAgeTitle = () => {
  const categoryMap: Record<string, string> = {
    low: '👶 低龄段游戏（6-8岁）',
    mid: '🧒 中龄段游戏（9-11岁）',
    high: '🧑 高龄段游戏（12岁以上）'
  }
  return categoryMap[selectedCategory.value] || ''
}

// 生成游戏
const generateGame = async (game: GameType, ageGroup: string) => {
  try {
    gameContent.value = null
    showSolution.value = false

    lastGameParams.value = { game, ageGroup }

    switch (game.type) {
      case 'idiom_chain':
        const idiomResult = await generateIdiomChain({ 
          age_group: ageGroup,
          chain_length: selectedCount.value 
        })
        gameContent.value = idiomResult.data
        gameTitle.value = '📝 成语接龙字谜'
        break

      case 'word_chain':
        const wordResult = await generateWordChain({ 
          age_group: ageGroup,
          chain_length: selectedCount.value 
        })
        gameContent.value = wordResult.data
        gameTitle.value = '🔤 单词接龙字谜'
        break

      case 'sudoku':
        const size = ageGroup === 'low' ? 4 : (ageGroup === 'mid' ? 6 : 9)
        const sudokuResult = await generateSudoku({ size })
        gameContent.value = sudokuResult.data
        gameTitle.value = '🔢 数独'
        break

      case 'point24':
        const point24Result = await generatePoint24Api({ difficulty: 'normal' })
        gameContent.value = point24Result.data
        gameTitle.value = '➕ 24点'
        break
    }

    setTimeout(() => {
      const preview = document.querySelector('.game-preview')
      if (preview) {
        preview.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('生成游戏失败:', error)
    alert('生成游戏失败，请重试')
  }
}

// 生成24点
const handleGeneratePoint24 = async () => {
  try {
    gameContent.value = null
    const result = await generatePoint24Api({})
    gameContent.value = result.data
    gameTitle.value = '➕ 24点'

    setTimeout(() => {
      const preview = document.querySelector('.game-preview')
      if (preview) {
        preview.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('生成24点失败:', error)
    alert('生成游戏失败，请重试')
  }
}

// 生成棋类游戏
const handleGenerateChess = async (chess: GameType) => {
  try {
    console.log('开始生成棋盘...')
    gameContent.value = null
    const size = selectedChessSize.value || chess.sizes?.[0] || 9
    console.log('棋盘大小:', size)
    
    const result = await generateChessApi({
      board_type: chess.type,
      board_size: size
    })
    console.log('后端返回数据:', result)
    console.log('游戏内容:', result.data)
    
    gameContent.value = result.data
    gameTitle.value = result.data.title || '棋盘'
    
    console.log('gameContent.value已设置:', gameContent.value)

    await nextTick()
    
    setTimeout(() => {
      const preview = document.querySelector('.game-preview')
      if (preview) {
        preview.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('生成棋盘失败:', error)
    alert('生成棋盘失败，请重试')
  }
}

// 生成棋子
const handleGenerateChessPieces = async (chess: GameType) => {
  try {
    console.log('开始生成棋子...')
    gameContent.value = null
    const size = selectedChessSize.value || chess.sizes?.[0] || 19
    console.log('棋类类型:', chess.type, '棋盘大小:', size)
    
    const result = await generateChessPiecesApi({
      chess_type: chess.type,
      board_size: chess.type === 'go' ? size : undefined
    })
    console.log('棋子生成结果:', result)
    
    gameContent.value = result.data
    gameTitle.value = result.data.title || '棋子'
    
    console.log('gameContent.value已设置:', gameContent.value)

    await nextTick()
    
    setTimeout(() => {
      const preview = document.querySelector('.game-preview')
      if (preview) {
        preview.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('生成棋子失败:', error)
    alert('生成棋子失败，请重试')
  }
}

// 生成亲子类游戏
const handleGenerateParentChild = async () => {
  try {
    gameContent.value = null
    const result = await generateParentChildGamesApi({
      game_types: [selectedParentGame.value]  // 单选：传递单个游戏类型的数组
    })
    gameContent.value = result.data
    gameTitle.value = '👨‍👩‍👧‍👦 亲子游戏卡片'

    setTimeout(() => {
      const preview = document.querySelector('.game-preview')
      if (preview) {
        preview.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('生成亲子游戏失败:', error)
    alert('生成游戏失败，请重试')
  }
}

// 重新生成游戏
const regenerateGame = () => {
  if (lastGameParams.value) {
    generateGame(lastGameParams.value.game, lastGameParams.value.ageGroup)
  }
}

// 打印游戏
const printGame = () => {
  window.print()
}

// 数独粗边框判断
const shouldHaveThickBorder = (size: number, index: number, direction: 'right' | 'bottom') => {
  if (size === 9) {
    return (index + 1) % 3 === 0 && index < size - 1
  } else if (size === 6) {
    return (index + 1) % 2 === 0 && index < size - 1
  } else if (size === 4) {
    return (index + 1) % 2 === 0 && index < size - 1
  }
  return false
}

// 判断是否有星位点
const hasStarPoint = (rowIndex: number, colIndex: number) => {
  if (gameContent.value?.star_points) {
    return gameContent.value.star_points.some((p: [number, number]) => p[0] === rowIndex && p[1] === colIndex)
  }
  return false
}

// 获取字谜格子的样式类
const getPuzzleCellClass = (rowIndex: number, cellIndex: number, cell: string) => {
  const classes: string[] = ['puzzle-cell']
  
  // 检查是否有字符
  const hasChar = cell !== '' && cell !== null && cell !== undefined
  if (hasChar) {
    classes.push('has-char')
  }
  
  // 检查是否是挖空位置
  if (gameContent.value?.chain && !hasChar) {
    const blankKey = `${rowIndex},${cellIndex}`
    const blankPositions: string[] = []
    
    gameContent.valforEach((item: any) => {
      const word = item.word
      const blanks = item.blanks || []
      const row = item.row ?? 0
      const col = item.col ?? 0
      const direction = item.direction || 'horizontal'
      
      blanks.forEach((isBlank: boolean, index: number) => {
        if (isBlank) {
          let posKey = ''
          if (direction === 'horizontal') {
            posKey = `${row},${col + index}`
          } else {
            posKey = `${row + index},${col}`
          }
          blankPositions.push(posKey)
        }
      })
    })
    
    if (blankPositions.includes(blankKey)) {
      classes.push('is-blank')
    }
  }
  
  return classes
}
</script>
