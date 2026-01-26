// 使用内嵌的数据（无需外部服务器）
function getData() {
    return window.quizData;
}

// 渲染选择题
function renderChoiceQuestion(question) {
    let html = `
        <div class="question">
            <div class="question-number">${question.number}. ${question.text}</div>
            <div class="options">
    `;
    
    question.options.forEach(option => {
        html += `<div class="option">${option}</div>`;
    });
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

// 渲染思考题
function renderEssayQuestion(question) {
    return `
        <div class="question thinking-question">
            <div class="question-number">${question.number}. 故事思考</div>
            <div class="thinking-text">
                <p>${question.text}</p>
                <p style="margin-top: 15px;">请写下你的想法：</p>
            </div>
            <div class="answer-space">
                <div class="answer-title">${question.placeholder}</div>
            </div>
        </div>
    `;
}

// 渲染填空题
function renderFillBlankQuestion(question) {
    // 替换下划线为输入框
    const questionHtml = question.text.replace(/__________/g, `
        <input type="text" class="fill-blank-input" placeholder="${question.placeholder}" data-answer="${question.answer}">
    `);
    
    return `
        <div class="question fill-blank-question">
            <div class="question-number">${question.number}. 填空题</div>
            <div class="question-text">${questionHtml}</div>
        </div>
    `;
}

// 渲染答案
function renderAnswers(sections) {
    let answersHtml = '<div class="answer-key">';
    
    let choiceAnswers = [];
    let essayAnswers = [];
    let fillBlankAnswers = [];
    
    sections.forEach(section => {
        section.questions.forEach(question => {
            if (question.type === 'choice') {
                choiceAnswers.push(question);
            } else if (question.type === 'essay') {
                essayAnswers.push(question);
            } else if (question.type === 'fill_in_blank') {
                fillBlankAnswers.push(question);
            }
        });
    });
    
    // 选择题答案
    if (choiceAnswers.length > 0) {
        answersHtml += `
            <div class="answer-item">
                <div class="answer-label">一、选择题</div>
                <div class="answer-content">
        `;
        
        choiceAnswers.forEach(q => {
            answersHtml += `
                <p style="margin-top: 15px;"><strong>${q.number}. ${q.answer}</strong></p>
                ${q.explanation ? `<p class="explanation"><strong>解析：</strong>${q.explanation}</p>` : ''}
            `;
        });
        
        answersHtml += `
                </div>
            </div>
        `;
    }
    
    // 思考题答案
    if (essayAnswers.length > 0) {
        answersHtml += `
            <div class="answer-item" style="margin-top: 15px;">
                <div class="answer-label">二、思考题（参考答案，答案不唯一）</div>
                <div class="answer-content">
                    <p>开放性问题，鼓励学生发挥想象力和创造力。可以从以下角度回答：</p>
                    <p style="margin-top: 10px;">1. 想要听冒险故事，因为向往勇敢和探索</p>
                    <p>2. 想要听温馨的家庭故事，因为感受到亲情的温暖</p>
                    <p>3. 想要听科幻故事，因为对未来的世界充满好奇</p>
                    <p>4. 想要听英雄故事，因为希望能帮助他人</p>
                    <p>5. 其他合理的想象和理由</p>
                    <p style="margin-top: 15px; color: #4caf50; font-weight: bold;">评分标准：只要理由充分、表达清楚、想象合理，即可得满分。</p>
                </div>
            </div>
        `;
    }
    
    // 填空题答案
    if (fillBlankAnswers.length > 0) {
        answersHtml += `
            <div class="answer-item" style="margin-top: 15px;">
                <div class="answer-label">三、填空题</div>
                <div class="answer-content">
        `;
        
        fillBlankAnswers.forEach(q => {
            answersHtml += `
                <p style="margin-top: 10px;"><strong>${q.number}. ${q.answer}</strong></p>
            `;
        });
        
        answersHtml += `
                </div>
            </div>
        `;
    }
    
    answersHtml += '</div>';
    return answersHtml;
}

// 主函数：初始化页面
function init() {
    const data = getData();
    
    if (!data) {
        alert('数据未加载');
        return;
    }
    
    // 设置标题
    document.getElementById('title').textContent = '📚 ' + data.title;
    document.getElementById('subtitle').textContent = data.subtitle;
    
    // 渲染题目
    const questionsContainer = document.getElementById('questions-container');
    let questionsHtml = '';
    
    data.sections.forEach(section => {
        questionsHtml += `
            <div class="section">
                <div class="section-title">${section.title}</div>
        `;
        
        section.questions.forEach(question => {
            switch (question.type) {
                case 'choice':
                    questionsHtml += renderChoiceQuestion(question);
                    break;
                case 'essay':
                    questionsHtml += renderEssayQuestion(question);
                    break;
                case 'fill_in_blank':
                    questionsHtml += renderFillBlankQuestion(question);
                    break;
                default:
                    console.warn('未知的题目类型:', question.type);
            }
        });
        
        questionsHtml += '</div>';
    });
    
    questionsContainer.innerHTML = questionsHtml;
    
    // 渲染答案
    const answersContainer = document.getElementById('answers-container');
    answersContainer.innerHTML = renderAnswers(data.sections);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
