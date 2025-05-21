# ROBOMCP
=======
##  MCP Client/Server for ROBOKOP

Multi-Component Protocol (MCP) agent for querying some by ROBOKOP endpoints [here](https://robokop-automat.apps.renci.org/) using OpenAI agents-and MCP servers calling our structured tools.

---

## Available Tools


| Tool                                                      | Description                                                                            |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `get_normalized_curie(text)`                              | Converts a biomedical name to a normalized CURIE.                                      |
| `get_current_nodes(curie)`                                | Retrieves detailed node info from ROBOKOP.                                             |
| `get_current_edges(curie, category=None, predicate=None)` | Fetches edges connected to a node, optionally filtered by category/predicate.          |
| `get_edge_summary(curie)`                                 | Returns a summary of all predicates and attached node types + counts for a given node. |



---

## Example Queries

What diseases are treated by Metformin?

Show me nodes related to MONDO:0005148

What types of relationships are connected to NCBIGene:19?

---

## Development Notes
- TOOLS:
    - Currently, tools are :
        - defined in the ```robokop_mcp_server.py``` module using ```@function_tool``` decorators from the openai-agents framework.
        - added to a list of tools that the mcp agent can use in ```main.py```

- MCP SERVER:
    - MCP Servers are started via uvx and handled using MCPServerStdio.

