from pathlib import Path
import os
from dotenv import load_dotenv
from phi.knowledge.text import TextKnowledgeBase
from phi.vectordb.qdrant import Qdrant

# لود کردن متغیرهای محیطی
load_dotenv()

# آیا اطلاعات دیباگ نمایش داده شود؟
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# مسیر فایل‌های راهنما
HELP_DIR = Path("/app/help-content")

# کش کردن نالج بیس
_knowledge_base_instance = None

def get_vector_db():
    """ایجاد دیتابیس برداری Qdrant"""
    if DEBUG:
        print("\n🔌 اتصال به Qdrant:")
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        print(f"URL: {url if url else 'تنظیم نشده!'}")
        print(f"API Key: {'تنظیم شده' if api_key else 'تنظیم نشده!'}")
        print(f"Collection: help-basalalm")
    
    if not os.getenv("QDRANT_URL") or not os.getenv("QDRANT_API_KEY"):
        raise ValueError("QDRANT_URL یا QDRANT_API_KEY تنظیم نشده است!")

    qdrant = Qdrant(
        collection="help-basalalm",
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        prefer_grpc=True,
    )
    
    if DEBUG:
        try:
            # تست اتصال
            collections = qdrant.client.get_collections()
            print(f"\n📚 کالکشن‌های موجود: {[c.name for c in collections.collections]}")
            
            # بررسی کالکشن مورد نظر
            collection_info = qdrant.client.get_collection("help-basalalm")
            print(f"\n📊 اطلاعات کالکشن help-basalalm:")
            print(f"تعداد وکتورها: {collection_info.points_count}")
            print(f"ابعاد وکتور: {collection_info.config.params.vectors.size}")
        except Exception as e:
            print(f"\n⚠️ خطا در اتصال به Qdrant: {str(e)}")
    
    return qdrant

class DebugKnowledgeBase(TextKnowledgeBase):
    def __init__(self, **kwargs):
        # اطمینان از وجود path
        if 'path' not in kwargs:
            kwargs['path'] = str(HELP_DIR)
        super().__init__(**kwargs)

    def search(self, *args, **kwargs):
        results = super().search(*args, **kwargs)
        if DEBUG:
            print("\n🔍 نتایج جستجو در نالج بیس:")
            for i, result in enumerate(results, 1):
                try:
                    source = getattr(result, 'source', None) or getattr(result, 'name', None) or 'نامشخص'
                    content = getattr(result, 'page_content', None) or getattr(result, 'content', None) or ''
                    score = getattr(result, 'score', None) or getattr(result, 'similarity', None) or 0.0
                    
                    print(f"\n--- نتیجه {i} ---")
                    print(f"📄 فایل: {source}")
                    print(f"📊 امتیاز: {score}")
                    print(f"📝 متن: {content[:200]}...")
                except Exception as e:
                    print(f"⚠️ خطا در نمایش نتیجه {i}: {str(e)}")
        return results

def get_knowledge_base():
    """دریافت نمونه نالج بیس"""
    global _knowledge_base_instance
    
    if _knowledge_base_instance is None:
        _knowledge_base_instance = DebugKnowledgeBase(
            vector_db=get_vector_db(),
            formats=[".txt"],
        )
    
    return _knowledge_base_instance

# نمونه پیش‌فرض نالج بیس
knowledge_base = get_knowledge_base()