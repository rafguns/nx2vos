nx2vos
======

nx2vos is a simple Python library that exports [networkx](https://networkx.org) graphs or networks to the [VOSviewer](https://www.vosviewer.com/) format.

## Installation

Install with [`pip`](https://pip.pypa.io/en/stable/):

```
pip install nx2vos
```


## Usage

Using nx2vos, you can write a networkx graph to [VOSviewer map and network files](https://app.vosviewer.com/docs/file-types/map-and-network-file-type/) or to a [VOSviewer JSON file](https://app.vosviewer.com/docs/file-types/json-file-type/).

### Map and network files

Originally, VOSviewer saved data in so-called map and network files:
- A **map file** contains information about the items (i.e., nodes) in a VOSviewer map. Items can be characterized by a number of attributes.
- A **network file** contains information about the links between the items in a map. A network file specifies which pairs of items are connected, as well as the strength of each link.

Typically, you want to save both the map and network file:

```python
import networkx as nx
import nx2vos

# Create example network
G = nx.Graph()
G.add_weighted_edges_from([("a", "b", 1), ("b", "c", 2), ("a", "c", 3)])

# Save map and network files to map.txt and network.txt
nx2vos.write_vos_map(G, "map.txt")
nx2vos.write_vos_network(G, "network.txt")
```

To visualize the result in VOSviewer, click `Create...` in the `File` tab on the left. Choose `Create a map based on network data` and point VOSviewer to your map and network file. In the following screens, you can adjust the map by, for instance, excluding certain nodes or edges. After clicking `Finish`, the resulting map is shown.

### JSON files

More recently, VOSviewer also supports a JSON file format, which contais both data on items and the links between them. In other words, one JSON file can replace both a map and network file.

To save:

```python
import networkx as nx
import nx2vos

# Create example network
G = nx.Graph()
G.add_weighted_edges_from([("a", "b", 1), ("b", "c", 2), ("a", "c", 3)])

# Save graph to JSON
nx2vos.write_vos_json(G, "graph.json")
```

To visualize the result in VOSviewer, click `Create...` in the `File` tab on the left. Choose `Create a map based on network data` and point VOSviewer to your JSON file. In the following screens, you can adjust the map by, for instance, excluding certain nodes or edges. After clicking `Finish`, the resulting map is shown.

VOSviewer JSON files can also store configuration of the visualization, such as color scheme or parameters of the VOS algorithm. This is not currently supported by nx2vos.

### Node attributes

You can instruct nx2vos which attribute on the networkx side corresponds to which attribute on the VOSviewer side. Let's look at an example, building on the previous code snippet:

```python
# Calculate Pagerank and add as node attribute
pr = nx.pagerank(G)
for n, val in pr.items():
    G.nodes[n]["pagerank"] = val

# Add example description to each node. Can include HTML formatting.
for n in G:
    G.nodes[n]["text"] = f"This is node <b>{n}</b>."

# Write to map file, including attribute data:
nx2vos.write_vos_map(
    G, "map2.txt", description_attr="text", weight_attrs=["pagerank"]
)
# Or write to JSON, including attribute data:
nx2vos.write_vos_json(
    G, "graph2.json", description_attr="text", weight_attrs=["pagerank"]
)
```

The description will be shown on hover in VOSviewer. The weight can be used in the visualization to display items with higher weight more prominently.

This table shows all supported VOSviewer attributes:

<table>
  <tr>
    <th>VOSviewer attribute</th>
    <th>Specify with...</th>
    <th>Value (if not <code>None</code>)</th>
  </tr>
  <tr>
    <td><code>sublabel</td>
    <td><code>sublabel_attr</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>description</td>
    <td><code>description_attr</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>url</td>
    <td><code>url_attr</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>x</td>
    <td><code>x_attr</code> (use together with <code>y_attr</code>)</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>y</td>
    <td><code>y_attr</code> (use together with <code>x_attr</code>)</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>cluster</td>
    <td><code>cluster_attr</td>
    <td>string (attribute name)</td>
  </tr>
  <tr>
    <td><code>weight</code> or <code>weights</code></td>
    <td><code>weight_attrs</td>
    <td>list of strings (attribute names)</td>
  </tr>
  <tr>
    <td><code>score</code> or <code>scores</code></td>
    <td><code>score_attrs</td>
    <td>list of strings (attribute names)</td>
  </tr>
</table>