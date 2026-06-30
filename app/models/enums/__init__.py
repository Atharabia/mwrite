from enum import Enum


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"


class Role(str, Enum):
    super_admin = "super_admin"
