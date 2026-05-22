import json

import networkx as nx

import nx2vos

G = nx.Graph()
G.add_weighted_edges_from([("a", "b", 1), ("b", "c", 2), ("a", "c", 3)])
nx2vos.write_vos_json(G, "graph.json")

with open("graph.json") as fh:
    graph_json = json.load(fh)

assert graph_json == {
    "network": {
        "items": [
            {"id": 1, "label": "a"},
            {"id": 2, "label": "b"},
            {"id": 3, "label": "c"},
        ],
        "links": [
            {"source_id": 1, "target_id": 2, "strength": 1},
            {"source_id": 1, "target_id": 3, "strength": 3},
            {"source_id": 2, "target_id": 3, "strength": 2},
        ],
    }
}
