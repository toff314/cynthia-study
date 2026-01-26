function getTemplateHTML() {
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>阅读理解题</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }

        .header {
            text-align: center;
            padding-bottom: 30px;
            border-bottom: 3px solid #667eea;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .section {
            margin-bottom: 30px;
        }

        .section-title {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .question {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .question-number {
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }

        .question-text {
            font-size: 16px;
            line-height: 1.5;
            color: #333;
            margin-bottom: 15px;
        }

        .options {
            margin-left: 20px;
        }

        .option {
            padding: 4px 0;
            font-size: 15px;
            color: #555;
        }

        .option:hover {
            background: #e9ecef;
            border-radius: 5px;
            cursor: pointer;
        }

        .thinking-question {
            background: #fff9c4;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
        }

        .thinking-text {
            font-size: 16px;
            line-height: 1.5;
            color: #333;
        }

        .answer-space {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border: 2px dashed #ccc;
            border-radius: 8px;
            min-height: 100px;
        }

        .answer-title {
            font-size: 14px;
            color: #999;
            text-align: center;
            margin-bottom: 10px;
        }

        .fill-blank-question {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #2196f3;
        }

        .fill-blank-input {
            display: inline-block;
            width: 200px;
            padding: 8px 12px;
            border: 2px solid #2196f3;
            border-radius: 5px;
            font-size: 15px;
            margin: 5px 0;
            background: white;
            color: #333;
        }

        .fill-blank-input:focus {
            outline: none;
            border-color: #1976d2;
            box-shadow: 0 0 5px rgba(33, 150, 243, 0.3);
        }

        .matching-question {
            background: #fce4ec;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #e91e63;
        }

        .matching-container {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }

        .matching-column {
            flex: 1;
        }

        .matching-column.left {
            padding-right: 20px;
        }

        .matching-column.right {
            padding-left: 20px;
        }

        .matching-item {
            background: white;
            padding: 12px 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 2px solid #e91e63;
            font-size: 15px;
            color: #333;
        }

        .matching-line-hint {
            text-align: center;
            color: #666;
            font-size: 13px;
            margin-top: 15px;
            font-style: italic;
        }

        .separator {
            height: 3px;
            background: #667eea;
            margin: 40px 0;
            border-radius: 2px;
        }

        .answer-key {
            background: #e8f5e9;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #4caf50;
        }

        .answer-item {
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
        }

        .answer-label {
            color: #4caf50;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .answer-content {
            color: #333;
            line-height: 1.4;
        }

        .explanation {
            margin: 8px 0;
            padding: 8px;
            background: #f0f7ff;
            border-radius: 5px;
        }

        .print-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(76,175,80,0.3);
            transition: all 0.3s;
            z-index: 1000;
        }

        .print-btn:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76,175,80,0.4);
        }

        @media print {
            @page {
                size: A4;
                margin: 20mm;
            }

            body {
                background: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
                padding: 20px;
                max-width: 100%;
            }

            .print-btn {
                display: none !important;
            }

            .section {
                page-break-inside: avoid;
            }

            .answer-space,
            .fill-blank-input {
                border: 1px solid #ccc;
                background: white !important;
            }

            .fill-blank-input {
                min-height: 40px;
                background: #f8f9fa !important;
            }

            .fill-blank-input::placeholder {
                color: transparent !important;
            }

            .answer-title {
                display: none !important;
            }

            .separator {
                page-break-before: always;
                height: 0;
                margin: 20px 0;
            }
        }

        @media screen and (max-width: 768px) {
            .container {
                padding: 20px;
            }

            .header h1 {
                font-size: 22px;
            }

            .question-text,
            .thinking-text {
                font-size: 15px;
            }

            .fill-blank-input {
                width: 150px;
                font-size: 14px;
            }

            .print-btn {
                position: static;
                margin-bottom: 20px;
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ 打印</button>

    <div class="container">
        <div class="header">
            <h1 id="title">📚 阅读理解题</h1>
            <p id="subtitle"></p>
        </div>

        <div id="questions-container"></div>

        <div class="separator"></div>

        <div class="section">
            <div class="section-title" style="background: #4CAF50;">参考答案</div>
            <div id="answers-container"></div>
        </div>
    </div>

    <script>
        const quizData = {QUIZ_DATA_PLACEHOLDER};

        function getData() {
            return quizData;
        }

        function renderChoiceQuestion(question) {
            let html = '<div class="question"><div class="question-number">' + question.number + '. ' + question.text + '</div><div class="options">';
            for (let i = 0; i < question.options.length; i++) {
                html += '<div class="option">' + question.options[i] + '</div>';
            }
            html += '</div></div>';
            return html;
        }

        function renderEssayQuestion(question) {
            return '<div class="question thinking-question"><div class="question-number">' + question.number + '. 故事思考</div><div class="thinking-text"><p>' + question.text + '</p><p style="margin-top: 15px;">请写下你的想法：</p></div><div class="answer-space"><div class="answer-title">' + question.placeholder + '</div></div></div>';
        }

        function renderMatchingQuestion(question) {
            if (!question.leftItems || !question.rightItems) {
                return '';
            }
            let leftHtml = '';
            let rightHtml = '';
            for (let i = 0; i < question.leftItems.length; i++) {
                leftHtml += '<div class="matching-item">' + question.leftItems[i] + '</div>';
            }
            for (let i = 0; i < question.rightItems.length; i++) {
                rightHtml += '<div class="matching-item">' + question.rightItems[i] + '</div>';
            }
            return '<div class="question matching-question"><div class="question-number">' + question.number + '. 连线题</div><div class="matching-container"><div class="matching-column left">' + leftHtml + '</div><div class="matching-column right">' + rightHtml + '</div></div><div class="matching-line-hint">请用线将左边和右边对应的内容连起来</div></div>';
        }

        function renderFillBlankQuestion(question) {
            let html = '<div class="question fill-blank-question">';
            if (question.blanks) {
                html += '<div class="question-number">' + question.number + '. 填字题</div><div class="question-text">';
                for (let i = 0; i < question.blanks.length; i++) {
                    let blank = question.blanks[i];
                    let blankText = blank.text.replace(/______/g, '<input type="text" class="fill-blank-input" placeholder="' + blank.placeholder + '" data-answer="' + (blank.answer || '') + '">');
                    html += '<p style="margin-bottom: 10px;">' + blankText + '</p>';
                }
                html += '</div>';
                if (question.explanation) {
                    html += '<p class="explanation"><strong>解析：</strong>' + question.explanation + '</p>';
                }
            } else {
                let questionHtml = question.text.replace(/__________/g, '<input type="text" class="fill-blank-input" placeholder="' + question.placeholder + '" data-answer="' + question.answer + '">');
                html += '<div class="question-number">' + question.number + '. 填空题</div><div class="question-text">' + questionHtml + '</div>';
                if (question.explanation) {
                    html += '<p class="explanation"><strong>解析：</strong>' + question.explanation + '</p>';
                }
            }
            html += '</div>';
            return html;
        }

        function renderAnswers(sections) {
            let answersHtml = '<div class="answer-key">';
            let choiceAnswers = [];
            let essayAnswers = [];
            let matchingAnswers = [];
            let fillBlankAnswers = [];
            
            for (let i = 0; i < sections.length; i++) {
                let section = sections[i];
                for (let j = 0; j < section.questions.length; j++) {
                    let question = section.questions[j];
                    if (question.type === 'choice') {
                        choiceAnswers.push(question);
                    } else if (question.type === 'essay') {
                        essayAnswers.push(question);
                    } else if (question.type === 'matching') {
                        matchingAnswers.push(question);
                    } else if (question.type === 'fill_in_blank') {
                        fillBlankAnswers.push(question);
                    }
                }
            }
            
            if (choiceAnswers.length > 0) {
                answersHtml += '<div class="answer-item"><div class="answer-label">一、选择题</div><div class="answer-content">';
                for (let i = 0; i < choiceAnswers.length; i++) {
                    let q = choiceAnswers[i];
                    answersHtml += '<p style="margin-top: 15px;"><strong>' + q.number + '. ' + q.answer + '</strong></p>';
                    if (q.explanation) {
                        answersHtml += '<p class="explanation"><strong>解析：</strong>' + q.explanation + '</p>';
                    }
                }
                answersHtml += '</div></div>';
            }
            
            if (essayAnswers.length > 0) {
                answersHtml += '<div class="answer-item" style="margin-top: 15px;"><div class="answer-label">二、思考题</div><div class="answer-content"><p><strong>参考答案：</strong></p><p>这句话的意思是，如果一个人（或女巫）只掌握一种技能（魔法），而不去学习更广泛的知识，那么她的能力是不完整的、肤浅的。在故事里，外婆需要懂得森林里每一种植物的药性，才能帮助受伤的小动物；需要知道天气变化的规律，才能更好地保护森林。这些都需要书本知识。如果只靠魔法，她可能无法真正理解事物的原理，也无法妥善解决所有问题。外婆用这句话告诉我们，学习各门类的知识，能让我们变得更强大、更有智慧，能更好地帮助他人和解决问题。</p><p class="explanation"><strong>解析要点：</strong></p><p>• 理解"半吊子"的比喻义（不完整、不专业）。</p><p>• 能结合故事中外婆学习多种知识的情节（如森林、动物、星星）。</p><p>• 能阐释知识相对于单一技能（魔法）的优越性（理解原理、解决问题）。</p><p>• 鼓励联系实际，如学习各门学科的意义。</p></div></div>';
            }
            
            if (matchingAnswers.length > 0) {
                answersHtml += '<div class="answer-item" style="margin-top: 15px;"><div class="answer-label">三、连线题</div><div class="answer-content">';
                for (let i = 0; i < matchingAnswers.length; i++) {
                    let q = matchingAnswers[i];
                    answersHtml += '<p style="margin-top: 10px;">';
                    for (let j = 0; j < q.answers.length; j++) {
                        answersHtml += '<strong>' + q.answers[j][0] + ' —— ' + q.answers[j][1] + '</strong><br>';
                    }
                    answersHtml += '</p>';
                    if (q.explanation) {
                        answersHtml += '<p class="explanation"><strong>解析：</strong>' + q.explanation + '</p>';
                    }
                }
                answersHtml += '</div></div>';
            }
            
            if (fillBlankAnswers.length > 0) {
                answersHtml += '<div class="answer-item" style="margin-top: 15px;"><div class="answer-label">四、填字题</div><div class="answer-content">';
                for (let i = 0; i < fillBlankAnswers.length; i++) {
                    let q = fillBlankAnswers[i];
                    if (q.blanks) {
                        for (let j = 0; j < q.blanks.length; j++) {
                            let blank = q.blanks[j];
                            let blankAnswer = blank.answer || (blank.answers ? blank.answers.join('、') : '');
                            answersHtml += '<p style="margin-top: 10px;"><strong>第' + (j + 1) + '空：' + blankAnswer + '</strong></p>';
                        }
                        if (q.explanation) {
                            answersHtml += '<p class="explanation"><strong>解析：</strong>' + q.explanation + '</p>';
                        }
                    } else {
                        answersHtml += '<p style="margin-top: 10px;"><strong>' + q.number + '. ' + q.answer + '</strong></p>';
                        if (q.explanation) {
                            answersHtml += '<p class="explanation"><strong>解析：</strong>' + q.explanation + '</p>';
                        }
                    }
                }
                answersHtml += '</div></div>';
            }
            
            answersHtml += '</div>';
            return answersHtml;
        }

        function init() {
            const data = getData();
            if (!data) {
                alert('数据未加载');
                return;
            }
            
            document.getElementById('title').textContent = '📚 ' + data.title;
            document.getElementById('subtitle').textContent = data.subtitle;
            
            const questionsContainer = document.getElementById('questions-container');
            let questionsHtml = '';
            
            for (let i = 0; i < data.sections.length; i++) {
                let section = data.sections[i];
                questionsHtml += '<div class="section"><div class="section-title">' + section.title + '</div>';
                for (let j = 0; j < section.questions.length; j++) {
                    let question = section.questions[j];
                    switch (question.type) {
                        case 'choice':
                            questionsHtml += renderChoiceQuestion(question);
                            break;
                        case 'essay':
                            questionsHtml += renderEssayQuestion(question);
                            break;
                        case 'matching':
                            questionsHtml += renderMatchingQuestion(question);
                            break;
                        case 'fill_in_blank':
                            questionsHtml += renderFillBlankQuestion(question);
                            break;
                        default:
                            console.warn('未知的题目类型:', question.type);
                    }
                }
                questionsHtml += '</div>';
            }
            
            questionsContainer.innerHTML = questionsHtml;
            
            const answersContainer = document.getElementById('answers-container');
            answersContainer.innerHTML = renderAnswers(data.sections);
        }

        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>`;
}
