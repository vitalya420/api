from datetime import timedelta, datetime

from sqlalchemy import select, update
from sqlalchemy.sql.operators import eq, and_
from typing_extensions import Optional, Union, Literal

from app.exceptions import SmsCooldown
from app.models import OTP, AccessToken, RefreshToken, User
from app.tasks import send_sms_to_phone
from app.utils.rand import random_code
from . import services
from .base import BaseService


@services('auth')
class Authorization(BaseService):
    async def issue_token_pair(self, user: Union[int, User],
                               *,
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None
                               ):
        user_id = user.id if isinstance(user, User) else user

        async with self.session_factory() as session:
            refresh = RefreshToken(user_id=user_id)
            session.add(refresh)
            await session.commit()
            await session.refresh(refresh)

            ip_address = ip_address or self.context.get('ip_address', '<unknown>')
            user_agent = user_agent or self.context.get('user_agent', '<unknown>')

            access = AccessToken(user_id=user_id,
                                 ip_addr=ip_address,
                                 user_agent=user_agent,
                                 refresh_token_jti=refresh.jti)
            session.add(access)
            await session.commit()

            await session.refresh(refresh)
            await session.refresh(access)

            return access, refresh

    async def revoke_token(self, type_: Union[str, Literal['access', 'refresh']], jti: str):
        if type_ not in ['access', 'refresh']:
            raise ValueError('Invalid token type')

    async def get_token_by_jti(self, type_: Union[str, Literal['access', 'refresh']], jti: str):
        cls_ = AccessToken if type_ == 'access' else RefreshToken
        query = select(cls_).where(and_(eq(cls_.jti, jti), eq(cls_.revoked, False)))
        async with self.session_factory() as session:
            res = await session.execute(query)
            return res.scalars().first()

    async def send_otp(self, phone: str, *,
                       lifetime: Optional[timedelta] = timedelta(minutes=10),
                       cooldown: Optional[timedelta] = timedelta(minutes=1),
                       revoke_old: Optional[bool] = True,
                       limit: Optional[int] = 5,
                       limit_delta: Optional[timedelta] = timedelta(hours=3)):

        now = datetime.utcnow()

        cooldown_expiry = now - cooldown
        query = select(OTP).where(
            and_(
                OTP.destination == phone,
                OTP.sent_at >= cooldown_expiry
            )
        )

        async with self.session_factory() as session:
            result = await session.execute(query)
            existing_otp = result.scalars().first()

            if existing_otp:
                raise SmsCooldown("You send to many codes.")

            limit_expiry = now - limit_delta
            limit_query = select(OTP).where(
                and_(
                    OTP.destination == phone,
                    OTP.sent_at >= limit_expiry
                )
            )
            limit_result = await session.execute(limit_query)
            sent_count = len(limit_result.scalars().all())

            if sent_count >= limit:
                raise SmsCooldown(f"You have exceeded the limit of {limit} OTPs.")

            if revoke_old:
                revoke_query = select(OTP).where(OTP.destination == phone)
                revoke_result = await session.execute(revoke_query)
                old_otps = revoke_result.scalars().all()

                for old_otp in old_otps:
                    old_otp.revoked = True
                await session.commit()

        code = random_code()
        await send_sms_to_phone(phone, code)
        async with self.session_factory() as session:
            async with session.begin():
                instance = OTP(destination=phone, code=code, sent_at=now, expires_at=now + lifetime)
                session.add(instance)
            await session.refresh(instance)

    async def get_otp(self, phone: str):
        now = datetime.utcnow()

        query = select(OTP).where(
            and_(
                eq(OTP.used, False),
                and_(
                    OTP.destination == phone,
                    OTP.expires_at > now,
                )
            ),
        ).order_by(OTP.sent_at.desc())

        async with self.session_factory() as session:
            result = await session.execute(query)
            valid_otp = result.scalars().first()

        return valid_otp

    async def set_code_used(self, code_id: int):
        async with self.session_factory() as session:
            async with session.begin():
                stmt = update(OTP).where(and_(OTP.id == code_id, eq(OTP.used, False))).values(used=True)
                result = await session.execute(stmt)
