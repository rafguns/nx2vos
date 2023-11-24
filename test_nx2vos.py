import networkx as nx
import pytest

import nx2vos


# region fixtures
@pytest.fixture()
def G_simple():  # noqa: N802 (Function name should be lowercase)
    G = nx.Graph()
    G.add_weighted_edges_from([("a", "b", 1), ("b", "c", 2), ("a", "c", 3)])

    return G


@pytest.fixture()
def tmp_file(tmp_path):
    return tmp_path / "file.txt"


@pytest.fixture()
def G_with_attrs(G_simple):  # noqa: N802 (Function name should be lowercase)
    G = G_simple.copy()
    for n in G:
        G.nodes[n]["shorttext"] = n * 20
        G.nodes[n]["logntext"] = n * 200

        G.nodes[n]["urllike"] = f"http://x.co/{n}"

        G.nodes[n]["smallint"] = 5
        G.nodes[n]["largeint"] = 50_000

        G.nodes[n]["float"] = 5.0

    return G


# endregion


def test_write_vos_network(tmp_file, G_simple):
    nx2vos.write_vos_network(G_simple, tmp_file)

    with open(tmp_file) as fh:
        contents = list(fh)

    expected = {"1\t2\t1\n", "1\t3\t3\n", "2\t3\t2\n"}
    assert set(contents) == expected


def test_write_vos_map_noattrs(tmp_file, G_simple):
    nx2vos.write_vos_map(G_simple, tmp_file)

    with open(tmp_file) as fh:
        contents = list(fh)

    expected_header = "id\tlabel\n"
    expected = {"1\ta\n", "2\tb\n", "3\tc\n"}
    assert contents[0] == expected_header
    assert set(contents[1:]) == expected


@pytest.mark.parametrize(
    ("vos_attribute", "network_attribute", "expected"),
    [
        (
            "sublabel",
            "shortttext",
            {f"1\ta\t{'a' * 20}\n", f"2\tb\t{'b' * 20}\n", f"3\tc\t{'c' * 20}\n"},
        ),
        (
            "description",
            "longtext",
            {f"1\ta\t{'a' * 200}\n", f"2\tb\t{'b' * 200}\n", f"3\tc\t{'c' * 200}\n"},
        ),
        (
            "url",
            "urllike",
            {"1\ta\thttp://x.co/a\n", "2\tb\thttp://x.co/b\n", "3\tc\thttp://x.co/c\n"},
        ),
        (
            "cluster",
            "shortttext",
            {f"1\ta\t{'a' * 20}\n", f"2\tb\t{'b' * 20}\n", f"3\tc\t{'c' * 20}\n"},
        ),
    ],
)
def test_write_vos_map_attribute(
    tmp_file, G_with_attrs, vos_attribute, network_attribute, expected
):
    kwargs = {f"{vos_attribute}_attr": network_attribute}
    nx2vos.write_vos_map(G_with_attrs, tmp_file, **kwargs)

    with open(tmp_file) as fh:
        contents = list(fh)

    expected_header = f"id\tlabel\t{vos_attribute}\n"
    assert contents[0] == expected_header
    assert set(contents[1:]) == expected


def test_write_vos_map_description(tmp_file, G_with_attrs):
    ...


def test_write_vos_map_xy(tmp_file, G_with_attrs):
    ...


def test_write_vos_map_weights(tmp_file, G_with_attrs):
    ...


def test_write_vos_map_scores(tmp_file, G_with_attrs):
    ...
