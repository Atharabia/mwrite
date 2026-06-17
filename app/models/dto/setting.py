from pydantic import BaseModel


class SettingDTO(BaseModel):
    key: str
    value: str
