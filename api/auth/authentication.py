from typing import Tuple, Any
from core.config import settings
import aiohttp


async def login(telephone: str, password: str) -> Tuple[int, None]:
    params = {"telephone": telephone,
              "password": password}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{settings.API_URL}/api/v1/auth/login-telegram',
                                json=params) as response:
            status_code = response.status
            if status_code == 200:
                result = await response.json()
                await session.close()
                return status_code, result["access_token"]
            else:
                await session.close()
                return status_code, None


async def decode_code(access_token: str) -> Tuple[int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{settings.API_URL}/api/v1/auth/user_data_by_token',
                                headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            if status_code == 200:
                result = await response.json()
                await session.close()
                return status_code, result["id"]
            else:
                await session.close()
                return status_code, None
