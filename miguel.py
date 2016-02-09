#!/usr/bin/env python
import json
import os
from cmd import Cmd
from functools import partial
from time import sleep
from traceback import format_exc

import readline
import click
import requests
from blessings import Terminal
from progressive.bar import Bar
from progressive.tree import ProgressTree, Value, BarDescriptor


# __version__ = "TODO Refactor this so that setup.py can import miguel and
# get version"

MAGDIR = os.path.expanduser("~/.magellan/miguel")
if not os.path.exists(MAGDIR):
    print("Creating directory {}...".format(MAGDIR))
    os.makedirs(MAGDIR)
HISTFILE = os.path.join(MAGDIR, "history")
if not os.path.exists(HISTFILE):
    print("Creating {} file...".format(HISTFILE))
    with open(HISTFILE, "w+") as f:
        f.write("")


class Miguel(Cmd):

    HTTP_VERBS = ["GET", "PUT", "POST", "PATCH", "DELETE"]

    def __init__(self, base_url, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.t = Terminal()
        self.base_url = base_url
        self.base_api_url = os.path.join(self.base_url, "api")
        self._make_commands()
        self.prompt = "{}\n$ ".format(
            self.t.green("magellan_repl@{}".format(base_url))
        )
        readline.read_history_file(HISTFILE)

    def _progress_loop(self, request_method, url, body):
        response = request_method(url, data=json.dumps(body))
        body = response.json()

        max_tasks = body["num_total_tasks"]

        bar = Bar(max_value=max_tasks, title="Completed Tasks",
                  num_rep="percentage", filled_color=2)

        n = ProgressTree(term=self.t)
        n.cursor.clear_lines(self.t.height - 1)

        while True:
            response = request_method(url, data=json.dumps(body))
            body = response.json()

            n.cursor.restore()
            n.cursor.clear_lines(self.t.height - 1)
            n.cursor.save()
            bar.draw(value=body["num_finished_tasks"])

            presp = body
            presp["energy_history"] = sorted(presp["energy_history"])[:10]
            del presp["best_location"]
            print(json.dumps(presp, indent=4))

            if response.status_code == 200:
                return response

            sleep(2.0)

    def _parse_value(self, value):
        transform_map = {
            'True': 'true',
            'False': 'false'
        }
        if value in transform_map:
            value = transform_map[value]

        try:
            return json.loads(value)
        except ValueError:
            pass

        # Handle cases like "2**16"
        if value[0].isdigit() and value[-1].isdigit():
            try:
                return eval(value)
            except (NameError, SyntaxError):
                pass

        return value

    def command(self, verb, line):
        chunks = line.strip().split()
        route = "/".join(chunk for chunk in chunks if "=" not in chunk)
        body = dict(chunk.split("=") for chunk in chunks if "=" in chunk)
        body = {k: self._parse_value(value=v) for k, v in body.items()}
        print(body)
        url = "{}/{}".format(self.base_api_url, route)
        request_method = getattr(requests, verb)
        response = request_method(url, data=json.dumps(body))

        if response.status_code == 202:
            response = self._progress_loop(request_method, url, body)

        print(json.dumps(response.json(), indent=4))

    def _quit(self):
        readline.write_history_file(HISTFILE)

    def do_EOF(self, line):
        self._quit()
        return "Quitting"

    def _make_commands(self):
        def do_command(verb, line):
            return self.command(verb, line)
        for verb in self.HTTP_VERBS:
            verb = verb.lower()
            verb_func = partial(do_command, verb)
            setattr(self, "do_{}".format(verb.lower()), verb_func)

    def precmd(self, line):
        if not line:
            return line
        if line.strip()[0] == "#":
            return ""
        return line


@click.command()
@click.option("-b", "--base-url", type=click.STRING, required=True)
def main(base_url):
    repl = Miguel(base_url)
    while True:
        try:
            repl.cmdloop()
            print("")
            break
        except KeyboardInterrupt:
            print("^C")
        except Exception:
            print(format_exc())


if __name__ == "__main__":
    main()
