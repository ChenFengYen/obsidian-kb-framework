"""
Note link graph analysis for obsidian-kb-framework.

Parses [[wikilinks]] across all vault notes and builds a directed graph.
Provides cluster detection, bridge identification, and gap analysis
to support /review-vault and /suggest-next skills.

Usage:
    python note_graph.py                  # Full report
    python note_graph.py --clusters       # Show connected clusters
    python note_graph.py --bridges        # Show bridge concepts (high betweenness)
    python note_graph.py --orphans        # Show isolated notes (no in/out links)
    python note_graph.py --top 20         # Limit output to top N items
    python note_graph.py --json           # Output as JSON (for programmatic use)
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

try:
    from config import VAULT_ROOT, DOMAIN_FOLDERS
except ImportError:
    VAULT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    DOMAIN_FOLDERS = {}

# ── Graph construction ────────────────────────────────────────

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]+?)?\]\]")


def _find_all_notes():
    """Find all .md files in */Note/ and */Map/ directories."""
    notes = {}  # stem -> full path
    for folder_path in DOMAIN_FOLDERS.values():
        for subdir in ("Note", "Map"):
            dirpath = os.path.join(folder_path, subdir)
            if not os.path.isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
                if fname.endswith(".md"):
                    stem = fname[:-3]
                    notes[stem] = os.path.join(dirpath, fname)
    return notes


def _extract_links(filepath):
    """Extract all [[target]] links from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []
    return list(set(WIKILINK_RE.findall(content)))


def build_graph(notes):
    """Build directed graph: {source_stem: [target_stems]}."""
    graph = defaultdict(set)      # outgoing
    in_graph = defaultdict(set)   # incoming
    all_stems = set(notes.keys())

    for stem, path in notes.items():
        targets = _extract_links(path)
        for t in targets:
            if t in all_stems and t != stem:
                graph[stem].add(t)
                in_graph[t].add(stem)

    return graph, in_graph, all_stems


# ── Analysis functions ────────────────────────────────────────

def find_orphans(graph, in_graph, all_stems):
    """Notes with no incoming AND no outgoing links."""
    orphans = []
    for stem in all_stems:
        if not graph.get(stem) and not in_graph.get(stem):
            orphans.append(stem)
    return sorted(orphans)


def find_hubs(graph, in_graph, all_stems, top_n=20):
    """Notes with highest combined degree (in + out)."""
    degrees = []
    for stem in all_stems:
        out_deg = len(graph.get(stem, set()))
        in_deg = len(in_graph.get(stem, set()))
        degrees.append((stem, in_deg + out_deg, in_deg, out_deg))
    degrees.sort(key=lambda x: x[1], reverse=True)
    return degrees[:top_n]


def find_clusters(graph, in_graph, all_stems):
    """Find connected components using BFS on undirected version."""
    visited = set()
    clusters = []

    # Build undirected adjacency
    adj = defaultdict(set)
    for s, targets in graph.items():
        for t in targets:
            adj[s].add(t)
            adj[t].add(s)

    for stem in sorted(all_stems):
        if stem in visited:
            continue
        # BFS
        cluster = []
        queue = [stem]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            cluster.append(node)
            for neighbor in adj.get(node, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        clusters.append(sorted(cluster))

    # Sort by size descending
    clusters.sort(key=len, reverse=True)
    return clusters


def find_bridges(graph, in_graph, all_stems, top_n=20):
    """Approximate betweenness centrality to find bridge concepts.

    Uses a simplified BFS-based approach (not full Brandes algorithm)
    to identify notes that connect otherwise separate clusters.
    Samples up to 100 source nodes for performance.
    """
    # Build undirected adjacency
    adj = defaultdict(set)
    for s, targets in graph.items():
        for t in targets:
            adj[s].add(t)
            adj[t].add(s)

    betweenness = defaultdict(float)
    nodes = sorted(all_stems)

    # Sample for performance
    import random
    sample = nodes if len(nodes) <= 100 else random.sample(nodes, 100)

    for source in sample:
        # BFS shortest paths
        dist = {source: 0}
        paths = defaultdict(int)
        paths[source] = 1
        queue = [source]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adj.get(node, set()):
                if neighbor not in dist:
                    dist[neighbor] = dist[node] + 1
                    queue.append(neighbor)
                if dist.get(neighbor) == dist[node] + 1:
                    paths[neighbor] += paths[node]

        # Accumulate betweenness (reverse BFS order)
        delta = defaultdict(float)
        for node in reversed(order):
            for neighbor in adj.get(node, set()):
                if dist.get(neighbor, -1) == dist[node] - 1:
                    delta[neighbor] += (paths[neighbor] / max(paths[node], 1)) * (1 + delta[node])
            if node != source:
                betweenness[node] += delta[node]

    # Normalize
    n = len(nodes)
    if n > 2:
        norm = 2.0 / ((n - 1) * (n - 2))
        for k in betweenness:
            betweenness[k] *= norm

    result = [(stem, betweenness.get(stem, 0)) for stem in all_stems]
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:top_n]


def cross_domain_gaps(graph, notes):
    """Identify domains that have few cross-links to other domains."""
    # Determine domain for each note
    note_domain = {}
    for stem, path in notes.items():
        for folder_name in DOMAIN_FOLDERS:
            if folder_name in path:
                note_domain[stem] = folder_name
                break

    # Count cross-domain links
    domain_links = defaultdict(lambda: defaultdict(int))
    for src, targets in graph.items():
        src_d = note_domain.get(src, "unknown")
        for tgt in targets:
            tgt_d = note_domain.get(tgt, "unknown")
            if src_d != tgt_d:
                domain_links[src_d][tgt_d] += 1

    return dict(domain_links)


# ── Report generation ─────────────────────────────────────────

def generate_report(notes, top_n=20):
    """Generate full analysis report."""
    graph, in_graph, all_stems = build_graph(notes)

    total_notes = len(all_stems)
    total_links = sum(len(targets) for targets in graph.values())
    orphans = find_orphans(graph, in_graph, all_stems)
    hubs = find_hubs(graph, in_graph, all_stems, top_n)
    clusters = find_clusters(graph, in_graph, all_stems)
    bridges = find_bridges(graph, in_graph, all_stems, top_n)
    domain_gaps = cross_domain_gaps(graph, notes)

    lines = [
        "# Note Graph Analysis Report",
        "",
        f"**Total notes**: {total_notes}",
        f"**Total links**: {total_links}",
        f"**Orphan notes** (no links at all): {len(orphans)}",
        f"**Connected clusters**: {len(clusters)}",
        f"**Avg links per note**: {total_links / max(total_notes, 1):.1f}",
        "",
    ]

    # Clusters
    lines.append("## Clusters")
    for i, c in enumerate(clusters[:10]):
        lines.append(f"- **Cluster {i+1}** ({len(c)} notes): {', '.join(c[:8])}{'...' if len(c) > 8 else ''}")
    if len(clusters) > 10:
        lines.append(f"- ... and {len(clusters) - 10} smaller clusters")
    lines.append("")

    # Hubs
    lines.append("## Top Hubs (most connected)")
    lines.append("| Note | Total | In | Out |")
    lines.append("|:--|:--|:--|:--|")
    for stem, total, in_d, out_d in hubs:
        lines.append(f"| [[{stem}]] | {total} | {in_d} | {out_d} |")
    lines.append("")

    # Bridges
    lines.append("## Bridge Concepts (connecting clusters)")
    lines.append("| Note | Betweenness |")
    lines.append("|:--|:--|")
    for stem, score in bridges:
        if score > 0:
            lines.append(f"| [[{stem}]] | {score:.4f} |")
    lines.append("")

    # Cross-domain
    if domain_gaps:
        lines.append("## Cross-Domain Links")
        for src_d, targets in sorted(domain_gaps.items()):
            tgt_str = ", ".join(f"{d}({n})" for d, n in sorted(targets.items(), key=lambda x: -x[1]))
            lines.append(f"- **{src_d}** → {tgt_str}")
        lines.append("")

    # Orphans
    if orphans:
        lines.append("## Orphan Notes (no links)")
        for o in orphans[:30]:
            lines.append(f"- [[{o}]]")
        if len(orphans) > 30:
            lines.append(f"- ... and {len(orphans) - 30} more")

    return "\n".join(lines)


def generate_json(notes, top_n=20):
    """Generate analysis as JSON dict."""
    graph, in_graph, all_stems = build_graph(notes)
    return {
        "total_notes": len(all_stems),
        "total_links": sum(len(t) for t in graph.values()),
        "orphans": find_orphans(graph, in_graph, all_stems),
        "hubs": [{"note": s, "total": t, "in": i, "out": o} for s, t, i, o in find_hubs(graph, in_graph, all_stems, top_n)],
        "clusters": find_clusters(graph, in_graph, all_stems),
        "bridges": [{"note": s, "betweenness": round(b, 4)} for s, b in find_bridges(graph, in_graph, all_stems, top_n) if b > 0],
        "cross_domain": cross_domain_gaps(graph, notes),
    }


# ── CLI ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyze note link graph")
    parser.add_argument("--clusters", action="store_true", help="Show connected clusters")
    parser.add_argument("--bridges", action="store_true", help="Show bridge concepts")
    parser.add_argument("--orphans", action="store_true", help="Show orphan notes")
    parser.add_argument("--top", type=int, default=20, help="Limit output (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    notes = _find_all_notes()
    if not notes:
        print("No notes found. Check `domains` in vault_config.yaml.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(generate_json(notes, args.top), ensure_ascii=False, indent=2))
        return

    graph, in_graph, all_stems = build_graph(notes)

    if args.clusters:
        clusters = find_clusters(graph, in_graph, all_stems)
        for i, c in enumerate(clusters):
            print(f"Cluster {i+1} ({len(c)} notes): {', '.join(c[:10])}{'...' if len(c) > 10 else ''}")
    elif args.bridges:
        bridges = find_bridges(graph, in_graph, all_stems, args.top)
        for stem, score in bridges:
            if score > 0:
                print(f"{stem}: {score:.4f}")
    elif args.orphans:
        for o in find_orphans(graph, in_graph, all_stems):
            print(o)
    else:
        # Full report
        report = generate_report(notes, args.top)
        report_path = os.path.join(VAULT_ROOT, "Papers", "scripts", "note_graph_report.md")
        try:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report saved to: {report_path}")
        except OSError:
            print(report)


if __name__ == "__main__":
    main()
