import csv
import pathlib
from collections.abc import Iterable

import networkx as nx


def write_vos_map(
    G: nx.Graph, fname: str | pathlib.Path, attrs: Iterable | None = None
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
