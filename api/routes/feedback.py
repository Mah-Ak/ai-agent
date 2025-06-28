from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os

router = APIRouter()

class FeedbackData(BaseModel):
    id: float
    type: str  # 'like' or 'dislike'
    messageIndex: int
    messageContent: str
    timestamp: str
    sessionId: str
    userAgent: str

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackData):
    """
    دریافت و ذخیره فیدبک کاربران
    """
    try:
        # ایجاد دایرکتوری feedbacks اگر وجود ندارد
        feedbacks_dir = "data/feedbacks"
        os.makedirs(feedbacks_dir, exist_ok=True)
        
        # ذخیره فیدبک در فایل JSON
        feedback_file = os.path.join(feedbacks_dir, f"feedback_{datetime.now().strftime('%Y%m%d')}.json")
        
        feedback_data = {
            "id": feedback.id,
            "type": feedback.type,
            "messageIndex": feedback.messageIndex,
            "messageContent": feedback.messageContent,
            "timestamp": feedback.timestamp,
            "sessionId": feedback.sessionId,
            "userAgent": feedback.userAgent,
            "received_at": datetime.now().isoformat()
        }
        
        # خواندن فیدبک‌های موجود
        existing_feedbacks = []
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                try:
                    existing_feedbacks = json.load(f)
                except json.JSONDecodeError:
                    existing_feedbacks = []
        
        # اضافه کردن فیدبک جدید
        existing_feedbacks.append(feedback_data)
        
        # ذخیره در فایل
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(existing_feedbacks, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "message": "فیدبک با موفقیت ذخیره شد",
            "feedback_id": feedback.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در ذخیره فیدبک: {str(e)}")

@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    دریافت آمار فیدبک‌ها
    """
    try:
        feedbacks_dir = "data/feedbacks"
        if not os.path.exists(feedbacks_dir):
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "positive_percentage": 0
            }
        
        total_feedbacks = 0
        positive_feedbacks = 0
        negative_feedbacks = 0
        
        # خواندن تمام فایل‌های فیدبک
        for filename in os.listdir(feedbacks_dir):
            if filename.startswith("feedback_") and filename.endswith(".json"):
                file_path = os.path.join(feedbacks_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        feedbacks = json.load(f)
                        for feedback in feedbacks:
                            total_feedbacks += 1
                            if feedback.get("type") == "like":
                                positive_feedbacks += 1
                            elif feedback.get("type") == "dislike":
                                negative_feedbacks += 1
                    except json.JSONDecodeError:
                        continue
        
        positive_percentage = (positive_feedbacks / total_feedbacks * 100) if total_feedbacks > 0 else 0
        
        return {
            "total": total_feedbacks,
            "positive": positive_feedbacks,
            "negative": negative_feedbacks,
            "positive_percentage": round(positive_percentage, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت آمار: {str(e)}")

@router.get("/feedback/list")
async def get_feedbacks(limit: Optional[int] = 50, offset: Optional[int] = 0):
    """
    دریافت لیست فیدبک‌ها
    """
    try:
        feedbacks_dir = "data/feedbacks"
        if not os.path.exists(feedbacks_dir):
            return {"feedbacks": [], "total": 0}
        
        all_feedbacks = []
        
        # خواندن تمام فایل‌های فیدبک
        for filename in os.listdir(feedbacks_dir):
            if filename.startswith("feedback_") and filename.endswith(".json"):
                file_path = os.path.join(feedbacks_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        feedbacks = json.load(f)
                        all_feedbacks.extend(feedbacks)
                    except json.JSONDecodeError:
                        continue
        
        # مرتب‌سازی بر اساس timestamp
        all_feedbacks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # اعمال pagination
        total = len(all_feedbacks)
        paginated_feedbacks = all_feedbacks[offset:offset + limit]
        
        return {
            "feedbacks": paginated_feedbacks,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت فیدبک‌ها: {str(e)}") 