from typing import Tuple, Any
from core.config import settings
import aiohttp


async def get_user_data(access_token: str, user_id: int) -> Tuple[int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'{settings.API_URL}/api/v1/user/{user_id}',
                               headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            if status_code == 200:
                user_data = await response.json()
                await session.close()
                return status_code, user_data
            else:
                await session.close()
                return status_code, None


async def update_password(access_token: str, user_id: int, password: str, new_password: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.patch(url=f'{settings.API_URL}/api/v1/user/update-password/{user_id}',
                                 json={"password": password,
                                       "new_password": new_password},
                                 headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            await session.close()
            return status_code
