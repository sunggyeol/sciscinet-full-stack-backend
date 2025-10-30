import networkx as nx
from src.database import get_db


async def compute_citation_network():
    """
    Build citation network for papers (2020-2022).
    Filter to nodes with citation_count > 5 OR in_degree > 1.
    """
    db = await get_db()

    # Get papers from 2020-2022
    papers_cursor = await db.execute(
        "SELECT paper_id, title, citation_count FROM papers WHERE year >= 2020 AND year <= 2022"
    )
    papers = await papers_cursor.fetchall()

    # Get citation links
    links_cursor = await db.execute(
        """
        SELECT pr.paper_id, pr.reference_id
        FROM paper_references pr
        JOIN papers p1 ON pr.paper_id = p1.paper_id
        JOIN papers p2 ON pr.reference_id = p2.paper_id
        WHERE p1.year >= 2020 AND p1.year <= 2022
        AND p2.year >= 2020 AND p2.year <= 2022
        """
    )
    links = await links_cursor.fetchall()

    await db.close()

    # Build directed graph
    G = nx.DiGraph()

    # Add nodes with attributes
    paper_map = {}
    for paper in papers:
        paper_id = paper["paper_id"]
        paper_map[paper_id] = {
            "id": paper_id,
            "title": paper["title"],
            "citation_count": paper["citation_count"] or 0,
        }
        G.add_node(paper_id, **paper_map[paper_id])

    # Add edges
    for link in links:
        if link["paper_id"] in G and link["reference_id"] in G:
            G.add_edge(link["paper_id"], link["reference_id"])

    # Filter: keep nodes with citation_count > 5 OR in_degree > 1
    filtered_nodes = set()
    for node in G.nodes():
        citation_count = G.nodes[node].get("citation_count", 0)
        in_degree = G.in_degree(node)
        if citation_count > 5 or in_degree > 1:
            filtered_nodes.add(node)

    # Create subgraph
    G_filtered = G.subgraph(filtered_nodes)

    # Run community detection on filtered graph
    G_undirected = G_filtered.to_undirected()
    communities = nx.algorithms.community.louvain_communities(G_undirected)
    
    # Create node to community mapping
    node_to_community = {}
    for community_id, community in enumerate(communities):
        for node in community:
            node_to_community[node] = community_id
    
    # Convert to JSON format
    nodes = [
        {
            "id": node,
            "title": G_filtered.nodes[node]["title"],
            "citation_count": G_filtered.nodes[node]["citation_count"],
            "community": node_to_community.get(node, 0),
        }
        for node in G_filtered.nodes()
    ]

    links_out = [
        {"source": u, "target": v}
        for u, v in G_filtered.edges()
    ]

    return {
        "nodes": nodes, 
        "links": links_out,
        "communities": len(communities)
    }


async def compute_collaboration_network():
    """
    Build collaboration network for papers (2020-2022).
    Filter to nodes with degree > 2.
    """
    db = await get_db()

    # Get paper-author affiliations for 2020-2022 papers
    cursor = await db.execute(
        """
        SELECT paa.author_id, paa.paper_id
        FROM paper_author_affiliations paa
        JOIN papers p ON paa.paper_id = p.paper_id
        WHERE p.year >= 2020 AND p.year <= 2022
        """
    )
    affiliations = await cursor.fetchall()

    await db.close()

    # Build undirected graph
    G = nx.Graph()

    # Group authors by paper
    papers_authors = {}
    for aff in affiliations:
        paper_id = aff["paper_id"]
        author_id = aff["author_id"]
        if paper_id not in papers_authors:
            papers_authors[paper_id] = []
        papers_authors[paper_id].append(author_id)

    # Add edges between co-authors
    for paper_id, authors in papers_authors.items():
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                if G.has_edge(author1, author2):
                    G[author1][author2]["weight"] += 1
                else:
                    G.add_edge(author1, author2, weight=1)

    # Filter: keep nodes with degree > 2
    filtered_nodes = {node for node in G.nodes() if G.degree(node) > 2}
    G_filtered = G.subgraph(filtered_nodes)

    # Run community detection on filtered graph
    communities = nx.algorithms.community.louvain_communities(G_filtered)
    
    # Create node to community mapping
    node_to_community = {}
    for community_id, community in enumerate(communities):
        for node in community:
            node_to_community[node] = community_id

    # Convert to JSON format
    nodes = [
        {
            "id": node,
            "community": node_to_community.get(node, 0)
        } 
        for node in G_filtered.nodes()
    ]

    links_out = [
        {"source": u, "target": v, "weight": G_filtered[u][v]["weight"]}
        for u, v in G_filtered.edges()
    ]

    return {
        "nodes": nodes, 
        "links": links_out,
        "communities": len(communities)
    }


async def compute_community_network():
    """
    Run Louvain community detection on full citation graph.
    Return hierarchical JSON for D3.js.
    """
    db = await get_db()

    # Get papers from 2020-2022
    papers_cursor = await db.execute(
        "SELECT paper_id, title FROM papers WHERE year >= 2020 AND year <= 2022"
    )
    papers = await papers_cursor.fetchall()

    # Get citation links
    links_cursor = await db.execute(
        """
        SELECT pr.paper_id, pr.reference_id
        FROM paper_references pr
        JOIN papers p1 ON pr.paper_id = p1.paper_id
        JOIN papers p2 ON pr.reference_id = p2.paper_id
        WHERE p1.year >= 2020 AND p1.year <= 2022
        AND p2.year >= 2020 AND p2.year <= 2022
        """
    )
    links = await links_cursor.fetchall()

    await db.close()

    # Build directed graph (convert to undirected for community detection)
    G = nx.DiGraph()

    paper_map = {}
    for paper in papers:
        paper_id = paper["paper_id"]
        paper_map[paper_id] = paper["title"]
        G.add_node(paper_id)

    for link in links:
        if link["paper_id"] in G and link["reference_id"] in G:
            G.add_edge(link["paper_id"], link["reference_id"])

    # Convert to undirected for community detection
    G_undirected = G.to_undirected()

    # Run Louvain community detection
    communities = nx.algorithms.community.louvain_communities(G_undirected)

    # Build hierarchical structure
    children = []
    for i, community in enumerate(communities):
        community_children = [
            {"name": paper_map.get(node, str(node)), "value": 1}
            for node in list(community)[:50]  # Limit to 50 nodes per community
        ]
        children.append({
            "name": f"Community {i+1}",
            "children": community_children
        })

    return {
        "name": "root",
        "children": children
    }


async def compute_papers_by_year():
    """
    Count papers by year (2015-2022).
    """
    db = await get_db()

    cursor = await db.execute(
        """
        SELECT year, COUNT(paper_id) as count
        FROM papers
        WHERE year >= 2015 AND year <= 2022
        GROUP BY year
        ORDER BY year
        """
    )
    rows = await cursor.fetchall()

    await db.close()

    return [{"year": row["year"], "count": row["count"]} for row in rows]


async def compute_patents_for_year(year: int):
    """
    Get patent counts for specific year.
    """
    db = await get_db()

    cursor = await db.execute(
        "SELECT patent_count FROM papers WHERE year = ? AND patent_count IS NOT NULL",
        (year,)
    )
    rows = await cursor.fetchall()

    await db.close()

    return [row["patent_count"] for row in rows]
