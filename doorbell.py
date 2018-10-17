#!/usr/bin/env python3

import os.path
import random
import requests
import signal
import subprocess
import sys
import threading

import toml

import doorbell
from doorbell import DoorbellBot

_doorbell_bot = None

def main():
    if not os.path.isfile("secrets.toml"):
        print("secrets.toml does not exist. Please create a copy from secrets.example.toml")
        exit(1)

    with open("secrets.toml") as f:
        config = toml.load(f)

    request_session = requests.Session()
    if "proxy" in config:
        print("configuring requests to use proxy")
        request_session.proxies.update(config["proxy"])

    print("Starting doorbell bot")
    _doorbell_bot = DoorbellBot(config, request_session)
    _doorbell_bot.start()


def signal_handler(sig, frame):
    print("stopping doorbell bot")
    if _doorbell_bot is not None:
        _doorbell_bot.stop()
    print("quitting")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
