<template>
  <div class="study">
    <QuickNav />
    <div class="container">
      <div class="header">
        <h1>📚 学习题库</h1>
        <p>数学·语文·英语题库练习，巩固知识，查漏补缺</p>
      </div>

      <div class="categories">
        <div
          v-for="category in categories"
          :key="category.id"
          :class="['category-card', { active: selectedCategory === category.id }]"
          @click="selectedCategory = category.id"
        >
          <span class="category-icon">{{ category.icon }}</span>
          <h3>{{ category.name }}</h3>
          <p>{{ category.description }}</p>
        </div>
      </div>

      <div v-if="selectedCategory" class="question-section">
        <div class="section-header">
          <h2>{{ getCategoryTitle() }}</h2>
          <div class="grade-selector">
            <span class="grade-label">年级：</span>
            <button
              v-for="grade in [1, 2, 3, 4, 5, 6]"
              :key="grade"
              :class="['grade-btn', { active: selectedGrade === grade }]"
              @click="selectedGrade = grade"
            >
              {{ grade }}年级
            </button>
          </div>
        </div>

        <div class="question-card" v-if="currentQuestion">
          <div class="question-header">
            <span class="question-number">第 {{ currentQuestionIndex + 1 }} 题</span>
            <span class="question-type">{{ currentQuestion.type }}</span>
          </div>
          <div class="question-content">
            <p class="question-text">{{ currentQuestion.text }}</p>
            <div v-if="currentQuestion.options && currentQuestion.options.length > 0" class="options">
              <div
                v-for="(option, index) in currentQuestion.options"
                :key="index"
                :class="['option', { 
                  selected: selectedAnswer === index, 
                  correct: submitted && option.label === currentQuestion.answer,
                  wrong: submitted && selectedAnswer === index && option.label !== currentQuestion.answer 
                }]"
                @click="selectAnswer(index)"
              >
                <span class="option-label">{{ option.label }}</span>
                <span class="option-text">{{ option.text }}</span>
              </div>
            </div>
            <div v-else class="text-answer">
              <textarea
                v-model="textAnswer"
                placeholder="请输入你的答案..."
                rows="3"
                :disabled="submitted"
              ></textarea>
              <div v-if="submitted" class="answer-feedback">
                <p>正确答案：{{ currentQuestion.answer }}</p>
              </div>
            </div>
          </div>
          <div class="question-footer">
            <button class="btn btn-submit" @click="submitAnswer" :disabled="submitted || loading">
              {{ submitted ? '已提交' : '提交答案' }}
            </button>
            <button class="btn btn-explain" @click="showExplanation = !showExplanation" v-if="submitted && currentQuestion.explanation">
              {{ showExplanation ? '隐藏解析' : '查看解析' }}
            </button>
            <div v-if="showExplanation && currentQuestion.explanation" class="explanation">
              <p><strong>解析：</strong>{{ currentQuestion.explanation }}</p>
            </div>
          </div>
        </div>

        <div v-else-if="loading" class="loading-state">
          <p>⏳ 正在加载题目...</p>
        </div>

        <div v-else class="empty-state">
          <p>📭 暂无题目</p>
          <p>请选择科目和年级开始练习</p>
        </div>

        <div class="navigation">
          <button class="btn btn-prev" @click="prevQuestion" :disabled="currentQuestionIndex === 0">
            ← 上一题
          </button>
          <span class="progress">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
          <button class="btn btn-next" @click="nextQuestion" :disabled="currentQuestionIndex >= questions.length - 1">
            下一题 →
          </button>
        </div>

        <div class="score-summary" v-if="submittedCount > 0">
          <div class="score-card">
            <span class="score-icon">📊</span>
            <span class="score-text">
              已答 {{ submittedCount }} 题，正确 {{ correctCount }} 题，正确率 {{ getAccuracy() }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import QuickNav from '@/components/QuickNav.vue'
import { ElMessage } from 'element-plus'

interface Question {
  id: number
  question_type: string
  question_text: string
  options?: { label: string; text: string }[]
  answer: string
  explanation?: string
  grade: number
  subject: string
}

function parseOptions(opts: any): { label: string; text: string }[] | undefined {
  if (!opts) return undefined
  if (Array.isArray(opts)) return opts
  if (typeof opts === 'string') {
    try { return JSON.parse(opts) } catch {
      return undefined
    }
  }
  return undefined
}

const categories = [
  { id: 'math', icon: '🔢', name: '数学', description: '口算、应用题、几何等' },
  { id: 'chinese', icon: '📖', name: '语文', description: '字词、阅读、作文等' },
  { id: 'english', icon: '🔤', name: '英语', description: '单词、语法、阅读等' }
]

const selectedCategory = ref('')
const selectedGrade = ref(4)  // 默认4年级，有最多题目
const selectedAnswer = ref<number | null>(null)
const textAnswer = ref('')
const submitted = ref(false)
const showExplanation = ref(false)
const currentQuestionIndex = ref(0)
const submittedCount = ref(0)
const correctCount = ref(0)
const loading = ref(false)

const questions = ref<Question[]>([])

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || null
})

const getCategoryTitle = () => {
  const cat = categories.find(c => c.id === selectedCategory.value)
  return cat ? `${cat.icon} ${cat.name} - ${selectedGrade.value}年级` : ''
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://10.58.144.3:8000'

const loadQuestions = async () => {
  if (!selectedCategory.value) return
  
  loading.value = true
  try {
    const subjectMap: Record<string, string> = {
      math: '数学',
      chinese: '语文',
      english: '英语'
    }
    
    const response = await fetch(`${API_BASE}/api/study/questions?subject=${subjectMap[selectedCategory.value]}&grade=${selectedGrade.value}&limit=50`)
    const data = await response.json()
    
    if (data.success && data.data) {
      questions.value = data.data.questions.map((q: any) => ({
        ...q,
        type: q.question_type,
        text: q.question_text,
        options: parseOptions(q.options)
      }))
      currentQuestionIndex.value = 0
      resetQuestion()
      ElMessage.success(`加载了 ${questions.value.length} 道题目`)
    } else {
      ElMessage.error('加载题目失败')
    }
  } catch (error) {
    console.error('Failed to load questions:', error)
    ElMessage.error('加载题目失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

watch([selectedCategory, selectedGrade], () => {
  loadQuestions()
})

const selectAnswer = (index: number) => {
  if (!submitted.value) {
    selectedAnswer.value = index
  }
}

const submitAnswer = async () => {
  if (submitted.value || !currentQuestion.value) return
  
  submitted.value = true
  submittedCount.value++
  
  const q = currentQuestion.value
  let isCorrect = false
  
  if (q.options) {
    if (selectedAnswer.value !== null) {
      const selectedOption = q.options[selectedAnswer.value]
      isCorrect = selectedOption.label === q.answer
    }
  } else {
    // For text answers, simple comparison
    isCorrect = textAnswer.value.trim() === q.answer.trim()
  }
  
  if (isCorrect) {
    correctCount.value++
  }
  
  // Save record to backend
  try {
    await fetch(`${API_BASE}/api/study/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: q.id,
        student_answer: q.options ? q.options[selectedAnswer.value || null]?.label : textAnswer.value,
        is_correct: isCorrect
      })
    })
  } catch (error) {
    console.error('Failed to save record:', error)
  }
}

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    resetQuestion()
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    resetQuestion()
  }
}

const resetQuestion = () => {
  selectedAnswer.value = null
  textAnswer.value = ''
  submitted.value = false
  showExplanation.value = false
}

const getAccuracy = () => {
  if (submittedCount.value === 0) return 0
  return Math.round((correctCount.value / submittedCount.value) * 100)
}

onMounted(() => {
  // Auto-select math category on load
  selectedCategory.value = 'math'
})
</script>

<style scoped src="./Study.css"></style>
