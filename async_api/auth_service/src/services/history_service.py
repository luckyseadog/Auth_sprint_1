from db.postgres import AsyncSession, get_session
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.entity import UserHistoryModel
from schemas.entity import History
from sqlalchemy import select


class HistoryService():
    async def make_note(self, user_history: History, db: AsyncSession = Depends(get_session)) -> History:
        user_history_json = jsonable_encoder(user_history, exclude_none=True)
        user_history_note = UserHistoryModel(**user_history_json)

        db.add(user_history_note)
        await db.commit()
        await db.refresh(user_history_note)
        return History(id=user_history_note.id,
                       user_id=user_history_note.user_id,
                       occured_at=user_history_note.occured_at,
                       action=user_history_note.action,
                       fingerprint=user_history_note.fingerprint)


    async def get_last_notes(self, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)) -> list[History]:
        result = await db.execute(select(UserHistoryModel).offset(skip).limit(limit))

        return [History(id=hist.id,
            user_id=hist.user_id,
            occured_at=hist.occured_at,
            action=hist.action,
            fingerprint=hist.fingerprint,
        ) for hist in result.scalars()]


    async def get_last_user_notes(self, user_id: str, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)) -> list[History]:
        result = await db.execute(select(UserHistoryModel).where(UserHistoryModel.user_id == user_id).offset(skip).limit(limit))

        return [History(id=hist.id,
            user_id=hist.user_id,
            occured_at=hist.occured_at,
            action=hist.action,
            fingerprint=hist.fingerprint,
        ) for hist in result.scalars()]