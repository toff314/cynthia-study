---
version: 1.0
name: cynthia-study-design
description: Cynthia Study 是专为小学生设计的在线学习工具集，融合活泼童趣的视觉语言与清晰的功能分区。主色调采用高饱和度的彩虹色系（蓝、绿、橙、粉、紫），通过 pastel 色卡区分不同模块，大圆角卡片承载内容，emoji 图标作为视觉引导。整体风格参考 Khan Academy 的儿童友好设计，但更强调卡片化布局和打印输出支持。

colors:
  # 主品牌色
  primary-blue: "#4A90D9"
  primary-green: "#5CB85C"
  primary-orange: "#F0AD4E"
  primary-pink: "#E91E63"
  primary-purple: "#9C27B0"
  primary-teal: "#00BCD4"
  primary-red: "#F44336"

  # Pastel 模块色卡（卡片背景）
  card-blue: "#E3F2FD"
  card-green: "#E8F5E9"
  card-orange: "#FFF3E0"
  card-pink: "#FCE4EC"
  card-purple: "#F3E5F5"
  card-teal: "#E0F7FA"
  card-yellow: "#FFFDE7"
  card-red: "#FFEBEE"

  # 渐变背景（页面级）
  gradient-blue-purple: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  gradient-blue-teal: "linear-gradient(135deg, #4A90D9 0%, #00BCD4 100%)"
  gradient-green-blue: "linear-gradient(135deg, #5CB85C 0%, #4A90D9 100%)"
  gradient-orange-pink: "linear-gradient(135deg, #F0AD4E 0%, #E91E63 100%)"
  gradient-purple-pink: "linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)"

  # 成就等级色
  bronze: "#CD7F32"
  bronze-light: "#FFF8F0"
  silver: "#C0C0C0"
  silver-light: "#F8F8F8"
  gold: "#FFD700"
  gold-light: "#FFFFF0"

  # 中性色
  canvas: "#FFFFFF"
  surface: "#F8F9FA"
  surface-hover: "#F0F0F0"
  border-light: "#E0E0E0"
  border-medium: "#DDDDDD"
  text-primary: "#333333"
  text-secondary: "#666666"
  text-muted: "#999999"
  text-white: "#FFFFFF"

  # 语义色
  success: "#4CAF50"
  warning: "#FF9800"
  error: "#F44336"
  info: "#2196F3"

typography:
  display-xl:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "42px"
    fontWeight: 700
    lineHeight: 1.2
    use: "页面标题（白色文字 + 文字阴影）"
  display-lg:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: 1.2
    use: "Achievement 页面标题"
  display-md:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.3
    use: "区块标题（section h2）"
  heading-lg:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.3
    use: "工具卡片标题"
  heading-md:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.4
    use: "分类卡片标题"
  heading-sm:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.4
    use: "卡片内标题"
  body-lg:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    use: "正文、描述文字"
  body-md:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
    use: "辅助文字、标签"
  body-sm:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
    use: "日期、提示文字"
  body-xs:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "10px"
    fontWeight: 400
    lineHeight: 1.4
    use: "日程表任务输入框内文字"
  button-text:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.4
    use: "按钮文字"
  stat-number:
    fontFamily: "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"
    fontSize: "48px"
    fontWeight: 700
    lineHeight: 1.1
    use: "统计数字"

rounded:
  sm: "5px"
  md: "8px"
  lg: "10px"
  xl: "15px"
  xxl: "20px"
  xxxl: "24px"
  full: "9999px"

spacing:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "15px"
  xl: "20px"
  xxl: "25px"
  xxxl: "30px"
  section: "40px"
  section-lg: "50px"

shadows:
  card: "0 10px 40px rgba(0,0,0,0.3)"
  card-hover: "0 20px 50px rgba(0,0,0,0.4)"
  card-light: "0 10px 30px rgba(0,0,0,0.2)"
  card-sm: "0 5px 15px rgba(0,0,0,0.1)"
  card-sm-hover: "0 8px 20px rgba(102,126,234,0.3)"
  card-xs: "0 2px 5px rgba(0,0,0,0.1)"
  card-game: "0 4px 15px rgba(0,0,0,0.2)"
  card-game-hover: "0 8px 25px rgba(0,0,0,0.3)"
  text-shadow: "0 4px 10px rgba(0,0,0,0.3)"
  text-shadow-sm: "0 2px 5px rgba(0,0,0,0.2)"

components:
  tool-card:
    backgroundColor: "{colors.canvas}"
    borderRadius: "{rounded.xxl}"
    padding: "50px 30px"
    shadow: "{shadows.card}"
    textAlign: "center"
    transition: "all 0.3s ease"
    use: "首页工具入口卡片"
  tool-card-hover:
    transform: "translateY(-10px)"
    shadow: "{shadows.card-hover}"
    border: "3px solid {module-color}"
  tool-icon:
    fontSize: "72px"
    display: "block"
    marginBottom: "20px"
  content-card:
    backgroundColor: "{colors.canvas}"
    borderRadius: "{rounded.xxl}"
    padding: "30px"
    shadow: "{shadows.card}"
    use: "内容区主卡片（成就墙、游戏预览等）"
  content-card-light:
    backgroundColor: "{colors.canvas}"
    borderRadius: "{rounded.xl}"
    padding: "20px"
    shadow: "{shadows.card-light}"
    use: "次级内容卡片（日程表、文件列表）"
  category-card:
    backgroundColor: "{colors.canvas}"
    borderRadius: "16px"
    padding: "25px"
    textAlign: "center"
    shadow: "{shadows.card-game}"
    transition: "all 0.3s ease"
    use: "分类选择卡片（游戏分类、学习模块）"
  category-card-active:
    border: "3px solid {colors.primary-blue}"
    background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
  achievement-card:
    borderRadius: "{rounded.xxl}"
    padding: "20px"
    border: "3px solid {border-color}"
    transition: "all 0.3s"
    use: "成就卡片"
  achievement-card-bronze:
    borderColor: "{colors.bronze}"
    backgroundColor: "{colors.bronze-light}"
  achievement-card-silver:
    borderColor: "{colors.silver}"
    backgroundColor: "{colors.silver-light}"
  achievement-card-gold:
    borderColor: "{colors.gold}"
    backgroundColor: "{colors.gold-light}"
    shadow: "0 5px 15px rgba(255,215,0,0.3)"
  achievement-card-unlocked:
    opacity: 1
    transform: "translateY(0)"
  achievement-card-locked:
    opacity: 0.6
  summary-card:
    background: "{colors.gradient-blue-purple}"
    color: "{colors.text-white}"
    padding: "25px 15px"
    borderRadius: "{rounded.xl}"
    textAlign: "center"
    shadow: "0 5px 15px rgba(102,126,234,0.4)"
    use: "统计摘要卡片"
  primary-button:
    background: "{colors.primary-blue}"
    color: "{colors.text-white}"
    borderRadius: "{rounded.md}"
    padding: "12px 25px"
    fontWeight: 700
    fontSize: "16px"
    border: "none"
    cursor: "pointer"
    shadow: "0 2px 5px rgba(0,0,0,0.2)"
    transition: "all 0.3s"
  primary-button-hover:
    transform: "translateY(-2px)"
    shadow: "0 4px 10px rgba(0,0,0,0.3)"
  gradient-button:
    background: "{colors.gradient-blue-purple}"
    color: "{colors.text-white}"
    borderRadius: "{rounded.full}"
    padding: "10px 20px"
    fontSize: "14px"
    border: "none"
    cursor: "pointer"
    transition: "all 0.3s"
    use: "游戏操作按钮"
  gradient-button-hover:
    transform: "scale(1.05)"
    shadow: "0 4px 15px rgba(102,126,234,0.4)"
  outline-button:
    background: "{colors.canvas}"
    color: "{colors.primary-blue}"
    border: "2px solid {colors.primary-blue}"
    borderRadius: "{rounded.full}"
    padding: "10px 20px"
    fontSize: "14px"
    cursor: "pointer"
    transition: "all 0.3s"
    use: "游戏预览区操作按钮"
  outline-button-hover:
    background: "{colors.primary-blue}"
    color: "{colors.text-white}"
  tab-button:
    background: "{colors.canvas}"
    border: "2px solid transparent"
    borderRadius: "{rounded.lg}"
    padding: "12px 30px"
    fontSize: "16px"
    fontWeight: 700
    shadow: "0 4px 10px rgba(0,0,0,0.2)"
    transition: "all 0.3s"
    use: "Tab 切换按钮"
  tab-button-active:
    background: "{colors.primary-orange}"
    color: "{colors.text-white}"
    borderColor: "{colors.primary-orange}"
  quick-nav:
    position: "fixed"
    left: "0"
    top: "50%"
    transform: "translateY(-50%)"
    zIndex: 1000
    display: "flex"
    flexDirection: "column"
    gap: "2px"
    use: "左侧快速导航栏"
  quick-nav-item:
    width: "50px"
    height: "50px"
    display: "flex"
    flexDirection: "column"
    alignItems: "center"
    justifyContent: "center"
    fontSize: "20px"
    textDecoration: "none"
    transition: "all 0.3s"
    color: "{colors.text-white}"
    backgroundColor: "rgba(255,255,255,0.15)"
  quick-nav-item-active:
    backgroundColor: "rgba(255,255,255,0.35)"
    transform: "translateX(5px)"
  quick-nav-item-hover:
    backgroundColor: "rgba(255,255,255,0.3)"
    transform: "translateX(5px)"
  page-header:
    textAlign: "center"
    marginBottom: "{colors.section}"
    position: "relative"
  page-title:
    color: "{colors.text-white}"
    fontWeight: 700
    textShadow: "{shadows.text-shadow}"
    marginBottom: "15px"
  page-subtitle:
    color: "{colors.text-white}"
    opacity: 0.9
    fontSize: "18px"
    marginBottom: "20px"
  input-field:
    padding: "10px 15px"
    border: "2px solid {colors.border-medium}"
    borderRadius: "{rounded.md}"
    fontSize: "16px"
    width: "200px"
  input-field-focused:
    borderColor: "{colors.primary-blue}"
    outline: "none"
  file-item:
    display: "flex"
    justifyContent: "space-between"
    alignItems: "center"
    padding: "13px 15px"
    marginBottom: "8px"
    background: "{colors.surface}"
    borderRadius: "{rounded.md}"
    cursor: "pointer"
    transition: "all 0.3s"
    borderLeft: "3px solid transparent"
  file-item-hover:
    background: "{colors.surface-hover}"
    borderLeftColor: "{colors.primary-blue}"
  file-item-selected:
    background: "{colors.primary-blue}"
    color: "{colors.text-white}"
    borderLeftColor: "{colors.primary-green}"
  puzzle-cell:
    width: "40px"
    height: "40px"
    display: "flex"
    alignItems: "center"
    justifyContent: "center"
    background: "#f9f9f9"
    border: "1px solid {colors.border-light}"
    fontSize: "18px"
    fontWeight: 700
  puzzle-cell-filled:
    background: "{colors.canvas}"
    color: "{colors.text-primary}"
    borderColor: "{colors.text-primary}"
  puzzle-cell-blank:
    background: "{colors.canvas}"
    border: "2px dashed {colors.text-primary}"
  ranking-item:
    display: "flex"
    alignItems: "center"
    padding: "20px"
    background: "{colors.surface}"
    borderRadius: "{rounded.xl}"
    borderLeft: "4px solid {colors.border-light}"
    transition: "all 0.3s"
  ranking-item-hover:
    transform: "translateX(5px)"
    shadow: "0 5px 15px rgba(0,0,0,0.1)"
  timeline-item:
    display: "flex"
    gap: "20px"
    padding: "15px"
    background: "{colors.surface}"
    borderRadius: "{rounded.xl}"
    borderLeft: "4px solid {colors.primary-blue}"

layout:
  max-width: "900px"
  page-padding: "20px"
  grid-gap: "20px"
  card-gap: "30px"
  sidebar-width: "50px"
  responsive-breakpoints:
    mobile: "480px"
    tablet: "768px"
    desktop: "1024px"

animations:
  card-hover: "translateY(-10px) 0.3s ease"
  tab-hover: "translateY(-2px) 0.3s ease"
  button-hover: "translateY(-2px) 0.3s ease"
  button-scale: "scale(1.05) 0.3s ease"
  nav-hover: "translateX(5px) 0.3s ease"
  achievement-pulse: "scale 1 → 1.05 → 1, 2s infinite"
  save-message: "opacity 0 → 1 → 0, 2s"

print:
  hide-elements: [".quick-nav", ".header", ".controls", ".task-config", ".tabs", ".button-group"]
  background: "{colors.canvas}"
  shadow: "none"
  border: "2px solid {colors.primary-blue}"
  color-adjust: "exact"

---

## Overview

Cynthia Study 是一个专为小学生 Cynthia 设计的学习工具集，由家人打造。应用包含**日程表**、**阅读题生成器**、**成就墙**、**益智游戏**和**学习题库**五大模块，帮助孩子管理每日学习任务、练习阅读理解和做题巩固知识。

整体设计采用**活泼童趣**的视觉语言：渐变背景营造沉浸式体验，白色大圆角卡片承载内容，emoji 图标作为功能入口的视觉引导，pastel 色卡区分不同模块。所有页面支持打印输出，方便孩子离线使用。

**核心设计特征：**
- 渐变背景（蓝紫渐变为主）+ 白色卡片 = 沉浸式体验
- 大圆角卡片（`{rounded.xxl}` 20px）= 亲和力
- 72px emoji 图标 = 直观的功能识别
- Pastel 色卡 = 模块区分（蓝/绿/橙/粉/紫/青）
- 固定左侧导航栏 = 快速切换模块
- 全页面打印支持 = 离线使用场景

## Colors

### 模块色卡

每个功能模块对应一个专属颜色，贯穿卡片边框、按钮、图标高亮：

| 模块 | 颜色 | Hex | 使用场景 |
|------|------|-----|---------|
| 📅 日程表 | Blue | `{colors.primary-blue}` | 卡片 hover 边框、按钮、日程标题 |
| 📖 阅读题 | Green | `{colors.primary-green}` | 卡片 hover 边框、生成按钮 |
| 🏆 成就墙 | Orange | `{colors.primary-orange}` | Tab 激活态、统计卡片 |
| 🎮 游戏 | Pink | `{colors.primary-pink}` | 卡片 hover 边框、游戏按钮 |
| 📚 学习题库 | Purple | `{colors.primary-purple}` | 卡片 hover 边框、做题按钮 |
| 📊 统计 | Purple | `{colors.primary-purple}` | 统计数字、分隔线 |

### 页面渐变背景

| 渐变 | 使用页面 |
|------|---------|
| `{colors.gradient-blue-purple}` | 全局默认（Home, Schedule, Quiz, Achievement, Games） |
| `{colors.gradient-blue-teal}` | Study 学习题库（可定制） |

### 成就等级色

| 等级 | 颜色 | 卡片背景 |
|------|------|---------|
| 🥉 Bronze | `{colors.bronze}` | `{colors.bronze-light}` |
| 🥈 Silver | `{colors.silver}` | `{colors.silver-light}` |
| 🥇 Gold | `{colors.gold}` | `{colors.gold-light}` |

### 语义色

| 用途 | 颜色 | Hex |
|------|------|-----|
| ✅ 成功 | `{colors.success}` | `#4CAF50` |
| ⚠️ 警告 | `{colors.warning}` | `#FF9800` |
| ❌ 错误 | `{colors.error}` | `#F44336` |
| ℹ️ 信息 | `{colors.info}` | `#2196F3` |

## Typography

### 字体

**Microsoft YaHei**（微软雅黑）为主字体，fallback 链：`'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif`

### 层级

| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `{typography.display-xl}` | 42px | 700 | 页面标题 |
| `{typography.display-lg}` | 36px | 700 | Achievement 标题 |
| `{typography.display-md}` | 28px | 700 | 区块标题 |
| `{typography.heading-lg}` | 24px | 700 | 工具卡片标题 |
| `{typography.heading-md}` | 20px | 700 | 分类卡片标题 |
| `{typography.heading-sm}` | 18px | 700 | 卡片内标题 |
| `{typography.body-lg}` | 16px | 400 | 正文 |
| `{typography.body-md}` | 14px | 400 | 辅助文字 |
| `{typography.body-sm}` | 12px | 400 | 日期、提示 |
| `{typography.body-xs}` | 10px | 400 | 日程任务输入框 |
| `{typography.stat-number}` | 48px | 700 | 统计数字 |

## Layout

### 容器

- **最大宽度**: `{layout.max-width}` (900px)，居中
- **页面内边距**: `{layout.page-padding}` (20px)
- **卡片间距**: `{layout.card-gap}` (30px)
- **网格间距**: `{layout.grid-gap}` (20px)

### 响应式

| 断点 | 宽度 | 变化 |
|------|------|------|
| Mobile | < 480px | 单列布局，统计卡片全宽 |
| Tablet | 480 - 767px | 双列网格，日程表 2 列 |
| Desktop | ≥ 768px | 完整布局，日程表 7 列 |

### 导航

- 左侧固定导航栏（50px 宽），垂直居中
- 每个模块一个 emoji 图标 + 文字标签
- 激活态高亮 + 右移 5px 动画

## Components

### 工具卡片（Tool Card）

首页核心组件。白色大圆角卡片，居中布局，hover 上浮 10px + 模块色边框。

```
┌─────────────────────────┐
│         📅              │  ← 72px emoji
│   假期每日任务日程表      │  ← 24px bold
│                         │
│   管理每日学习任务        │  ← 14px 辅助文字
│   记录学习进度           │
│                         │
│   点击进入 →            │  ← 24px 箭头
└─────────────────────────┘
```

### 内容卡片（Content Card）

内容区主卡片，20px 圆角，30px 内边距，深色投影。

### 分类卡片（Category Card）

游戏和学习模块的分类选择卡片。16px 圆角，选中态蓝边框 + 渐变背景。

### 成就卡片（Achievement Card）

3px 边框区分等级（铜/银/金），解锁态 100% 不透明度 + hover 上浮，锁定态 60% 不透明度。

### 统计摘要卡片（Summary Card）

渐变背景 + 白色文字，展示数字统计。

### 按钮体系

| 类型 | 样式 | 使用场景 |
|------|------|---------|
| Primary | 纯色填充，8px 圆角 | 操作按钮（保存/清除/打印） |
| Gradient | 渐变填充，全圆角 | 游戏操作按钮 |
| Outline | 描边，全圆角 | 游戏预览区操作 |
| Tab | 白色卡片，激活态橙色 | Tab 切换 |

### 快速导航（Quick Nav）

左侧固定导航栏，50×50px 图标按钮，白色半透明背景，hover/激活态右移 5px。

## Depth & Elevation

| 级别 | 阴影 | 使用 |
|------|------|------|
| Card | `{shadows.card}` | 首页工具卡片 |
| Card Light | `{shadows.card-light}` | 内容区卡片 |
| Card Game | `{shadows.card-game}` | 游戏分类卡片 |
| Card SM | `{shadows.card-sm}` | 次级卡片 |
| Card XS | `{shadows.card-xs}` | 任务项、文件项 |

## Shapes

| Token | Value | Use |
|-------|-------|-----|
| `{rounded.sm}` | 5px | 周导航按钮 |
| `{rounded.md}` | 8px | 输入框、操作按钮 |
| `{rounded.lg}` | 10px | Tab 按钮 |
| `{rounded.xl}` | 15px | 内容卡片 |
| `{rounded.xxl}` | 20px | 工具卡片、主内容卡片 |
| `{rounded.full}` | 9999px | 游戏按钮、箭头按钮 |

## Do's and Don'ts

### Do
- ✅ 使用渐变背景营造沉浸式体验
- ✅ 白色大圆角卡片承载内容，与渐变背景形成对比
- ✅ 72px emoji 作为工具卡片的视觉引导
- ✅ 模块色卡区分功能（蓝/绿/橙/粉/紫）
- ✅ hover 动画统一使用 `translateY(-10px)` 上浮效果
- ✅ 所有页面支持打印输出，隐藏导航和操作控件
- ✅ 左侧固定导航栏保持模块间快速切换

### Don't
- ❌ 不要使用纯色背景替代渐变
- ❌ 不要在小屏幕上保留 7 列表格（日程表需降级为 2 列）
- ❌ 不要在卡片上使用过多阴影层级
- ❌ 不要在打印模式下显示导航栏和按钮
- ❌ 不要混用圆角尺寸（工具卡片统一 20px，内容卡片统一 15px）

## Page Structure

所有子页面（非首页）必须遵循统一的结构规范：

### 页面模板

```
┌──────────────────────────────────────┐
│  QuickNav (左侧固定导航栏)            │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  .page-wrapper                 │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  .page-header             │  │  │
│  │  │  ← 返回首页               │  │  │
│  │  │  🎯 页面标题               │  │  │
│  │  │  页面描述                  │  │  │
│  │  └──────────────────────────┘  │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  .content-card            │  │  │
│  │  │  页面主内容               │  │  │
│  │  └──────────────────────────┘  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### 结构规则

| 规则 | 说明 |
|------|------|
| 外层容器 | `.page-wrapper`，与首页一致的渐变背景 + 20px padding |
| 内容容器 | `.container`，max-width 900px，居中，白色大圆角卡片（20px），`{shadows.card}` |
| 页面头部 | `.page-header`，居中，40px 下边距 |
| 返回按钮 | 所有子页面**必须**在头部之前显示 `← 返回首页`，链接到 `/` |
| 标题 | emoji + 标题文本，32px bold，`{colors.primary-blue}` |
| 描述 | 16px，`{colors.text-secondary}` |
| 快速导航 | 除首页外，所有页面均引入 `<QuickNav />` |

### 返回按钮规范

```css
.btn-back {
  display: inline-block;
  padding: 8px 20px;
  background: {colors.surface};
  color: {colors.primary-blue};
  border: 2px solid {colors.border-light};
  border-radius: {rounded.md};
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  margin-bottom: 15px;
  transition: all 0.3s;
}
.btn-back:hover {
  background: {colors.primary-blue};
  color: {colors.text-white};
  border-color: {colors.primary-blue};
}
```

### 首页例外

首页不包含 QuickNav，不显示返回按钮，标题使用 `display-xl`（42px），白色文字 + 文字阴影。

### 各页面状态

| 页面 | QuickNav | 返回按钮 | 标题样式 | 背景渐变 |
|------|----------|---------|---------|---------|
| Home | ❌ | ❌ | 42px 白色 | blue-purple |
| Schedule | ✅ | ✅ | 32px blue | blue-purple |
| QuizGenerator | ✅ | ✅ | 32px blue | blue-purple |
| AchievementWall | ✅ | ✅ | 32px blue | blue-purple |
| PuzzleGames | ✅ | ✅ | 32px blue | blue-purple |
| Study | ✅ | ✅ | 32px blue | blue-purple |

## Print Behavior

所有页面必须支持打印输出：
- 隐藏 `.quick-nav`、`.header`、`.controls`、`.task-config`、`.tabs`、`.button-group`
- 背景变为白色
- 卡片投影移除，改为 2px 实线边框
- 输入框边框移除，显示纯文本
- 操作按钮隐藏
- 强制 `print-color-adjust: exact` 保留颜色

## Agent Prompt Guide

> 你是 Cynthia Study 项目的开发助手。遵循以下设计规范：
>
> **颜色**: 模块色卡 — 日程表 `#4A90D9`、阅读题 `#5CB85C`、成就 `#F0AD4E`、游戏 `#E91E63`、学习 `#9C27B0`
> **圆角**: 工具卡片 `20px`、内容卡片 `15px`、按钮 `8px`、游戏按钮 `full`
> **阴影**: 卡片 `0 10px 40px rgba(0,0,0,0.3)`、hover `0 20px 50px rgba(0,0,0,0.4)`
> **字体**: 微软雅黑，页面标题 `42px bold`，卡片标题 `24px bold`，正文 `14px`
> **布局**: 最大宽度 `900px`，居中，卡片间距 `30px`
> **动画**: hover 上浮 `translateY(-10px)`，过渡 `0.3s ease`
> **打印**: 所有页面必须支持打印，隐藏导航和操作控件