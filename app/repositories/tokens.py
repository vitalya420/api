from datetime import datetime, timedelta
from typing import Optional, Tuple, Type, TypeVar, Union

from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.operators import eq

from app.base import BaseRepository
from app.enums import Realm
from app.exceptions import BusinessCodeNotProvided, RefreshTokenNotFound
from app.models import AccessToken, RefreshToken

TokenType = TypeVar("TokenType", AccessToken, RefreshToken)


class TokensRepository(BaseRepository):
    """
    Repository for managing access and refresh tokens in the database.

    This class provides methods to create, retrieve, revoke, and manage tokens
    associated with users in a specific realm. It interacts with the database
    using SQLAlchemy ORM.
    """

    async def create_tokens(
        self,
        user_id: int,
        realm: Realm,
        business_code: Optional[str] = None,
        ip_address: Optional[str] = "<no ip>",
        user_agent: Optional[str] = "<no user agent>",
    ) -> Tuple[AccessToken, RefreshToken]:
        """
        Creates and stores a new access token and refresh token for a user.

        Args:
            user_id (int): The ID of the user for whom the tokens are being created.
            realm (Realm): The realm in which the tokens are valid.
            business_code (Optional[str]): An optional business code associated with the tokens.
            ip_address (Optional[str]): The IP address of the user (default is "<no ip>").
            user_agent (Optional[str]): The user agent string of the user's device (default is "<no user agent>").

        Returns:
            Tuple[AccessToken, RefreshToken]: The created access token and refresh token.
        """
        now = datetime.utcnow()

        refresh_token = RefreshToken(
            user_id=user_id,
            realm=realm,
            business_code=business_code,
            issued_at=now,
            expires_at=now + timedelta(days=14),
        )
        self.session.add(refresh_token)
        await self.session.flush()

        access_token = AccessToken(
            user_id=user_id,
            realm=realm,
            business_code=business_code,
            ip_address=ip_address,
            user_agent=user_agent,
            issued_at=now,
            expires_at=now + timedelta(days=7),
            refresh_token_jti=refresh_token.jti,
        )
        self.session.add(access_token)
        await self.session.flush()
        refresh_token.access_token_jti = access_token.jti
        return access_token, refresh_token

    async def get_token(
        self, class_: Type[TokenType], jti: str, alive_only: bool = True
    ) -> TokenType:
        """
        Retrieves a token (either AccessToken or RefreshToken) by its JTI (JWT ID).

        Args:
            class_ (Type[TokenType]): The class type of the token to retrieve (AccessToken or RefreshToken).
            jti (str): The JWT ID of the token to retrieve.
            alive_only (bool): If True, only retrieves tokens that are not revoked and are still valid (default is True).

        Returns:
            T: The retrieved token, or None if not found.
        """
        query = select(class_).where(class_.jti == jti)  # noqa
        if alive_only:
            query = query.where(
                and_(class_.revoked == False, class_.expires_at >= datetime.utcnow())
            )
        if class_ is RefreshToken:
            query = query.options(joinedload(class_.access_token))
        elif class_ is AccessToken:
            query = query.options(joinedload(class_.refresh_token))
        res = await self.session.execute(query)
        return res.scalars().first()

    async def revoke_token(self, class_: Type[TokenType], jti: str):
        """
        Revokes a token (either AccessToken or RefreshToken) by its JTI.

        Args:
            class_ (Type[T]): The class type of the token to revoke (AccessToken or RefreshToken).
            jti (str): The JWT ID of the token to revoke.
        """
        if (token := await self.get_token(class_, jti)) is not None:
            token.revoked = True

    async def get_tokens(self, user_id: int, realm: Realm, business_code: str):
        """
        Retrieves all access tokens for a specific user in a given realm and business code.

        Args:
            user_id (int): The ID of the user whose tokens are being retrieved.
            realm (Realm): The realm in which the tokens are valid.
            business_code (str): The business code associated with the tokens.

        Returns:
            List[AccessToken]: A list of access tokens associated with the user.

        Raises:
            BusinessCodeNotProvided: If the realm is mobile and no business code is provided.
        """
        and_clause = and_(
            AccessToken.user_id == user_id,
            AccessToken.realm == realm,
        )

        if realm == Realm.mobile:
            if business_code is None:
                raise BusinessCodeNotProvided(
                    "For mobile app business id should be provided."
                )
            eq_ = eq(AccessToken.business_code, business_code)
            and_clause = and_(and_clause, eq(AccessToken.business_code, business_code))
        query = select(AccessToken).where(and_clause)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def refresh_revoke(
        self, refresh_jti: str
    ) -> Tuple[AccessToken, RefreshToken]:
        """
        Revokes a refresh token and its associated access token by the refresh token's JTI.

        Args:
            refresh_jti (str): The JWT ID of the refresh token to revoke.

        Returns:
            Tuple[AccessToken, RefreshToken]: The revoked access token and refresh token.

        Raises:
            RefreshTokenNotFound: If the refresh token with the specified JTI is not found.
        """
        refresh_token = await self.get_token(RefreshToken, refresh_jti)
        if refresh_token is None:
            raise RefreshTokenNotFound(
                f"Active refresh token with jti {refresh_jti} not found."
            )
        refresh_token.revoked = True
        refresh_token.access_token.revoked = True
        return refresh_token.access_token, refresh_token
