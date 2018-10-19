import binascii
import random
import signal
import subprocess
import sys
import threading

from datetime import datetime, timedelta

import jmespath
import requests


class DoorbellBot(object):
    def __init__(self, config, requests_session=None):
        self.config = config

        self.doorbell_proc = None
        self.requests = requests.Session() if requests_session is None else requests_session


    def start(self):
        self.doorbell_proc = subprocess.Popen(
            [
                'rtl_433',
                '-X', self.config["doorbell"]["spec"],  # spec for decoding OOK modulated data from the doorbell button
                '-R', '0'  # disable decoding of all other devices
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        print("rtl_433 started with PID: {}".format(self.doorbell_proc.pid))

        things = binascii.hexlify(bytes(self.config["doorbell"]["payload"]))
        needle = b"{%d}%s" % (self.config["doorbell"]["payload_length"], things)

        print("needle is {}".format(needle))

        doorbell_next = datetime.now()

        for line in iter(self.doorbell_proc.stdout.readline, b''):
            if needle in line and doorbell_next < datetime.now():
                doorbell_next = datetime.now() + timedelta(seconds=5)
                print("Received doorbell signal at {}".format(datetime.now()))

                sourceName = random.choice([source for source in self.config["facts"]])
                source = self.config["facts"][sourceName]

                print("Fetching message")
                try:
                    joke = self.requests.get(source['url'], timeout=1)
                    joke = "{}{}".format(source['prefix'], jmespath.search(source['jmespath'], joke.json()))
                except:
                    print("Failed to fetch message. Using backup")
                    joke = random.choice(self.config["messages"])

                print(joke)
                try:
                    self.requests.post(self.config["mattermost"]["webhook"],
                        timeout=1,
                        json={
                            "username": "Doorbell",
                            "text": joke
                        })
                except Exception as ex:
                    print("Failed to post message")
                    print(ex)


    def stop(self):
        if self.doorbell_proc is None:
            return

        self.doorbell_proc.wait()
