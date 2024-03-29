from typing import Optional, List

from aiohttp import ClientSession
from audiobookshelf.helper import remove_none_values, build_url

__all__ = ['ABSClient']


class ABSClient:

    user: Optional[dict] = None

    def __init__(self, base_url: str):
        self.base_url = base_url
        if self.base_url[-1] != '/':
            self.base_url += '/'

    async def _api_call(self,
                        method: str,
                        endpoint: str,
                        data: dict,
                        req_auth: bool = True,
                        return_result: bool = True):
        if req_auth and self.user is None:
            raise Exception('Missing Authorization')
        async with ClientSession() as session:
            header = {}
            if req_auth:
                header['Authorization'] = f'Bearer {self.user['token']}'
            result = await session.request(method, f'{self.base_url}{endpoint}', json=data, headers=header)
            if result.status != 200:
                raise Exception(f'Raised Error {result.status}')
            if return_result:
                return await result.json()

    async def authorize(self, username: str, password: str):
        data = await self._api_call('POST',
                                    'login',
                                    {'username': username, 'password': password},
                                    req_auth=False)
        self.user = data['user']

    # Libraries

    async def create_library(self,
                             name: str,
                             folders: List[str],
                             icon: Optional[str] = None,
                             media_type: Optional[str] = None,
                             provider: Optional[str] = None,
                             cover_aspect_ratio: Optional[bool] = None,
                             disable_watcher: Optional[bool] = None,
                             skip_matching_media_with_asin: Optional[bool] = None,
                             skip_matching_media_with_isbn: Optional[bool] = None,
                             auto_scan_cron_expression: Optional[str] = None) -> dict:
        settings = remove_none_values({
            'coverAspectRatio': (1 if cover_aspect_ratio else 0) if cover_aspect_ratio is not None else None,
            'disableWatcher': disable_watcher,
            'skipMatchingMediaWithAsin': skip_matching_media_with_asin,
            'skipMatchingMediaWithIsbn': skip_matching_media_with_isbn,
            'autoScanCronExpression': auto_scan_cron_expression
        })
        param = remove_none_values({
            'name': name,
            'folders': [{'fullPath': x} for x in folders],
            'icon': icon,
            'mediaType': media_type,
            'provider': provider,
            'settings': settings
        })
        data = await self._api_call('POST', 'api/libraries', param)
        return data

    async def get_libraries(self) -> dict:
        data = await self._api_call('GET', 'api/libraries', {})
        return data['libraries']

    async def get_library(self,
                          library_id: str,
                          include: Optional[List[str]] = None) -> List[dict]:
        param = remove_none_values({
            'include': ','.join(include) if include is not None else None
        })
        data = await self._api_call('GET', f'api/libraries/{library_id}', param)
        return data

    async def delete_library(self, library_id: str):
        await self._api_call('DELETE', f'api/libraries/{library_id}', {})

    async def get_library_authors(self, library_id: str) -> dict:
        data = await self._api_call('GET', f'api/libraries/{library_id}/authors', {})
        return data['authors']

    async def delete_author(self, author_id: str):
        await self._api_call('DELETE', f'api/authors/{author_id}', {}, return_result=False)

    async def get_sessions_page(self, user_id: str, items_per_page: Optional[int] = None, page: Optional[int] = None) -> dict:
        param = remove_none_values({
            'user': user_id,
            'itemsPerPage': items_per_page,
            'page': page
        })
        data = await self._api_call('GET', build_url('api/sessions', param), {})
        return data

    async def get_user_year_stats(self, year: int) -> dict:
        return await self._api_call('GET', f'api/me/stats/year/{year}', {})

    async def get_library_items(self,
                                library_id: str,
                                limit: Optional[int] = None,
                                page: Optional[int] = None,
                                sort: Optional[str] = None,
                                desc: Optional[bool] = None,
                                _filter: Optional[str] = None,
                                minified: Optional[bool] = None,
                                collapse_series: Optional[bool] = None,
                                include: Optional[str] = None) -> dict:
        param = remove_none_values({
            'limit': limit,
            'page': page,
            'sort': sort,
            'desc': desc,
            'filter': _filter,
            'minified': minified,
            'collapseseries': collapse_series,
            'include': include
        })
        return await self._api_call('GET', build_url(f'api/libraries/{library_id}/items', param), {})
