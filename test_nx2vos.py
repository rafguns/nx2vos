import re

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
        G.nodes[n]["longtext"] = n * 200

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
    ("attribute_mapping", "expected"),
    [
        (
            {"sublabel": "shorttext"},
            {f"1\ta\t{'a' * 20}\n", f"2\tb\t{'b' * 20}\n", f"3\tc\t{'c' * 20}\n"},
        ),
        (
            {"description": "longtext"},
            {f"1\ta\t{'a' * 200}\n", f"2\tb\t{'b' * 200}\n", f"3\tc\t{'c' * 200}\n"},
        ),
        (
            {"url": "urllike"},
            {"1\ta\thttp://x.co/a\n", "2\tb\thttp://x.co/b\n", "3\tc\thttp://x.co/c\n"},
        ),
        (
            {"x": "smallint", "y": "smallint"},
            {"1\ta\t5\t5\n", "2\tb\t5\t5\n", "3\tc\t5\t5\n"},
        ),
        (
            {"x": "float", "y": "float"},
            {"1\ta\t5.0\t5.0\n", "2\tb\t5.0\t5.0\n", "3\tc\t5.0\t5.0\n"},
        ),
        (
            {"cluster": "smallint"},
            {"1\ta\t1\n", "2\tb\t1\n", "3\tc\t1\n"},
        ),
    ],
)
def test_write_vos_map_attribute(tmp_file, G_with_attrs, attribute_mapping, expected):
    mapping = {f"{k}_attr": v for k, v in attribute_mapping.items()}
    nx2vos.write_vos_map(G_with_attrs, tmp_file, **mapping)

    with open(tmp_file) as fh:
        contents = list(fh)

    vos_attributes = "\t".join(attribute_mapping.keys())
    expected_header = f"id\tlabel\t{vos_attributes}\n"
    assert contents[0] == expected_header
    assert set(contents[1:]) == expected


@pytest.mark.parametrize(
    ("attribute_mapping", "expected_pattern"),
    [
        ({"cluster": "shorttext"}, "[123]\t[abc]\t[123]\n"),
        ({"cluster": "longtext"}, "[123]\t[abc]\t[123]\n"),
    ],
)
def test_write_vos_map_cluster(
    tmp_file, G_with_attrs, attribute_mapping, expected_pattern
):
    mapping = {f"{k}_attr": v for k, v in attribute_mapping.items()}
    nx2vos.write_vos_map(G_with_attrs, tmp_file, **mapping)

    with open(tmp_file) as fh:
        contents = list(fh)

    vos_attributes = "\t".join(attribute_mapping.keys())
    expected_header = f"id\tlabel\t{vos_attributes}\n"
    assert contents[0] == expected_header
    for line in contents[1:]:
        assert re.match(expected_pattern, line) is not None


@pytest.mark.parametrize(
    ("attribute_mapping", "expected_header", "expected_contents"),
    [
        (
            {"weight": ["smallint", "largeint"]},
            "id\tlabel\tweight<smallint>\tweight<largeint>\n",
            {"1\ta\t5\t50000\n", "2\tb\t5\t50000\n", "3\tc\t5\t50000\n"},
        ),
                (
            {"score": ["smallint", "largeint"]},
            "id\tlabel\tscore<smallint>\tscore<largeint>\n",
            {"1\ta\t5\t50000\n", "2\tb\t5\t50000\n", "3\tc\t5\t50000\n"},
        ),
        (
            {"weight": ["smallint"], "score": ["largeint"]},
            "id\tlabel\tweight<smallint>\tscore<largeint>\n",
            {"1\ta\t5\t50000\n", "2\tb\t5\t50000\n", "3\tc\t5\t50000\n"},
        ),
    ],
)
def test_write_vos_map_weights_scores(
    tmp_file, G_with_attrs, attribute_mapping, expected_header, expected_contents
):
    mapping = {f"{k}_attrs": v for k, v in attribute_mapping.items()}
    nx2vos.write_vos_map(G_with_attrs, tmp_file, **mapping)

    with open(tmp_file) as fh:
        contents = list(fh)

    assert contents[0] == expected_header
    assert set(contents[1:]) == expected_contents


def test_nonexisting_attr(G_simple):
    with pytest.raises(nx2vos.Nx2VosError):
        nx2vos.write_vos_map(G_simple, "x", sublabel_attr="foo")
