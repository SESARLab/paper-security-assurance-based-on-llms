# Folder content

- `data/100-m-m.ods`: the inventory, query and correct probes selected by the expert
- `data/selection_results/original`: directory containing the original responses of the LLM-based advisor
- `data/selection_results/`: directory containing the manually cleaned responses, then converted into full JSON using `src/jsonify_results.py` (those prefixed with `json_`).

## Open Jupyter notebooks

Mount the volume on the root dir of the project

```bash
docker run -d -p 8888:8888     -v ".:/home/jovyan/work"     --name paper-radicchi-notebook     quay.io/jupyter/scipy-notebook:python-3.13 start-notebook.sh --NotebookApp.token='mytoken'
```
