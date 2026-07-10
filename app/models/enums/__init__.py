from enum import Enum


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"
