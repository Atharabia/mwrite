from enum import Enum


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"


class Role(str, Enum):
    super_admin = "super_admin"
    editor = "editor"
    writer = "writer"


class SettingKey(str, Enum):
    blog_name = "blog_name"
    blog_description = "blog_description"
    blog_author = "blog_author"
    blog_tagline = "blog_tagline"
    footer_text = "footer_text"
    posts_per_page = "posts_per_page"
    allow_indexing = "allow_indexing"
    og_image_id = "og_image_id"
