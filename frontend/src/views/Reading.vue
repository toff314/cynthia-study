<template>
  <div class="reading-page">
    <QuickNav />
    <div class="container">
      <div class="header">
        <router-link to="/" class="btn-back">← 返回首页</router-link>
        <h1>📖 绘本阅读</h1>
        <p>从云端选择绘本，在线全屏阅读，支持打印</p>
      </div>

      <div class="content-card reading-card">
        <div class="reading-layout">
          <div class="tree-panel">
            <h2 class="panel-title">📁 绘本目录</h2>
            <div v-if="treeLoading" class="loading">加载中...</div>
            <div v-else-if="treeError" class="error-message">{{ treeError }}</div>
            <el-tree
              v-else
              :load="loadNode"
              :props="treeProps"
              lazy
              accordion
              @node-click="onNodeClick"
            />
          </div>

          <div class="file-panel">
            <h2 class="panel-title">📄 绘本列表</h2>
            <div v-if="fileLoading" class="loading">加载中...</div>
            <div v-else-if="currentFiles.length === 0" class="empty-state">
              请在左侧选择目录
            </div>
            <div v-else class="file-list">
              <div
                v-for="file in currentFiles"
                :key="file.path"
                class="file-item"
                @click="onFileClick(file)"
              >
                <span class="file-icon">{{ getFileIcon(file) }}</span>
                <span class="file-name">{{ file.name }}</span>
                <span v-if="file.size" class="file-size">{{ formatSize(file.size) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Reader
      v-if="showReader"
      :image-urls="readerImages"
      :title="readerTitle"
      @close="closeReader"
    />

    <div v-if="reading" class="reading-loading">
      <div class="loading-spinner">正在打开绘本...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import QuickNav from '@/components/QuickNav.vue'
import Reader from '@/components/Reader.vue'
import { listReadingDirectory, readBook, type ReadingItem } from '@/api/reading'

interface TreeNode {
  label: string
  path: string
  is_dir: boolean
  isLeaf?: boolean
  children?: TreeNode[]
}

const treeLoading = ref(false)
const treeError = ref('')

const currentFiles = ref<ReadingItem[]>([])
const fileLoading = ref(false)

const showReader = ref(false)
const readerImages = ref<string[]>([])
const readerTitle = ref('')
const reading = ref(false)

const treeProps = {
  label: 'label',
  children: 'children',
  isLeaf: 'isLeaf',
}

const loadNode = async (node: any, resolve: (data: TreeNode[]) => void) => {
  const path = node.level === 0 ? undefined : node.data.path
  try {
    const res = await listReadingDirectory(path) as any
    if (res.success && res.data) {
      const children = res.data.map((item: ReadingItem) => ({
        label: item.name,
        path: item.path,
        is_dir: item.is_dir,
        isLeaf: !item.is_dir,
      }))
      resolve(children)
    } else {
      resolve([])
    }
  } catch (e) {
    if (node.level === 0) {
      treeError.value = '加载目录失败，请检查云端配置'
    }
    resolve([])
  } finally {
    if (node.level === 0) {
      treeLoading.value = false
    }
  }
}

const onNodeClick = async (data: TreeNode) => {
  if (!data.is_dir) return
  fileLoading.value = true
  try {
    const res = await listReadingDirectory(data.path) as any
    if (res.success && res.data) {
      currentFiles.value = res.data.filter((item: ReadingItem) => {
        if (item.is_dir) return false
        const name = item.name.toLowerCase()
        return name.endsWith('.pdf') || name.endsWith('.ppt') || name.endsWith('.pptx')
      })
    }
  } finally {
    fileLoading.value = false
  }
}

const getFileIcon = (file: ReadingItem) => {
  const name = file.name.toLowerCase()
  if (name.endsWith('.pdf')) return '📕'
  if (name.endsWith('.ppt') || name.endsWith('.pptx')) return '📊'
  return '📄'
}

const formatSize = (size: number) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const onFileClick = async (file: ReadingItem) => {
  if (reading.value) return
  reading.value = true
  try {
    const res = await readBook(file.path) as any
    if (res.success && res.data) {
      readerImages.value = res.data.image_urls
      readerTitle.value = file.name
      showReader.value = true
    }
  } catch (e: any) {
    alert(e?.response?.data?.detail || '打开绘本失败')
  } finally {
    reading.value = false
  }
}

const closeReader = () => {
  showReader.value = false
  readerImages.value = []
  readerTitle.value = ''
}

</script>

<style scoped>
.reading-page {
  font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.header h1 {
  color: #00BCD4;
  font-size: 32px;
  margin-bottom: 15px;
  text-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.header p {
  color: white;
  opacity: 0.9;
  font-size: 18px;
  margin-bottom: 20px;
}

.btn-back {
  display: inline-block;
  padding: 8px 20px;
  background: #f8f9fa;
  color: #4A90D9;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #4A90D9;
  color: #fff;
  border-color: #4A90D9;
}

.content-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.reading-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 400px;
}

@media screen and (max-width: 768px) {
  .reading-layout {
    grid-template-columns: 1fr;
  }
}

.panel-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
  font-weight: 700;
}

.tree-panel,
.file-panel {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 20px;
  min-height: 350px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 13px 15px;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
  gap: 10px;
}

.file-item:hover {
  background: #f0f0f0;
  border-left-color: #00BCD4;
  transform: translateX(5px);
}

.file-icon {
  font-size: 20px;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #999;
}

.loading {
  text-align: center;
  color: #999;
  padding: 30px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px;
}

.error-message {
  color: #F44336;
  padding: 20px;
  text-align: center;
}

.reading-loading {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
}
</style>
