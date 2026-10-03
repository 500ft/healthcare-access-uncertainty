# Graph Report - .  (2026-08-10)

## Corpus Check
- Corpus is ~7,214 words - fits in a single context window. You may not need a graph.

## Summary
- 77 nodes · 90 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Technical Design and Validation|Technical Design and Validation]]
- [[_COMMUNITY_Visual Method Pipeline|Visual Method Pipeline]]
- [[_COMMUNITY_Concept and Claim Boundaries|Concept and Claim Boundaries]]
- [[_COMMUNITY_Imagery and Results Workflow|Imagery and Results Workflow]]
- [[_COMMUNITY_Result Figure Semantics|Result Figure Semantics]]
- [[_COMMUNITY_Repository Documentation Policy|Repository Documentation Policy]]
- [[_COMMUNITY_Figure Composition Utility|Figure Composition Utility]]
- [[_COMMUNITY_Passability Reference Vehicle|Passability Reference Vehicle]]

## God Nodes (most connected - your core abstractions)
1. `Desire Lines Method` - 8 edges
2. `Temporal Activity Classification` - 7 edges
3. `Probabilistic Activity Classification` - 7 edges
4. `Season-Matched NDVI Change Analysis` - 6 edges
5. `Node-Seeded Branch Tracing` - 6 edges
6. `Desire Lines — Method Overview` - 6 edges
7. `Corridor Grouping` - 5 edges
8. `NDVI-change result` - 5 edges
9. `Desire Lines Technical Design` - 4 edges
10. `Branch Detection` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Desire Lines Method` --references--> `Desire Lines Technical Design`  [EXTRACTED]
  README.md → docs/design.md
- `NDVI Change Figure` --conceptually_related_to--> `Season-Matched NDVI Change Analysis`  [INFERRED]
  results/README.md → README.md
- `Desire Lines Technical Design` --references--> `Catan Roads Project`  [EXTRACTED]
  docs/design.md → README.md
- `Catan Roads Project` --references--> `Results Figure Workflow`  [EXTRACTED]
  README.md → results/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Desire Lines Processing Pipeline** — readme_node_seeded_search, readme_unmapped_branch_detection, readme_trail_tracing, readme_braided_corridor_modeling, readme_temporal_activity_classification [EXTRACTED 1.00]
- **Multi-Year Activity Evidence System** — docs_design_activity_feature_vector, docs_design_activity_index, docs_design_probabilistic_activity_classification, docs_design_ground_truth_labels [EXTRACTED 1.00]
- **Desire Lines Classification Pipeline** — assets_method_seed_nodes, assets_method_search_region, assets_method_branch_detection, assets_method_trail_tracing, assets_method_corridor_grouping, assets_method_activity_over_time [EXTRACTED 1.00]
- **NDVI-change figure generation workflow** — results_ndvi_change_ndvi_change_analysis_script, results_ndvi_change_google_earth_engine, results_ndvi_change_figure_composition_script, results_ndvi_change_ndvi_change_result [EXTRACTED 1.00]

## Communities (9 total, 1 thin omitted)

### Community 0 - "Technical Design and Validation"
Cohesion: 0.14
Nodes (17): Four-Stage Ablation Experiment, Multi-Year Activity Feature Vector, Segment Activity Index, Adaptive Seed Search Radius, Braided Route Corridor, Branch Evidence Score, Graph-Growth Trail Following, Independent Ground-Truth Labels (+9 more)

### Community 1 - "Visual Method Pipeline"
Cohesion: 0.19
Nodes (15): Active vs. Abandoned, Activity Over Time, Braided Tracks, Branch Detection, Corridor Grouping, Desire Lines — Method Overview, Graph Growth, Mapped Intersections (+7 more)

### Community 2 - "Concept and Claim Boundaries"
Cohesion: 0.25
Nodes (11): Braided-Corridor Modeling, Evidence of Change in Use, Desire Lines Method, Informal Route Corridors, Surrounding Control-Area Comparison, Node-Seeded Search, Season and Sensor Matching, Temporal Activity Classification (+3 more)

### Community 3 - "Imagery and Results Workflow"
Cohesion: 0.20
Nodes (11): Google Earth Engine, Season-Matched NDVI Change Analysis, OpenStreetMap, QGIS, Copernicus Sentinel-2, Figure Composition Workflow, Copernicus Attribution Requirement, Earth Engine NDVI Export (+3 more)

### Community 4 - "Result Figure Semantics"
Cohesion: 0.33
Nodes (7): Abandonment, Active use, Exported figure placeholder, tools/compose_figure.py, Google Earth Engine, gee/ndvi_change.js, NDVI-change result

### Community 5 - "Repository Documentation Policy"
Cohesion: 0.33
Nodes (6): Desire Lines Technical Design, OpenStreetMap Contributors, Copernicus Sentinel-2, Catan Roads Project, Finished-Figures-Only Repository Policy, Results Figure Workflow

### Community 6 - "Figure Composition Utility"
Cohesion: 0.60
Nodes (4): fmt_dist(), main(), nice_length(), Round a target distance down to a 1/2/5 x 10^k value.

## Knowledge Gaps
- **15 isolated node(s):** `Informal Route Corridors`, `Copernicus Sentinel-2`, `Google Earth Engine`, `QGIS`, `Probabilistic Passability Classification` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Season-Matched NDVI Change Analysis` connect `Imagery and Results Workflow` to `Concept and Claim Boundaries`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Temporal Activity Classification` connect `Concept and Claim Boundaries` to `Imagery and Results Workflow`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `NDVI Change Figure` connect `Imagery and Results Workflow` to `Repository Documentation Policy`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **What connects `Round a target distance down to a 1/2/5 x 10^k value.`, `Informal Route Corridors`, `Copernicus Sentinel-2` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Technical Design and Validation` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._