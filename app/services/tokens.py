import asyncio
from datetime import datetime
from typing import Union, Optional, Tuple, List, Sequence

from sanic import Request, BadRequest, NotFound
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.db import async_session_factory
from app.models import RefreshToken, AccessToken
from app.types import TokenType, UserType, BusinessType, get_token_class, TokenPairType
from app.utils import force_id, force_business_code
from .business import business_service
from app.base import BaseService
from app.schemas.user import Realm
from app.repositories.tokens import TokensRepository

# from app.request import ApiRequest


class TokenService(BaseService):
    __repository_class__ = TokensRepository

    async def _create_tokens_using_context(
        self,
        user_id: int,
        session: AsyncSession,
        *,
        realm: Realm,
        business: Optional[str] = None,
    ) -> TokenPairType:
        """
        Create a new pair of access and refresh tokens for a user.

        This method requires the request context to save the user's IP address and user-agent in the database.
        Raises a RuntimeError if the request context is not provided.

        Args:
            user_id (int): The ID of the user for whom the tokens are being created.
            business (Optional[str]): The business code associated with the user.
            realm (Realm): The realm.
            session (AsyncSession): The database session to use for the operation.

        Returns:
            Tuple[AccessToken, RefreshToken]: The created access and refresh tokens.
        """
        request: Request | None = self.context.get("request", None)
        if request is None:
            raise RuntimeError("Need to provide request in context")
        ip_addr = request.headers.get("X-Real-IP", "<no ip>")
        user_agent = request.headers.get("User-Agent", "<no agent>")

        refresh = RefreshToken(user_id=user_id, realm=realm, business_code=business)
        session.add(refresh)
        await session.commit()

        access = AccessToken(
            user_id=user_id,
            business_code=business,
            ip_addr=ip_addr,
            user_agent=user_agent,
            realm=realm,
            refresh_token_jti=refresh.jti,
        )
        session.add(access)
        await session.commit()

        await session.refresh(access)
        return access, refresh

    async def user_revokes_access_token_by_jti(self, user: UserType, jti: str) -> bool:
        """
        Revoke an access token by its JTI (JWT ID).

        This method also revokes the associated refresh token and removes both tokens from the cache.

        Args:
            user (UserType): The user who is revoking the token.
            jti (str): The JTI of the access token to revoke.

        Returns:
            True: On success.
            False: On failure.

        Raises:
            Exception: If the access token is invalid.
        """
        query = select(AccessToken).where(
            and_(
                eq(AccessToken.jti, jti),
                eq(AccessToken.user_id, force_id(user)),
                eq(AccessToken.revoked, False),
                AccessToken.expires_at >= datetime.now(),  # noqa
            ),
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            access_token = result.scalars().first()
            if access_token is None:
                return False
            refresh_jti = access_token.refresh_token_jti

            amount = await self._revoke_token_by_jti(
                "access", access_token.jti, session
            )
            await self._revoke_token_by_jti("refresh", refresh_jti, session)

        await asyncio.gather(
            self.cache_delete(AccessToken.lookup_key(access_token.jti)),
            self.cache_delete(RefreshToken.lookup_key(access_token.refresh_token_jti)),
        )

        return not not amount

    async def refresh_tokens(self, refresh_jti: str) -> TokenPairType:
        """
        Refresh the access and refresh tokens using the provided refresh token JTI.

        This method revokes the old tokens and generates new ones.

        Args:
            refresh_jti (str): The JTI of the refresh token to use for generating new tokens.

        Returns:
            Tuple[AccessToken, RefreshToken]: The newly created access and refresh tokens.

        Raises:
            BadRequest: If the provided refresh token is not valid.
        """
        keys_to_remove_from_cache = []
        async with self.get_session() as session:
            refresh = await self._get_token("refresh", refresh_jti, session)
            if not refresh:
                raise BadRequest("This refresh token is not valid")
            await self._revoke_token_by_jti("refresh", refresh_jti, session)
            keys_to_remove_from_cache.append(RefreshToken.lookup_key(refresh_jti))

            access = await self._get_access_token_by_refresh_jti(refresh_jti, session)
            if access.is_alive():
                await self._revoke_token_by_jti("access", access.jti, session)
            keys_to_remove_from_cache.append(AccessToken.lookup_key(access.jti))

            new_tokens = await self.with_context(
                {"session": session}
            ).create_tokens_for_user(
                access.user_id, realm=access.realm, business=access.business_code
            )
        await asyncio.gather(
            *[self.cache_delete(key) for key in keys_to_remove_from_cache]
        )
        return new_tokens

    async def revoke_access_token(self, access_token: AccessToken) -> None:
        """
        Revoke a specific access token and its associated refresh token.

        This method also removes both tokens from the cache.

        Args:
            access_token (AccessToken): The access token to revoke.

        Returns:
            None: On success.
        """
        async with self.get_session() as session:
            await self._revoke_token_by_jti("access", access_token.jti, session)
            await self._revoke_token_by_jti(
                "refresh", access_token.refresh_token_jti, session
            )
        await asyncio.gather(
            self.cache_delete(AccessToken.lookup_key(access_token.jti)),
            self.cache_delete(RefreshToken.lookup_key(access_token.refresh_token_jti)),
        )

    async def get_access_token_by_jti(self, jti: str) -> Union[AccessToken, None]:
        """
        Retrieve an access token by its JTI.

        Args:
            jti (str): The JTI of the access token to retrieve.

        Returns:
            AccessToken: The access token associated with the provided JTI, or None if not found.
        """
        async with self.get_session() as session:
            return await self._get_token("access", jti, session)

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken:
        """
        Retrieve a refresh token by its JTI.

        Args:
            jti (str): The JTI of the refresh token to retrieve.

        Returns:
            RefreshToken: The refresh token associated with the provided JTI, or None if not found.
        """
        async with self.get_session() as session:
            return await self._get_token("refresh", jti, session)

    async def revoke_all(
        self,
        user: UserType,
        business: BusinessType,
        exclude: Optional[Sequence[str]] = None,
    ) -> int:
        """
        Revoke all access tokens and their associated refresh tokens for a user and business.

        Optionally, exclude specific tokens from revocation based on their JTI.

        Args:
            user (UserType): The user whose tokens are to be revoked.
            business (BusinessType): The business associated with the tokens.
            exclude (Optional[Sequence[str]]): A list of JTI strings to exclude from revocation.

        Returns:
            int: The number of tokens revoked.
        """
        exclude = exclude or []
        keys_to_remove_from_cache = []

        query = select(AccessToken).where(
            and_(
                eq(AccessToken.user_id, force_id(user)),
                eq(AccessToken.business, force_business_code(business)),
                eq(AccessToken.revoked, False),
                AccessToken.expires_at >= datetime.now(),  # noqa
            ),
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            tokens = result.scalars().all()

            counter = 0
            for token in tokens:
                access_jti = token.jti
                if access_jti in exclude:
                    continue

                refresh_jti = token.refresh_token_jti

                await self._revoke_token_by_jti("access", access_jti, session)
                await self._revoke_token_by_jti("refresh", refresh_jti, session)

                keys_to_remove_from_cache.extend(
                    [
                        AccessToken.lookup_key(access_jti),
                        RefreshToken.lookup_key(refresh_jti),
                    ]
                )

                counter += 1
        await asyncio.gather(
            *[self.cache_delete(key) for key in keys_to_remove_from_cache]
        )
        return counter

    async def create_tokens_for_user(
        self, user: UserType, *, realm: Realm, business: Optional[BusinessType] = None
    ) -> TokenPairType:
        """
        Create a new access and refresh token pair for a user.

        Args:
            user (UserType): The user for whom the tokens are being created.
            realm (Realm): The realm the tokens are being created.
            business (BusinessType): The business associated with the user.

        Returns:
            Tuple[AccessToken, RefreshToken]: The created access and refresh tokens.
        """
        if realm == Realm.mobile and business is None:
            raise BadRequest("For mobile app business id should be provided.")

        if (
            business
            and await business_service.get_business_by_code_with_cache(business) is None
        ):
            raise NotFound(f"Business with code {business} not found.")

        async with self.get_session() as session:
            access, refresh = await self._create_tokens_using_context(
                force_id(user),
                session,
                realm=realm,
                business=business if realm == Realm.mobile else None,
            )
        await self.save_tokens_in_cache(access, refresh)
        return access, refresh

    async def list_user_issued_tokens(
        self,
        user: UserType,
        realm: Realm,
        business: Optional[BusinessType] = None,
        limit: int = 0,
        offset: int = 0,
    ):

        and_clause = and_(
            AccessToken.user_id == force_id(user),
            AccessToken.realm == realm,
        )
        if realm == Realm.mobile:
            if business is None:
                raise BadRequest("For mobile app business id should be provided.")

            eq_ = eq(AccessToken.business_code, force_business_code(business))
            and_clause = and_(
                and_clause, eq(AccessToken.business_code, force_business_code(business))
            )

        query = select(AccessToken).where(and_clause)
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def _get_user_access_tokens(
        self,
        user_id: int,
    ):
        pass

    async def list_user_issued_tokens_tokens(
        self, user: UserType, business: BusinessType, limit: int = 0, offset: int = 0
    ) -> List[AccessToken]:
        """
        Retrieve all access tokens issued to a user for a specific business.

        This method currently does not implement pagination.

        Args:
            user (UserType): The user whose tokens are to be listed.
            business (BusinessType): The business associated with the tokens.
            limit (int): The maximum number of tokens to return (default is 0, which means no limit).
            offset (int): The number of tokens to skip before starting to collect the result set (default is 0).

        Returns:
            List[AccessToken]: A list of access tokens issued to the user.
        """
        # TODO: Pagination
        query = select(AccessToken).where(
            and_(
                eq(AccessToken.user_id, force_id(user)),
                eq(AccessToken.business_code, force_business_code(business)),
                eq(AccessToken.revoked, False),
                AccessToken.expires_at >= datetime.utcnow(),
            )
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def save_tokens_in_cache(
        self, *tokens: Union[AccessToken, RefreshToken]
    ) -> None:
        """
        Save multiple tokens in the cache.

        Args:
            tokens (Union[AccessToken, RefreshToken]): The tokens to save in the cache.
        """
        await asyncio.gather(*[self.cache_object(token) for token in tokens])

    async def remove_tokens_from_cache(
        self, *tokens: Union[AccessToken, RefreshToken]
    ) -> None:
        """
        Remove multiple tokens from the cache.

        Args:
            tokens (Union[AccessToken, RefreshToken]): The tokens to remove from the cache.
        """
        await asyncio.gather(*[self.cache_delete_object(token) for token in tokens])

    async def get_access_token_with_cache(self, jti: str) -> Union[AccessToken, None]:
        """
        Retrieve an access token from the cache or compute it if not found.

        This method attempts to retrieve an access token associated with the
        given JWT ID (jti) from the cache. If the access token is not found
        in the cache, it calls the `get_access_token_by_jti` method to
        compute the access token, caches it, and then returns it.

        Args:
            jti (str): The JWT ID (jti) associated with the access token to be retrieved.

        Returns:
            Union[AccessToken, None]: The cached access token if found, or the newly
                                       computed access token if not found, or None if
                                       no access token is available.
        """
        return await self.with_cache(
            AccessToken, jti, self.get_access_token_by_jti, jti
        )

    @staticmethod
    async def _get_access_token_by_refresh_jti(
        refresh_jti: str, session: AsyncSession
    ) -> Union[AccessToken, None]:
        """
        Retrieve an access token associated with a given refresh token JTI.

        Args:
            refresh_jti (str): The JTI of the refresh token.

        Returns:
            AccessToken: The access token associated with the provided refresh token JTI, or None if not found.
        """
        query = select(AccessToken).where(
            eq(AccessToken.refresh_token_jti, refresh_jti)
        )
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def _revoke_token_by_jti(
        type_: TokenType, jti: str, session: AsyncSession
    ) -> int:
        """
        Revoke a token (access or refresh) by its JTI.

        Args:
            type_ (TokenType): The type of the token (access or refresh).
            jti (str): The JTI of the token to revoke.
            session (AsyncSession): The database session to use for the operation.

        Returns:
            int: The number of rows affected (should be 1 if the token was revoked).
        """
        class_ = get_token_class(type_)
        query = (
            update(class_)
            .where(
                and_(
                    eq(class_.jti, jti),
                    eq(class_.revoked, False),
                    class_.expires_at >= datetime.utcnow(),  # noqa
                )
            )
            .values(revoked=True)
        )
        result = await session.execute(query)
        return result.rowcount  # noqa

    @staticmethod
    async def _get_token(
        type_: TokenType, jti: str, session: AsyncSession
    ) -> Union[AccessToken, RefreshToken, None]:
        """
        Retrieve a token (access or refresh) by its JTI.

        Args:
            type_ (TokenType): The type of the token (access or refresh).
            jti (str): The JTI of the token to retrieve.
            session (AsyncSession): The database session to use for the operation.

        Returns:
            Union[AccessToken, RefreshToken]: The token associated with the provided JTI, or None if not found.
        """
        class_ = get_token_class(type_)
        now = datetime.utcnow()  # noqa
        query = select(class_).where(
            and_(
                eq(class_.jti, jti), eq(class_.revoked, False), class_.expires_at >= now
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def create_tokens(
        self,
        user_id: int,
        request: "ApiRequest",
        realm: Realm,
        business_code: Optional[str] = None,
    ):
        async with self.get_repo() as repo:
            return await repo.create_tokens(
                user_id,
                realm,
                business_code,
                request.headers.get("X-Real-IP", "<no ip>"),
                request.headers.get("User-Agent", "<no user agent>"),
            )


tokens_service = TokenService(async_session_factory)
