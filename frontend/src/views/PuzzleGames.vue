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
          <button class="play-btn" @click="handleGenerateChess(chess)">
            生成棋盘
          </button>
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
        <div class="chain-info">
          <p>难度：{{ gameContent.difficulty }}</p>
          <p>数量：{{ gameContent.chain_length }}个词</p>
          <p>说明：字/字母在交叉点重叠，找出所有隐藏的成语/单词</p>
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

      <!-- 数独 -->
      <div v-if="gameContent.grid && gameContent.size" class="sudoku-game">
        <div class="sudoku-info">
          <p>大小：{{ gameContent.size }}×{{ gameContent.size }}</p>
          <p>难度：{{ gameContent.difficulty }}</p>
        </div>
        <div class="sudoku-board" :class="`size-${gameContent.size}`">
          <div
            v-for="(row, rowIndex) in gameContent.grid"
            :key="rowIndex"
            class="sudoku-row"
          >
            <div
              v-for="(cell, cellIndex) in row"
              :key="cellIndex"
              :class="['sudoku-cell', {
                'border-thick-right': shouldHaveThickBorder(gameContent.size, cellIndex, 'right'),
                'border-thick-bottom': shouldHaveThickBorder(gameContent.size, rowIndex, 'bottom')
              }]"
            >
              {{ typeof cell === 'number' && cell > 0 ? cell : '' }}
            </div>
          </div>
        </div>
        <div v-if="showSolution" class="sudoku-solution">
          <h4>参考答案：</h4>
          <div class="sudoku-board" :class="`size-${gameContent.size}`">
            <div
              v-for="(row, rowIndex) in gameContent.solution"
              :key="rowIndex"
              class="sudoku-row"
            >
              <div
                v-for="(cell, cellIndex) in row"
                :key="cellIndex"
                :class="['sudoku-cell', {
                  'border-thick-right': shouldHaveThickBorder(gameContent.size!, cellIndex, 'right'),
                  'border-thick-bottom': shouldHaveThickBorder(gameContent.size!, rowIndex, 'bottom')
                }]"
              >
                {{ cell }}
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
        <div v-if="gameContent.solutions && gameContent.solutions.length > 0" class="solutions-hint">
          <p>提示示例：{{ gameContent.solutions[0] }}</p>
        </div>
        <div class="point24-tips">
          <p>💡 使用加减乘除（+ - × ÷）和括号，将这四个数字计算出24</p>
          <p>✨ 每个数字必须使用一次且只能使用一次</p>
        </div>
      </div>

      <!-- 棋类 -->
      <div v-if="gameContent.board_type" class="chess-game">
        <div class="chess-info">
          <h3>{{ gameContent.title }}</h3>
          <div class="chess-instructions">{{ gameContent.instructions }}</div>
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
  generateParentChildGames as generateParentChildGamesApi,
  type GameCategory,
  type GameType,
  type GameState
} from '@/api/games'

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
    
    gameContent.value.chain.forEach((item: any) => {
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

<style scoped>
.puzzle-games {
  font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
  position: relative;
}

.header h1 {
  font-size: 42px;
  margin-bottom: 15px;
  text-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.header p {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.back-link {
  display: inline-block;
  color: white;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  transition: all 0.3s;
}

.back-link:hover {
  background: rgba(255,255,255,0.3);
}

.section {
  max-width: 1200px;
  margin: 0 auto 40px;
}

.section h2 {
  color: white;
  font-size: 28px;
  margin-bottom: 20px;
  text-align: center;
  text-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.categories-grid,
.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.category-card,
.game-card {
  background: white;
  border-radius: 16px;
  padding: 25px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  position: relative;
}

.category-card:hover,
.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.category-card.active,
.game-card.selected {
  border: 3px solid #667eea;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.category-icon,
.game-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.category-info h3,
.game-card h3 {
  color: #333;
  font-size: 20px;
  margin-bottom: 8px;
}

.category-info p {
  color: #666;
  font-size: 14px;
}

.play-btn,
.generate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 15px;
}

.play-btn:hover,
.generate-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.generate-btn {
  display: block;
  margin: 20px auto;
  padding: 12px 30px;
  font-size: 16px;
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.size-selector {
  margin: 15px 0;
}

.size-selector span {
  color: #666;
  font-size: 14px;
  margin-right: 10px;
}

.size-btn {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 5px;
  margin: 0 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.size-btn:hover {
  background: #e0e0e0;
}

.size-btn.active,
.count-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.count-selector {
  margin: 15px 0;
  text-align: center;
}

.count-label {
  color: #666;
  font-size: 14px;
  margin-right: 10px;
}

.count-btn {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 5px 15px;
  border-radius: 5px;
  margin: 0 5px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.count-btn:hover {
  background: #e0e0e0;
}

.check-mark {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* 游戏预览区域 */
.game-preview {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.preview-header h2 {
  color: #333;
  margin: 0;
  text-align: left;
}

.preview-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 10px 20px;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  background: #667eea;
  color: white;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

/* 字谜游戏 */
.word-puzzle-game {
  text-align: center;
}

.chain-info {
  margin-bottom: 20px;
  color: #666;
}

.chain-info p {
  margin: 5px 0;
}

.puzzle-grid {
  display: inline-flex;
  flex-direction: column;
  background: white;
  border: 3px solid #333;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  margin: 0 auto;
  max-width: 100%;
  overflow-x: auto;
}

.puzzle-row {
  display: flex;
}

.puzzle-cell {
  width: 24px;
  min-width: 24px;
  aspect-ratio: 1 / 1.414;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border: 1px solid #ddd;
  font-size: 14px;
  font-weight: bold;
  color: #999;
}

.puzzle-cell.has-char {
  background: #fff;
  color: #333;
  border-color: #333;
}

.puzzle-cell.has-char:nth-child(odd) {
  background: #f0f9ff;
}

.puzzle-cell.is-blank {
  background: #fff;
  border: 2px solid #333;
  border-style: dashed;
}

.answer-hint {
  margin-top: 30px;
}

.toggle-answer-btn {
  padding: 10px 20px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.toggle-answer-btn:hover {
  background: #f57c00;
}

.answer-list {
  margin-top: 20px;
  text-align: left;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 10px;
}

.answer-list h4 {
  color: #333;
  margin-bottom: 15px;
}

.answer-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.answer-list li {
  padding: 8px 0;
  border-bottom: 1px solid #ddd;
  color: #666;
}

.answer-list li:last-child {
  border-bottom: none;
}

.answer-list strong {
  color: #667eea;
  font-size: 16px;
}

.position-hint {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

/* 数独游戏 */
.sudoku-game {
  text-align: center;
}

.sudoku-info {
  margin-bottom: 20px;
  color: #666;
}

.sudoku-board {
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  border: 3px solid #333;
  background: white;
}

.sudoku-board.size-4 {
  max-width: 400px;
}

.sudoku-board.size-4 .sudoku-cell {
  width: 100px;
  height: 100px;
  font-size: 36px;
}

.sudoku-board.size-6 {
  max-width: 480px;
}

.sudoku-board.size-6 .sudoku-cell {
  width: 80px;
  height: 80px;
  font-size: 32px;
}

.sudoku-board.size-9 {
  max-width: 400px;
}

.sudoku-board.size-9 .sudoku-cell {
  width: 45px;
  height: 45px;
  font-size: 24px;
}

.sudoku-row {
  display: flex;
}

.sudoku-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 1px solid #ddd;
  background: #f9f9f9;
}

.sudoku-cell.border-thick-right {
  border-right: 3px solid #333;
}

.sudoku-cell.border-thick-bottom {
  border-bottom: 3px solid #333;
}

.toggle-solution-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.toggle-solution-btn:hover {
  background: #f57c00;
}

.sudoku-solution {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px dashed #ddd;
}

.sudoku-solution h4 {
  color: #666;
  margin-bottom: 15px;
}

/* 24点游戏 */
.point24-game {
  text-align: center;
}

.numbers-container {
  margin: 30px 0;
}

.numbers-display {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.number-card {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.target-display {
  font-size: 48px;
  font-weight: bold;
  color: #333;
}

.solutions-hint {
  color: #666;
  font-style: italic;
  margin-bottom: 20px;
}

.point24-tips {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 10px;
  text-align: left;
  max-width: 600px;
  margin: 20px auto;
}

.point24-tips p {
  color: #666;
  margin: 8px 0;
}

/* 棋类游戏（围棋） */
.chess-game {
  text-align: center;
}

.chess-info {
  margin-bottom: 20px;
  text-align: left;
}

.chess-info h3 {
  color: #333;
  margin-bottom: 15px;
}

.chess-instructions {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 10px;
  line-height: 1.8;
  color: #666;
  white-space: pre-line;
}

.chess-board {
  display: flex;
  flex-direction: column;
  margin: 20px auto;
  border: 2px solid #000;
  background: #dcb35c;
  width: fit-content;
  width: 100%;
  max-width: 800px;
}

.chess-board.size-9 {
  max-width: 720px;
}

.chess-board.size-13 {
  max-width: 780px;
}

.chess-board.size-19 {
  max-width: 850px;
}

.chess-row {
  display: flex;
  width: 100%;
}

.chess-cell {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #000;
  background: #dcb35c;
  position: relative;
}

.chess-board.size-9 .chess-cell {
  height: 80px;
  min-height: 80px;
}

.chess-board.size-13 .chess-cell {
  height: 60px;
  min-height: 60px;
}

.chess-board.size-19 .chess-cell {
  height: 45px;
  min-height: 45px;
}

.chess-cell.has-star {
  background: #dcb35c;
}

.star-point {
  font-size: 24px;
  color: #000;
  line-height: 1;
}

/* 亲子类游戏卡片 */
.parent-child-game {
  text-align: center;
}

/* 统一游戏规则样式 */
.common-rules {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: left;
}

.common-rules h3 {
  color: white;
  margin: 0 0 15px 0;
  font-size: 20px;
}

.rules-content {
  color: white;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-line;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.game-card-item {
  border: 3px solid #667eea;
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  background: #f9f9f9;
}

.card-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-weight: bold;
  font-size: 18px;
  margin: 0 auto 15px;
}

.card-content {
  text-align: center;
  line-height: 1.6;
  color: #333;
  font-size: 24px;
  font-weight: bold;
  padding: 15px 10px;
  background: white;
  border-radius: 10px;
  margin-top: 10px;
}

.cards-info {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
  font-size: 16px;
}

/* 打印样式 */
@media print {
  .header,
  .section:not(.game-preview),
  .preview-actions,
  .toggle-solution-btn,
  .back-link {
    display: none !important;
  }

  .puzzle-games {
    background: white;
    min-height: auto;
    padding: 0;
  }

  .game-preview {
    box-shadow: none;
    border: none;
    padding: 0;
  }

  .preview-header {
    display: none;
  }

  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .header h1 {
    font-size: 28px;
  }

  .categories-grid,
  .games-grid {
    grid-template-columns: 1fr;
  }

  .sudoku-board.size-4 .sudoku-cell {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .sudoku-board.size-6 .sudoku-cell {
    width: 45px;
    height: 45px;
    font-size: 22px;
  }

  .sudoku-board.size-9 .sudoku-cell {
    width: 35px;
    height: 35px;
    font-size: 18px;
  }

  .chess-board {
    max-width: 100% !important;
  }

  .chess-board.size-9 .chess-cell {
    height: 45px;
    min-height: 45px;
  }

  .chess-board.size-13 .chess-cell {
    height: 35px;
    min-height: 35px;
  }

  .chess-board.size-19 .chess-cell {
    height: 26px;
    min-height: 26px;
  }

  .star-point {
    font-size: 16px;
  }

  .puzzle-cell {
    width: 18px;
    min-width: 18px;
    font-size: 12px;
  }

  .number-card {
    width: 60px;
    height: 60px;
    font-size: 28px;
  }

  .preview-header {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
