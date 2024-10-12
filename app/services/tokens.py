import asyncio
from typing import Union, Optional, Tuple

from app.request import ApiRequest
from app.base import BaseService
from app.db import async_session_factory
from app.models import AccessToken, Business, RefreshToken
from app.repositories.tokens import TokensRepository
from app.schemas.user import User
from app.enums import Realm
from app.utils import force_id, force_code


class TokenService(BaseService):
    __repository_class__ = TokensRepository

    async def create_tokens(
        self,
        user_id: int,
        request: ApiRequest,
        realm: Realm,
        business_code: Optional[str] = None,
    ) -> Tuple[AccessToken, RefreshToken]:
        """
        Create access and refresh tokens for a user.

        This method generates a new access token and refresh token for the specified user,
        capturing the request's IP address and user agent for security purposes.

        Args:
            user_id (int): The ID of the user for whom the tokens are being created.
            request (ApiRequest): The API request object containing headers for IP and user agent.
            realm (Realm): The realm indicating the context in which the tokens are used (e.g., web or mobile).
            business_code (Optional[str]): The unique code of the business associated with the tokens, if applicable.

        Returns:
            Tuple[AccessToken, RefreshToken]: A tuple containing the newly created AccessToken and RefreshToken instances.
        """
        async with self.get_repo() as repo:
            return await repo.create_tokens(
                user_id,
                realm,
                business_code,
                request.headers.get("X-Real-IP", "<no ip>"),
                request.headers.get("User-Agent", "<no user agent>"),
            )

    async def get_access_token(
        self, jti: str, alive_only: bool = True, use_cache: bool = True
    ) -> Union[AccessToken, None]:
        """
        Retrieve an access token by its unique identifier (JTI).

        This method queries the repository for an AccessToken instance that matches the provided JTI.
        It can optionally filter for only alive tokens and use caching for improved performance.

        Args:
            jti (str): The unique identifier of the access token.
            alive_only (bool, optional): Whether to return only tokens that are currently alive. Defaults to True.
            use_cache (bool, optional): Whether to use the cache for retrieval. Defaults to True.

        Returns:
            Union[AccessToken, None]: The AccessToken instance if found and alive, or None if not found.
        """
        async with self.get_repo() as token_repo:
            if use_cache:
                return await self.with_cache(
                    AccessToken, jti, token_repo.get_token, AccessToken, jti, alive_only
                )
            return await token_repo.get_token(AccessToken, jti, alive_only)

    async def list_user_issued_tokens(
        self,
        user: Union[User, int],
        realm: Realm,
        business: Union[Business, str, None],
        limit: int = 20,
        offset: int = 0,
    ):
        """
        List all tokens issued to a specific user.

        This method retrieves all access and refresh tokens associated with the specified user,
        realm, and optional business code. The results can be paginated using the `limit` and `offset`
        parameters.

        Args:
            user (Union[User, int]): The user instance or the user's ID. If an integer is provided,
                                      it should correspond to the user's unique identifier.
            realm (Realm): The realm indicating the context in which the tokens are used (e.g., web or mobile).
            business (Union[Business, str, None]): The business instance or its unique code, if applicable.
                                                    If None, tokens for all businesses will be retrieved.
            limit (int, optional): The maximum number of tokens to return. Defaults to 20.
            offset (int, optional): The number of tokens to skip before starting to collect the result set.
                                    Defaults to 0.

        Returns:
            List[Union[AccessToken, RefreshToken]]: A list of tokens (access and refresh) issued to the user.
                                                     The list may be empty if no tokens are found.

        Raises:
            ValueError: If the `limit` is less than 1 or if the `offset` is negative.
            UserNotFoundError: If the specified user does not exist.
            RealmNotFoundError: If the specified realm is invalid.
            BusinessNotFoundError: If the specified business does not exist (if applicable).
        """
        async with self.get_repo() as token_repo:
            return await token_repo.get_tokens(
                force_id(user),
                realm,
                force_code(business) if business is not None else None,
                limit,
                offset,
            )

    async def count_access_tokens(
        self, user: Union[User, int], realm: Realm, business: Union[Business, str, None]
    ):
        async with self.get_repo() as token_repo:
            return await token_repo.count_access_tokens(
                force_id(user), realm, force_code(business)
            )

    async def refresh_tokens(
        self, refresh_jti: str, request: ApiRequest
    ) -> Tuple[AccessToken, RefreshToken]:
        """
        Refresh access and refresh tokens using a refresh token's unique identifier (JTI).

        This method revokes the existing access and refresh tokens associated with the provided
        refresh token JTI and generates new tokens for the user.

        Args:
            refresh_jti (str): The unique identifier of the refresh token.
            request (ApiRequest): The API request object containing headers for IP and user agent.

        Returns:
            Tuple[AccessToken, RefreshToken]: A tuple containing the newly created AccessToken and RefreshToken instances.
        """
        async with self.get_repo() as tokens_repo:
            # Revoke access and refresh tokens
            # And delete it from cache
            access, refresh = await tokens_repo.refresh_revoke(refresh_jti)

            await asyncio.gather(
                self.cache_delete_object(access), self.cache_delete_object(refresh)
            )
            return await self.reuse_session().create_tokens(
                user_id=access.user_id,
                request=request,
                realm=access.realm,
                business_code=access.business_code,
            )

    async def revoke_access_token(self, access_token: AccessToken):
        """
        Revoke a specified access token and its associated refresh token.

        This method marks the provided access token as revoked and also revokes its
        associated refresh token. It also removes both tokens from the cache.

        Args:
            access_token (AccessToken): The AccessToken instance to be revoked.

        Returns:
            None: This method does not return a value.
        """
        async with self.get_repo() as tokens_repo:
            await tokens_repo.revoke_token(AccessToken, access_token.jti)
            await tokens_repo.revoke_token(RefreshToken, access_token.refresh_token_jti)
            await asyncio.gather(
                self.cache_delete_object(access_token),
                self.cache_delete_object(access_token.refresh_token),
            )

    async def user_revokes_access_token_by_jti(
        self, user: Union[User, int], jti: str
    ) -> Union[Tuple[AccessToken, RefreshToken], None]:
        """
        Revoke an access token for a specific user by its unique identifier (JTI).

        This method checks if the access token associated with the provided JTI belongs
        to the specified user. If it does, the token is marked as revoked along with its
        associated refresh token.

        Args:
            user (Union[User, int]): The user instance or the user's ID.
            jti (str): The unique identifier of the access token to be revoked.

        Returns:
            Union[Tuple[AccessToken, RefreshToken], None]: A tuple containing the revoked AccessToken and RefreshToken instances,
                                                           or None if the token does not belong to the user.
        """
        async with self.get_repo() as tokens_repo:
            access = await tokens_repo.get_token(AccessToken, jti)
            if access is not None and access.user_id == force_id(user):
                access.revoked = True
                access.refresh_token.revoked = True
                await asyncio.gather(
                    self.cache_delete_object(access),
                    self.cache_delete_object(access.refresh_token),
                )
                return access, access.refresh_token


tokens_service = TokenService(async_session_factory)
