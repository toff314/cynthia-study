<template>
  <div class="quick-nav">
    <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
      <span class="nav-icon">🏠</span>
    </router-link>
    <router-link to="/schedule" class="nav-item" :class="{ active: $route.path === '/schedule' }">
      <span class="nav-icon">📅</span>
    </router-link>
    <router-link to="/study" class="nav-item" :class="{ active: $route.path === '/study' }">
      <span class="nav-icon">📚</span>
    </router-link>
    <router-link to="/quiz" class="nav-item" :class="{ active: $route.path === '/quiz' }">
      <span class="nav-icon">📖</span>
    </router-link>
    <router-link to="/achievement" class="nav-item" :class="{ active: $route.path === '/achievement' }">
      <span class="nav-icon">🏆</span>
    </router-link>
    <router-link to="/reading" class="nav-item" :class="{ active: $route.path === '/reading' }">
      <span class="nav-icon">📖</span>
    </router-link>
    <router-link to="/games" class="nav-item" :class="{ active: $route.path === '/games' }">
      <span class="nav-icon">🎮</span>
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
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  width: 50px;
  height: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  text-decoration: none;
  transition: all 0.3s;
  color: #fff;
  background-color: rgba(255, 255, 255, 0.15);
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateX(5px);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.35);
  transform: translateX(5px);
}

  .nav-icon {
    display: block;
  }

  @media print {
    .quick-nav {
      display: none !important;
    }
  }

  @media screen and (max-width: 768px) {
  .nav-item {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
}
</style>
