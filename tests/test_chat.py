import pytest
from backend.database import SessionLocal
from backend.services.chat_service import ChatService

def test_grounded_chat_answers():
    db = SessionLocal()
    try:
        chat = ChatService(db)

        # Test September revenue query
        res1 = chat.answer_query("What was my total revenue in September?", user_id=1)
        assert "17,559,830.81" in res1["message"]

        # Test stockout query
        res2 = chat.answer_query("Which products have inventory risks?", user_id=1)
        assert "reorder" in res2["message"].lower() or "stockout" in res2["message"].lower()

        # Test customer segments query
        res3 = chat.answer_query("Which customer segments are valuable?", user_id=1)
        assert "wholesale" in res3["message"].lower()

    finally:
        db.close()
