#!/usr/bin/env python
import json
class FakeConnection:
    def __init__(self):
        self.command_list = []

    def command(self, command, result=None):
        if result is None:
            result = [{'success': True}]

        self.command_list.append(command)
        return result

    def clear(self):
        self.command_list = []

    def get_outputs(self):
        with open('tests/setup.json') as f:
            data = json.loads(f.read())

        return data
