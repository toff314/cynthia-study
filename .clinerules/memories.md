# Data Management
- read.html页面需支持从项目`@read`目录和本地上传JSON文件的两种方式。
- 用户偏好使用逗号分隔的输入框配合导入按钮来配置和还原默认任务列表，而非硬编码数组。
- Achievement badge systems, including names and unlock criteria, must be configured via external JSON data.
- get_schedule的学生姓名和班级参数必须设为必填，create_or_update_schedule调用时需从data传入，严禁简化为取第一条。

# Development Tools
- Prefer backend stack using FastAPI and SQLite, serving static files via backend services for simplicity.
- For data visualization features, prefer using ECharts or Chart.js libraries.

# Environment Configuration
- 英文Windows环境下需解决ASGI默认latin-1编码与UTF-8文件保存的冲突及IDE乱码问题。
- 前端开发服务器需将host配置为0.0.0.0以暴露IP供局域网访问。

# Default_Data
- The default task list includes 晨读, 完成作业, 体育锻炼, 阅读, and 家务.

# UI/UX
- 用户偏好默认任务配置的整体div布局应位于三个操作按钮整体的上方。
- 保存日程表操作完成后需显示保存成功的提示消息。
- 打印日程表时仅需输出每周任务安排内容，需排除寒假每日任务日程表、默认任务配置区域及按钮。
- 打印测验生成器时仅输出预览内容，且参考答案的分页符必须位于“参考答案”文字之前。
- QuizGenerator组件需允许重复选择JSON文件并支持生成页面预览。
- Home.vue 页面底部需添加创作者 Cynthia 的署名及家长联系方式的版权文案。
- In achievement displays, unlocked badges should be listed before locked ones, and use CSS animations.
- AchievementWall顶部需统计隐藏成就数量，未解锁时隐藏相关区域，解锁后展开，且每个成就需展示翻译为中文的匹配规则。
- Home.vue页面底部统计模块需包含总访问人数、总访问次数、日程数、阅读题数及成就数，且置于页面最后。

# Data Persistence
- Schedule页面需将班级和姓名通过Cookie持久化，并在下次加载时从Cookie自动恢复数据。

# Business Logic
- 成就计算逻辑根据 task_name 包含“阅读”或“读书”关键词进行匹配。
- AchievementWall.vue页面应移除学生选择相关逻辑，仅展示当前用户自己的成就。

# Security
- 文件上传必须限制大小不超过1M，并实施防止文件注入攻击的安全验证措施。
