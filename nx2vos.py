"""nx2vos: export networkx graphs to VOSviewer format

This simple library exposes two functions:
* write_vos_map()
* write_vos_network()
You will typically want to use them both, especailly if you have node-level data.

"""
import csv
import pathlib
from collections.abc import Iterable
from typing import Optional

import networkx as nx

__version__ = "0.1"


def write_vos_map(
    G: nx.Graph, fname: str | pathlib.Path, attrs: Optional[Iterable] = None
):
    if attrs is None:
        attrs = []
    with open(fname, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["id", "label", *attrs])
        for i, n in enumerate(G.nodes(), start=1):
            writer.writerow([i, n] + [G.nodes[n][attr] for attr in attrs])


def write_vos_network(G: nx.Graph, fname: str | pathlib.Path):
    nodes = dict(zip(G.nodes(), range(1, len(G) + 1)))
    with open(fname, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for u, v, d in G.edges(data=True):
            writer.writerow([nodes[u], nodes[v], d["weight"]])
