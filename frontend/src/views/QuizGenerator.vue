<template>
  <div class="quiz-generator">
    <div class="container">
      <div class="header">
        <h1>📚 阅读题生成器</h1>
        <p>选择JSON数据文件，生成阅读理解题页面</p>
      </div>

      <div class="info-box">
        <p><strong>💡 使用说明：</strong></p>
        <ul class="info-list">
          <li>选择JSON文件后，系统会自动将其保存到数据目录</li>
          <li>点击文件列表中的下载图标可下载JSON文件</li>
          <li>下载文件后，可使用AI工具生成新的阅读题JSON数据</li>
        </ul>
      </div>

      <div class="tip-box" @click="showAIPrompt = !showAIPrompt">
        <p><strong>🤖 AI生成提示词（点击展开/折叠）</strong></p>
        <div v-if="showAIPrompt" class="ai-prompt">
          <p>你可以将下载的JSON文件内容发送给AI工具（如ChatGPT、DeepSeek等），使用以下提示词生成新的阅读题：</p>
          <div class="prompt-text">你是一个文学专家，请根据以下示例JSON结构生成 [书籍名称] 的阅读题目，包含4个选择题和1个思考题，并包含答案解析，请只返回JSON数据便于我保存。</div>
          <p class="prompt-note">💡 提示：将 "[书籍名称]" 替换为你想要生成阅读题的书名</p>
        </div>
      </div>

      <div class="upload-method">
        <div 
          :class="['method-tab', { active: uploadMethod === 'server' }]" 
          @click="uploadMethod = 'server'"
        >
          📂 从项目选择
        </div>
        <div 
          :class="['method-tab', { active: uploadMethod === 'local' }]" 
          @click="uploadMethod = 'local'"
        >
          💻 本地上传
        </div>
      </div>

      <div v-show="uploadMethod === 'server'" class="card">
        <div class="card-header">
          <h3>项目文件列表</h3>
          <button class="btn-refresh" @click="loadServerFiles">🔄 刷新</button>
        </div>
        <div class="file-list" v-if="files.length > 0">
          <div 
            v-for="file in files" 
            :key="file.name"
            :class="['file-item', { selected: selectedFile === file.name }]"
          >
            <div class="file-item-info" @click="selectFile(file.name)">
              <span class="file-item-icon">📄</span>
              <span class="file-item-name">{{ file.name }}</span>
            </div>
            <div class="file-item-actions">
              <button 
                class="btn-download-icon" 
                @click.stop="downloadFile(file.name)"
                title="下载JSON文件"
              >
                ⬇️
              </button>
              <span class="file-item-date">{{ file.modified }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          {{ loading ? '加载中...' : '📭 暂无文件' }}
        </div>
        <div class="card-footer">
          <button class="btn btn-primary" :disabled="!selectedFile" @click="loadSelectedFile">
            ✅ 选择此文件
          </button>
        </div>
      </div>

      <div v-show="uploadMethod === 'local'" class="card">
        <div class="card-header">
          <h3>本地上传</h3>
        </div>
        <div class="file-upload">
          <input type="file" id="jsonFile" class="file-input" @change="handleFileUpload" accept=".json" />
          <label for="jsonFile" class="file-label">
            <span class="file-label-icon">📁</span>
            <span class="file-label-text">点击选择JSON文件</span>
          </label>
          <p class="file-upload-hint">支持 .json 格式文件</p>
        </div>
      </div>

      <div class="button-group">
        <button class="btn btn-generate" :disabled="!loadedData" @click="generatePage">
          ✨ 生成页面
        </button>
        <button class="btn btn-download" :disabled="!generatedHTML" @click="printQuiz">
          🖨️ 打印阅读题
        </button>
      </div>

      <div class="preview" v-if="generatedHTML">
        <div class="preview-title">预览</div>
        <iframe :srcdoc="generatedHTML" style="width: 100%; height: 600px; border: none;"></iframe>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { quizApi, type FileInfo } from '@/api/quiz'
import type { QuizData, ApiResponse } from '@/types'

const uploadMethod = ref<'server' | 'local'>('server')
const files = ref<FileInfo[]>([])
const selectedFile = ref('')
const loadedData = ref<QuizData | null>(null)
const generatedHTML = ref<string>('')
const loading = ref(false)
const showAIPrompt = ref(false)

const loadServerFiles = async () => {
  loading.value = true
  try {
    const res = await quizApi.getFiles() as unknown as ApiResponse<{ files: FileInfo[] }>
    if (res.success) {
      files.value = res.data.files
    }
  } catch (error) {
    console.error('加载文件列表失败:', error)
  } finally {
    loading.value = false
  }
}

const selectFile = (filename: string) => {
  selectedFile.value = filename
}

const loadSelectedFile = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  try {
    const res = await quizApi.getFile(selectedFile.value) as unknown as ApiResponse<{ content: string }>
    if (res.success) {
      loadedData.value = JSON.parse(res.data.content)
      if (loadedData.value) {
        await saveToServer(loadedData.value)
      }
    }
  } catch (error) {
    console.error('加载文件内容失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      loadedData.value = JSON.parse(e.target?.result as string)
      if (loadedData.value) {
        await saveToServer(loadedData.value)
      }
      // 清空input的value，允许重复选择同一文件
      target.value = ''
    } catch (error) {
      alert('JSON文件格式错误，请检查文件内容')
    }
  }
  reader.readAsText(file)
}

const saveToServer = async (data: QuizData) => {
  try {
    const res = await quizApi.saveQuiz(data) as unknown as ApiResponse<{ path: string }>
    if (res.success) {
      alert(`✅ 文件加载成功！包含 ${data.sections.length} 个章节\n\n📁 文件已保存`)
    }
  } catch (error) {
    console.error('保存文件失败:', error)
  }
}

const generatePage = () => {
  if (!loadedData.value) return
  
  const template = getTemplateHTML()
  const dataString = JSON.stringify(loadedData.value, null, 2)
  
  generatedHTML.value = template.replace(
    'const quizData = {};',
    `const quizData = ${dataString};`
  )
}

const printQuiz = () => {
  if (!generatedHTML.value) return
  
  const iframe = document.querySelector('.preview iframe') as HTMLIFrameElement
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.print()
  }
}

const downloadFile = (filename: string) => {
  quizApi.downloadFile(filename)
}

const copyPrompt = () => {
  const prompt = `你是一个文学专家，请根据以下示例JSON结构生成 [书籍名称] 的阅读题目，包含4个选择题和1个思考题，并包含答案解析，请只返回JSON数据便于我保存。`
  navigator.clipboard.writeText(prompt).then(() => {
    alert('✅ 提示词已复制到剪贴板')
  }).catch(() => {
    alert('❌ 复制失败，请手动复制')
  })
}

const getTemplateHTML = () => {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>阅读理解题</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: "Microsoft YaHei", Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
    .header { text-align: center; padding-bottom: 30px; border-bottom: 3px solid #667eea; }
    .header h1 { color: #667eea; font-size: 28px; }
    .section { margin-bottom: 30px; }
    .section-title { background: #667eea; color: white; padding: 10px 20px; border-radius: 8px; font-size: 18px; margin-bottom: 20px; }
    .question { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #667eea; }
    .question-number { color: #667eea; font-weight: bold; font-size: 18px; margin-bottom: 10px; }
    .options { margin-left: 20px; }
    .option { padding: 4px 0; font-size: 15px; }
    .answer-key { background: #e8f5e9; padding: 20px; border-radius: 10px; border: 2px solid #4caf50; }
    .page-break { page-break-before: always; }
    .answer-section { page-break-before: always; }
    .answer-item { padding: 15px; margin-bottom: 10px; background: white; border-radius: 8px; }
    .answer-label { color: #4caf50; font-weight: bold; font-size: 16px; margin-bottom: 8px; }
    .answer-explanation { color: #666; font-size: 14px; line-height: 1.6; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e0e0e0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 id="title">📚 阅读理解题</h1>
    </div>
    <div id="questions-container"></div>
    <div class="section answer-section">
      <div class="section-title" style="background: #4CAF50;">参考答案</div>
      <div id="answers-container"></div>
    </div>
  </div>
  <script>
    const quizData = {};
    function init() {
      document.getElementById('title').textContent = '📚 ' + quizData.title;
      const questionsContainer = document.getElementById('questions-container');
      let html = '';
      quizData.sections.forEach(section => {
        html += '<div class="section"><div class="section-title">' + section.title + '</div>';
        section.questions.forEach(q => {
          html += '<div class="question"><div class="question-number">' + q.number + '. ' + q.text + '</div>';
          if (q.options) {
            html += '<div class="options">';
            q.options.forEach(opt => html += '<div class="option">' + opt + '</div>');
            html += '</div>';
          }
          html += '</div>';
        });
        html += '</div>';
      });
      questionsContainer.innerHTML = html;
      
      let answerHtml = '<div class="answer-key">';
      quizData.sections.forEach(section => {
        section.questions.forEach(q => {
          if (q.answer) {
            answerHtml += '<div class="answer-item"><div class="answer-label">' + q.number + '. ' + q.answer + '</div>';
            if (q.explanation) {
              answerHtml += '<div class="answer-explanation"><strong>解析：</strong>' + q.explanation + '</div>';
            }
            answerHtml += '</div>';
          }
        });
      });
      answerHtml += '</div>';
      document.getElementById('answers-container').innerHTML = answerHtml;
    }
    document.addEventListener('DOMContentLoaded', init);
  <\/script>
</body>
</html>`
}

onMounted(() => {
  loadServerFiles()
})
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.quiz-generator {
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
  background: white;
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.header h1 { color: #667eea; font-size: 28px; margin-bottom: 10px; }
.header p { color: #666; font-size: 16px; }

.info-box {
  background: white;
  border-radius: 10px;
  padding: 15px 20px;
  margin-bottom: 20px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.info-list {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.tip-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  padding: 15px 20px;
  margin-bottom: 20px;
  cursor: pointer;
  color: white;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.tip-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.tip-box p {
  margin: 0;
  font-size: 14px;
}

.ai-prompt {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.ai-prompt p {
  margin-bottom: 10px;
  font-size: 13px;
  line-height: 1.6;
}

.prompt-text {
  background: rgba(0,0,0,0.2);
  padding: 12px 15px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.8;
  margin-bottom: 10px;
  word-break: break-all;
}

.prompt-note {
  margin-bottom: 0 !important;
  color: rgba(255,255,255,0.9);
  font-style: italic;
}

.upload-method {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.method-tab {
  padding: 10px 25px;
  background: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.method-tab:hover { border-color: #667eea; }
.method-tab.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.card {
  background: white;
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 15px;
}

.card-header h3 { color: #667eea; font-size: 18px; }

.file-list {
  max-height: 350px;
  overflow-y: auto;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px 15px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.file-item:hover { 
  background: #f0f0f0;
  border-left-color: #667eea;
}

.file-item.selected { 
  background: #667eea; 
  color: white; 
  border-left-color: #4CAF50;
}

.file-item-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  cursor: pointer;
}

.file-item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-item-icon { font-size: 18px; }
.file-item-name { flex: 1; font-size: 14px; }
.file-item-date { font-size: 12px; color: #666; }
.file-item.selected .file-item-date { color: rgba(255,255,255,0.8); }

.btn-download-icon {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  padding: 0;
}

.btn-download-icon:hover {
  background: #45a049;
  transform: scale(1.1);
}

.file-item.selected .btn-download-icon {
  background: rgba(255,255,255,0.2);
}

.file-item.selected .btn-download-icon:hover {
  background: rgba(255,255,255,0.3);
}

.file-upload {
  padding: 40px;
  text-align: center;
}

.file-input { display: none; }
.file-label {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 40px;
  border-radius: 10px;
  cursor: pointer;
  border: 2px dashed rgba(255,255,255,0.5);
  transition: all 0.3s;
}

.file-label:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }

.file-label-icon { font-size: 32px; }
.file-label-text { font-size: 16px; font-weight: bold; }

.file-upload-hint { margin-top: 15px; color: #999; font-size: 14px; }

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.btn:disabled { background: #ccc; cursor: not-allowed; opacity: 0.6; }

.btn-refresh {
  background: #FF9800;
  color: white;
  padding: 8px 15px;
  font-size: 14px;
}

.btn-primary {
  background: #2196F3;
  color: white;
}

.btn-generate { background: #4CAF50; color: white; }
.btn-download { background: #2196f3; color: white; }

.card-footer {
  text-align: center;
  padding-top: 15px;
  border-top: 2px solid #e0e0e0;
}

.preview {
  background: white;
  border-radius: 15px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.preview-title {
  color: #667eea;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}
</style>
