from typing import TypedDict


class FileType(TypedDict):
    name: str
    raw: bytes
    res_id: int
    res_model: str
