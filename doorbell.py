#!/usr/bin/env python3

import os.path, random, requests, signal, subprocess, sys, threading

import mmpy_bot, toml

from mmpy_bot.mattermost_v4 import MattermostAPIv4
from mmpy_bot.mattermost import MattermostAPI

from doorbell import DoorbellBot

_doorbell_bot = None

def main():
    if not os.path.isfile("secrets.toml"):
        print("secrets.toml does not exist. Please create a copy from secrets.example.toml")
        exit(1)

    with open("secrets.toml") as f:
        config = toml.load(f)

    if "proxy" in config:
        request_session = requests.Session()
        request_session.proxies.update(config["proxy"])
        # Replace the requests import in mmpy_bot to use our proxied Session instance.
        mmpy_bot.mattermost_v4.requests = request_session
        mmpy_bot.mattermost.requests = request_session

    client = MattermostAPIv4(config["mattermost"]["server"], ssl_verify=config["mattermost"]["server_ssl"])
    user = client.login(config["mattermost"]["team"], config["mattermost"]["user"], config["mattermost"]["password"])

    _doorbell_bot = DoorbellBot(client, user, config["doorbell"])
    _doorbell_bot.start()


def signal_handler(sig, frame):
    if _doorbell_bot is not None:
        _doorbell_bot.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()