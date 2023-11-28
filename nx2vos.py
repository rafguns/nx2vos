"""nx2vos: export networkx graphs to VOSviewer format

This simple library exposes two functions:
* write_vos_map()
* write_vos_network()
You will typically want to use them both, especailly if you have node-level data.

"""
import csv
import pathlib

import networkx as nx

__version__ = "0.1"


class Nx2VosError(ValueError):
    pass


def _to_inc_number(node_vals):
    unique_vals = {val for _, val in node_vals}
    vals2number = dict(zip(unique_vals, range(1, len(unique_vals) + 1), strict=True))
    return [(n, vals2number[v]) for n, v in node_vals]


def _prepare_attrs(
    G: nx.Graph,
    sublabel_attr: str | None = None,
    description_attr: str | None = None,
    url_attr: str | None = None,
    x_attr: str | None = None,
    y_attr: str | None = None,
    cluster_attr: str | None = None,
    weight_attrs: list[str] | None = None,
    score_attrs: list[str] | None = None,
):
    attrs = []

    # weight and score are complex, so we first transform these so we can handle them
    # the same as, e.g., cluster.
    weights_scores = []
    for attrlist, keyword in [
        (weight_attrs, "weight"),
        (score_attrs, "score"),
    ]:
        if not attrlist:
            continue
        for attr in attrlist:
            weights_scores.append((attr, f"{keyword}<{attr}>", None))

    for nx_attr, vos_attr, validate_transform in [
        (sublabel_attr, "sublabel", None),
        (description_attr, "description", None),
        (url_attr, "url", None),
        (x_attr, "x", None),
        (y_attr, "y", None),
        (cluster_attr, "cluster", _to_inc_number),
        *weights_scores,
    ]:
        if not nx_attr:
            continue

        node_vals = G.nodes(data=nx_attr)
        if any(val is None for _, val in node_vals):
            err = f"Attribute '{nx_attr}' not defined for all nodes"
            raise Nx2VosError(err)

        to_write = validate_transform(node_vals) if validate_transform else node_vals
        for n, val_to_write in to_write:
            G.nodes[n][vos_attr] = val_to_write
        attrs.append(vos_attr)

    return G, attrs


def write_vos_map(
    G: nx.Graph,
    fname: str | pathlib.Path,
    *,
    sublabel_attr: str | None = None,
    description_attr: str | None = None,
    url_attr: str | None = None,
    x_attr: str | None = None,
    y_attr: str | None = None,
    cluster_attr: str | None = None,
    weight_attrs: list[str] | None = None,
    score_attrs: list[str] | None = None,
):
    # Transform attributes to VOSviewer format
    G, attrs = _prepare_attrs(
        G,
        sublabel_attr,
        description_attr,
        url_attr,
        x_attr,
        y_attr,
        cluster_attr,
        weight_attrs,
        score_attrs,
    )
    # Write to file
    with open(fname, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["id", "label", *attrs])
        for i, n in enumerate(G.nodes(), start=1):
            writer.writerow([i, n] + [G.nodes[n][attr] for attr in attrs])


def write_vos_network(G: nx.Graph, fname: str | pathlib.Path):
    nodes = dict(zip(G.nodes(), range(1, len(G) + 1), strict=True))
    with open(fname, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for u, v, d in G.edges(data=True):
            writer.writerow([nodes[u], nodes[v], d["weight"]])
