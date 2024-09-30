from datetime import datetime
from typing import Union, Literal, Optional

from sqlalchemy import select, and_
from sqlalchemy.sql.operators import eq

from .base import BaseService
from . import services
from app.models import AccessToken, RefreshToken


@services('tokens')
class TokenService(BaseService):
    async def get_all_users_tokens(self,
                                   type_: Union[str, Literal["access", "refresh"]] = "access",
                                   user_id: Optional[int] = None,
                                   limit: int = 10,
                                   offset: int = 0):
        if type_ not in ["access", "refresh"]:
            raise ValueError("Type must be either access or refresh")
        if not user_id and not self.context.get('user_id', None):
            raise RuntimeError("user_id should be provided via context or as argument")

        cls_ = AccessToken if type_ == "access" else RefreshToken

        now = datetime.utcnow()

        query = select(cls_).where(and_(
            eq(cls_.user_id, user_id or self.context['user_id']),
            eq(cls_.revoked, False),
            cls_.expires_at > now
        )).limit(limit).offset(offset)

        async with self.session_factory() as session:
            result = await session.execute(query)
            tokens = result.scalars().all()

        return tokens
