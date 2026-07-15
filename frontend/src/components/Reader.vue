<template>
  <div class="reader-overlay" @click.self="onBackdropClick">
    <div class="reader-controls">
      <div class="reader-title">{{ title }}</div>
      <div class="reader-actions">
        <button class="reader-btn" @click="printAll">🖨️ 打印</button>
        <button class="reader-btn" @click="emit('close')">✕ 关闭</button>
      </div>
    </div>

    <div class="reader-stage">
      <button class="reader-nav reader-nav-left" @click="prevPage" :disabled="currentPage <= 0">
        ‹
      </button>

      <div class="reader-image-wrapper">
        <img
          v-for="(url, index) in imageUrls"
          :key="index"
          :src="url"
          :class="['reader-image', { active: index === currentPage }]"
          :alt="`${title} 第 ${index + 1} 页`"
          @load="onImageLoad(index)"
        />
        <div v-if="imageUrls.length === 0" class="reader-empty">暂无图片</div>
      </div>

      <button class="reader-nav reader-nav-right" @click="nextPage" :disabled="currentPage >= imageUrls.length - 1">
        ›
      </button>
    </div>

    <div class="reader-footer">
      <span>{{ currentPage + 1 }} / {{ imageUrls.length }}</span>
    </div>

    <div class="reader-print-area">
      <img
        v-for="(url, index) in imageUrls"
        :key="index"
        :src="url"
        class="reader-print-image"
        :alt="`${title} 第 ${index + 1} 页`"
      />
    </div>
    <div v-if="isPrinting" class="reader-print-loading">
      <div class="print-loading-text">正在准备打印，图片加载中 {{ loadedCount }}/{{ imageUrls.length }}...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  imageUrls: string[]
  title: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const currentPage = ref(0)
const loadedMap = ref<Record<number, boolean>>({})
const isPrinting = ref(false)

const allImagesLoaded = computed(() => {
  return props.imageUrls.length > 0 && props.imageUrls.every((_, index) => loadedMap.value[index])
})

const loadedCount = computed(() => Object.keys(loadedMap.value).length)

const markLoaded = (index: number) => {
  loadedMap.value[index] = true
}

const preloadAllImages = () => {
  props.imageUrls.forEach((url, index) => {
    const img = new Image()
    img.src = url
    img.onload = () => markLoaded(index)
  })
}

const onImageLoad = (index: number) => {
  markLoaded(index)
}

const nextPage = () => {
  if (currentPage.value < props.imageUrls.length - 1) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}

const doPrint = () => {
  setTimeout(() => window.print(), 100)
}

const printAll = () => {
  if (allImagesLoaded.value) {
    doPrint()
  } else {
    isPrinting.value = true
  }
}

watch(allImagesLoaded, (loaded) => {
  if (loaded && isPrinting.value) {
    isPrinting.value = false
    doPrint()
  }
})

const onBackdropClick = () => {
  emit('close')
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowRight') nextPage()
  if (e.key === 'ArrowLeft') prevPage()
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  preloadAllImages()
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.reader-overlay {
  position: fixed;
  inset: 0;
  background: #1a1a1a;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.reader-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 25px;
  background: rgba(0, 0, 0, 0.6);
}

.reader-title {
  font-size: 18px;
  font-weight: 700;
}

.reader-actions {
  display: flex;
  gap: 10px;
}

.reader-btn {
  background: #00BCD4;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.reader-btn:hover {
  background: #00acc1;
  transform: translateY(-2px);
}

.reader-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 10px 20px;
  overflow: hidden;
}

.reader-image-wrapper {
  flex: 1;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reader-image {
  position: absolute;
  max-width: 100%;
  max-height: calc(100vh - 140px);
  object-fit: contain;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  opacity: 0;
  transform: scale(0.92) translateY(10px);
  transition: opacity 0.45s ease, transform 0.45s ease;
  pointer-events: none;
}

.reader-image.active {
  opacity: 1;
  transform: scale(1) translateY(0);
  pointer-events: auto;
}

.reader-empty {
  font-size: 16px;
  color: #999;
}

.reader-nav {
  width: 50px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 36px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.reader-nav:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.reader-nav:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.reader-footer {
  text-align: center;
  padding: 10px;
  font-size: 14px;
  color: #ccc;
}

.reader-print-area {
  display: none;
}

.reader-print-loading {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.print-loading-text {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

@media print {
  @page {
    size: landscape;
  }

  :global(.reading-page .header),
  :global(.reading-page .content-card) {
    display: none !important;
  }

  .reader-controls,
  .reader-nav,
  .reader-footer,
  .reader-print-loading {
    display: none !important;
  }

  .reader-overlay {
    position: static;
    background: #fff;
  }

  .reader-stage {
    display: none;
  }

  .reader-print-area {
    display: block;
  }

  .reader-print-image {
    max-width: 100%;
    page-break-after: always;
    display: block;
  }

  .reader-print-image:last-child {
    page-break-after: auto;
  }
}
</style>
