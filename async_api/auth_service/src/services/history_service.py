from functools import lru_cache

from db.postgres_db import AsyncSession, get_session
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.entity import UserHistoryModel
from schemas.entity import History
from sqlalchemy import select


class HistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def make_note(self, user_history: History) -> History:
        user_history_json = jsonable_encoder(user_history, exclude_none=True)
        user_history_note = UserHistoryModel(**user_history_json)

        self.db.add(user_history_note)
        await self.db.commit()
        await self.db.refresh(user_history_note)
        return History(
            id=user_history_note.id,
            user_id=user_history_note.user_id,
            occured_at=user_history_note.occured_at,
            action=user_history_note.action,
            fingerprint=user_history_note.fingerprint,
        )

    async def get_last_notes(self, skip: int = 0, limit: int = 10) -> list[History]:
        result = await self.db.execute(
            select(UserHistoryModel)
            .offset(skip)
            .limit(limit)
            .order_by(UserHistoryModel.occured_at.desc()),
        )

        return [
            History(
                id=hist.id,
                user_id=hist.user_id,
                occured_at=hist.occured_at,
                action=hist.action,
                fingerprint=hist.fingerprint,
            ) for hist in result.scalars()
        ]

    async def get_last_user_notes(
            self,
            user_id: str,
            skip: int = 0,
            limit: int = 10,
    ) -> list[History]:
        result = await self.db.execute(
            select(UserHistoryModel)
            .where(UserHistoryModel.user_id == user_id)
            .offset(skip).limit(limit),
        )

        return [
            History(
                id=hist.id,
                user_id=hist.user_id,
                occured_at=hist.occured_at,
                action=hist.action,
                fingerprint=hist.fingerprint,
            ) for hist in result.scalars()
        ]


@lru_cache
def get_history_service(
        db: AsyncSession = Depends(get_session),
) -> HistoryService:
    return HistoryService(db=db)
