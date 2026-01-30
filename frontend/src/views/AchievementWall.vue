<template>
  <div class="achievement-wall">
    <QuickNav />
    <div class="container">
      <div class="header">
        <h1>🏆 寒假成就墙 🏆</h1>
        <p>展示成就徽章，记录成长足迹</p>
      </div>

      <div class="tabs">
        <div :class="['tab', { active: currentTab === 'all' }]" @click="currentTab = 'all'">
          📊 全榜排名
        </div>
        <div :class="['tab', { active: currentTab === 'personal' }]" @click="currentTab = 'personal'">
          👤 我的成就
        </div>
        <div :class="['tab', { active: currentTab === 'timeline' }]" @click="currentTab = 'timeline'">
          📅 时间线
        </div>
      </div>

      <!-- 全榜排名 -->
      <div v-if="currentTab === 'all'" class="content-section">
        <div class="section-header">
          <h2>👑 所有学生成就排名</h2>
          <button class="btn-refresh" @click="refreshRankings">🔄 刷新</button>
        </div>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="rankings.length === 0" class="empty-state">暂无数据</div>
        <div v-else class="ranking-list">
          <div v-for="(student, index) in rankings" :key="student.schedule_id" 
               :class="['ranking-item', { highlighted: isHighlightStudent(student) }]">
            <div class="rank-number">
              <span v-if="index === 0" class="gold">🥇</span>
              <span v-else-if="index === 1" class="silver">🥈</span>
              <span v-else-if="index === 2" class="bronze">🥉</span>
              <span v-else class="normal">{{ index + 1 }}</span>
            </div>
            <div class="student-info" @click="showStudentDetail(student)">
              <div class="student-name">{{ student.student_name }}</div>
              <div class="student-class">{{ student.student_class || '' }}</div>
              <div class="achievement-count">🏆 {{ student.total_achievements }} 个成就</div>
            </div>
            <div class="achievement-icons">
              <span v-for="ach in student.achievement_list.slice(0, 5)" :key="ach.id" class="icon">
                {{ ach.icon }}
              </span>
              <span v-if="student.achievement_list.length > 5" class="more">
                +{{ student.achievement_list.length - 5 }}
              </span>
            </div>
            <button class="btn-view" @click="showStudentDetail(student)">查看详情</button>
          </div>
        </div>
      </div>

      <!-- 我的成就 -->
      <div v-if="currentTab === 'personal'" class="content-section">
        <div class="section-header">
          <h2>⭐ 我的成就</h2>
          <button v-if="scheduleId !== null" class="btn-reset" @click="resetAchievements">🗑️ 重置</button>
        </div>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="scheduleId === null" class="empty-state">
          请先在日程表页面创建日程数据
        </div>
        <div v-else>
          <!-- 统计摘要 -->
          <div class="summary-cards">
            <div class="summary-card">
              <div class="icon">🏆</div>
              <div class="number">{{ statistics.achievements_summary.total_achievements }}</div>
              <div class="label">总成就</div>
            </div>
            <div class="summary-card unlocked">
              <div class="icon">✅</div>
              <div class="number">{{ statistics.achievements_summary.unlocked_achievements }}</div>
              <div class="label">已解锁</div>
            </div>
            <div class="summary-card locked">
              <div class="icon">🔒</div>
              <div class="number">{{ statistics.achievements_summary.locked_achievements }}</div>
              <div class="label">未解锁</div>
            </div>
            <div v-if="statistics.achievements_summary.hidden_achievements > 0" class="summary-card hidden">
              <div class="icon">🎁</div>
              <div class="number">{{ statistics.achievements_summary.hidden_achievements }}</div>
              <div class="label">隐藏成就</div>
            </div>
            <div class="summary-card">
              <div class="icon">📊</div>
              <div class="number">{{ statistics.achievements_summary.completion_rate }}%</div>
              <div class="label">完成率</div>
            </div>
          </div>

          <!-- 隐藏成就未解锁提示 -->
          <div v-if="statistics.achievements_summary.hidden_achievements > 0" class="hidden-achievement-tip">
            🎁 还有 {{ statistics.achievements_summary.hidden_achievements }} 个隐藏成就等待你去发现！继续完成任务解锁惊喜吧~
          </div>

          <!-- 已解锁成就 -->
          <div class="achievements-grid">
            <div v-for="achievement in achievements.filter(a => a.unlocked)" :key="achievement.id"
                 :class="['achievement-card', { 
                   unlocked: true,
                   bronze: achievement.level === 'bronze',
                   silver: achievement.level === 'silver',
                   gold: achievement.level === 'gold'
                 }]">
              <div class="achievement-icon">{{ achievement.icon }}</div>
              <div class="achievement-info">
                <div class="achievement-name">{{ achievement.name }}</div>
                <div class="achievement-desc">{{ achievement.description }}</div>
                <div class="match-rule">
                  📋 {{ getMatchRuleDescription(achievement) }}
                </div>
                <div class="unlock-info">
                  <span class="unlock-time">解锁时间：{{ formatDate(achievement.unlocked_at) }}</span>
                  <span v-if="achievement.unlock_count && achievement.unlock_count > 1" class="unlock-count">
                    完成 {{ achievement.unlock_count }} 次
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 未解锁成就 -->
          <div class="locked-section">
            <div class="locked-header" @click="showLockedAchievements = !showLockedAchievements">
              <h3>🔒 未解锁成就</h3>
              <span :class="['toggle-icon', { expanded: showLockedAchievements }]">▼</span>
            </div>
            <div v-show="showLockedAchievements" class="achievements-grid">
              <div v-for="achievement in achievements.filter(a => !a.unlocked)" :key="achievement.id"
                   :class="['achievement-card', { 
                   unlocked: false,
                   bronze: achievement.level === 'bronze',
                   silver: achievement.level === 'silver',
                   gold: achievement.level === 'gold'
                 }]">
                <div class="achievement-icon">{{ achievement.icon }}</div>
                <div class="achievement-info">
                  <div class="achievement-name">{{ achievement.name }}</div>
                  <div class="achievement-desc">{{ achievement.description }}</div>
                  <div class="match-rule">
                    📋 {{ getMatchRuleDescription(achievement) }}
                  </div>
                  <div class="lock-condition">
                    🔒 {{ achievement.unlock_condition }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时间线 -->
      <div v-if="currentTab === 'timeline'" class="content-section">
        <h2>📅 成长时间线</h2>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="scheduleId === null" class="empty-state">
          请先在日程表页面创建日程数据
        </div>
        <div v-else>
          <div class="timeline">
            <div v-for="(event, index) in timeline" :key="index" class="timeline-item">
              <div class="timeline-date">{{ event.date }}</div>
              <div class="timeline-content">
                <span class="timeline-icon">{{ event.icon }}</span>
                <div class="timeline-description">{{ event.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 学生详情弹窗 -->
      <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="showDetailModal = false">✕</button>
          <h3>{{ selectedStudent?.student_name }} 的成就</h3>
          <div v-if="selectedStudent" class="student-achievements">
            <div v-for="ach in selectedStudent.achievement_list" :key="ach.id" 
                 class="small-achievement">
              <span class="icon">{{ ach.icon }}</span>
              <span class="name">{{ ach.name }}</span>
              <span class="level-icon">{{ getLevelIcon(ach.level) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { achievementApi } from '@/api/achievement'
import './AchievementWall.css'
import { useScheduleStore } from '@/stores/schedule'
import type { Achievement, StudentRanking, TimelineEvent, StatisticsData } from '@/types'
import QuickNav from '@/components/QuickNav.vue'

const currentTab = ref<'all' | 'personal' | 'timeline'>('all')
const loading = ref(false)
const rankings = ref<StudentRanking[]>([])
const achievements = ref<Achievement[]>([])
const timeline = ref<TimelineEvent[]>([])
const scheduleStore = useScheduleStore()
const statistics = ref<StatisticsData>({
  reading_days: 0,
  exercise_duration: 0,
  challenges_completed: 0,
  total_stars: 0,
  achievements_summary: {
    total_achievements: 0,
    unlocked_achievements: 0,
    locked_achievements: 0,
    hidden_achievements: 0,
    completion_rate: 0
  }
})

const showLockedAchievements = ref(false)
const scheduleId = ref<number | null>(null)

const showDetailModal = ref(false)
const selectedStudent = ref<StudentRanking | null>(null)

const loadAllRankings = async () => {
  loading.value = true
  try {
    const res = await achievementApi.getAllStudentsRanking()
    if (res.success) {
      rankings.value = res.data
    }
  } catch (error) {
    console.error('加载排名失败:', error)
  } finally {
    loading.value = false
  }
}

const loadPersonalAchievements = async () => {
  if (scheduleId.value === null) return
  
  loading.value = true
  try {
    const res = await achievementApi.getStudentAchievements(scheduleId.value)
    if (res.success) {
      achievements.value = res.data
      // 检查并解锁新成就
      await checkAndUnlock()
    }
  } catch (error) {
    console.error('加载成就失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  if (scheduleId.value === null) return
  
  try {
    const res = await achievementApi.getStatistics(scheduleId.value)
    if (res.success) {
      statistics.value = res.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadTimeline = async () => {
  if (scheduleId.value === null) return
  
  try {
    const res = await achievementApi.getTimeline(scheduleId.value)
    if (res.success) {
      timeline.value = res.data
    }
  } catch (error) {
    console.error('加载时间线失败:', error)
  }
}

const checkAndUnlock = async () => {
  if (scheduleId.value === null) return
  
  try {
    const res = await achievementApi.checkAndUnlock(scheduleId.value)
    if (res.success && res.data.newly_unlocked_count > 0) {
      alert(`🎉 恭喜！${res.message}`)
      // 重新加载成就列表
      await loadPersonalAchievements()
      await loadStatistics()
    }
  } catch (error) {
    console.error('检查成就失败:', error)
  }
}

const loadScheduleId = () => {
  // 从 cookie 读取 scheduleId
  scheduleId.value = scheduleStore.getScheduleIdFromCookie()
  console.log('从 cookie 读取 scheduleId:', scheduleId.value)
}

const showStudentDetail = (student: StudentRanking) => {
  selectedStudent.value = student
  showDetailModal.value = true
}

const isHighlightStudent = (student: StudentRanking) => {
  return student.schedule_id === scheduleId.value
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getLevelLabel = (level?: string) => {
  const labels: Record<string, string> = {
    bronze: '铜牌',
    silver: '银牌',
    gold: '金牌'
  }
  return labels[level || ''] || ''
}

const getLevelIcon = (level?: string) => {
  const icons: Record<string, string> = {
    bronze: '🥉',
    silver: '🥈',
    gold: '🥇'
  }
  return icons[level || ''] || ''
}

// 翻译匹配类型
const translateMatchType = (matchType?: string) => {
  const translations: Record<string, string> = {
    exact: '完全匹配',
    contains: '包含',
    prefix: '前缀匹配',
    any: '任意任务'
  }
  return translations[matchType || ''] || matchType || ''
}

// 获取匹配规则描述（中文）
const getMatchRuleDescription = (achievement: Achievement) => {
  if (!achievement.task_match_type) return ''
  
  const typeLabel = translateMatchType(achievement.task_match_type)
  let keywords = achievement.task_keywords || ''
  
  if (keywords) {
    const keywordList = keywords.split(',').map(k => k.trim())
    // 移除空关键词
    const validKeywords = keywordList.filter(k => k)
    if (validKeywords.length > 0) {
      // 如果关键词太多，只显示前几个
      const displayKeywords = validKeywords.length > 5 
        ? validKeywords.slice(0, 5).join('、') + '等' 
        : validKeywords.join('、')
      return `${typeLabel}：${displayKeywords}`
    }
  }
  
  return typeLabel
}

// 初始化成就数据
const initializeAchievements = async () => {
  try {
    await achievementApi.initializeAchievements()
  } catch (error) {
    console.error('初始化成就失败:', error)
  }
}

// 重置成就
const resetAchievements = async () => {
  if (scheduleId.value === null) return
  
  const confirmed = confirm('⚠️ 确定要重置所有成就吗？此操作将删除所有已解锁的成就记录，不可恢复！')
  if (!confirmed) return
  
  try {
    const res = await achievementApi.resetAchievements(scheduleId.value)
    if (res.success) {
      alert(`✅ ${res.message}`)
      // 重新加载成就和数据
      await loadPersonalAchievements()
      await loadStatistics()
      await loadTimeline()
    }
  } catch (error) {
    console.error('重置成就失败:', error)
    alert('重置失败，请稍后重试')
  }
}

// 刷新排名
const refreshRankings = async () => {
  await loadAllRankings()
}

// 刷新成就
const refreshAchievements = async () => {
  await loadPersonalAchievements()
  await loadStatistics()
  await loadTimeline()
}

onMounted(async () => {
  // 初始化默认成就
  await initializeAchievements()
  
  // 加载日程ID
  await loadScheduleId()
  
  // 加载全榜排名
  await loadAllRankings()
  
  // 如果有日程数据，加载个人成就和时间线
  if (scheduleId.value) {
    await loadPersonalAchievements()
    await loadStatistics()
    await loadTimeline()
  }
})
</script>
