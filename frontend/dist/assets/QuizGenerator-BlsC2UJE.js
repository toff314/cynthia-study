import{d as I,o as T,c as n,b as A,a as e,m as M,j as _,n as h,e as z,p as C,F as $,k as L,t as g,r as o,h as l,q as Q}from"./index-CpVmrF2H.js";import{r as w,_ as B}from"./_plugin-vue_export-helper-D_9GqElE.js";import{Q as j}from"./QuickNav-DTpNmUod.js";const m={getFiles:()=>w.get("/api/quiz/files"),getFile:r=>w.get("/api/quiz/file",{params:{name:r}}),saveQuiz:r=>w.post("/api/quiz/save",r),downloadFile:r=>{window.open(`/api/quiz/download?name=${encodeURIComponent(r)}`,"_blank")}},P={class:"quiz-generator"},V={class:"container"},G={key:0,class:"ai-prompt"},U={class:"upload-method"},R={class:"card"},W={key:0,class:"file-list"},Y=["onClick"],K={class:"file-item-name"},X={class:"file-item-actions"},Z=["onClick"],ee={class:"file-item-date"},te={key:1,class:"empty-state"},ae={class:"card-footer"},se=["disabled"],ie={class:"card"},ne={class:"file-upload"},oe={class:"button-group"},le=["disabled"],re=["disabled"],de={key:0,class:"preview"},ce=["srcdoc"],ue=I({__name:"QuizGenerator",setup(r){const d=o("server"),f=o([]),c=o(""),i=o(null),u=o(""),p=o(!1),b=o(!1),x=async()=>{p.value=!0;try{const a=await m.getFiles();a.success&&(f.value=a.data.files)}catch(a){console.error("加载文件列表失败:",a)}finally{p.value=!1}},S=a=>{c.value=a},F=async()=>{if(c.value){p.value=!0;try{const a=await m.getFile(c.value);a.success&&(i.value=JSON.parse(a.data.content),i.value&&await k(i.value))}catch(a){console.error("加载文件内容失败:",a)}finally{p.value=!1}}},N=async a=>{var y;const t=a.target,s=(y=t.files)==null?void 0:y[0];if(!s)return;const v=new FileReader;v.onload=async H=>{var q;try{i.value=JSON.parse((q=H.target)==null?void 0:q.result),i.value&&await k(i.value),t.value=""}catch{alert("JSON文件格式错误，请检查文件内容")}},v.readAsText(s)},k=async a=>{try{(await m.saveQuiz(a)).success&&alert(`✅ 文件加载成功！包含 ${a.sections.length} 个章节

`)}catch(t){console.error("文件加载失败:",t)}},O=()=>{if(!i.value)return;const a=E(),t=JSON.stringify(i.value,null,2);u.value=a.replace("const quizData = {};",`const quizData = ${t};`)},D=()=>{if(!u.value)return;const a=document.querySelector(".preview iframe");a&&a.contentWindow&&a.contentWindow.print()},J=a=>{m.downloadFile(a)},E=()=>`<!DOCTYPE html>
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
</html>`;return T(()=>{x()}),(a,t)=>(l(),n("div",P,[A(j),e("div",V,[t[11]||(t[11]=e("div",{class:"header"},[e("h1",null,"📚 阅读题生成器"),e("p",null,"选择JSON数据文件，生成阅读理解题页面")],-1)),t[12]||(t[12]=e("div",{class:"info-box"},[e("p",null,[e("strong",null,"💡 使用说明：")]),e("ul",{class:"info-list"},[e("li",null,"选择JSON文件后，系统会自动将其保存到数据目录"),e("li",null,"点击文件列表中的下载图标可下载JSON文件"),e("li",null,"下载文件后，可使用AI工具生成新的阅读题JSON数据")])],-1)),e("div",{class:"tip-box",onClick:t[0]||(t[0]=s=>b.value=!b.value)},[t[4]||(t[4]=e("p",null,[e("strong",null,"🤖 AI生成提示词（点击展开/折叠）")],-1)),b.value?(l(),n("div",G,[...t[3]||(t[3]=[M('<p data-v-75089246>你可以将下载的JSON文件内容发送给AI工具（如ChatGPT、DeepSeek等），使用以下提示词生成新的阅读题：</p><div class="prompt-text" data-v-75089246>你是一个文学专家，请根据以下示例JSON结构生成 [书籍名称] 的阅读题目，包含4个选择题和1个思考题，并包含答案解析，请只返回JSON数据便于我保存。</div><p class="prompt-note" data-v-75089246>💡 提示：将 &quot;[书籍名称]&quot; 替换为你想要生成阅读题的书名</p><div class="ai-links" data-v-75089246><p class="ai-links-title" data-v-75089246>🔗 推荐AI工具：</p><div class="ai-links-list" data-v-75089246><a href="https://chat.deepseek.com/" target="_blank" class="ai-link" data-v-75089246>💬 DeepSeek</a><a href="https://www.doubao.com/chat/" target="_blank" class="ai-link" data-v-75089246>☕ 豆包</a><a href="https://tongyi.aliyun.com/" target="_blank" class="ai-link" data-v-75089246>🌊 通义千问</a><a href="https://kimi.moonshot.cn/" target="_blank" class="ai-link" data-v-75089246>🌙 Kimi</a><a href="https://yiyan.baidu.com/" target="_blank" class="ai-link" data-v-75089246>🧠 文心一言</a><a href="https://chatglm.cn/" target="_blank" class="ai-link" data-v-75089246>🤖 智谱清言</a></div></div>',4)])])):_("",!0)]),e("div",U,[e("div",{class:h(["method-tab",{active:d.value==="server"}]),onClick:t[1]||(t[1]=s=>d.value="server")}," 📂 从项目选择 ",2),e("div",{class:h(["method-tab",{active:d.value==="local"}]),onClick:t[2]||(t[2]=s=>d.value="local")}," 💻 本地上传 ",2)]),z(e("div",R,[e("div",{class:"card-header"},[t[5]||(t[5]=e("h3",null,"项目文件列表",-1)),e("button",{class:"btn-refresh",onClick:x},"🔄 刷新")]),f.value.length>0?(l(),n("div",W,[(l(!0),n($,null,L(f.value,s=>(l(),n("div",{key:s.name,class:h(["file-item",{selected:c.value===s.name}])},[e("div",{class:"file-item-info",onClick:v=>S(s.name)},[t[6]||(t[6]=e("span",{class:"file-item-icon"},"📄",-1)),e("span",K,g(s.name),1)],8,Y),e("div",X,[e("button",{class:"btn-download-icon",onClick:Q(v=>J(s.name),["stop"]),title:"下载JSON文件"}," ⬇️ ",8,Z),e("span",ee,g(s.modified),1)])],2))),128))])):(l(),n("div",te,g(p.value?"加载中...":"📭 暂无文件"),1)),e("div",ae,[e("button",{class:"btn btn-primary",disabled:!c.value,onClick:F}," ✅ 选择此文件 ",8,se)])],512),[[C,d.value==="server"]]),z(e("div",ie,[t[9]||(t[9]=e("div",{class:"card-header"},[e("h3",null,"本地上传")],-1)),e("div",ne,[e("input",{type:"file",id:"jsonFile",class:"file-input",onChange:N,accept:".json"},null,32),t[7]||(t[7]=e("label",{for:"jsonFile",class:"file-label"},[e("span",{class:"file-label-icon"},"📁"),e("span",{class:"file-label-text"},"点击选择JSON文件")],-1)),t[8]||(t[8]=e("p",{class:"file-upload-hint"},"支持 .json 格式文件",-1))])],512),[[C,d.value==="local"]]),e("div",oe,[e("button",{class:"btn btn-generate",disabled:!i.value,onClick:O}," ✨ 生成页面 ",8,le),e("button",{class:"btn btn-download",disabled:!u.value,onClick:D}," 🖨️ 打印阅读题 ",8,re)]),u.value?(l(),n("div",de,[t[10]||(t[10]=e("div",{class:"preview-title"},"预览",-1)),e("iframe",{srcdoc:u.value,style:{width:"100%",height:"600px",border:"none"}},null,8,ce)])):_("",!0)])]))}}),be=B(ue,[["__scopeId","data-v-75089246"]]);export{be as default};
