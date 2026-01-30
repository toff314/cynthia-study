/** 益智游戏API */

import request from './index'

export interface GameCategory {
  id: string
  name: string
  description: string
  icon: string
}

export interface GameType {
  type: string
  name: string
  icon: string
  size?: number
  sizes?: number[]
}

export interface IdiomChainItem {
  word: string
  chars: string[]
  blanks: boolean[]
  row?: number
  col?: number
  direction?: 'horizontal' | 'vertical'
}

export interface WordChainItem {
  word: string
  letters: string[]
  blanks: boolean[]
  row?: number
  col?: number
  direction?: 'horizontal' | 'vertical'
}

export interface SudokuPuzzle {
  grid: (number | string)[][]
  solution: number[][]
  index: number
}

export interface GameState {
  // 字谜网格游戏（共享字段）
  grid?: (string | number)[][]
  
  // 接龙游戏
  chain?: IdiomChainItem[] | WordChainItem[]
  chain_length?: number
  difficulty?: string
  
  // 数独游戏（新格式支持多个谜题）
  puzzles?: SudokuPuzzle[]
  count?: number
  solution?: number[][]
  size?: number
  
  // 24点游戏
  numbers?: number[]
  target?: number
  solutions?: string[]
  
  // 棋类游戏
  board_type?: string  // 棋盘类型（如 "go" 围棋）
  board_size?: number  // 棋盘大小（9, 13, 19）
  title?: string
  instructions?: string
  star_points?: [number, number][]
  
  // 亲子类游戏
  common_instructions?: string
  cards?: Record<string, string>
  total?: number
}

/**
 * 获取所有游戏分类
 */
export async function getGameCategories() {
  return request.get('/api/games/categories')
}

/**
 * 根据年龄段获取游戏类型
 */
export async function getGamesByAgeGroup(ageGroup: string) {
  return request.get(`/api/games/age-group/${ageGroup}`)
}

/**
 * 获取棋类游戏类型
 */
export async function getChessTypes() {
  return request.get('/api/games/chess-types')
}

/**
 * 获取亲子类游戏类型
 */
export async function getParentChildTypes() {
  return request.get('/api/games/parent-child-types')
}

/**
 * 生成成语接龙游戏
 */
export async function generateIdiomChain(params: {
  age_group: string
  difficulty?: string
  chain_length?: number
  blank_ratio?: number
}) {
  return request.post('/api/games/generate/idiom-chain', params)
}

/**
 * 生成英语单词接龙游戏
 */
export async function generateWordChain(params: {
  age_group: string
  difficulty?: string
  chain_length?: number
  blank_ratio?: number
}) {
  return request.post('/api/games/generate/word-chain', params)
}

/**
 * 生成数独游戏
 */
export async function generateSudoku(params: {
  size: number
  difficulty?: string
}) {
  return request.post('/api/games/generate/sudoku', params)
}

/**
 * 生成24点游戏
 */
export async function generatePoint24(params: {
  difficulty?: string
}) {
  return request.post('/api/games/generate/point24', params)
}

/**
 * 生成棋类游戏
 */
export async function generateChess(params: {
  board_type: string
  board_size?: number
}) {
  return request.post('/api/games/generate/chess', params)
}

/**
 * 生成亲子类游戏
 */
export async function generateParentChildGames(params: {
  game_types: string[]
}) {
  return request.post('/api/games/generate/parent-child', params)
}

/**
 * 保存游戏记录
 */
export async function saveGame(gameData: any) {
  return request.post('/api/games/save', gameData)
}

/**
 * 获取游戏列表
 */
export async function getGameList(gameType: string, ageGroup?: string) {
  const url = `/api/games/list/${gameType}${ageGroup ? `?age_group=${ageGroup}` : ''}`
  return request.get(url)
}
