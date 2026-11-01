from sqlalchemy import select, update, delete, insert
from src.db.models import Action, User, UserMedia, ReactionType
from datetime import datetime
from src.db.database import async_session

class ActionQueries:
    @classmethod
    async def add_action(cls, from_user_id: int, to_user_id: int, reaction_type: ReactionType, message: str | None = None) -> bool:
        async with async_session() as session:
            fields = {
                    "from_user_id": from_user_id,
                    "to_user_id": to_user_id,
                    "reaction": reaction_type,
                    "created_at": datetime.now()
                }
            if message is None:
                query_no_message = insert(Action).values(
                    **fields
                )
                await session.execute(query_no_message)
            if message is not None:
                query_with_message = insert(Action).values(
                    **fields,
                    message=str(message),

                )
                await session.execute(query_with_message)
            await session.commit()
            return True


