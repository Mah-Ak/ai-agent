from pathlib import Path
import uuid
from typing import Optional, Literal
from phi.agent.python import PythonAgent
from phi.model.openai import OpenAIChat
from phi.model.google import Gemini
from phi.model.openrouter import OpenRouter
from phi.file import File

from agents.settings import agent_settings

# ایجاد دایرکتوری‌ها
CHARTS_DIR = Path(agent_settings.charts_dir)
if not CHARTS_DIR.exists():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

cwd = Path(__file__).parent.resolve()
tmp = cwd.joinpath("tmp")
if not tmp.exists():
    tmp.mkdir(exist_ok=True, parents=True)

# تنظیم آدرس API
API_URL = "http://localhost:8000"

def get_product_catalog_agent(
    model_provider: Literal["openai", "gemini", "openrouter"] = "openrouter",
    model_id: Optional[str] = None,
    debug_mode: bool = True,
) -> PythonAgent:
    """
    ایجاد ایجنت تحلیل کاتالوگ محصولات با قابلیت انتخاب مدل
    
    Args:
        model_provider: نوع مدل ("openai"، "gemini" یا "openrouter")
        model_id: شناسه مدل (اختیاری)
        debug_mode: حالت دیباگ
    """
    
    # انتخاب مدل بر اساس provider
    if model_provider == "gemini":
        model = Gemini(
            id=model_id or agent_settings.gemini_model,
            temperature=agent_settings.default_temperature,
        )
    elif model_provider == "openrouter":
        model = OpenRouter(
            id=model_id or agent_settings.openrouter_model,
            api_key=agent_settings.openrouter_api_key,
            max_tokens=agent_settings.default_max_completion_tokens,
            temperature=agent_settings.default_temperature,
            base_url="https://openrouter.ai/api/v1",
            http_client_timeout=120,
        )
    else:
        model = OpenAIChat(
            id=model_id or agent_settings.gpt_4,
            max_tokens=agent_settings.default_max_completion_tokens,
            temperature=agent_settings.default_temperature,
            api_key=agent_settings.openai_api_key,
        )

    return PythonAgent(
        name="Product Catalog Agent",
        role="تحلیل کاتالوگ محصولات و آمار کلی فروش و بازدید",
        model=model,
        base_dir=tmp,
        files=[
            File(
                path=str(cwd.joinpath("products.csv")),
                description="""
                فایل CSV حاوی اطلاعات کاتالوگ محصولات با ستون‌های زیر:
                - id: شناسه محصول
                - vendor_id: شناسه فروشنده
                - title: عنوان محصول
                - price: قیمت پایه
                - inventory: موجودی فعلی
                - sales_count: تعداد کل فروش تا کنون
                - view_count: تعداد کل بازدید تا کنون
                - category_title: عنوان دسته‌بندی
                - category_parent_title: عنوان دسته‌بندی والد
                - category_root_title: عنوان دسته‌بندی ریشه

                توجه: این فایل فقط شامل اطلاعات کلی محصولات است و برای موارد زیر مناسب نیست:
                - گزارش فروش در بازه زمانی خاص
                - تحلیل مالی و درآمد
                - وضعیت سفارش‌ها
                - تخفیف‌ها و کارمزدها
                برای این موارد باید از sales_analysis_agent استفاده شود.
                """
            )
        ],
        instructions=[
            "برای هر درخواست، یک فایل پایتون جدید ایجاد کن",
            "همیشه از pandas برای خواندن و تحلیل داده‌ها استفاده کن",
            "مسیر فایل CSV را به صورت '/app/agents/products.csv' استفاده کن",
            "برای نمایش نتایج از to_markdown() استفاده کن",
            "قیمت‌ها را به فرمت فارسی و با جداکننده هزارتایی نمایش بده",
            "برای نمودارها از plotly استفاده کن",
            "نمودارها را با فونت فارسی و از راست به چپ رسم کن",
            "نمودار را به صورت کم‌حجم و بهینه ذخیره کن",
            "از fig.write_html استفاده کن و config={'displayModeBar': False} رو تنظیم کن",
            "برای هر نمودار یک نام یتا با uuid4 بساز",
            "مثال برای ساخت نام فایل: chart_name = f'chart_{uuid.uuid4()}.html'",
            f"نمودار را در {CHARTS_DIR}/[chart_name] ذخیره کن",
            "در خروجی به جای مسیر کامل فایل، از URL استفاده کن",
            f"مسیر نمودار را به صورت {API_URL}/static/charts/[chart_name] برگردان",
            "خروجی را به صورت دیکشنری با دو کلید 'text' و 'chart_url' برگردان",
            "خروجی رو بدون دستور پرینت برگردون",
            "بعد از ذخیره نمودار، مسیر کامل فایل رو پرینت کن تا مطمئن بشیم درست ذخیره شده",
            "این عامل فقط برای موارد زیر مناسب است:",
            "- تحلیل کاتالوگ محصولات",
            "- بررسی موجودی فعلی",
            "- آمار کلی فروش و بازدید",
            "- تحلیل دسته‌بندی‌ها",
            "- قیمت‌گذاری پایه محصولات",
            "برای موارد زیر باید درخواست را به sales_analysis_agent ارجاع دهید:",
            "- گزارش فروش در بازه زمانی خاص",
            "- تحلیل مالی و درآمد",
            "- وضعیت سفارش‌ها",
            "- تخفیف‌ها و کارمزدها",
            "- هزینه‌های ارسال",
            "- عودت و رضایت مشتری"
        ],
        markdown=True,
        pip_install=True,
        show_tool_calls=True,
        monitoring=True,
        debug_mode=debug_mode,
        tool_call_limit=3
    )

# ایجاد نمونه پیش‌فرض ایجنت با تنظیمات پیش‌فرض
product_catalog_agent = get_product_catalog_agent(
    model_provider=agent_settings.default_model_provider,
    model_id=agent_settings.default_model_id,
    debug_mode=True
) 