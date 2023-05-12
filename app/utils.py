import logging
import os
import time
from datetime import datetime

from colorama import Fore, Style

from .globals import PING_HOST

logger = logging.getLogger(__name__)


def time_now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def warn(text: str):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def create_response(
    message: str = "",
    *,
    time_str: str = "",
    sender: str = "",
    receiver: str = "",
    italic: bool = False,
    strong: bool = False,
    color: str = "",
    complete: bool = True,
):
    response = {
        "time_str": time_str,
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "italic": italic,
        "strong": strong,
        "color": color,
        "complete": complete,
    }
    return response


def keep_network_alive(cooldown: int = 55):
    while True:
        _ = os.popen(f"ping {PING_HOST} -c 3").read()
        for i in range(cooldown):
            time.sleep(1)
