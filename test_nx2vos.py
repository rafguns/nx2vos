import networkx as nx
import pytest

import nx2vos


@pytest.fixture()
def simple_network():
    G = nx.Graph()
    G.add_weighted_edges_from(
        [("a", "b", 1), ("b", "c", 2), ("a", "c", 3)]
    )
    # assign each node to cluster 1 or 2
    for i, n in enumerate(G.nodes()):
        G.nodes[n]["cluster"] = int(i % 2 == 0) + 1

    return G

def test_write_vos_network(tmp_path, simple_network):
    fname = tmp_path / "network.txt"
    nx2vos.write_vos_network(simple_network, fname)

    with open(fname) as fh:
        contents = list(fh)

    expected = {"1\t2\t1\n", "1\t3\t3\n", "2\t3\t2\n"}
    assert set(contents) == expected


def test_write_vos_map(tmp_path, simple_network):
    fname = tmp_path / "map.txt"
    nx2vos.write_vos_map(simple_network, fname, attrs=["cluster"])

    with open(fname) as fh:
        contents = list(fh)

    expected_header = "id\tlabel\tcluster\n"
    expected = {"1\ta\t2\n", "2\tb\t1\n", "3\tc\t2\n"}
    assert contents[0] == expected_header
    assert set(contents[1:]) == expected
