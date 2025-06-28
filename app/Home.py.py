import base64
from os import getenv, environ
from io import BytesIO
from typing import List
from pathlib import Path
import os
import json

import nest_asyncio
import streamlit as st
from PIL import Image
from phi.agent import Agent
from phi.document import Document
from phi.document.reader import Reader
from phi.document.reader.website import WebsiteReader
from phi.document.reader.pdf import PDFReader
from phi.document.reader.text import TextReader
from phi.document.reader.docx import DocxReader
from phi.document.reader.csv_reader import CSVReader
from phi.utils.log import logger

from agents.example import get_example_agent, get_product_catalog_agent, get_sales_analysis_agent
from agents.settings import agent_settings
import logging

logging.basicConfig(level=logging.DEBUG)


# تنظیم مسیر استاتیک برای نمودارها
CHARTS_DIR = Path(agent_settings.charts_dir)
if not CHARTS_DIR.exists():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ایجاد لینک به مسیر استاتیک اگر وجود نداشت
STATIC_PATH = Path("/app/static")
if not STATIC_PATH.exists():
    os.symlink("/app/storage", STATIC_PATH)

# تنظیم آدرس API
API_URL = "http://localhost:8000"

nest_asyncio.apply()

st.set_page_config(
    page_title="AdminAI",
    page_icon=":orange_heart:",
    menu_items={},
    initial_sidebar_state="collapsed",
    layout="wide"
)

st.markdown("""
<style>
/* تنظیم تم روشن */
:root {
    --primary-color: #1976d2;
    background-color: white;
}

[data-testid="stAppViewContainer"] {
    background-color: white;
}

[data-testid="stSidebar"] {
    background-color: white;
}

[data-testid="stHeader"] {
    background-color: white;
}

.stApp {
    background-color: white !important;
}

.main {
    background-color: white !important;
}

/* استایل‌های جدید برای هدر */
.column-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f0f0f0;
}

.column-header h2 {
    color: #1976d2;
    font-size: 1.8rem;
    margin: 0;
    text-align: center;
}

/* بهبود استایل کارت‌ها */
.question-category {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.question-category:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* استایل‌های قبلی */
[data-testid="stMarkdownContainer"] {
    direction: rtl;
    text-align: right;
}

.stChatMessage {
    direction: rtl;
    text-align: right;
}

.stChatMessageContent {
    direction: rtl;
    text-align: right;
}

[data-testid="stChatInput"] {
    direction: rtl;
    text-align: right;
}

[data-testid="stToolbar"] {
    display: none;
}

[data-testid="stChatInput"]::placeholder {
    content: "پیام خود را بنویسید...";
}

.st-emotion-cache-s1k4sy {
    flex-direction: row-reverse !important;
}

.st-emotion-cache-f4ro0r {
    position: absolute !important;
    left: 0 !important;
    right: unset !important;
}

.st-emotion-cache-1up18o9 svg,
.st-emotion-cache-1ch8vux svg {
    transform: rotate(180deg) !important;
}

.st-emotion-cache-1up18o9,
.st-emotion-cache-1ch8vux {
    padding: 0.5rem !important;
}

/* استایل‌های جدید برای گرید سوالات */
.questions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    width: 100%;
    padding: 1rem;
    margin: 0 auto;
}

.category-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid #f0f0f0;
}

.category-icon {
    font-size: 1.8rem;
    margin-left: 0.8rem;
    color: #2196f3;
}

.category-title {
    color: #1976d2;
    font-size: 1.3rem;
    font-weight: 600;
}

/* استایل‌های دکمه‌ها */
.stButton>button {
    width: 100%;
    text-align: right !important;
    background-color: #f8f9fa !important;
    border: 1px solid #e9ecef !important;
    border-radius: 8px !important;
    padding: 0.8rem 1rem !important;
    color: #2c3e50 !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    background-color: #e3f2fd !important;
    border-color: #bbdefb !important;
    color: #1976d2 !important;
    transform: translateX(-4px);
}

/* استایل‌های کانتینر */
.block-container {
    padding: 1rem !important;
    max-width: 1200px;
    margin: 0 auto;
}

/* استایل‌های هدر اصلی */
.main-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    border-bottom: 2px solid #f0f0f0;
}

.main-header h1 {
    margin: 0;
    color: #1976d2;
    font-size: 2.5rem;
}

.main-header h5 {
    margin: 0.5rem 0 0 0;
    color: #666;
}

/* مخفی کردن هدر */
.stApp > header {
    display: none;
}

/* استایل‌های جدید برای هدر با استایل کوچکتر */
.compact-header {
    text-align: center;
    margin-bottom: 1rem;
    padding: 0.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.compact-header h1 {
    margin: 0;
    color: #1976d2;
    font-size: 1.8rem;
}

.header-divider {
    height: 1px;
    background-color: #f0f0f0;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


def restart_agent():
    logger.debug("---*--- Restarting Agent ---*---")
    st.session_state["example_agent"] = None
    st.session_state["example_agent_session_id"] = None
    st.session_state["uploaded_image"] = None
    if "url_scrape_key" in st.session_state:
        st.session_state["url_scrape_key"] += 1
    if "file_uploader_key" in st.session_state:
        st.session_state["file_uploader_key"] += 1
    if "image_uploader_key" in st.session_state:
        st.session_state["image_uploader_key"] += 1
    st.rerun()


def encode_image(image_file):
    image = Image.open(image_file)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    encoding = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoding}"


def load_questions():
    questions_file = Path("app/data/questions.json")
    if questions_file.exists():
        with open(questions_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"questions": []}


def get_category_icon(category: str) -> str:
    icons = {
        "فروش": "💰",
        "محصولات": "📦",
        "مشتریان": "👥",
    }
    return icons.get(category, "📌")


def main() -> None:
    # Get OpenAI key from environment variable
    if not getenv("OPENAI_API_KEY"):
        st.error("لطفا کلید OpenAI را در فایل .env تنظیم کنید")
        return

    # Initialize messages if not exists
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["messages"].append({"role": "assistant", "content": "هر سوالی دارید بپرسید..."})

    # نمایش هدر یکبار با استایل کوچکتر
    st.markdown("""
    <div class="compact-header">
        <h1>AdminAI</h1>
        <div class="header-divider"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # نمایش چت
    for message in st.session_state["messages"]:
        if message.get("role") in ["system", "tool"]:
            continue
            
        with st.chat_message(message["role"]):
            content = message.get("content")
            if isinstance(content, dict):
                if 'text' in content:
                    st.write(content['text'])
                if 'chart_url' in content:
                    try:
                        st.components.v1.iframe(content['chart_url'], height=500, scrolling=False)
                    except Exception as e:
                        logger.error(f"Error displaying chart: {str(e)}")
                        st.error(f"خطا در نمایش نمودار")
            elif isinstance(content, list):
                for item in content:
                    if item["type"] == "text":
                        st.write(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"], use_column_width=True)
            else:
                st.write(content)
    
    # ورودی چت
    if prompt := st.chat_input(placeholder="پیام خود را بنویسید..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.rerun()

    # نمایش کارت‌های سوال فقط در شروع چت
    if len(st.session_state["messages"]) == 1 and st.session_state["messages"][0]["role"] == "assistant":
        st.markdown("""
        <div class="questions-header">
            <h2>سوالات متداول</h2>
        </div>
        """, unsafe_allow_html=True)
        
        questions_data = load_questions()
        
        # ایجاد دو ستون برای سوالات
        left_col, right_col = st.columns(2)
        
        # تقسیم دسته‌های سوالات به دو گروه
        categories = questions_data["questions"]
        mid_point = len(categories) // 2
        left_categories = categories[:mid_point]
        right_categories = categories[mid_point:]
        
        # نمایش سوالات ستون سمت راست
        with right_col:
            for category in right_categories:
                st.markdown(f"""
                <div class="question-category">
                    <div class="category-header">
                        <span class="category-icon">{get_category_icon(category['category'])}</span>
                        <span class="category-title">{category['category']}</span>
                    </div>
                    <div class="question-content">
                """, unsafe_allow_html=True)
                
                for question in category["items"]:
                    if st.button(question, key=f"btn_right_{hash(question)}"):
                        st.session_state["messages"].append({"role": "user", "content": question})
                        st.rerun()
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        # نمایش سوالات ستون سمت چپ
        with left_col:
            for category in left_categories:
                st.markdown(f"""
                <div class="question-category">
                    <div class="category-header">
                        <span class="category-icon">{get_category_icon(category['category'])}</span>
                        <span class="category-title">{category['category']}</span>
                    </div>
                    <div class="question-content">
                """, unsafe_allow_html=True)
                
                for question in category["items"]:
                    if st.button(question, key=f"btn_left_{hash(question)}"):
                        st.session_state["messages"].append({"role": "user", "content": question})
                        st.rerun()
                
                st.markdown('</div></div>', unsafe_allow_html=True)

    # Function to create/recreate an agent
    def create_or_recreate_agent(agent_type: str, get_agent_func, current_agent=None):
        try:
            if current_agent:
                try:
                    # Test if agent is still valid
                    current_agent.list_tools()
                    return current_agent, st.session_state.get(f"{agent_type}_session_id")
                except Exception:
                    logger.warning(f"Agent {agent_type} is invalid, recreating...")
                    
            logger.info(f"Creating {agent_type}")
            new_agent = get_agent_func(
                model_id=agent_settings.default_model_id,
                debug_mode=True
            )
            session_id = new_agent.create_session()
            st.session_state[agent_type] = new_agent
            st.session_state[f"{agent_type}_session_id"] = session_id
            return new_agent, session_id
        except Exception as e:
            logger.error(f"Error creating {agent_type}: {str(e)}")
            return None, None

    # Initialize or verify all agents
    try:
        # Main agent
        example_agent, example_session_id = create_or_recreate_agent(
            "example_agent", 
            get_example_agent,
            st.session_state.get("example_agent")
        )
        if not example_agent:
            st.error("خطا در ایجاد ایجنت اصلی")
            return

        # Product catalog agent
        product_catalog_agent, product_catalog_session_id = create_or_recreate_agent(
            "product_catalog_agent",
            get_product_catalog_agent,
            st.session_state.get("product_catalog_agent")
        )

        # Sales analysis agent
        sales_analysis_agent, sales_analysis_session_id = create_or_recreate_agent(
            "sales_analysis_agent",
            get_sales_analysis_agent,
            st.session_state.get("sales_analysis_agent")
        )

        logger.info("All agents verified and created if needed")

    except Exception as e:
        st.error(f"خطا در مدیریت ایجنت‌ها: {str(e)}")
        logger.error(f"Error managing agents: {str(e)}")
        return

    # Get the main agent from session state
    example_agent = st.session_state["example_agent"]
    
    # Verify agent session is valid
    if not example_agent or not st.session_state.get("example_agent_session_id"):
        st.error("خطا در session ایجنت اصلی")
        return

    # Generate response for last user message
    if (st.session_state["messages"] and 
        len(st.session_state["messages"]) > 0 and
        st.session_state["messages"][-1].get("role") == "user"):
        
        try:
            question = st.session_state["messages"][-1]["content"]
            with st.chat_message("assistant"):
                with st.spinner("در حال فکر کردن..."):
                    resp_container = st.empty()
                    response = ""
                    
                    try:
                        for delta in example_agent.run(message=question, stream=True):
                            if delta and delta.content:
                                response += delta.content
                                resp_container.markdown(response)
                        
                        if response.strip():
                            st.session_state["messages"].append({"role": "assistant", "content": response})
                        else:
                            logger.warning("Empty response received, attempting to recreate session...")
                            example_agent, example_session_id = create_or_recreate_agent(
                                "example_agent", 
                                get_example_agent,
                                None  # Force recreation
                            )
                            if example_agent:
                                for delta in example_agent.run(message=question, stream=True):
                                    if delta and delta.content:
                                        response += delta.content
                                        resp_container.markdown(response)
                                
                                if response.strip():
                                    st.session_state["messages"].append({"role": "assistant", "content": response})
                                else:
                                    st.error("پاسخی دریافت نشد")
                                    logger.error("Empty response received after session recreation")
                            else:
                                st.error("خطا در بازسازی ایجنت")
                                logger.error("Failed to recreate agent")
                                
                    except Exception as run_error:
                        logger.error(f"Error during agent run: {str(run_error)}")
                        # Try to recreate the session and retry
                        try:
                            example_agent, example_session_id = create_or_recreate_agent(
                                "example_agent", 
                                get_example_agent,
                                None  # Force recreation
                            )
                            if example_agent:
                                for delta in example_agent.run(message=question, stream=True):
                                    if delta and delta.content:
                                        response += delta.content
                                        resp_container.markdown(response)
                                
                                if response.strip():
                                    st.session_state["messages"].append({"role": "assistant", "content": response})
                                else:
                                    st.error("پاسخی دریافت نشد")
                                    logger.error("Empty response received after error recovery")
                            else:
                                st.error("خطا در بازسازی ایجنت")
                                logger.error("Failed to recreate agent after error")
                        except Exception as recovery_error:
                            st.error(f"خطا در بازیابی ایجنت: {str(recovery_error)}")
                            logger.error(f"Error during recovery: {str(recovery_error)}")
                        
        except Exception as e:
            st.error(f"خطا در دریافت پاسخ: {str(e)}")
            logger.error(f"Error getting response: {str(e)}")


if __name__ == "__main__":
    main()
