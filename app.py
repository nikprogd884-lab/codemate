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

# --- 6. АНИМАЦИЯ МАТРИЦЫ НА ВЕСЬ ФОН (ПОЛНОСТЬЮ ИСПРАВЛЕНО) ---
matrix_fullscreen_html = """
<style>
/* КРИТИЧЕСКИ ВАЖНО: перебить все стили Streamlit */
.stApp {
    position: relative !important;
    overflow: hidden !important;
}
#matrix-bg {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    z-index: -1 !important;
    pointer-events: none !important;
    background-color: #000 !important;
}
#matrix-canvas {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
}
</style>

<div id="matrix-bg">
    <canvas id="matrix-canvas"></canvas>
</div>

<script>
// Запускаем анимацию после полной загрузки
window.addEventListener('load', function() {
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    
    // Убедимся, что canvas имеет правильные размеры
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Настройки анимации
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = Array(columns).fill().map(() => Math.random() * -100);
    
    function draw() {
        // Очистим предыдущий кадр
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Нарисуем новые символы
        ctx.fillStyle = '#0F0';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < columns; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Если символ вышел за пределы экрана, вернем его в начало
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            drops[i]++;
        }
        
        requestAnimationFrame(draw);
    }
    
    // Запустим анимацию
    draw();
});
</script>
"""

html(matrix_fullscreen_html, height=1000)  # высота не важна — canvas растягивается на весь экран
