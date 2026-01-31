<template>
  <div class="home">
    <div class="container">
      <div class="header">
        <h1>🎄 寒假工具集 🎄</h1>
        <p>高效规划寒假时光，轻松提升学习效率</p>
      </div>

      <div class="tools-container">
        <router-link to="/schedule" class="tool-card schedule">
          <span class="tool-icon">📅</span>
          <h2>寒假每日任务日程表</h2>
          <p>管理每日任务，记录学习收获<br/>合理安排时间，养成良好习惯</p>
          <span class="tool-arrow">→</span>
        </router-link>

        <router-link to="/quiz" class="tool-card reading">
          <span class="tool-icon">📚</span>
          <h2>寒假阅读题生成器</h2>
          <p>导入阅读材料，生成阅读理解题<br/>智能创建题目，提升阅读能力</p>
          <span class="tool-arrow">→</span>
        </router-link>

        <router-link to="/achievement" class="tool-card achievement">
          <span class="tool-icon">🏆</span>
          <h2>寒假成就墙</h2>
          <p>展示成就徽章，记录成长足迹<br/>可视化呈现进步，激励持续学习</p>
          <span class="tool-arrow">→</span>
        </router-link>

        <router-link to="/games" class="tool-card games">
          <span class="tool-icon">🎮</span>
          <h2>益智游戏中心</h2>
          <p>远离电子产品保护视力<br/>益智游戏纸上学习乐无穷</p>
          <span class="tool-arrow">→</span>
        </router-link>

        <div class="tool-card statistics" v-loading="loading">
          <span class="tool-icon">📊</span>
          <h2>使用统计</h2>
          <div class="statistics-content">
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_users }}</div>
              <div class="stat-label">使用人数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_visits }}</div>
              <div class="stat-label">页面访问次数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_schedules }}</div>
              <div class="stat-label">日程数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_quizzes }}</div>
              <div class="stat-label">阅读题数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_achievements }}</div>
              <div class="stat-label">成就数</div>
            </div>
          </div>
          <div class="stat-footer">
            最后更新：{{ formatTime(statistics.last_updated) }}
          </div>
        </div>
      </div>

      <div class="footer">
        <p>© 2026 寒假学习助手 | 祝您学业进步！</p>
        <p class="creator-info">由 Cynthia 倾心创作 | 欢迎家长们提出宝贵建议，如需反馈请与 Cynthia 的家人联系</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStatisticsSummary, recordVisit } from '@/api/statistics'

interface StatisticsData {
  total_users: number
  total_visits: number
  total_schedules: number
  total_quizzes: number
  total_achievements: number
  last_updated: string
}

const loading = ref(true)
const statistics = ref<StatisticsData>({
  total_users: 0,
  total_visits: 0,
  total_schedules: 0,
  total_quizzes: 0,
  total_achievements: 0,
  last_updated: ''
})

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const response = await getStatisticsSummary()
    if (response.success && response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 并行执行：记录访问和获取统计
  await Promise.all([
    recordVisit().catch(err => console.error('记录访问失败:', err)),
    fetchStatistics()
  ])
})
</script>

<style scoped src="./Home.css"></style>
