from datetime import datetime, timezone
from dateutil import parser as du_parser
from typing import Union, Optional, List
from enum import Enum
from audiobookshelf.helper import camel


class APIObject:

    @staticmethod
    def _val_by_instance(instance, val):
        if val is None:
            return None
        origin = instance.__origin__ if hasattr(instance, '__origin__') else None
        if instance == datetime:
            if isinstance(val, int):
                # asume unix timestamp
                return None if val == 0 else datetime.fromtimestamp(val / 1000, tz=timezone.utc)
            # asume ISO8601 string
            return du_parser.isoparse(val) if len(val) > 0 else None
        elif origin == list:
            c = instance.__args__[0]
            return [APIObject._val_by_instance(c, x) for x in val]
        elif origin == dict:
            c1 = instance.__args__[0]
            c2 = instance.__args__[1]
            return {APIObject._val_by_instance(c1, x1): APIObject._val_by_instance(c2, x2) for x1, x2 in val.items()}
        elif origin == Union:
            # TODO: only works for optional pattern, fix to try out all possible patterns?
            c1 = instance.__args__[0]
            return APIObject._val_by_instance(c1, val)
        elif issubclass(instance, APIObject):
            return instance(**val)
        else:
            return instance(val)

    @staticmethod
    def _dict_val_by_instance(instance, val, include_none_values):
        if val is None:
            return None
        if instance is None:
            return val
        origin = instance.__origin__ if hasattr(instance, '__origin__') else None
        if instance == datetime:
            return val.isoformat() if val is not None else None
        elif origin == list:
            c = instance.__args__[0]
            return [APIObject._dict_val_by_instance(c, x, include_none_values) for x in val]
        elif origin == dict:
            c1 = instance.__args__[0]
            c2 = instance.__args__[1]
            return {APIObject._dict_val_by_instance(c1, x1, include_none_values):
                    APIObject._dict_val_by_instance(c2, x2, include_none_values) for x1, x2 in val.items()}
        elif origin == Union:
            # TODO: only works for optional pattern, fix to try out all possible patterns?
            c1 = instance.__args__[0]
            return APIObject._dict_val_by_instance(c1, val, include_none_values)
        elif issubclass(instance, APIObject):
            return val.to_dict(include_none_values)
        elif isinstance(val, Enum):
            return val.value
        return instance(val)

    @classmethod
    def _get_annotations(cls):
        d = {}
        for c in cls.mro():
            try:
                d.update(**c.__annotations__)
            except AttributeError:
                pass
        return d

    def to_dict(self, include_none_values: bool = False) -> dict:
        """build dict based on annotation types

        :param include_none_values: if fields that have None values should be included in the dictionary
        """
        d = {}
        annotations = self._get_annotations()
        for name, val in self.__dict__.items():
            val = None
            cls = annotations.get(name)
            try:
                val = getattr(self, name)
            except AttributeError:
                pass
            if val is None and not include_none_values:
                continue
            if name[0] == '_':
                continue
            d[name] = APIObject._dict_val_by_instance(cls, val, include_none_values)
        return d

    def __init__(self, **kwargs):
        merged_annotations = self._get_annotations()
        # for debug
        camel_annos = [camel(k) for k in merged_annotations.keys()]
        self.__reject__ = {k: w for k, w in kwargs.items() if k not in camel_annos}
        for name, cls in merged_annotations.items():
            api_name = camel(name)
            if api_name not in kwargs.keys():
                continue
            self.__setattr__(name, APIObject._val_by_instance(cls, kwargs.get(api_name)))


class MediaProgressItem(APIObject):
    id: str
    library_item_id: str
    episode_id: str
    duration: float
    progress: float
    current_time: float
    is_finished: bool
    hide_from_continue_listening: bool
    last_update: datetime
    started_at: datetime
    finished_at: Optional[datetime]


class Permissions(APIObject):
    access_all_libraries: bool
    access_all_tags: bool
    access_explicit_content: bool
    delete: bool
    download: bool
    update: bool
    upload: bool


class AudioBookmark(APIObject):
    library_item_id: str
    title: str
    time: int
    created_at: datetime


class User(APIObject):
    id: str
    username: str
    type: str
    token: str
    created_at: datetime
    media_progress: List[MediaProgressItem]
    email: Optional[str]
    is_active: bool
    is_locked: bool
    last_seen: Optional[datetime]
    old_user_id: Optional[str]
    permissions: Permissions
    bookmarks: List[AudioBookmark]
    libraries_accessible: List[str]
    item_tags_selected: List[str]
    series_hide_from_continue_listening: List[str]


class LibraryFolder(APIObject):
    id: str
    full_path: str
    library_id: str


class LibrarySettings(APIObject):
    cover_aspect_ratio: int
    disable_watcher: bool
    skip_matching_media_with_asin: bool
    skip_matching_media_with_isbn: bool
    auto_scan_cron_expression: Optional[str]
    audiobooks_only: bool
    hide_single_book_series: bool
    metadata_precedence: List[str]


class Library(APIObject):
    id: str
    name: str
    folders: List[LibraryFolder]
    display_order: int
    icon: str
    media_type: str
    provider: str
    settings: LibrarySettings
    created_at: datetime
    last_update: datetime
    last_scan: Optional[datetime]
    last_scan_version: Optional[str]
    old_library_id: Optional[str]


class Author(APIObject):
    id: str
    asin: Optional[str]
    name: str
    description: Optional[str]
    image_path: Optional[str]
    added_at: datetime
    updated_at: datetime
    num_books: Optional[int]
    library_id: str
