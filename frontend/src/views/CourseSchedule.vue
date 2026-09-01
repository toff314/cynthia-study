<template>
  <div class="course-schedule-page" :class="{ 'print-mode': isPrinting }">
    <QuickNav v-if="!isPrinting" />
    <div class="container">
      <!-- 非打印模式：显示操作区 -->
      <div v-if="!isPrinting" class="editor-section">
        <router-link to="/" class="btn-back">← 返回首页</router-link>
        <h1 class="page-title">📚 课程表生成器</h1>

        <!-- 基本信息填写 -->
        <div class="info-form">
          <div class="form-row">
            <div class="form-item">
              <label>学校名称</label>
              <input type="text" v-model="form.schoolName" placeholder="如：建华实验学校" />
            </div>
            <div class="form-item">
              <label>年级班级</label>
              <input type="text" v-model="form.className" placeholder="如：二年级9班" />
            </div>
            <div class="form-item">
              <label>学期</label>
              <input type="text" v-model="form.semester" placeholder="如：2026-2027第一学期" />
            </div>
            <div class="form-item">
              <label>学生姓名</label>
              <input type="text" v-model="form.studentName" placeholder="如：Cynthia" />
            </div>
            <div class="form-item">
              <label>开学日期</label>
              <input type="date" v-model="form.startDate" />
            </div>
            <div class="form-item">
              <label>放假日期</label>
              <input type="date" v-model="form.endDate" />
            </div>
          </div>
        </div>

        <!-- 主题选择 -->
        <div class="theme-selector">
          <span class="theme-label">🎨 海报主题：</span>
          <button v-for="t in themes" :key="t.id" class="btn-theme" :class="{ active: activeTheme === t.id }"
                  @click="activeTheme = t.id">
            {{ t.emoji }} {{ t.name }}
          </button>
        </div>

        <!-- 快捷操作按钮 -->
        <div class="action-bar">
          <button class="btn btn-render" @click="renderPreview">🎨 渲染预览</button>
          <button class="btn btn-print-action" @click="handlePrint">🖨️ 打印课程表</button>
          <button class="btn btn-download" @click="exportPng">📥 下载图片</button>
          <button class="btn btn-example" @click="fillExample">✨ 填入示例</button>
          <button class="btn btn-reset" @click="resetForm">🔄 重置</button>
        </div>
        <div v-if="previewMessage" class="preview-message">{{ previewMessage }}</div>

        <!-- 课程编辑区 -->
        <div class="edit-section">
          <h3 class="section-title">✏️ 编辑课程内容（双击单元格编辑课程名，下方小框填老师/教室）</h3>

          <!-- 时间段配置 -->
          <div class="time-slot-config">
            <h4>⏰ 课时段（每行一个，格式：开始-结束）</h4>
            <div class="time-slots-editor">
              <div v-for="(slot, idx) in timeSlots" :key="idx" class="time-slot-row">
                <input type="text" v-model="timeSlots[idx]" class="time-slot-input" />
                <button v-if="timeSlots.length > 1" class="btn-remove-slot" @click="removeTimeSlot(idx)">×</button>
                <button v-if="idx === timeSlots.length - 1" class="btn-add-slot" @click="addTimeSlot">+</button>
              </div>
            </div>
            <div class="preset-times">
              <span>快捷模板：</span>
              <button class="btn-preset" @click="loadGrade2Class9">📋 二年级9班课表</button>
              <button class="btn-preset" @click="applyPreset('primary')">小学模板</button>
              <button class="btn-preset" @click="applyPreset('middle')">中学模板</button>
            </div>
          </div>

          <!-- 课程表格编辑 -->
          <div class="table-edit-wrapper">
            <table class="edit-table">
              <thead>
                <tr>
                  <th class="col-time">时间</th>
                  <th v-for="d in weekdays" :key="d.key">{{ d.label }}</th>
                  <th class="col-note">备注</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(slot, rowIdx) in timeSlots" :key="rowIdx"
                    :class="{ 'row-break': isBreakRow(rowIdx), 'row-class': !isBreakRow(rowIdx) }">
                  <td class="cell-time">{{ slot }}</td>
                  <td v-for="d in weekdays" :key="d.key"
                      class="cell-course"
                      :class="{ 'cell-break': isBreakRow(rowIdx) }">
                    <div class="cell-course-main"
                         contenteditable="true"
                         @blur="endEdit($event, d.key, rowIdx)"
                         :data-day="d.key"
                         :data-row="rowIdx"
                    >{{ getCourse(d.key, rowIdx) }}</div>
                    <input type="text" class="cell-course-note"
                           :value="getCourseNote(d.key, rowIdx)"
                           @blur="updateCourseNote(d.key, rowIdx, $event)"
                           placeholder="老师/教室" />
                  </td>
                  <td class="cell-note"
                      contenteditable="true"
                      @blur="updateNote(rowIdx, $event)"
                  >{{ getNote(rowIdx) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="tips">
            💡 提示：双击课程名可编辑；每个课程格下方可填老师/教室（海报小字显示）；课后服务/社团等填备注列；留空则该格不显示边框
          </div>
        </div>
      </div>

      <!-- 渲染预览 / 打印区域 -->
      <div v-show="showPreview || isPrinting" class="preview-section" ref="previewRef">
        <div class="schedule-poster" :class="'theme-' + activeTheme">
          <!-- 装饰元素 -->
          <div class="deco deco-left">✏️📏🖍️📐</div>
          <div class="deco deco-right">🌈</div>
          <div class="deco deco-student"><span class="student-name-label">{{ form.studentName || '学生姓名' }}</span></div>
          <div class="deco deco-bottom-right">🎒</div>

          <!-- 标题区 -->
          <div class="poster-header">
            <h1 class="poster-title">{{ form.schoolName || 'XX学校' }}</h1>
            <h2 class="poster-subtitle">{{ form.className || 'X年级X班' }}课程表</h2>
            <div class="poster-semester">{{ form.semester || '' }}</div>
            <div v-if="form.startDate || form.endDate" class="poster-dates">
              <span v-if="form.startDate">🗓️ {{ form.startDate }}</span>
              <span v-if="form.startDate && form.endDate"> 至 </span>
              <span v-if="form.endDate">{{ form.endDate }}</span>
              <span v-if="semesterWeeks" class="poster-weeks">（共 {{ semesterWeeks }} 周）</span>
            </div>
          </div>

          <!-- 课程表主体 -->
          <div class="schedule-table-wrapper">
            <table class="schedule-table">
              <thead>
                <tr>
                  <th class="col-time">时间</th>
                  <th v-for="d in weekdays" :key="d.key">{{ d.label }}</th>
                  <th class="col-note-th">备注</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(slot, rowIdx) in timeSlots" :key="'r-' + rowIdx">
                  <!-- 休息/活动行（整行合并） -->
                  <tr v-if="isEmptyRow(rowIdx)" class="row-break-row">
                    <td class="break-cell" :colspan="weekdays.length + 2">{{ getNote(rowIdx) || '&nbsp;' }}</td>
                  </tr>
                  <!-- 普通课程行（连堂课已被合并吸收的行不渲染） -->
                  <tr v-else-if="!isRowHidden(rowIdx)" class="row-period">
                    <td class="time-cell">{{ mergedTimeText(rowIdx) }}</td>
                    <template v-for="d in weekdays" :key="d.key + '-' + rowIdx">
                      <td v-if="!mergeInfo.skip[`${d.key}-${rowIdx}`]"
                          class="course-cell"
                          :rowspan="mergeInfo.colSpan[`${d.key}-${rowIdx}`] > 1 ? mergeInfo.colSpan[`${d.key}-${rowIdx}`] : undefined"
                          :class="{
                            'has-content': hasCourseContent(d.key, rowIdx),
                            'cell-break-content': isBreakContent(d.key, rowIdx)
                          }"
                          :style="courseCellStyle(d.key, rowIdx)"
                      >
                        <span class="course-text">{{ displayCourse(d.key, rowIdx) }}</span><sup v-if="courseSeq[`${d.key}-${rowIdx}`]" class="course-seq">{{ seqText(courseSeq[`${d.key}-${rowIdx}`]) }}</sup>
                        <span v-if="getCourseNote(d.key, rowIdx)" class="course-note">{{ getCourseNote(d.key, rowIdx) }}</span>
                      </td>
                    </template>
                    <td class="note-cell">
                      <span v-if="getNote(rowIdx)" class="note-text">{{ getNote(rowIdx) }}</span>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <!-- 课程统计 -->
          <div v-if="courseStats.length" class="course-stats">
            <span class="course-stats-title">📊 课程统计：</span>
            <span v-for="s in courseStats" :key="s.name" class="course-stat-item">{{ s.name }}×{{ s.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, watch, onMounted, computed } from 'vue'
import QuickNav from '@/components/QuickNav.vue'

// ===== 星期定义 =====
const weekdays = [
  { key: 'mon', label: '星期一' },
  { key: 'tue', label: '星期二' },
  { key: 'wed', label: '星期三' },
  { key: 'thu', label: '星期四' },
  { key: 'fri', label: '星期五' }
]

// ===== 表单数据 =====
const form = reactive({
  schoolName: '',
  className: '',
  semester: '',
  studentName: '',
  startDate: '',
  endDate: ''
})

// ===== 默认时间段模板 =====
const defaultTimeSlotsPrimary = [
  '7:50-8:15', '8:20-9:00', '9:15-9:55', '9:55-10:10', '10:10-10:50',
  '11:05-11:45', '11:45-13:40', '13:40-14:20', '14:20-14:40', '14:40-15:20',
  '15:20-15:30', '15:30-16:10', '16:10-17:00', '17:00-17:30'
]

const defaultTimeSlotsMiddle = [
  '7:40-8:00', '8:10-8:55', '9:05-9:50', '9:50-10:10', '10:10-10:55',
  '11:05-11:50', '11:50-13:30', '13:30-14:15', '14:25-15:10', '15:20-16:05',
  '16:15-17:00', '17:10-17:40'
]

// ===== 核心数据 =====
const timeSlots = ref<string[]>([...defaultTimeSlotsPrimary])
// 课程数据：key = "day-row", value = 课程名称
const courseData = reactive<Record<string, string>>({})
// 课程格附注（老师/教室）：key = "day-row"
const courseNoteData = reactive<Record<string, string>>({})
// 备注/休息数据：rowIdx -> 文字
const noteData = reactive<Record<number, string>>({})

// ===== 主题 =====
const themes = [
  { id: 'green', name: '清新绿', emoji: '🍃' },
  { id: 'orange', name: '活力橙', emoji: '🍊' },
  { id: 'pink', name: '少女粉', emoji: '🌸' },
  { id: 'blue', name: '海洋蓝', emoji: '🌊' }
]
const activeTheme = ref('green')

// ===== 课程自动配色 =====
const COURSE_COLOR_PALETTE: [string, string][] = [
  ['#e3f2fd', '#0d47a1'],
  ['#fce4ec', '#ad1457'],
  ['#e8f5e9', '#2e7d32'],
  ['#f3e5f5', '#6a1b9a'],
  ['#fff3e0', '#e65100'],
  ['#e0f7fa', '#006064'],
  ['#f1f8e9', '#33691e'],
  ['#fff8e1', '#f57f17'],
  ['#fbe9e7', '#bf360c'],
  ['#ede7f6', '#4527a0']
]

function courseColor(name: string): [string, string] {
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0
  return COURSE_COLOR_PALETTE[h % COURSE_COLOR_PALETTE.length]
}

function courseCellStyle(day: string, rowIdx: number): Record<string, string> {
  const name = getCourse(day, rowIdx).trim()
  if (!name || isBreakContent(day, rowIdx)) return {}
  const [bg, fg] = courseColor(name)
  return { background: bg, color: fg }
}

// ===== 行/单元格判定 =====
function isBreakRow(rowIdx: number): boolean {
  const slot = timeSlots.value[rowIdx] || ''
  return slot.includes('-') && getTimeSpan(slot) <= 20
}

function getTimeSpan(slot: string): number {
  const parts = slot.split('-')
  if (parts.length !== 2) return 999
  try {
    const [h1, m1] = parts[0].trim().split(':').map(Number)
    const [h2, m2] = parts[1].trim().split(':').map(Number)
    return (h2 * 60 + m2) - (h1 * 60 + m1)
  } catch {
    return 999
  }
}

function isEmptyRow(rowIdx: number): boolean {
  const hasAnyCourse = weekdays.some(d => hasCourseContent(d.key, rowIdx))
  return !hasAnyCourse && (getNote(rowIdx) || '').length > 0
}

function isBreakContent(day: string, rowIdx: number): boolean {
  const val = getCourse(day, rowIdx)
  if (!val) return false
  const breakKeywords = ['操', '餐', '午休', '午间', '休息', '眼保', '加餐', '活动', '大课间', '晚']
  return breakKeywords.some(k => val.includes(k))
}

function hasCourseContent(day: string, rowIdx: number): boolean {
  return (getCourse(day, rowIdx) || '').trim().length > 0
}

function getCourse(day: string, rowIdx: number): string {
  return courseData[`${day}-${rowIdx}`] || ''
}

function getCourseNote(day: string, rowIdx: number): string {
  return courseNoteData[`${day}-${rowIdx}`] || ''
}

function displayCourse(day: string, rowIdx: number): string {
  return getCourse(day, rowIdx)
}

function getNote(rowIdx: number): string {
  return noteData[rowIdx] || ''
}

// ===== 编辑区交互 =====
function endEdit(evt: FocusEvent, day: string, rowIdx: number) {
  const target = evt.target as HTMLElement
  const val = target.innerText?.trim() || ''
  const key = `${day}-${rowIdx}`
  if (val) {
    courseData[key] = val
  } else {
    delete courseData[key]
  }
}

function updateCourseNote(day: string, rowIdx: number, evt: Event) {
  const val = (evt.target as HTMLInputElement).value.trim()
  const key = `${day}-${rowIdx}`
  if (val) {
    courseNoteData[key] = val
  } else {
    delete courseNoteData[key]
  }
}

function updateNote(rowIdx: number, evt: FocusEvent) {
  const target = evt.target as HTMLElement
  const val = target.innerText?.trim() || ''
  if (val) {
    noteData[rowIdx] = val
  } else {
    delete noteData[rowIdx]
  }
}

// ===== 时间段管理 =====
function addTimeSlot() {
  timeSlots.value.push('')
}

function removeTimeSlot(idx: number) {
  timeSlots.value.splice(idx, 1)

  // 重新索引课程数据
  const newKeys: Record<string, string> = {}
  for (const [k, v] of Object.entries(courseData)) {
    const parts = k.split('-')
    const oldRow = parseInt(parts[parts.length - 1])
    let newRow = oldRow
    if (oldRow > idx) newRow = oldRow - 1
    newKeys[`${parts.slice(0, -1).join('-')}-${newRow}`] = v
  }
  Object.keys(courseData).forEach(k => delete courseData[k])
  Object.assign(courseData, newKeys)

  // 重新索引课程附注
  const newNotes2: Record<string, string> = {}
  for (const [k, v] of Object.entries(courseNoteData)) {
    const parts = k.split('-')
    const oldRow = parseInt(parts[parts.length - 1])
    let newRow = oldRow
    if (oldRow > idx) newRow = oldRow - 1
    newNotes2[`${parts.slice(0, -1).join('-')}-${newRow}`] = v
  }
  Object.keys(courseNoteData).forEach(k => delete courseNoteData[k])
  Object.assign(courseNoteData, newNotes2)

  // 重新索引备注
  const newNotes: Record<number, string> = {}
  for (const [k, v] of Object.entries(noteData)) {
    const oldRow = parseInt(k)
    let newRow = oldRow
    if (oldRow > idx) newRow = oldRow - 1
    newNotes[newRow] = v
  }
  Object.keys(noteData).forEach(k => delete noteData[k])
  Object.assign(noteData, newNotes)
}

// ===== 模板应用 =====
function applyPreset(type: 'primary' | 'middle') {
  if (!confirm('应用模板将覆盖当前时间段设置，确定吗？')) return

  if (type === 'primary') {
    timeSlots.value = [...defaultTimeSlotsPrimary]
  } else {
    timeSlots.value = [...defaultTimeSlotsMiddle]
  }

  Object.keys(courseData).forEach(k => delete courseData[k])
  Object.keys(courseNoteData).forEach(k => delete courseNoteData[k])
  Object.keys(noteData).forEach(k => delete noteData[k])

  if (type === 'primary') {
    noteData[3] = '眼保健操、加餐'
    noteData[6] = '午饭/午休/午间习字'
    noteData[8] = '眼保健操'
    noteData[10] = '课间休息'
    noteData[13] = '体育活动/晚托'
  } else {
    noteData[3] = '大课间'
    noteData[6] = '午饭/午休'
    noteData[11] = '自习/答疑'
  }
}

// ===== 二年级9班课表模板（来源于课程安排表 a.xlsx）=====
const GRADE2_CLASS9_TEMPLATE = {
  form: { schoolName: '建华实验学校', className: '二年级9班', semester: '2026-2027学年第一学期', studentName: 'Cynthia', startDate: '', endDate: '' },
  timeSlots: [
    '7:50-8:15', '8:20-9:00', '9:00-9:30', '9:30-10:10', '10:10-10:25',
    '10:25-11:05', '11:20-12:00', '12:00-13:20', '13:20-13:30', '13:30-14:10',
    '14:10-14:15', '14:25-15:05', '15:05-15:30', '15:30-16:10', '16:20-17:00',
    '17:05-17:25', '17:30'
  ],
  courses: {
    'mon-1': '道德与法治', 'tue-1': '数学', 'wed-1': '音乐', 'thu-1': '语文', 'fri-1': '数学',
    'mon-3': '美术', 'tue-3': '数学学科拓展', 'wed-3': '英语', 'thu-3': '数学', 'fri-3': '语文',
    'mon-5': '语文', 'tue-5': '语文', 'wed-5': '语文', 'thu-5': '英语试听', 'fri-5': '体育',
    'mon-6': '英语', 'tue-6': '外教', 'wed-6': '数学', 'thu-6': '语文', 'fri-6': '美术',
    'mon-9': '体育外教', 'tue-9': '语文', 'wed-9': '科学', 'thu-9': '班队会', 'fri-9': '跨学科课程',
    'mon-11': '音乐', 'tue-11': '形体', 'wed-11': '体育', 'thu-11': '体育', 'fri-11': '红领巾心向党',
    'mon-13': '英语学科拓展', 'tue-13': '劳动', 'wed-13': '语文学科拓展', 'thu-13': '数学学科拓展', 'fri-13': '十大场',
    'mon-14': '综合选修', 'tue-14': '综合选修', 'wed-14': '综合选修', 'thu-14': '综合选修', 'fri-14': '班级大扫除'
  },
  notes: {
    0: '晨读（自愿参加）',
    2: '体育阳光跑',
    4: '眼保健操、加餐',
    7: '午餐/午自习/午休',
    8: '午间习字',
    10: '眼保健操',
    12: '体育大课间',
    15: '体育活动/晚餐',
    16: '放学'
  }
}

function loadGrade2Class9() {
  Object.assign(form, GRADE2_CLASS9_TEMPLATE.form)
  timeSlots.value = [...GRADE2_CLASS9_TEMPLATE.timeSlots]
  Object.keys(courseData).forEach(k => delete courseData[k])
  Object.keys(courseNoteData).forEach(k => delete courseNoteData[k])
  Object.keys(noteData).forEach(k => delete noteData[k])
  Object.assign(courseData, GRADE2_CLASS9_TEMPLATE.courses)
  Object.assign(noteData, GRADE2_CLASS9_TEMPLATE.notes)
  showPreview.value = true
}

// ===== 预览控制 =====
const showPreview = ref(false)
const previewRef = ref<HTMLElement | null>(null)
const previewMessage = ref('')

async function renderPreview() {
  showPreview.value = true
  previewMessage.value = '✅ 预览已生成（海报在下方，输入框不受影响）'
  setTimeout(() => { previewMessage.value = '' }, 3500)
}

// ===== 打印 =====
const isPrinting = ref(false)

function handlePrint() {
  if (!showPreview.value) showPreview.value = true
  nextTick(() => {
    isPrinting.value = true
    setTimeout(() => {
      window.print()
      setTimeout(() => { isPrinting.value = false }, 1000)
    }, 300)
  })
}

// ===== 重置 =====
function resetForm() {
  if (!confirm('确定要重置所有内容吗？')) return
  form.schoolName = ''
  form.className = ''
  form.semester = ''
  form.studentName = ''
  form.startDate = ''
  form.endDate = ''
  timeSlots.value = [...defaultTimeSlotsPrimary]
  Object.keys(courseData).forEach(k => delete courseData[k])
  Object.keys(courseNoteData).forEach(k => delete courseNoteData[k])
  Object.keys(noteData).forEach(k => delete noteData[k])
  showPreview.value = false
}

// ===== 填入示例数据 =====
function fillExample() {
  form.schoolName = '建华实验学校'
  form.className = '一年级9班'
  form.semester = '2025-2026学年第一学期'
  form.studentName = 'Cynthia'

  timeSlots.value = [...defaultTimeSlotsPrimary]
  Object.keys(courseData).forEach(k => delete courseData[k])
  Object.keys(courseNoteData).forEach(k => delete courseNoteData[k])
  Object.keys(noteData).forEach(k => delete noteData[k])

  const weekCourses = [
    ['晨读', '晨读', '晨读', '晨读', '晨读'],
    ['语文', '数学', '语文', '数学', '语文'],
    ['数学', '语文', '数学', '语文', '数学'],
    ['眼保健操、加餐', '眼保健操、加餐', '眼保健操、加餐', '眼保健操、加餐', '眼保健操、加餐'],
    ['英语', '科学', '英语', '科学', '英语'],
    ['体育', '音乐', '道德与法治', '美术', '体育'],
    ['午饭/午休/午间习字', '午饭/午休/午间习字', '午饭/午休/午间习字', '午饭/午休/午间习字', '午饭/午休/午间习字'],
    ['语文', '数学', '语文', '数学', '语文'],
    ['眼保健操', '眼保健操', '眼保健操', '眼保健操', '眼保健操'],
    ['数学', '语文', '英语', '语文', '数学'],
    ['课间休息', '课间休息', '课间休息', '课间休息', '课间休息'],
    ['体育', '美术', '音乐', '体育', '英语'],
    ['课后服务/自习', '课后服务/自习', '课后服务/自习', '课后服务/自习', '课后服务/自习'],
    ['体育活动/晚托', '体育活动/晚托', '体育活动/晚托', '体育活动/晚托', '体育活动/晚托']
  ]

  weekCourses.forEach((row, rowIdx) => {
    row.forEach((course, dayIdx) => {
      if (course) courseData[`${weekdays[dayIdx].key}-${rowIdx}`] = course
    })
  })

  noteData[3] = '眼保健操、加餐'
  noteData[6] = '午饭/午休/午间习字'
  noteData[8] = '眼保健操'
  noteData[10] = '课间休息'
  noteData[13] = '体育活动/晚托'

  showPreview.value = true
}

// ===== 课程出现序号与统计 =====
const courseSeq = computed<Record<string, number>>(() => {
  const counter: Record<string, number> = {}
  const seq: Record<string, number> = {}
  timeSlots.value.forEach((_, rowIdx) => {
    weekdays.forEach(d => {
      const key = `${d.key}-${rowIdx}`
      const name = (courseData[key] || '').trim()
      if (!name) return
      counter[name] = (counter[name] || 0) + 1
      seq[key] = counter[name]
    })
  })
  return seq
})

const courseStats = computed(() => {
  const counter: Record<string, number> = {}
  timeSlots.value.forEach((_, rowIdx) => {
    weekdays.forEach(d => {
      const name = (courseData[`${d.key}-${rowIdx}`] || '').trim()
      if (!name) return
      counter[name] = (counter[name] || 0) + 1
    })
  })
  return Object.entries(counter)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh'))
})

const seqDigits = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
function seqText(n: number): string {
  return String(n).split('').map(ch => seqDigits[Number(ch)]).join('')
}

// ===== 学期周数 =====
const semesterWeeks = computed(() => {
  if (!form.startDate || !form.endDate) return 0
  const s = new Date(form.startDate).getTime()
  const e = new Date(form.endDate).getTime()
  if (!s || !e || e < s) return 0
  const days = Math.round((e - s) / 86400000) + 1
  return Math.ceil(days / 7)
})

// ===== 连堂课合并 =====
const mergeInfo = computed(() => {
  const colSpan: Record<string, number> = {}
  const skip: Record<string, boolean> = {}
  weekdays.forEach(d => {
    let prevName = ''
    let runStart = -1
    timeSlots.value.forEach((_, r) => {
      const key = `${d.key}-${r}`
      const name = getCourse(d.key, r).trim()
      if (!name) {
        prevName = ''
        runStart = -1
        colSpan[key] = 1
        skip[key] = false
        return
      }
      if (name === prevName && runStart >= 0) {
        colSpan[`${d.key}-${runStart}`] = (colSpan[`${d.key}-${runStart}`] || 1) + 1
        skip[key] = true
      } else {
        runStart = r
        colSpan[key] = 1
        skip[key] = false
      }
      prevName = name
    })
  })
  return { colSpan, skip }
})

function isRowHidden(rowIdx: number): boolean {
  return weekdays.every(d => mergeInfo.value.skip[`${d.key}-${rowIdx}`])
}

function mergedTimeText(rowIdx: number): string {
  const day = weekdays.find(d => (mergeInfo.value.colSpan[`${d.key}-${rowIdx}`] || 1) > 1)
  const span = day ? mergeInfo.value.colSpan[`${day.key}-${rowIdx}`] : 1
  if (!day || span <= 1) return timeSlots.value[rowIdx] || ''
  const first = (timeSlots.value[rowIdx] || '').split('-')[0]?.trim() || ''
  const last = (timeSlots.value[rowIdx + span - 1] || '').split('-')[1]?.trim() || ''
  return first && last ? `${first}-${last}` : timeSlots.value[rowIdx] || ''
}

// ===== PNG DPI 嵌入（pHYs chunk），保证图片按物理尺寸打印 =====
function crc32(data: Uint8Array): number {
  let crc = 0xffffffff
  for (let i = 0; i < data.length; i++) {
    crc ^= data[i]
    for (let j = 0; j < 8; j++) {
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1))
    }
  }
  return (crc ^ 0xffffffff) >>> 0
}

async function embedPngDpi(blob: Blob, dpi: number): Promise<Blob> {
  // 将像素/米写入 pHYs chunk（1 inch = 0.0254 m）
  const ppm = Math.round(dpi / 0.0254)
  const phys = new Uint8Array(21)
  const dv = new DataView(phys.buffer)
  dv.setUint32(0, 9)                       // chunk length
  phys.set([0x70, 0x48, 0x59, 0x73], 4)     // 'pHYs'
  dv.setUint32(8, ppm)                     // x pixels/meter
  dv.setUint32(12, ppm)                    // y pixels/meter
  phys[16] = 1                             // unit: meter
  dv.setUint32(17, crc32(phys.subarray(4, 17)))  // CRC

  const bytes = new Uint8Array(await blob.arrayBuffer())
  const out = new Uint8Array(bytes.length + phys.length)
  out.set(bytes.subarray(0, 33))           // 8 字节签名 + IHDR chunk(25)
  out.set(phys, 33)
  out.set(bytes.subarray(33), 33 + phys.length)
  return new Blob([out], { type: 'image/png' })
}

// ===== 导出图片（SVG foreignObject + canvas，无外部依赖）=====
async function exportPng() {
  if (!showPreview.value) showPreview.value = true
  await nextTick()
  const node = document.querySelector('.schedule-poster') as HTMLElement | null
  if (!node) return

  try {
    const w = node.offsetWidth
    const h = node.offsetHeight
    if (!w || !h) throw new Error('poster size zero')

    // 递归内联计算样式：样式必须从文档中的原始节点获取（getComputedStyle 对脱离文档的节点返回空）
    const clone = node.cloneNode(true) as HTMLElement
    const SKIP_PROPS = new Set([
      'transform', 'transform-origin', 'transition', 'transition-property',
      'transition-duration', 'transition-timing-function', 'transition-delay',
      'animation', 'animation-name', 'animation-duration', 'animation-timing-function',
      'animation-delay', 'animation-iteration-count', 'animation-direction',
      'animation-fill-mode', 'animation-play-state'
    ])
    const cloneWithStyles = (source: Element, target: Element) => {
      const computed = window.getComputedStyle(source)
      const props: string[] = []
      for (let i = 0; i < computed.length; i++) {
        const p = computed[i]
        if (SKIP_PROPS.has(p)) continue
        props.push(`${p}:${computed.getPropertyValue(p)}`)
      }
      const elStyle = (target as HTMLElement).getAttribute('style')
      ;(target as HTMLElement).setAttribute('style', props.join(';') + (elStyle ? ';' + elStyle : ''))
      const srcChildren = Array.from(source.children)
      const cloneChildren = Array.from(target.children)
      srcChildren.forEach((child, i) => {
        if (cloneChildren[i]) cloneWithStyles(child, cloneChildren[i])
      })
    }
    cloneWithStyles(node, clone)

    // A4 横向 300dpi 画布：3508×2480，海报等比缩放居中，四周留白
    const A4_W = 3508
    const A4_H = 2480
    const marginRatio = 0.08
    const availW = A4_W * (1 - marginRatio * 2)
    const availH = A4_H * (1 - marginRatio * 2)
    const fitScale = Math.min(availW / w, availH / h)
    const drawW = Math.round(w * fitScale)
    const drawH = Math.round(h * fitScale)
    const offX = Math.round((A4_W - drawW) / 2)
    const offY = Math.round((A4_H - drawH) / 2)

    // 克隆根节点按 fitScale 放大，保证导出 1:1 清晰
    ;(clone as HTMLElement).style.transform = `scale(${fitScale})`
    ;(clone as HTMLElement).style.transformOrigin = '0 0'

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${drawW}" height="${drawH}">
      <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">${clone.outerHTML}</div>
      </foreignObject>
    </svg>`

    const img = new Image()
    img.decoding = 'sync'
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve()
      img.onerror = () => reject(new Error('svg render failed'))
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
    })

    const canvas = document.createElement('canvas')
    canvas.width = A4_W
    canvas.height = A4_H
    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('no canvas context')
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, A4_W, A4_H)
    ctx.imageSmoothingQuality = 'high'
    ctx.drawImage(img, offX, offY, drawW, drawH)

    let blob = await new Promise<Blob | null>(res => canvas.toBlob(res, 'image/png'))
    if (!blob) throw new Error('toBlob failed')
    // 嵌入 300dpi（pHYs chunk），保证打印时按物理尺寸 A4 输出
    blob = await embedPngDpi(blob, 300)

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `课程表-${form.className || '默认'}.png`
    document.body.appendChild(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(url), 5000)
  } catch (e) {
    console.error('导出图片失败:', e)
    alert('导出图片失败，请重试，或改用"打印课程表"功能（可另存为 PDF）')
  }
}

// ===== 本地持久化 =====
const STORAGE_KEY = 'course_schedule_v1'

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      form: { ...form },
      timeSlots: timeSlots.value,
      courseData: { ...courseData },
      courseNoteData: { ...courseNoteData },
      noteData: { ...noteData },
      activeTheme: activeTheme.value
    }))
  } catch (e) {
    // 忽略存储错误（隐私模式等）
  }
}

function restore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return false
    const data = JSON.parse(raw)
    if (data.form) Object.assign(form, data.form)
    if (Array.isArray(data.timeSlots) && data.timeSlots.length > 0) {
      timeSlots.value = data.timeSlots
    }
    if (data.courseData) Object.assign(courseData, data.courseData)
    if (data.courseNoteData) Object.assign(courseNoteData, data.courseNoteData)
    if (data.noteData) Object.assign(noteData, data.noteData)
    if (data.activeTheme && themes.some(t => t.id === data.activeTheme)) {
      activeTheme.value = data.activeTheme
    }
    return true
  } catch (e) {
    return false
  }
}

watch([form, timeSlots, courseData, courseNoteData, noteData, activeTheme], persist, { deep: true })

onMounted(() => {
  const restored = restore()
  if (!restored) {
    // 首次使用：默认加载二年级9班课表
    loadGrade2Class9()
  }
})
</script>

<style scoped src="./CourseSchedule.css"></style>