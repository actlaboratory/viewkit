import os
import sys
import traceback
import viewkit
from windows import *


def handleException(type, exc, tb):
    print("exchandler")
    msg = traceback.format_exception(type, exc, tb)
    if not hasattr(sys, "frozen"):
        print("".join(msg))
    else:
        viewkit.dialog.win("error", "An error has occurred. Contact the developer for further assistance. Details:" + "\n".join(msg[-2:]))
    try:
        f = open("errorLog.txt", "a")
        f.writelines(msg)
        f.close()
    except BaseException:
        pass
    os._exit(1)


sys.excepthook = handleException


user_name_field = viewkit.CustomSettingField(
    "user_name",
    {
        "type": "string",
        "default": "nekochan"
    }
)

user_age_field = viewkit.CustomSettingField(
    "user_age",
    {
        "type": "integer",
        "default": 27
    }
)

ctx = viewkit.ApplicationContext(
    application_name="viewkitExample",
    application_version="0.1.0",
    short_name="vk",
    supported_languages={"ja-JP": "日本語", "en-US": "English"},
    language="ja-JP",
    setting_file_name="settings.json",
    custom_setting_fields=[user_name_field, user_age_field],
)
viewkit.run(ctx, TestWindow)
