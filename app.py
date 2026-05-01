import streamlit as st
from groq import Groq
from streamlit.components.v1 import html

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="CodeMate 💻", page_icon="🚀", layout="wide")

# --- 2. ФУНКЦИЯ ИИ (МОЗГИ) ---
def get_ai_response(messages, language="General", deep_thinking=False):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        if deep_thinking:
            # === ЭТАП 1: ГЕНЕРАЦИЯ ЧЕРНОВИКА ===
            draft_system_prompt = f"""Ты — CodeMate, Senior Developer.
Проанализируй задачу и напиши ЧЕРНОВИК решения на языке: {language}.
Не оптимизируй, не объясняй — просто запиши рабочий код или структуру.
Если задача непонятна — задай уточняющие вопросы в черновике."""
            
            draft_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": draft_system_prompt}] + messages,
                max_tokens=2000,
                temperature=0.7
            )
            draft = draft_resp.choices[0].message.content
            
            # === ЭТАП 2: УЛУЧШЕНИЕ ЧЕРНОВИКА ===
            refine_system_prompt = f"""Ты — CodeMate, эксперт-ревьювер.
Проанализируй ЧЕРНОВИК и создай финальное решение на языке: {language}.
Следуй правилам:
1. Сделай код безопасным, читаемым и эффективным.
2. Добавь комментарии к сложным местам.
3. Объясни ключевые архитектурные решения.
4. Убери лишнее, оптимизируй.
5. Если в черновике есть ошибки — исправь их.
6. Ответ должен быть готов к использованию."""
            
            refine_messages = [
                {"role": "system", "content": refine_system_prompt},
                {"role": "user", "content": f"ЧЕРНОВИК:\n{draft}"}
            ]
            
            final_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=refine_messages,
                max_tokens=4000,
                temperature=0.3
            )
            return final_resp.choices[0].message.content
        
        else:
            # === БЫСТРЫЙ РЕЖИМ (ОДИН ЭТАП) ===
            system_prompt = f"""Ты — CodeMate, опытный Senior Developer.
Твоя задача — помогать с кодом на языке: {language}.

Правила:
1. Пиши чистый, рабочий код.
2. Объясняй ошибки простым языком.
3. Если код сломан — сначала скажи ГДЕ ошибка, потом дай исправление.
4. Используй Markdown для выделения кода (```).
5. Отвечай кратко, без лишней воды."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}] + messages,
                max_tokens=2000,
                temperature=0.1
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

# --- 3. ПАМЯТЬ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lang" not in st.session_state:
    st.session_state.lang = "Python"
if "deep_thinking" not in st.session_state:
    st.session_state.deep_thinking = False

# --- 4. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.title("⚙️ Настройки")
    st.session_state.lang = st.selectbox("Язык программирования:", 
                                         ["Python", "JavaScript", "C# (Unity)", "C++", "Java", "HTML/CSS"], 
                                         index=0)
    st.session_state.deep_thinking = st.toggle("🧠 Глубокое размышление", value=False)
    st.divider()
    if st.button("🗑️ Очистить чат"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Powered by Groq & Llama 3.3")

# --- 5. ОСНОВНОЙ ЭКРАН ---
st.title("💻 CodeMate")
st.caption(f"Режим: **{st.session_state.lang}** | {'🧠 Глубокий' if st.session_state.deep_thinking else '⚡ Быстрый'}")

# История чата
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ввод
if prompt := st.chat_input("Вставь код или задай вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_text = "Думаю глубоко..." if st.session_state.deep_thinking else "Пишу код..."
        with st.spinner(status_text):
            response = get_ai_response(
                st.session_state.messages, 
                st.session_state.lang, 
                st.session_state.deep_thinking
            )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Автопрокрутка вниз
    st.markdown('<script>setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 100);</script>', unsafe_allow_html=True)

# --- 6. АНИМАЦИЯ МАТРИЦЫ (весь фон) ---
matrix_html = """
<div id="matrix-bg" style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    z-index: -1;
    background: #000;
">
    <canvas id="matrix-canvas" style="display: block; width: 100%; height: 100%;"></canvas>
</div>

<script>
(function() {
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = Array(columns).fill().map(() => Math.random() * -100);

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0F0';
        ctx.font = `${fontSize}px monospace`;

        for (let i = 0; i < columns; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }

        requestAnimationFrame(draw);
    }

    draw();
})();
</script>
"""

html(matrix_html, height=0, width=0)
