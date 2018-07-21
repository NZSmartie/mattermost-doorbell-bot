import random, requests, signal, subprocess, sys, threading


class DoorbellBot(object):
    _doorbell_proc = None
    _doorbell_thread = None
    _user = None
    _running = True

    def __init__(self, client, user, config):
        self.client = client
        self._user = user
        self._config = config


    def start(self):
        self._doorbell_proc = subprocess.Popen(
            [
                'rtl_433',
                '-X', self._config["spec"],  # spec for decoding OOK modulated data from the doorbell button
                '-R', '0'  # disable decoding of all other devices
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        self._running = True

        for line in iter(self._doorbell_proc.stdout.readline, b''):
            print('got line: {0}'.format(line.decode('utf-8')), end='')
            # self.client.create_post(self._user['id'], self._room_id, random.choice(self._door_jokes))

    def stop(self):
        if self._doorbell_proc is None:
            return

        self._doorbell_proc.wait()
