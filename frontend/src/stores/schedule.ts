import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ScheduleData, Task, WeeklyTasks, ApiResponse } from '@/types'
import { scheduleApi } from '@/api/schedule'
import Cookies from 'js-cookie'

export const useScheduleStore = defineStore('schedule', () => {
  const scheduleData = ref<ScheduleData>({
    student_name: '',
    student_class: '',
    week_offset: 0,
    weekly_tasks: {}
  })

  const loading = ref(false)

  // 计算属性
  const studentName = computed(() => scheduleData.value.student_name)
  const studentClass = computed(() => scheduleData.value.student_class)
  const weekOffset = computed(() => scheduleData.value.week_offset)

  // 加载日程表
  const loadSchedule = async () => {
    loading.value = true
    try {
      const res = await scheduleApi.getSchedule()
      if (res.success) {
        scheduleData.value = res.data
      }
    } catch (error) {
      console.error('加载日程表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 根据学生信息加载或创建日程表
  const loadOrCreateSchedule = async (studentName: string, studentClass: string) => {
    // 验证必填项
    if (!studentName || !studentName.trim()) {
      throw new Error('学生姓名不能为空')
    }
    if (!studentClass || !studentClass.trim()) {
      throw new Error('学生班级不能为空')
    }

    loading.value = true
    try {
      // 先尝试获取该学生的日程表
      const res = await scheduleApi.getSchedule({
        student_name: studentName,
        student_class: studentClass
      })

      if (res.success && res.data.id) {
        // 找到了现有日程表，加载它
        scheduleData.value = res.data
        // 保存到 cookie（包含 scheduleId）
        saveStudentInfoToCookie(studentName, studentClass, res.data.id)
        return { success: true, message: '拉取成功' }
      } else {
        // 没有找到，创建新的空日程表
        scheduleData.value = {
          student_name: studentName,
          student_class: studentClass,
          week_offset: 0,
          weekly_tasks: {}
        }
        // 保存新日程表到数据库
        const saveRes = await scheduleApi.saveSchedule(scheduleData.value) as ApiResponse<{ id: number }>
        // 保存到 cookie（包含 scheduleId）
        saveStudentInfoToCookie(studentName, studentClass, saveRes.data?.id)
        return { success: true, message: '创建成功' }
      }
    } catch (error) {
      console.error('加载或创建日程表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 保存学生信息到 cookie
  const saveStudentInfoToCookie = (studentName: string, studentClass: string, scheduleId?: number) => {
    Cookies.set('student_name', studentName, { expires: 30 })
    Cookies.set('student_class', studentClass, { expires: 30 })
    if (scheduleId) {
      Cookies.set('schedule_id', scheduleId.toString(), { expires: 30 })
    }
  }

  // 从 cookie 读取学生信息
  const loadStudentInfoFromCookie = () => {
    const studentName = Cookies.get('student_name') || ''
    const studentClass = Cookies.get('student_class') || ''
    return { studentName, studentClass }
  }

  // 从 cookie 读取 scheduleId
  const getScheduleIdFromCookie = (): number | null => {
    const scheduleId = Cookies.get('schedule_id')
    return scheduleId ? parseInt(scheduleId, 10) : null
  }

  // 清除 cookie 中的学生信息
  const clearStudentInfoCookie = () => {
    Cookies.remove('student_name')
    Cookies.remove('student_class')
    Cookies.remove('schedule_id')
  }

  // 清理空任务
  const _cleanEmptyTasks = (tasks: Task[]) => {
    return tasks.filter(task => task.task_name && task.task_name.trim() !== '')
  }

  // 保存日程表
  const saveSchedule = async () => {
    loading.value = true
    try {
      // 清理数据：移除null值和空任务
      const cleanedData: ScheduleData = {
        ...scheduleData.value,
        weekly_tasks: {}
      }
      
      for (const [dateKey, dayData] of Object.entries(scheduleData.value.weekly_tasks)) {
        const cleanedTasks = _cleanEmptyTasks(dayData.tasks)
        if (cleanedTasks.length > 0) {
          cleanedData.weekly_tasks[dateKey] = {
            tasks: cleanedTasks
          }
        }
      }
      
      const res = await scheduleApi.saveSchedule(cleanedData) as ApiResponse
      return res.success
    } catch (error) {
      console.error('保存日程表失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新任务
  const updateTask = (dateKey: string, taskIndex: number, task: Task) => {
    if (!scheduleData.value.weekly_tasks[dateKey]) {
      scheduleData.value.weekly_tasks[dateKey] = { tasks: [] }
    }
    // 确保数组长度足够，填充空对象防止出现null
    const tasks = scheduleData.value.weekly_tasks[dateKey].tasks
    while (tasks.length <= taskIndex) {
      tasks.push({ task_name: '', stars: 0 })
    }
    tasks[taskIndex] = task
  }

  // 添加任务
  const addTask = (dateKey: string, task: Task) => {
    if (!scheduleData.value.weekly_tasks[dateKey]) {
      scheduleData.value.weekly_tasks[dateKey] = { tasks: [] }
    }
    scheduleData.value.weekly_tasks[dateKey].tasks.push(task)
  }

  // 删除任务
  const deleteTask = (dateKey: string, taskIndex: number) => {
    if (scheduleData.value.weekly_tasks[dateKey]) {
      scheduleData.value.weekly_tasks[dateKey].tasks.splice(taskIndex, 1)
    }
  }

  // 清空所有
  const clearAll = async () => {
    loading.value = true
    try {
      const res = await scheduleApi.clearSchedule()
      if (res.success) {
        scheduleData.value = {
          student_name: '',
          student_class: '',
          week_offset: 0,
          weekly_tasks: {}
        }
      }
      return res.success
    } catch (error) {
      console.error('清空日程表失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    scheduleData,
    loading,
    studentName,
    studentClass,
    weekOffset,
    loadSchedule,
    loadOrCreateSchedule,
    saveSchedule,
    updateTask,
    addTask,
    deleteTask,
    clearAll,
    saveStudentInfoToCookie,
    loadStudentInfoFromCookie,
    getScheduleIdFromCookie,
    clearStudentInfoCookie
  }
})
