import streamlit as st
from groq import Groq

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="CodeMate 💻", page_icon="🚀", layout="wide")

# --- 2. ФУНКЦИЯ ИИ (МОЗГИ) ---
def get_ai_response(messages, language="General", deep_thinking=False):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Базовый промпт
        system_prompt = f"""Ты — CodeMate, опытный Senior Developer.
Твоя задача — помогать с кодом на языке: {language}.

Правила:
1. Пиши чистый, рабочий код.
2. Объясняй ошибки простым языком.
3. Если код сломан — сначала скажи ГДЕ ошибка, потом дай исправление.
4. Используй Markdown для выделения кода (```).
5. Отвечай кратко, без лишней воды."""

        # Если включен режим глубокого размышления — расширяем промпт
        if deep_thinking:
            system_prompt += """
Дополнительно:
- Подумай шаг за шагом перед тем, как дать ответ.
- Рассмотри несколько подходов, если это уместно.
- Объясни плюсы и минусы предложенного решения.
- Удели внимание безопасности, читаемости и производительности кода.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=4000 if deep_thinking else 2000,  # Больше токенов для анализа
            temperature=0.3 if deep_thinking else 0.1   # Чуть больше креатива при анализе
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
    # Добавляем вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ ИИ
    with st.chat_message("assistant"):
        with st.spinner("Думаю..." if st.session_state.deep_thinking else "Пишу код..."):
            response = get_ai_response(
                st.session_state.messages, 
                st.session_state.lang, 
                st.session_state.deep_thinking
            )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
