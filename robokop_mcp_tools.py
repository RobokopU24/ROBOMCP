from agents import function_tool
import httpx
import aiohttp


# ----------- Function tools -----------
@function_tool
async def get_current_edges(curie: str, category: str = None, predicate: str = None) -> dict:
    """Fetch current edges for a given CURIE from the ROBOKOP endpoint.
    Args:
        curie: The CURIE identifier to query.
        category: Optional category filter (e.g., 'biolink:Drug').
        predicate: Optional predicate filter (e.g., 'biolink:treats').

    Returns:
        The JSON response as a Python dictionary.
    """
    base_url = f"https://robokop-automat.apps.renci.org/robokopkg/edges/{curie}"
    query_params = {}
    if category: query_params["category"] = category
    if predicate: query_params["predicate"] = predicate

    url = f"{base_url}?{httpx.QueryParams(query_params)}" if query_params else base_url
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[ERROR] get_current_edeg failed: {e}")
        return {}

@function_tool
async def get_current_nodes(curie: str) -> str:
    """Fetch current node data for a given CURIE from ROBOKOP endpoint.
    Args:
        curie: The CURIE identifier to query.
    """
    url = f"https://robokop-automat.apps.renci.org/robokopkg/node/{curie}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[ERROR] get_current_nodes failed: {e}")
        return {}


@function_tool
async def get_edge_summary(curie: str) -> dict:
    """
    Fetch a summary or kinds of edges connected to a given CURIE from the ROBOKOP endpoint.

    Returns:
        A dictionary with predicates as keys, and lists of [ [node_types], edge_count ] pairs.
    """
    url = f"https://robokop-automat.apps.renci.org/robokopkg/edge_summary/{curie}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[ERROR] get_edge_summary failed: {e}")
        return {}


@function_tool
async def get_normalized_curie(text: str) -> str:
    """Normalize a text string into a standardized CURIE."""
    url = f"https://name-resolution-sri.renci.org/lookup?string={text}&autocomplete=true&highlighting=false&offset=0&limit=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"accept": "application/json"}) as resp:
                data = await resp.json()

        for item in data:
            if item["label"].lower() == text.lower():
                return item["curie"]
    except Exception as e:
        print(f"[ERROR] get_normalized_curie failed: {e}")
    return ""
