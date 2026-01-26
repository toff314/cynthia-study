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

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home {
  font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  max-width: 900px;
  width: 100%;
}

.header {
  text-align: center;
  margin-bottom: 50px;
}

.header h1 {
  color: white;
  font-size: 42px;
  margin-bottom: 15px;
  text-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.header p {
  color: rgba(255,255,255,0.9);
  font-size: 18px;
}

.tools-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  padding: 20px 0;
}

.tool-card {
  background: white;
  border-radius: 20px;
  padding: 50px 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  text-align: center;
  text-decoration: none;
  display: block;
  transition: all 0.3s ease;
}

.tool-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
}

.tool-card.schedule:hover {
  border: 3px solid #667eea;
}

.tool-card.reading:hover {
  border: 3px solid #4CAF50;
}

.tool-card.achievement:hover {
  border: 3px solid #FF9800;
}

.tool-card.statistics:hover {
  border: 3px solid #9C27B0;
}

/* 统计卡片样式 */
.tool-card.statistics {
  cursor: default;
}

.statistics-content {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 25px 0;
}

.stat-item {
  flex: 1;
  padding: 0 15px;
}

.stat-value {
  font-size: 48px;
  font-weight: 700;
  color: #9C27B0;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stat-divider {
  width: 2px;
  height: 60px;
  background: linear-gradient(to bottom, transparent, #E0E0E0, transparent);
}

.stat-footer {
  font-size: 12px;
  color: #999;
  margin-top: 15px;
}

@media screen and (max-width: 768px) {
  .statistics-content {
    flex-wrap: wrap;
  }

  .stat-item {
    flex: 1 1 45%;
    padding: 10px;
  }

  .stat-divider {
    display: none;
  }

  .stat-value {
    font-size: 36px;
  }
}

@media screen and (max-width: 480px) {
  .stat-item {
    flex: 1 1 100%;
  }
}

.tool-icon {
  font-size: 72px;
  margin-bottom: 20px;
  display: block;
}

.tool-card h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 10px;
}

.tool-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.tool-arrow {
  font-size: 24px;
  color: #999;
  transition: all 0.3s;
}

.tool-card:hover .tool-arrow {
  transform: translateX(10px);
  color: #667eea;
}

.footer {
  text-align: center;
  margin-top: 50px;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
}

.footer p {
  margin-bottom: 10px;
}

.creator-info {
  color: rgba(255,255,255,0.7);
  font-size: 13px;
}

@media screen and (max-width: 768px) {
  .header h1 {
    font-size: 32px;
  }

  .tools-container {
    grid-template-columns: 1fr;
    padding: 0;
  }

  .tool-icon {
    font-size: 60px;
  }

  .tool-card h2 {
    font-size: 20px;
  }
}
</style>
