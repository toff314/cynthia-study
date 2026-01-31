<template>
  <div class="quick-nav">
    <h3 class="quick-nav-title">🔗 快捷导航</h3>
    <div class="nav-items">
      <router-link to="/schedule" class="nav-item" :class="{ active: $route.path === '/schedule' }">
        <span class="nav-icon">📋</span>
        <span class="nav-text">任务管理</span>
      </router-link>
      <router-link to="/quiz" class="nav-item" :class="{ active: $route.path === '/quiz' }">
        <span class="nav-icon">📚</span>
        <span class="nav-text">阅读练习</span>
      </router-link>
      <router-link to="/achievement" class="nav-item" :class="{ active: $route.path === '/achievement' }">
        <span class="nav-icon">🏆</span>
        <span class="nav-text">我的成就</span>
      </router-link>
      <router-link to="/games" class="nav-item" :class="{ active: $route.path === '/games' }">
        <span class="nav-icon">🎮</span>
        <span class="nav-text">益智游戏</span>
      </router-link>
    </div>
    <router-link to="/" class="nav-item home-link" :class="{ active: $route.path === '/' }">
      <span class="nav-icon">🏠</span>
      <span class="nav-text">返回首页</span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.quick-nav {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  padding: 20px 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  width: 120px;
}

.quick-nav-title {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin: 0 0 15px 0;
  padding: 0 10px;
  font-weight: bold;
}

.nav-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 10px;
  text-decoration: none;
  color: #666;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.nav-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(-3px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-icon {
  font-size: 28px;
  margin-bottom: 4px;
  display: block;
}

.nav-text {
  font-size: 12px;
  font-weight: 500;
}

.home-link {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.home-link:hover {
  background: linear-gradient(135deg, #FF9800 0%, #FF5722 100%);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
}

.home-link.active {
  background: linear-gradient(135deg, #FF9800 0%, #FF5722 100%);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
}

@media screen and (max-width: 768px) {
  .quick-nav {
    right: 10px;
    width: 80px;
    padding: 15px 0;
  }

  .quick-nav-title {
    font-size: 10px;
    margin-bottom: 10px;
  }

  .nav-icon {
    font-size: 20px;
  }

  .nav-text {
    font-size: 10px;
  }

  .nav-item {
    padding: 8px 6px;
  }

  .home-link {
    padding-top: 10px;
    margin-top: 10px;
  }
}
</style>
