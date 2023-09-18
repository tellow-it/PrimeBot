from typing import Tuple, Any, List
from core.config import settings
import aiohttp


async def get_buildings(access_token: str) -> Tuple[int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'{settings.API_URL}/api/v1/building/?on_page=-1&order_by_field=building_name',
                               headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            if status_code == 200:
                building_data = await response.json()
                await session.close()
                return status_code, building_data["buildings"]
            else:
                await session.close()
                return status_code, None


async def get_data_by_param(access_token: str, param: str) -> Tuple[int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'{settings.API_URL}/api/v1/{param}/',
                               headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            if status_code == 200:
                param_data = await response.json()
                await session.close()
                return status_code, param_data
            else:
                await session.close()
                return status_code, None


async def get_orders(access_token: str, user_id: int) -> Tuple[int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'{settings.API_URL}/api/v1/order/for-user/{user_id}?order_by_field=created_at',
                               headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            if status_code == 200:
                order_data = await response.json()
                await session.close()
                return status_code, order_data["order_list"]
            else:
                await session.close()
                return status_code, None


async def create_order(access_token: str,
                       order_name: str,
                       building_id: int,
                       system_id: int,
                       important_id: int,
                       materials: List,
                       creator_id: int,
                       status_id: int,
                       description: str = None) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{settings.API_URL}/api/v1/order/create',
                                json={
                                    "order_name": order_name,
                                    "building_id": building_id,
                                    "system_id": system_id,
                                    "important_id": important_id,
                                    "materials": materials,
                                    "creator_id": creator_id,
                                    "status_id": status_id,
                                    "description": description
                                },
                                headers={"Authorization": f"Bearer {access_token}"}) as response:
            status_code = response.status
            return status_code
