#!/usr/bin/python3
import os

import jinja2
import logging

templ = """\"\"\"
This is the Vega gRPC API client.

Code generated by `generate_init.py`. DO NOT EDIT.
\"\"\"

from . import (
    api,
    checkpoint,
    commands,
    events,
    data,
    snapshot,
    wallet,
{%- for i in imports %}
    {{ i }},
{%- endfor %}
)

__all__ = [
    "api",
    "checkpoint",
    "commands",
    "events",
    "data",
    "snapshot",
    "tm",
    "wallet",
{%- for a in all_list %}
    "{{ a }}",
{%- endfor %}
]
"""


def main():
    p = "vega_protos/protos/vega"
    exclude_pb2 = []
    pb2_files = sorted(
        f[:-7]
        for f in os.listdir(p)
        if os.path.isfile(os.path.join(p, f))
        and f.endswith("_pb2.py")
        and f not in exclude_pb2
    )
    exclude_pb2_grpc = []
    pb2_grpc_files = sorted(
        f[:-12]
        for f in os.listdir(p)
        if os.path.isfile(os.path.join(p, f))
        and f.endswith("_pb2_grpc.py")
        and f not in exclude_pb2_grpc
    )
    imports = sorted(
        [f"{f}_pb2 as {f}" for f in pb2_files]
        + [f"{f}_pb2_grpc as {f}_grpc" for f in pb2_grpc_files]
    )
    all_list = sorted(pb2_files + [f"{f}_grpc" for f in pb2_grpc_files])
    print(jinja2.Template(templ).render({"imports": imports, "all_list": all_list}))


if __name__ == "__main__":
    main()
