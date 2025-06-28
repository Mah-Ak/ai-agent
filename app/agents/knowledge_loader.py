from pathlib import Path
import os
from dotenv import load_dotenv
from phi.knowledge.text import TextKnowledgeBase
from phi.vectordb.qdrant import Qdrant

# لود کردن متغیرهای محیطی
load_dotenv()

# تنظیم مسیر فایل‌های راهنما
HELP_DIR = Path("/app/help-content")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

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

def populate_knowledge_base():
    """پر کردن نالج بیس از روی فایل‌ها"""
    try:
        if DEBUG:
            print("\n🔄 شروع بارگذاری نالج بیس:")
            print(f"📂 مسیر: {HELP_DIR}")
        
        # حذف کالکشن قبلی
        vector_db = get_vector_db()
        try:
            vector_db.delete_collection()
        except:
            pass
            
        # ایجاد نالج بیس جدید
        kb = TextKnowledgeBase(
            path=str(HELP_DIR),
            formats=[".txt"],
            vector_db=vector_db,
            batch_size=100,
        )
        
        # بارگذاری فایل‌ها
        kb.load(recreate=True)
        
        if DEBUG:
            print("✅ نالج بیس با موفقیت پر شد")
            print("\n📚 فایل‌های بارگذاری شده:")
            for file in HELP_DIR.glob("*.txt"):
                print(f"  📄 {file.name}")
                
        return True
        
    except Exception as e:
        print(f"❌ خطا در پر کردن نالج بیس: {str(e)}")
        return False

if __name__ == "__main__":
    # اجرای مستقیم برای پر کردن نالج بیس
    populate_knowledge_base() 