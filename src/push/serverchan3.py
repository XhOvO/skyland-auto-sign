import logging
import os
import re
from datetime import date
from typing import Tuple

import requests


def push_serverchan3(all_logs: list[str]):
    # === Server酱³ 推送（可选，通过环境变量控制） ===
    # 在本地或 GitHub Actions 设置：
    #   SC3_SENDKEY: 必填
    #   SC3_UID: 可选（若不设，将自动从 sendkey 中提取）
    sendkey = os.environ.get('SC3_SENDKEY', '').strip()
    if not sendkey:
        return
    uid = os.environ.get('SC3_UID', '').strip() or None
    title = f'森空岛自动签到结果 - {date.today().strftime("%Y-%m-%d")}'

    desp = '\n'.join(all_logs) if all_logs else '今日无可用账号或无输出'

    if uid is None:
        m = re.match(r"^sctp(\d+)t", sendkey)
        if not m:
            logging.error("cannot extract uid from sendkey; please pass uid explicitly")
            return
        uid = m.group(1)

    api = f"https://{uid}.push.ft07.com/send/{sendkey}.send"
    payload = {
        "title": title or "通知",
        "desp": desp or "",
    }
    # if tags:
    #     payload["tags"] = tags
    # if short:
    #     payload["short"] = short

    try:
        r = requests.post(api, json=payload)
        ok = (r.status_code == 200)
        if not ok:
            logging.error(f"serverchan推送失败,http代码{r.status_code},{r.text}")
    except Exception as e:
        logging.error("serverchan推送失败", exc_info=e)
