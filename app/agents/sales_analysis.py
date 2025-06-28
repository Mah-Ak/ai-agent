from pathlib import Path
import uuid
from typing import Optional, Literal
from phi.agent.python import PythonAgent
from phi.model.openai import OpenAIChat
from phi.model.google import Gemini
from phi.model.openrouter import OpenRouter
from phi.file import File

from agents.settings import agent_settings

import requests  # اضافه کردن import جدید

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

def test_openrouter_api():  # تابع جدید برای تست API
    headers = {
        "HTTP-Referer": agent_settings.app_domain,
        "Authorization": f"Bearer {agent_settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": agent_settings.openrouter_model,
        "messages": [{"role": "user", "content": "Hi!"}]
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        print(f"API Test Response: {response.status_code}")
        print(f"Response Text: {response.text[:200]}")
        return response.ok
    except Exception as e:
        print(f"API Test Error: {str(e)}")
        return False

def get_sales_analysis_agent(
    model_provider: Literal["openai", "gemini", "openrouter"] = "openrouter",
    model_id: Optional[str] = None,
    debug_mode: bool = True,
) -> PythonAgent:
    """
    ایجاد ایجنت تحلیل فروش با قابلیت انتخاب مدل
    
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
            headers={
                "HTTP-Referer": agent_settings.app_domain,
                "X-Title": "Basalam Assistant"
            }
        )
    else:
        model = OpenAIChat(
            id=model_id or agent_settings.gpt_4,
            max_tokens=agent_settings.default_max_completion_tokens,
            temperature=agent_settings.default_temperature,
            api_key=agent_settings.openai_api_key,
        )

    if not test_openrouter_api():  # تست API قبل از ادامه
        print("Warning: OpenRouter API test failed!")

    return PythonAgent(
        name="Sales Analysis Agent",
        role="تحلیل داده‌های فروش و گزارش‌های مالی پلتفرم",
        model=model,
        base_dir=tmp,
        files=[
            File(
                path=str(cwd.joinpath("model_sales.csv")),
                description="""
                فایل CSV حاوی داده‌های تراکنش‌های تجارت الکترونیک با جزئیات سارش، مشتری و فروشنده:
                ارقام به ریال هستن باید تقسیم به ده بکنی که تومن بشن    
 ### شناسه‌های اصلی
- item_id,order_id,parcel_id,customer_id,product_id,variation_id,vendor_id,session_id,vendor_user_id,address_id

### داده‌های مالی
- price,gmv,delivery_cost,delivery_cost_without_free_shipping,amount_total,amount_online_payment,amount_wallet,
amount_bnpl,amount_other,amount_per_item,online_amount_payment_per_item,wallet_amount_per_item,
bnpl_amount_per_item,other_amount_per_item,basalam_product_discount,basalam_delivery_discount,
vendor_product_discount,vendor_delivery_discount,public_delivery_discount,basalam_discount,vendor_discount,
commission,satisfaction_commission,refund_amount,category_commission_percent


### عناوین و اطلاعات توصیفی
- product_title,product_title_at_purchase,vendor_title,customer_name,customerTypeNameFa,vendorTypeNameFa,
recipient_nickname,recipient_mobile,recipient_address,recipient_postal_code,coupon_code


### وضعیت‌ها
- has_problem,is_cancelled,is_free_shipping,is_same_city,is_default_shipping_cost,has_review,has_reviewcomment,
requesthasresponded,requestisaccept,requestforagreementondelaysending,agreementondelaysending


### زمان‌ها و تاریخ‌ها
- purchase_at,addtocart_at,seen_at,sent_at,satisfaction_at,canceled_at,closed_at,review_created_at,refund_at,
vendor_approved_at,problem_at
### معیارهای سفارش
- quantity,tot_weight,weight_at_purchase,review_rate,product_preparation_days_at_purchase,postpone_days,
customer_order_number,vendor_order_number,product_order_number,customer_leafcat_order_number,
customer_rootcat_order_number,customer_product_order_number,customer_vendor_order_number

### اطلاعات مکانی
- recipient_city_id, recipient_province_id, vendor_city_id, vendor_province_id, customer_city_title,
 customer_province_title, vendor_city_title, vendor_province_title, adjacency_type_id

### دسته‌بندی محصول
- category_id,cat_lvl1_id,cat_lvl2_id,cat_lvl1_title,cat_lvl2_title,cat_lvl3_title,cat_leaf_title

### اطلاعات ارجاع و دستگه
- utm_source,utm_medium,utm_campaign,utm_content,utm_term,creation_tags_device_id,paid_tags_device_id,
platform_id,shipping_method_id,final_shipping_method_id,parcel_shipping_method_id

### معیارهای سن و زمان
- customer_age,vendor_age,product_age,purchase_date_id,purchase_time_id,addtocart_date_id,addtocart_time_id,
persian_year,Hour24,Hour12FullString

### شناسه‌های کاربر عملیات‌ها
- satisfaction_by,dissatisfaction_by,closed_by,problem_by,cancelled_by_user_id,satisfaction_by_user_id,
dissatisfaction_by_user_id
-problem_by_user_id,closed_by_user_id,refund_by,refund_by_user_id,agreementondelaysending_by,
agreementondelaysending_by_user_id
- product_problem_by,product_problem_by_user_id,not_arrived_by,not_arrived_by_user_id,
incorrect_shipping_information_by,
incorrect_shipping_information_by_user_id,created_by_user_id_list


### لیست‌های وضعیت و دلایل
- status_list,problem_status_list,final_status,problem_reason_id,product_problem_reason_id,cancellation_reason_id,
cancellation_request_reason,cancellation_of_cancellation_request_reason


### سایر فیلدها
- post_receipt_id,coupon_id,version,financial_version,created_at_list

### تاریخ‌های شمسی
- persiandate_purchase_date,persiandate_purchase_yearmonth,persianweekyear,weekfirstdate,weekfirstdateshamsi,
persiandate_purchase_date_string,persiandate_purchase_yearmonth_string

                """
            )
        ],
        instructions=[
            "برای هر درخواست، یک فایل پایتون جدید ایجاد کن",
            "همیشه از pandas برای خواندن و تحلیل داده‌ها استفاده کن",
            "مسیر فایل CSV را به صورت '/app/agents/model_sales.csv' استفاده کن",
            "برای نمایش نتایج از to_markdown() استفاده کن",
            "قیمت‌ها را به فرمت فارسی و با جداکننده هزارتایی نمایش بده",
            "برای نمودارها از plotly استفاده کن",
            "نمودارها را با فونت فارسی و از راست به چپ رسم کن",
            "نمودار را به صورت کم‌حجم و بهینه ذخیره کن",
            "برای ذخیره نمودار از کد زیر استفاده کن:",
            '''
            # ایجاد نام یکتا برای نمودار
            chart_name = f'chart_{uuid.uuid4()}.html'
            chart_path = f'/app/storage/charts/{chart_name}'
            
            # تنظیمات نمودار
            fig.update_layout(
                font=dict(family='Tahoma', size=12),
                xaxis={'categoryorder': 'category ascending'},
                yaxis_tickprefix='تومان ',
                margin=dict(t=50, b=50, r=50, l=50),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # ذخیره نمودار
            config = {'displayModeBar': False}
            fig.write_html(chart_path, config=config)
            
            # آدرس نمودار برای نمایش
            chart_url = f'http://localhost:8000/static/charts/{chart_name}'
            ''',
            "برای خروجی از فرمت زیر استفاده کن:",
            '''
            result_output = {
                'text': df.to_markdown(index=False),
                'chart_url': chart_url
            }
            result_output
            ''',
            "برای محاسبات هزینه ارسال:",
            "- از ستون‌های delivery_cost و *_delivery_discount استفاده کن",
            "- هزینه ارسال خالص = delivery_cost - basalam_delivery_discount - public_delivery_discount",
            "- برای سفارش‌های رایگان از is_free_shipping استفاده کن",
            "برای کار با تاریخ‌ها:",
            "- تاریخ‌ها در فرمت 'YYYY-MM-DD HH:mm:ss' هستند",
            "- برای تبدیل به تاریخ از pd.to_datetime استفاده کن",
            "- برای فیلتر کردن بازه زمانی از کد زیر استفاده کن:",
            '''
            def filter_date_range(df, days=90):
                df['purchase_date'] = pd.to_datetime(df['purchase_at'])
                last_date = df['purchase_date'].max()
                start_date = last_date - pd.Timedelta(days=days)
                return df[df['purchase_date'].between(start_date, last_date)]
            ''',
            "برای تحلیل فروش روزانه:",
            "- از ستون‌ها gmv�� *_discount و commission اس��فاده کن",
            "- فروش خالص = gmv - basalam_product_discount - vendor_product_discount - commission",
            "- برای گروه‌بندی روزانه از کد زیر استفاده کن:",
            '''
            df['date'] = pd.to_datetime(df['purchase_at']).dt.date
            daily_sales = df.groupby('date').agg({
                'gmv': 'sum',
                'basalam_product_discount': 'sum',
                'vendor_product_discount': 'sum',
                'commission': 'sum',
                'item_id': 'count'  # تعداد تراکنش
            }).reset_index()
            
            daily_sales['net_sales'] = (
                daily_sales['gmv'] -
                daily_sales['basalam_product_discount'] -
                daily_sales['vendor_product_discount'] -
                daily_sales['commission']
            )
            ''',
            "برای فرمت‌بندی اعداد فارسی:",
            '''
            def format_price(x):
                return f'{x:,.0f}'.replace(',', '،')
            
            df['price_fa'] = df['price'].apply(format_price)
            ''',
            "برای تحلیل وضعیت سفارش‌ها:",
            "- از ستون‌های is_cancelled، has_problem و has_review استفاده کن",
            "- برای محاسبه نرخ لغو از is_cancelled استفاده کن",
            "- برای محاسبه نرخ مشکل از has_problem استفاده کن",
            "- برای محاسبه نرخ نظردهی از has_review استفاده کن",
            "برای محاسبات مالی:",
            "- از ستون‌های مربوط به مبلغ (amount_*)، تخفیف (*_discount) و کارمزد (commission) استفاده کن",
            "- مبالغ را به تومان و با جداکننده هزارتایی نمایش بده",
            "- سود خالص را با کسر تخفیف‌ها و کارمزدها محاسبه کن",
            "برای تحلیل زمانی:",
            "- از ستون‌های *_at استفاده کن",
            "- داده‌ها را بر اساس روز، هفته یا ماه گروه‌بندی کن",
            "- روندها را با نمودار خطی نمایش بده",
            "امکان تحلیل‌های زیر را فراهم کن:",
            "- گزارش فروش روزانه/هفتگی/ماهانه",
            "- تحلیل سودآوری محصولات و دسته‌بندی‌ها",
            "- نرخ لغو و مشکلات سفارش‌ها",
            "- تحلیل تخفیف‌ها و تاثیر آن بر فروش",
            "- محاسبه کارمزدها و درآمد خالص",
            "- روند فروش در بازه‌های زمانی مختلف",
            "- تحلیل هزینه‌های ارسال و تخفیف‌های آن",
            "- تحلیل جغرافیایی فروش بر اساس شهر و استان",
            "- تحلیل رفتار مشتریان و فروشندگان",
            "برای هر تحلیل:",
            "- ابتدا داده‌های خام را نمایش بده",
            "- سپس محاسبات و درصدها را نشان بده",
            "- در نهایت یک نمودار مناسب رسم کن",
            "- یک جمع‌بندی کوتاه از نتایج ارائه کن",
            "برای تبدیل رقم به تومان:",
            "-ارقام رو حتما حتما تقسیم بر ده بکن",
            "-و با فرمت فارسی بیار و همیشه به تومان تبدیلشون بکن یعنی تقسیم بر ده باید بکنی همه رقم ها ریال هستند" ,
            "برای خواندن داده‌ها از کد زیر استفاده کن:"
            "این ها دیتای فروش یه غرفه در باسلام هست اسم غرفه خانبار هست و فایل سی اس وی هست",
            '''
            df = pd.read_csv(file_path, on_bad_lines='skip', low_memory=False)
            ''',
        ],
        markdown=True,
        pip_install=True,
        show_tool_calls=True,
        monitoring=True,
        debug_mode=debug_mode,
        tool_call_limit=3
    )

# ایجاد نمونه پیش‌فرض ایجنت با تنظیمات پیش‌فرض
sales_analysis_agent = get_sales_analysis_agent(
    model_provider=agent_settings.default_model_provider,
    model_id=agent_settings.default_model_id,
    debug_mode=True
) 