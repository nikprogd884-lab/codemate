import streamlit as st
from groq import Groq

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="CodeMate 💻", page_icon="🚀", layout="wide")

# --- 2. ФУНКЦИЯ ИИ (МОЗГИ) ---
def get_ai_response(messages, language="General"):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Промпт для программирования
        system_prompt = f"""Ты — CodeMate, опытный Senior Developer.
Твоя задача — помогать с кодом на языке: {language}.

Правила:
1. Пиши чистый, рабочий код.
2. Объясняй ошибки простым языком.
3. Если код сломан — сначала скажи ГДЕ ошибка, потом дай исправление.
4. Используй Markdown для выделения кода (```).
5. Отвечай кратко, без лишней воды."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Отличная модель для кода
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=2000,
            temperature=0.1 # Меньше фантазий, больше точности
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

# --- 3. ПАМЯТЬ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lang" not in st.session_state:
    st.session_state.lang = "Python"

# --- 4. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.title("⚙️ Настройки")
    st.session_state.lang = st.selectbox("Язык программирования:", 
                                         ["Python", "JavaScript", "C# (Unity)", "C++", "Java", "HTML/CSS"], 
                                         index=0)
    st.divider()
    if st.button("🗑️ Очистить чат"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Powered by Groq & Llama 3.3")

# --- 5. ОСНОВНОЙ ЭКРАН ---
st.title("💻 CodeMate")
st.caption(f"Режим: **{st.session_state.lang}**")

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
        with st.spinner("Думаю..."):
            response = get_ai_response(st.session_state.messages, st.session_state.lang)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
