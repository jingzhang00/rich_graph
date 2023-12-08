## Learning Graph Structures for Collaborative Tasks

### Install
```bash
pip install -r requirements.txt
python main.py
```
### UI introduction
The window looks like:

<img src="img/window.png" height="75%" width="75%">

Once the graph is built, you can select start node and end node by click it, then a solution between these nodes will be highlighted

<img src="img/original_graph.png" height="75%" width="75%">

`Clear` means you can clear the selected nodes and choose another pair.

`Refine` will remove unnecessary edge and node through additional rich information.

<img src="img/refined_graph.png" height="75%" width="75%">

`Recover` will back to original graph structure.

`Save` will save current graph image to your computer.