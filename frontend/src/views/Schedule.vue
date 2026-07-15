<template>
  <div class="schedule">
    <QuickNav />
    <div class="container">
      <div class="header-info">
        <router-link to="/" class="btn-back">← 返回首页</router-link>
        <h1>🎄 寒假每日任务日程表 🎄</h1>
        <div class="week-display" id="winterWeekText"></div>
        <div class="input-group">
          <div class="input-field">
            <label>姓名：</label>
            <input type="text" v-model="store.scheduleData.student_name" placeholder="请输入姓名" />
          </div>
          <div class="input-field">
            <label>班级：</label>
            <input type="text" v-model="store.scheduleData.student_class" placeholder="请输入班级" />
          </div>
          <button class="btn btn-load" @click="handleLoadOrCreate">📥 一键创建/拉取</button>
        </div>
      </div>

      <div class="task-config">
        <label>默认任务配置（英文逗号分隔）：</label>
        <div class="task-config-row">
          <input 
            type="text" 
            v-model="taskConfig" 
            placeholder="例如：晨读, 完成作业, 体育锻炼"
            class="task-config-input"
          />
          <button class="btn btn-import" @click="importDefaultTasks">🔄 一键导入</button>
        </div>
      </div>

      <div class="controls">
        <button class="btn btn-save" @click="saveSchedule">💾 保存日程表</button>
        <button class="btn btn-clear-week" @click="clearCurrentWeek">🗑️ 清空本周</button>
        <button class="btn btn-print" @click="printSchedule">🖨️ 打印日程表</button>
      </div>

      <div class="save-message" v-if="loadMessage">{{ loadMessage }}</div>
      <div class="save-message" v-if="saveMessage">✅ 保存成功！</div>

      <div class="schedule-card">
        <div class="schedule-header">
          <h2>每周任务安排</h2>
          <p>{{ store.scheduleData.student_name }} - {{ store.scheduleData.student_class }}</p>
        </div>

        <div class="week-info">
          <button @click="changeWeek(-1)">◀ 上一周</button>
          <span id="weekRange">{{ weekRangeText }}</span>
          <button @click="changeWeek(1)">下一周 ▶</button>
        </div>

        <div class="days-container">
          <div 
            v-for="(day, index) in currentWeekDays" 
            :key="index" 
            class="day-column"
            :class="{ today: isToday(day.date) }"
          >
            <div class="day-header">
              <div class="day-name">{{ day.dayName }}</div>
              <div class="day-date">{{ formatDate(day.date) }}</div>
            </div>
            <div class="tasks-list">
              <div v-for="(task, taskIndex) in day.tasks" :key="taskIndex" class="task-item">
                <div class="task-header">
                  <div class="task-name">
                    <input 
                      type="text" 
                      class="task-name-input" 
                      :value="task.task_name"
                      @input="handleUpdateTaskName(index, taskIndex, $event)"
                      placeholder="任务名称"
                    />
                  </div>
                  <button class="delete-task-btn" @click="handleDeleteTask(index, taskIndex)">×</button>
                </div>
                <div class="stars">
                  <span 
                    v-for="i in 5" 
                    :key="i"
                    :class="i <= task.stars ? 'star filled' : 'star empty'"
                    @click="handleSetStar(index, taskIndex, i)"
                  ></span>
                </div>
              </div>
            </div>
            <button class="add-task-btn" @click="handleAddTask(index)">+ 添加任务</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useScheduleStore } from '@/stores/schedule'
import QuickNav from '@/components/QuickNav.vue'

const store = useScheduleStore()
const saveMessage = ref('')
const loadMessage = ref('')
const currentWeekOffset = ref(0)
const taskConfig = ref('晨读, 完成作业, 体育锻炼, 阅读, 家务')

const parsedDefaultTasks = computed(() => {
  const tasks = taskConfig.value
    .split(',')
    .map(t => t.trim())
    .filter(t => t.length > 0)
  return tasks.map(name => ({ task_name: name, stars: 0 }))
})

const weekRangeText = computed(() => {
  const days = getCurrentWeek()
  return `${formatDate(days[0].date)} 至 ${formatDate(days[6].date)}`
})

const currentWeekDays = computed(() => getCurrentWeek())

const formatDate = (date: Date) => {
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const isToday = (date: Date) => {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

const getCurrentWeek = () => {
  const today = new Date()
  const monday = new Date(today)
  const dayOfWeek = today.getDay()
  const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1
  monday.setDate(today.getDate() - diff + (currentWeekOffset.value * 7))

  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const days = []

  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    const savedTasks = store.scheduleData.weekly_tasks[dateKey]?.tasks
    
    days.push({
      date,
      dayName: dayNames[i],
      dateKey,
      tasks: savedTasks && savedTasks.length > 0 ? savedTasks : []
    })
  }

  return days
}

const addTask = (dayIndex: number) => {
  const days = currentWeekDays.value
  const dateKey = days[dayIndex].dateKey
  store.addTask(dateKey, { task_name: '', stars: 0 })
}

const deleteTask = (dayIndex: number, taskIndex: number) => {
  const days = currentWeekDays.value
  const dateKey = days[dayIndex].dateKey
  store.deleteTask(dateKey, taskIndex)
}

const setStar = (dayIndex: number, taskIndex: number, starCount: number) => {
  const days = currentWeekDays.value
  const dateKey = days[dayIndex].dateKey
  const task = days[dayIndex].tasks[taskIndex]
  store.updateTask(dateKey, taskIndex, { ...task, stars: starCount })
}

const updateTaskName = (dayIndex: number, taskIndex: number, task_name: string) => {
  const days = currentWeekDays.value
  const dateKey = days[dayIndex].dateKey
  const task = days[dayIndex].tasks[taskIndex]
  store.updateTask(dateKey, taskIndex, { ...task, task_name })
}

// 模板事件处理包装函数（接受 string | number 类型）
const handleUpdateTaskName = (index: string | number, taskIndex: number, event: Event) => {
  updateTaskName(Number(index), taskIndex, (event.target as HTMLInputElement).value)
}

const handleDeleteTask = (index: string | number, taskIndex: number) => {
  deleteTask(Number(index), taskIndex)
}

const handleSetStar = (index: string | number, taskIndex: number, starCount: number) => {
  setStar(Number(index), taskIndex, starCount)
}

const handleAddTask = (index: string | number) => {
  addTask(Number(index))
}

// 一键创建/拉取学生日程表
const handleLoadOrCreate = async () => {
  const studentName = store.scheduleData.student_name
  const studentClass = store.scheduleData.student_class
  
  if (!studentName || studentName.trim() === '') {
    loadMessage.value = '❌ 请先输入姓名'
    setTimeout(() => { loadMessage.value = '' }, 2000)
    return
  }
  
  if (!studentClass || studentClass.trim() === '') {
    loadMessage.value = '❌ 请先输入班级'
    setTimeout(() => { loadMessage.value = '' }, 2000)
    return
  }
  
  try {
    const result = await store.loadOrCreateSchedule(studentName, studentClass)
    loadMessage.value = `✅ ${result.message}`
    setTimeout(() => { loadMessage.value = '' }, 2000)
  } catch (error: any) {
    loadMessage.value = `❌ ${error.message || '操作失败'}`
    setTimeout(() => { loadMessage.value = '' }, 2000)
  }
}

const saveSchedule = async () => {
  const success = await store.saveSchedule()
  if (success) {
    saveMessage.value = '✅ 保存成功！'
    setTimeout(() => { saveMessage.value = '' }, 2000)
  }
}

// 检测是否为微信手机浏览器
const isWeChatMobile = (): boolean => {
  const ua = navigator.userAgent.toLowerCase()
  return /micromessenger/i.test(ua) && /mobile/i.test(ua)
}

const printSchedule = () => {
  // 检测是否为微信手机浏览器
  if (isWeChatMobile()) {
    loadMessage.value = '💡 为保证打印效果，请使用电脑浏览器访问本页面进行导出'
    setTimeout(() => { loadMessage.value = '' }, 5000)
    return
  }
  
  saveSchedule().then(() => {
    setTimeout(() => window.print(), 100)
  })
}

const clearCurrentWeek = () => {
  const days = currentWeekDays.value
  const startDateStr = formatDate(days[0].date)
  const endDateStr = formatDate(days[6].date)
  
  if (confirm(`确定要清空本周（${startDateStr} 至 ${endDateStr}）的所有任务吗？此操作不可恢复！`)) {
    days.forEach(day => {
      store.scheduleData.weekly_tasks[day.dateKey] = { tasks: [] }
    })
  }
}

const importDefaultTasks = async () => {
  if (confirm('确定要用配置的默认任务覆盖当前日程表吗？此操作不可恢复！')) {
    const tasks = parsedDefaultTasks.value
    const days = currentWeekDays.value
    
    days.forEach(day => {
      store.scheduleData.weekly_tasks[day.dateKey] = { 
        tasks: JSON.parse(JSON.stringify(tasks))
      }
    })
    
    // 自动保存
    await store.saveSchedule()
    saveMessage.value = '✅ 默认任务导入成功！'
    setTimeout(() => { saveMessage.value = '' }, 2000)
  }
}

const changeWeek = (offset: number) => {
  currentWeekOffset.value += offset
}

onMounted(() => {
  // 先从 cookie 加载学生信息
  const { studentName, studentClass } = store.loadStudentInfoFromCookie()
  
  if (studentName && studentClass) {
    // 如果有 cookie 信息，恢复到输入框
    store.scheduleData.student_name = studentName
    store.scheduleData.student_class = studentClass
    
    // 然后尝试加载该学生的日程表
    handleLoadOrCreateQuiet()
  } else {
    // 如果没有 cookie 信息，加载默认日程表
    store.loadSchedule()
  }
})

// 静默加载（不显示错误消息）
const handleLoadOrCreateQuiet = async () => {
  const studentName = store.scheduleData.student_name || ''
  const studentClass = store.scheduleData.student_class || ''
  
  try {
    const result = await store.loadOrCreateSchedule(studentName, studentClass)
    console.log(result.message)
  } catch (error) {
    console.error('静默加载失败，使用默认日程表')
    // 如果加载失败，加载默认日程表
    store.loadSchedule()
  }
}
</script>

<style scoped src="./Schedule.css"></style>
