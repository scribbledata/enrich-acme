import os
import sys
import json
import click

from enrichsdk.commands import log_activity

@click.command('acme.stats')
@log_activity
@click.pass_obj
def _stats(config):
    """
    Show pipeline stats
    """
    path = config.get_file("%(enrich_data)s/_status")

    runs = os.listdir(path)
    summary = {}
    for r in runs:
        fullpath = os.path.join(path, r)
        name = "UNKNOWN"
        nature = ""
        try:
            d = json.load(open(fullpath))
            name = d['name']
            nature = d['nature']
        except:
            pass
        name = "{}:{}".format(name, nature)
        summary[name] = summary.get(name, 0) + 1

    summary = sorted(summary.items(), key=lambda r: r[1], reverse=True)
    for k,v in summary:
        name, nature = k.split(":")
        print("{:10} ({:10}): {}".format(name, nature,v))

entrypoint = _stats
