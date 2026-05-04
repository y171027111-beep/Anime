import os

BOT_TOKEN  = os.environ.get("8616053081:AAHJ1uIfXsGCzRQzMTXDwPPj5apz3EkqBys", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@anime_uzbekchao")
ADMIN_IDS  = [int(x) for x in os.environ.get("ADMIN_IDS", "8467353523,8348353169").split(",")]
