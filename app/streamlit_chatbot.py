import streamlit as st
from typing import List, Dict

# داده‌های سوالات پیشنهادی
questions_data = [
    {
        "category": "تحلیل فروش",
        "questions": [
            "کارمزد و فروش ده روز گذشته چقدر بوده و چند درصد فروش کارمزد بوده؟",
            "در کدام زیر دسته سطح سوم بیشترین رشد فروش را در ۹ ماه گذشته داشته‌ایم؟",
            "مقایسه فروش ماه جاری با ماه قبل چگونه است؟",
            "پرفروش‌ترین محصولات در ماه گذشته کدام بوده‌اند؟",
            "روند فروش روزانه در ماه جاری چگونه است؟"
        ]
    },
    {
        "category": "تحلیل مشتریان",
        "questions": [
            "درصد مشتریان بازگشتی (ریترن) در هر ماه چقدر بوده است؟",
            "تعداد مشتریان جدید و بازگشتی در هر ماه چقدر بوده است؟",
            "میانگین خرید هر مشتری در ماه چقدر است؟",
            "وفادارترین مشتریان ما چه کسانی هستند؟",
            "توزیع جغرافیایی مشتریان ما چگونه است؟"
        ]
    },
    {
        "category": "مدیریت محصولات",
        "questions": [
            "کدام محصولات پربازدید در حال حاضر ناموجود هستند؟",
            "محصولات با موجودی کم کدام هستند؟",
            "کدام محصولات بیشترین حاشیه سود را دارند؟",
            "محصولات با بیشترین نرخ خرید مجدد کاربر کدام هستند؟",
            "کدام محصولات نیاز به بروزرسانی قیمت دارند؟"
        ]
    },
    {
        "category": "کیفیت خدمات",
        "questions": [
            "نرخ کنسلی ماهیانه سفارش‌ها در ده ماه گذشته چقدر بوده است؟",
            "میانگین زمان ارسال سفارش‌های من چقدر بوده است؟",
            "نرخ رضایت مشتریان در ماه‌های اخیر چگونه بوده است؟",
            "بیشترین دلایل مرجوعی محصولات چه بوده است؟",
            "وضعیت پاسخگویی به پیام‌های مشتریان چگونه است؟"
        ]
    }
]

# پاسخ‌های آماده با کلیدواژه‌های متنوع و منطق AND
responses = [
    {
        "keywords": ["کارمزد", "فروش", "پرداخت", "مبلغ کارمزد", "کارمزد پرداختی", "چقدر کارمزد", "درصد فروش کارمزد", "کارمزد ده روز"],
        "answer": "📊 گزارش کارمزد و فروش ده روز گذشته:\n\n💰 کل فروش: 1,250,000,000 تومان\n💸 کارمزد: 125,000,000 تومان (10%)\n📈 درصد کارمزد از کل فروش: 10%\n\nتفکیک روزانه:\n• روز 1: 120M فروش، 12M کارمزد\n• روز 2: 115M فروش، 11.5M کارمزد\n• روز 3: 130M فروش، 13M کارمزد\n• روز 4: 125M فروش، 12.5M کارمزد\n• روز 5: 140M فروش، 14M کارمزد\n\n🎯 تحلیل: کارمزد در محدوده استاندارد 8-12% قرار دارد و روند پایدار است."
    },
    {
        "keywords": ["مقایسه", "فروش", "رشد", "ماه جاری", "ماه قبل", "مقایسه فروش", "رشد فروش"],
        "answer": "📈 مقایسه فروش ماه جاری با ماه قبل:\n\nماه جاری: 3,450,000,000 تومان\nماه قبل: 2,980,000,000 تومان\nرشد: +15.8% (470M تومان)\n\n🏆 دسته‌بندی‌های برتر:\n1. الکترونیک: +25% رشد\n2. پوشاک: +12% رشد\n3. کتاب: +8% رشد\n4. لوازم خانگی: +18% رشد\n\nروند هفتگی:\n• هفته 1: 850M\n• هفته 2: 920M\n• هفته 3: 880M\n• هفته 4: 800M (پیش‌بینی)\n\n🎯 نتیجه: رشد مثبت و پایدار در تمام دسته‌ها مشاهده می‌شود."
    },
    {
        "keywords": ["پرفروش", "محصولات", "پرفروش‌ترین", "پرفروش ترین", "محصولات پرفروش", "پرفروش ماه"],
        "answer": "🏆 پرفروش‌ترین محصولات ماه گذشته:\n\n1. 📱 iPhone 15 Pro - 156 فروش - 5.4M تومان\n2. 💻 Dell XPS 13 - 89 فروش - 4.0M تومان\n3. 📱 Samsung Galaxy S24 - 134 فروش - 3.8M تومان\n4. 🎧 AirPods Pro - 245 فروش - 2.9M تومان\n5. ⌚ Apple Watch - 98 فروش - 1.2M تومان\n\nآمار کلی:\n• کل فروش: 17.3M تومان\n• میانگین قیمت: 346,000 تومان\n• تعداد کل فروش: 722 عدد\n\nروند: رشد 15% نسبت به ماه قبل در تمام محصولات برتر"
    },
    {
        "keywords": ["محصولات", "ناموجود", "پربازدید", "محصولات ناموجود", "محصولات پربازدید ناموجود", "ناموجود پربازدید"],
        "answer": "⚠️ محصولات پربازدید ناموجود:\n\n1. 📱 iPhone 15 Pro Max (256GB) - 89 بازدید/روز\n2. 💻 MacBook Air M2 - 67 بازدید/روز\n3. 🎧 Sony WH-1000XM5 - 45 بازدید/روز\n4. 📱 Samsung Galaxy S24 Ultra - 34 بازدید/روز\n5. ⌚ Apple Watch Series 9 - 28 بازدید/روز\n\nآمار:\n• کل محصولات ناموجود: 23 عدد\n• میانگین بازدید روزانه: 52.6\n• تخمین فروش از دست رفته: 2.1M تومان/روز\n\n🎯 توصیه: افزایش موجودی این محصولات در اولویت است."
    },
    {
        "keywords": ["نرخ رضایت", "رضایت", "میزان رضایت", "رضایت مشتریان", "رضایت کاربران", "رضایت مشتری"],
        "answer": "⭐ نرخ رضایت مشتریان ماه‌های اخیر:\n\nآمار کلی:\n• میانگین رضایت: 4.2/5 (84%)\n• تعداد نظرات: 1,247\n• رضایت مثبت: 1,047 (84%)\n• رضایت منفی: 200 (16%)\n\nروند ماهانه:\n• فروردین: 4.1/5\n• اردیبهشت: 4.2/5\n• خرداد: 4.3/5\n• تیر: 4.2/5\n\n🏆 عوامل رضایت:\n1. کیفیت محصولات: 4.4/5\n2. سرعت ارسال: 4.1/5\n3. پشتیبانی: 4.0/5\n4. قیمت: 3.9/5\n\n🎯 بهبود: تمرکز بر بهبود قیمت‌گذاری و پشتیبانی"
    }
]

def generate_response(question: str) -> str:
    lower_question = question.lower()
    word_count = len(lower_question.split())
    for item in responses:
        match_count = sum(1 for key in item["keywords"] if key in lower_question)
        if (word_count <= 5 and match_count >= 1) or (word_count > 5 and match_count >= 2) or (len(item["keywords"]) == 1 and match_count == 1):
            return item["answer"]
    return "🤖 من به این اطلاعات دسترسی ندارم. لطفاً سوال مرتبط با فروش، مشتری یا محصولات غرفه بپرس."

# --- UI Streamlit ---
st.set_page_config(page_title="دستیار غرفه‌داران باسلام", page_icon="🤖", layout="wide")
st.markdown("""
    <style>
    .stChatMessage.user {background: #ede9fe !important; color: #4b2997 !important; border-radius: 1.5rem 1.5rem 0.5rem 1.5rem;}
    .stChatMessage.assistant {background: #fff !important; color: #4b2997 !important; border-radius: 1.5rem 1.5rem 1.5rem 0.5rem; border: 1px solid #ede9fe;}
    .stButton>button {background: #ede9fe; color: #4b2997; border-radius: 8px; border: none;}
    .stButton>button:hover {background: #c4b5fd; color: #fff;}
    .sidebar-category {font-weight: bold; color: #7c3aed; margin-top: 1.5rem; margin-bottom: 0.5rem;}
    .sidebar-question {background: #f3f0ff; color: #4b2997; border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; cursor: pointer; transition: background 0.2s;}
    .sidebar-question:hover {background: #ede9fe;}
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state["history"] = []

st.title("🤖 دستیار غرفه‌داران باسلام")

# Sidebar
with st.sidebar:
    st.markdown("## سوالات پیشنهادی")
    for cat in questions_data:
        st.markdown(f'<div class="sidebar-category">{cat["category"]}</div>', unsafe_allow_html=True)
        for q in cat["questions"]:
            if st.button(q, key=f"sidebar_{q}"):
                st.session_state["history"].append({"role": "user", "content": q})
                st.session_state["history"].append({"role": "assistant", "content": generate_response(q)})
                st.experimental_rerun()

# Chat UI
for i, msg in enumerate(st.session_state["history"]):
    is_user = msg["role"] == "user"
    with st.chat_message("user" if is_user else "assistant"):
        st.markdown(msg["content"])
        # دکمه فیدبک فقط برای پیام مدل
        if not is_user:
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("👍 بله، مفید بود", key=f"like_{i}"):
                    st.toast("ممنون از بازخوردت! 😊")
            with col2:
                if st.button("👎 نه، نیاز به بهبود داره", key=f"dislike_{i}"):
                    st.toast("بازخوردت ثبت شد، ممنون! 🙏")

# Chat input
user_input = st.chat_input("پیام خود را بنویسید...")
if user_input:
    st.session_state["history"].append({"role": "user", "content": user_input})
    st.session_state["history"].append({"role": "assistant", "content": generate_response(user_input)})
    st.experimental_rerun() 