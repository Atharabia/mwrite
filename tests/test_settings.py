import pytest


@pytest.mark.asyncio
async def test_setting_controller_set_and_get():
    from app.controller.setting import SettingController
    await SettingController.set(key="blog_name", value="My Blog")
    result = await SettingController.get(key="blog_name")
    assert result == "My Blog"
