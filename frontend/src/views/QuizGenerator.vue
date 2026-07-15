<template>
  <div class="quiz-generator">
    <QuickNav />
    <div class="container">
      <div class="header">
        <router-link to="/" class="btn-back">← 返回首页</router-link>
        <h1>📚 学习题库</h1>
        <p>选择学科和年级，查看完整试卷</p>
      </div>

      <!-- 学科选择 -->
      <div class="subject-selector">
        <div class="subject-buttons">
          <button
            v-for="sub in subjects"
            :key="sub.key"
            :class="['subject-btn', { active: selectedSubject === sub.key }]"
            @click="selectSubject(sub.key)"
          >
            {{ sub.icon }} {{ sub.name }}
          </button>
        </div>
      </div>

      <!-- 年级选择 -->
      <div v-if="selectedSubject" class="grade-selector">
        <h3>选择学期</h3>
        <div class="grade-buttons">
          <button
            v-for="g in gradeOptions"
            :key="g.value"
            :class="['grade-btn', { active: selectedGrade === g.value }]"
            @click="selectGrade(g.value)"
          >
            {{ g.label }}
          </button>
        </div>
      </div>

      <!-- 试卷列表 -->
      <div v-if="selectedGrade && !selectedPaper && !loadingPapers" class="paper-list">
        <h3>试卷列表</h3>
        <div v-if="papers.length > 0" class="paper-cards">
          <div
            v-for="paper in papers"
            :key="paper.paper_id"
            class="paper-card"
            @click="selectPaper(paper)"
          >
            <div class="paper-card-title">{{ paper.title }}</div>
            <div class="paper-card-info">
              <span :class="['paper-type-badge', paper.paper_type === '同步教学' ? 'sync' : 'test']">{{ paper.paper_type }}</span>
              <span>{{ paper.question_count }} 道题</span>
              <span v-if="paper.semester">{{ paper.semester }}学期</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">📭 该学期暂无试卷</div>
      </div>

      <div v-else-if="loadingPapers" class="loading-state">⏳ 加载试卷列表...</div>

      <!-- 试卷内容 -->
      <div v-if="selectedPaper && !loadingQuestions" class="quiz-paper">
        <button class="btn-back-paper" @click="backToPaperList">← 返回试卷列表</button>
        <div class="paper-header">
          <h2>{{ selectedPaper.title }}</h2>
          <p>{{ questions.length }} 道题目</p>
        </div>

        <div class="paper-content">
          <div v-for="(q, index) in questions" :key="q.id" class="question-item">
            <div class="question-header">
              <span class="question-number">{{ index + 1 }}.</span>
              <span class="question-type-badge">{{ typeLabel(q.question_type) }}</span>
            </div>

            <!-- 音频播放器 -->
            <div v-if="q.audio_url" class="audio-player">
              <audio :src="q.audio_url" controls preload="none"></audio>
            </div>

            <!-- 题目图片 -->
            <div v-if="q.images && q.images.length > 0" class="question-images">
              <img
                v-for="(img, imgIdx) in q.images"
                :key="imgIdx"
                :src="img"
                :alt="'题目' + (index+1) + '图片' + (imgIdx+1)"
                class="question-img"
                @click="previewImage(img)"
              />
            </div>

            <div class="question-text">{{ q.question_text }}</div>

            <div v-if="q.options && parsedOptions(q.options).length > 0" class="question-options">
              <div v-for="(opt, oi) in parsedOptions(q.options)" :key="oi" class="option-item">
                {{ typeof opt === 'object' ? (opt.label + '. ' + opt.text) : opt }}
              </div>
            </div>

            <div v-if="q.question_type === 'short_answer' || q.question_type === 'fill_blank'" class="answer-blank">
              <div class="blank-lines"></div>
            </div>
          </div>
        </div>

        <!-- 答案（仅当有答案时才显示） -->
        <div v-if="hasAnswers" class="answer-section">
          <h3 class="answer-title">参考答案</h3>
          <div v-for="(q, index) in questions" :key="'a' + q.id" class="answer-item">
            <div v-if="q.answer" class="answer-line">
              <span class="answer-num">{{ index + 1 }}.</span>
              <span class="answer-val">{{ q.answer }}</span>
              <span v-if="q.explanation" class="answer-exp">（{{ q.explanation }}）</span>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button class="btn btn-print" @click="printPaper">🖨️ 打印试卷</button>
        </div>
      </div>

      <div v-else-if="loadingQuestions" class="loading-state">⏳ 加载题目...</div>

      <!-- 图片预览 -->
      <div v-if="previewImgUrl" class="image-preview-overlay" @click="previewImgUrl = ''">
        <img :src="previewImgUrl" class="preview-full-img" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import QuickNav from '@/components/QuickNav.vue'

interface DbQuestion {
  id: number
  subject: string
  grade: number
  semester: string
  question_type: string
  question_text: string
  options: any
  answer: string
  explanation: string
  images: string[] | null
  audio_url: string | null
  paper_id: string
  paper_title: string
}

interface Paper {
  paper_id: string
  title: string
  subject: string
  grade: number
  semester: string
  question_count: number
  paper_type: string
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://10.58.144.3:8000'

const subjects = [
  { key: 'chinese', icon: '📖', name: '语文' },
  { key: 'math', icon: '🔢', name: '数学' },
  { key: 'english', icon: '🔤', name: '英语' },
]

const gradeOptions = [
  { value: '1-up', label: '一（上）' },
  { value: '1-down', label: '一（下）' },
  { value: '2-up', label: '二（上）' },
  { value: '2-down', label: '二（下）' },
  { value: '3-up', label: '三（上）' },
  { value: '3-down', label: '三（下）' },
  { value: '4-up', label: '四（上）' },
  { value: '4-down', label: '四（下）' },
  { value: '5-up', label: '五（上）' },
  { value: '5-down', label: '五（下）' },
  { value: '6-up', label: '六（上）' },
  { value: '6-down', label: '六（下）' },
]

const selectedSubject = ref('')
const selectedGrade = ref('')
const selectedPaper = ref<Paper | null>(null)
const papers = ref<Paper[]>([])
const questions = ref<DbQuestion[]>([])
const loadingPapers = ref(false)
const loadingQuestions = ref(false)
const previewImgUrl = ref('')

const hasAnswers = computed(() => questions.value.some(q => q.answer && q.answer.trim()))

const subjectMap: Record<string, string> = { math: '数学', chinese: '语文', english: '英语' }

const selectSubject = (key: string) => {
  selectedSubject.value = key
  selectedGrade.value = ''
  selectedPaper.value = null
  papers.value = []
  questions.value = []
}

const selectGrade = async (val: string) => {
  selectedGrade.value = val
  selectedPaper.value = null
  questions.value = []
  await loadPapers()
}

const selectPaper = async (paper: Paper) => {
  selectedPaper.value = paper
  await loadQuestions()
}

const backToPaperList = () => {
  selectedPaper.value = null
  questions.value = []
}

const parsedOptions = (opts: any): any[] => {
  if (!opts) return []
  if (Array.isArray(opts)) return opts
  if (typeof opts === 'string') {
    try { return JSON.parse(opts) } catch { return [] }
  }
  return []
}

const typeLabel = (t: string) => {
  const m: Record<string, string> = {
    choice: '选择题', fill_blank: '填空题',
    true_false: '判断题', short_answer: '简答题'
  }
  return m[t] || t
}

const gradeToInt = (val: string): number => parseInt(val.split('-')[0])
const semesterFromGrade = (val: string): string => val.endsWith('-up') ? '上' : '下'

const loadPapers = async () => {
  if (!selectedSubject.value || !selectedGrade.value) return
  loadingPapers.value = true
  try {
    const params = new URLSearchParams({
      subject: subjectMap[selectedSubject.value],
      grade: String(gradeToInt(selectedGrade.value)),
    })
    const res = await fetch(`${API_BASE}/api/study/papers?${params}`)
    const data = await res.json()
    if (data.success) {
      // 按学期过滤
      const sem = semesterFromGrade(selectedGrade.value)
      papers.value = data.data.papers.filter((p: Paper) => {
        if (!p.semester) return true
        return p.semester === sem
      })
      // 如果没有学期匹配，显示全部
      if (papers.value.length === 0 && data.data.papers.length > 0) {
        papers.value = data.data.papers
      }
    }
  } catch (e) {
    console.error('加载试卷列表失败:', e)
  } finally {
    loadingPapers.value = false
  }
}

const loadQuestions = async () => {
  if (!selectedPaper.value) return
  loadingQuestions.value = true
  try {
    const params = new URLSearchParams({
      paper_id: selectedPaper.value.paper_id,
      limit: '200'
    })
    const res = await fetch(`${API_BASE}/api/study/questions?${params}`)
    const data = await res.json()
    if (data.success) {
      questions.value = data.data.questions
    }
  } catch (e) {
    console.error('加载题目失败:', e)
  } finally {
    loadingQuestions.value = false
  }
}

const previewImage = (url: string) => {
  previewImgUrl.value = url
}

const printPaper = () => {
  if (!selectedPaper.value) return
  const w = window.open('', '_blank')
  if (!w) return
  w.document.write(buildPrintHTML())
  w.document.close()
  setTimeout(() => w.print(), 500)
}

const buildPrintHTML = () => {
  const title = selectedPaper.value?.title || '试卷'
  let h = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>${title}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Microsoft YaHei",sans-serif;font-size:14px;line-height:1.8;color:#333;padding:20px;background:#fff}
.container{max-width:800px;margin:0 auto;padding:40px}
.paper-header{text-align:center;padding-bottom:15px;border-bottom:2px solid #333;margin-bottom:25px}
.paper-header h2{font-size:22px;margin-bottom:6px}
.paper-header p{color:#666;font-size:14px}
.question-item{margin-bottom:18px;padding:12px 15px;background:#fafafa;border-radius:4px;page-break-inside:avoid}
.question-header{display:flex;align-items:center;margin-bottom:8px}
.question-number{font-weight:bold;font-size:15px;margin-right:8px}
.question-type-badge{background:#e0e0e0;color:#333;padding:1px 8px;border-radius:3px;font-size:11px}
.audio-player{margin-bottom:10px}
.question-images{margin:10px 0;text-align:center}
.question-images img{max-width:100%;max-height:300px;border-radius:4px;margin:5px}
.question-text{margin-bottom:10px;line-height:1.8}
.question-options{margin-left:20px}
.option-item{padding:3px 0}
.answer-blank{margin-top:10px}
.blank-lines{height:60px;border-bottom:1px dashed #ccc}
.answer-section{margin-top:30px;padding-top:15px;border-top:2px solid #333;page-break-before:always}
.answer-title{font-size:18px;font-weight:bold;margin-bottom:15px}
.answer-item{padding:6px 0}
.answer-line{font-size:14px}
.answer-num{font-weight:bold;margin-right:6px}
.answer-val{color:#333}
.answer-exp{color:#888;font-size:13px}
@media print{body{padding:0}.container{padding:20px}.question-item{page-break-inside:avoid}.answer-section{page-break-before:always}.audio-player{display:none}}
</style></head><body><div class="container">
<div class="paper-header"><h2>${title}</h2><p>${questions.value.length} 道题目</p></div>`

  questions.value.forEach((q, i) => {
    h += `<div class="question-item">
<div class="question-header"><span class="question-number">${i + 1}.</span><span class="question-type-badge">${typeLabel(q.question_type)}</span></div>`
    if (q.audio_url) {
      h += `<div class="audio-player"><audio src="${q.audio_url}" controls></audio></div>`
    }
    if (q.images && q.images.length > 0) {
      h += '<div class="question-images">'
      q.images.forEach(img => {
        h += `<img src="${img}" />`
      })
      h += '</div>'
    }
    h += `<div class="question-text">${q.question_text}</div>`
    const opts = parsedOptions(q.options)
    if (opts.length > 0) {
      h += '<div class="question-options">'
      opts.forEach(o => {
        h += `<div class="option-item">${typeof o === 'object' ? (o.label + '. ' + o.text) : o}</div>`
      })
      h += '</div>'
    }
    if (q.question_type === 'short_answer' || q.question_type === 'fill_blank') {
      h += '<div class="answer-blank"><div class="blank-lines"></div></div>'
    }
    h += '</div>'
  })

  h += '<div class="answer-section"><div class="answer-title">参考答案</div>'
  questions.value.forEach((q, i) => {
    h += `<div class="answer-item"><div class="answer-line"><span class="answer-num">${i + 1}.</span><span class="answer-val">${q.answer || '—'}</span>`
    if (q.explanation) h += `<span class="answer-exp">（${q.explanation}）</span>`
    h += '</div></div>'
  })
  h += '</div></div></body></html>'
  return h
}
</script>

<style scoped>
.quiz-generator { min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }
.container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 15px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
.header { text-align: center; margin-bottom: 30px; }

.btn-back {
  display: inline-block; padding: 8px 20px; background: rgba(102, 126, 234, 0.15);
  color: #667eea; border: 2px solid rgba(102, 126, 234, 0.3); border-radius: 8px;
  font-size: 14px; font-weight: 600; cursor: pointer; text-decoration: none;
  margin-bottom: 15px; transition: all 0.3s;
}
.btn-back:hover { background: #667eea; color: #fff; border-color: #667eea; transform: translateX(-3px); }

.btn-back-paper {
  display: inline-block; padding: 8px 16px; background: #f0f0f0; color: #555;
  border: none; border-radius: 6px; font-size: 14px; cursor: pointer; margin-bottom: 15px; transition: all 0.3s;
}
.btn-back-paper:hover { background: #e0e0e0; }

.subject-selector { margin-bottom: 25px; }
.subject-buttons { display: flex; gap: 12px; justify-content: center; }
.subject-btn { padding: 14px 32px; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 8px; font-size: 18px; cursor: pointer; transition: all 0.3s; }
.subject-btn:hover, .subject-btn.active { background: #667eea; color: white; }

.grade-selector { margin-bottom: 25px; }
.grade-selector h3 { color: #333; margin-bottom: 12px; font-size: 17px; }
.grade-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.grade-btn { padding: 10px 18px; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 6px; font-size: 15px; cursor: pointer; transition: all 0.3s; }
.grade-btn:hover, .grade-btn.active { background: #667eea; color: white; }

.paper-list { margin-top: 20px; }
.paper-list h3 { color: #333; margin-bottom: 15px; font-size: 20px; }
.paper-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
.paper-card { background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 18px; cursor: pointer; transition: all 0.3s; }
.paper-card:hover { border-color: #667eea; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.paper-card-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 8px; }
.paper-card-info { display: flex; gap: 12px; color: #666; font-size: 13px; align-items: center; }
.paper-type-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.paper-type-badge.sync { background: #e8f5e9; color: #2e7d32; }
.paper-type-badge.test { background: #fff3e0; color: #e65100; }

.quiz-paper { margin-top: 20px; }
.paper-header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #dee2e6; }
.paper-header h2 { color: #333; font-size: 26px; }
.paper-header p { color: #666; font-size: 15px; margin-top: 6px; }

.question-item { background: white; padding: 18px 20px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.question-header { display: flex; align-items: center; margin-bottom: 10px; }
.question-number { color: #667eea; font-weight: bold; font-size: 17px; margin-right: 10px; }
.question-type-badge { background: #e9ecef; color: #495057; padding: 3px 10px; border-radius: 4px; font-size: 12px; }

.audio-player { margin: 10px 0; }
.audio-player audio { width: 100%; max-width: 400px; }

.question-images { margin: 10px 0; }
.question-img { max-width: 100%; max-height: 400px; border-radius: 8px; margin: 5px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

.question-text { color: #333; font-size: 15px; line-height: 1.9; margin-bottom: 12px; }
.question-options { margin-left: 20px; }
.option-item { padding: 5px 0; color: #495057; font-size: 14px; }
.answer-blank { margin-top: 10px; }
.blank-lines { height: 60px; border-bottom: 1px dashed #ccc; }

.answer-section { margin-top: 30px; padding-top: 20px; border-top: 2px solid #dee2e6; }
.answer-title { color: #28a745; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
.answer-item { padding: 6px 0; }
.answer-line { font-size: 14px; }
.answer-num { font-weight: bold; color: #333; margin-right: 6px; }
.answer-val { color: #28a745; }
.answer-exp { color: #6c757d; font-size: 13px; margin-left: 8px; }

.action-buttons { display: flex; justify-content: center; gap: 15px; margin-top: 25px; }
.btn-print { background: #28a745; color: white; padding: 12px 32px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
.btn-print:hover { background: #218838; }

.loading-state, .empty-state { text-align: center; padding: 40px; color: #6c757d; font-size: 16px; }

.image-preview-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 9999; cursor: pointer; }
.preview-full-img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }

@media (max-width: 768px) {
  .container { padding: 20px; }
  .subject-buttons { flex-direction: column; }
  .subject-btn { width: 100%; }
  .grade-buttons { flex-direction: column; }
  .grade-btn { width: 100%; }
  .paper-cards { grid-template-columns: 1fr; }
}
</style>