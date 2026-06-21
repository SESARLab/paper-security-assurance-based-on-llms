# Folder content

- `data/100-m-m.ods`: the inventory, query and correct probes selected by the expert
- `data/selection_results/original`: directory containing the original responses of the LLM-based advisor
- `data/selection_results/`: directory containing the manually cleaned responses, then converted into full JSON using `src/jsonify_results.py` (those prefixed with `json_`).