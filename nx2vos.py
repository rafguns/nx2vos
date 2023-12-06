"""nx2vos: export networkx graphs to VOSviewer format

This simple library exposes two functions:
* write_vos_map()
* write_vos_network()
You will typically want to use them both, especailly if you have node-level data.

"""
import csv
import json
import pathlib

import networkx as nx

__version__ = "0.1"


class Nx2VosError(ValueError):
    pass


def _to_inc_number(node_vals):
    unique_vals = {val for _, val in node_vals}
    vals2number = dict(zip(unique_vals, range(1, len(unique_vals) + 1), strict=True))
    return [(n, vals2number[v]) for n, v in node_vals]


def _is_numeric(val):
    return isinstance(val, int | float)


def _transform_weight_score(attr_dict):
    tmp = {}
    for keyword in ["weight", "score"]:
        for attr in attr_dict.pop(keyword, []):
            tmp[f"{keyword}<{attr}>"] = attr
    return {**attr_dict, **tmp}


def _prepare_attrs(G: nx.Graph, attr_dict: dict[str, str | None]):
    attrs = []

    # Leave out all unspecified attributes (None or empty iterable)
    attr_dict = {k: v for k, v in attr_dict.items() if v}
    # Transform weight and score so we can handle them the same as other attributes.
    attr_dict = _transform_weight_score(attr_dict)

    # Check: x and y need to occur together
    if len(attr_dict.keys() & {"x", "y"}) == 1:
        err = "Attributes 'x' and 'y' cannot occur separately"
        raise Nx2VosError(err)

    for vos_attr, nx_attr in attr_dict.items():
        node_vals = G.nodes(data=nx_attr)

        # Check 1: attribute needs to be defined for every node
        if any(val is None for _, val in node_vals):
            err = f"Attribute '{nx_attr}' not defined for all nodes"
            raise Nx2VosError(err)
        # Check 2: numeric values where applicable
        if (
            vos_attr in {"x", "y"} or vos_attr.startswith(("weight", "score"))
        ) and not all(_is_numeric(val) for _, val in node_vals):
            err = f"Attribute '{vos_attr}' requires numeric values"
            raise Nx2VosError(err)
        # Transform: transform cluster names to incrementing numbers
        if vos_attr == "cluster":
            node_vals = _to_inc_number(node_vals)
            # Check 3: no more than 1000 clusters
            if any(val > 1000 for _, val in node_vals):  # noqa: PLR2004
                err = "VOSviewer does not support more than 1000 clusters"
                raise Nx2VosError(err)

        for n, val_to_write in node_vals:
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
        {
            "sublabel": sublabel_attr,
            "description": description_attr,
            "url": url_attr,
            "x": x_attr,
            "y": y_attr,
            "cluster": cluster_attr,
            "weight": weight_attrs,
            "score": score_attrs,
        },
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
        for u, v, weight in G.edges(data="weight"):
            row = (
                (nodes[u], nodes[v]) if weight is None else (nodes[u], nodes[v], weight)
            )
            writer.writerow(row)


def output_vos_json(
    G: nx.Graph,
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
        {
            "sublabel": sublabel_attr,
            "description": description_attr,
            "url": url_attr,
            "x": x_attr,
            "y": y_attr,
            "cluster": cluster_attr,
            "weight": weight_attrs,
            "score": score_attrs,
        },
    )

    data = {"network": {"items": [], "links": []}}
    for i, n in enumerate(G.nodes(), start=1):
        # TODO fix weights and scores
        data["network"]["items"].append(
            {"id": i, "label": n, **{attr: G.nodes[n][attr] for attr in attrs}}
        )

    nodes = dict(zip(G.nodes(), range(1, len(G) + 1), strict=True))
    for u, v, d in G.edges(data=True):
        data["network"]["links"].append(
            {"source_id": nodes[u], "target_id": nodes[v], "strength": d["weight"]}
        )


def write_vos_json(
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
    data = output_vos_json(
        G,
        sublabel_attr=sublabel_attr,
        description_attr=description_attr,
        url_attr=url_attr,
        x_attr=x_attr,
        y_attr=y_attr,
        cluster_attr=cluster_attr,
        weight_attrs=weight_attrs,
        score_attrs=score_attrs,
    )
    with open(fname, "w") as fh:
        json.dump(data, fh)
