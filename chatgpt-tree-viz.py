import json
import dash
import dash_cytoscape as cyto
from dash import html


with open("./conversation_object.json", "r", encoding="utf-8") as file:
    conversation_data = json.load(file)

mapping_data = conversation_data.get("mapping", {})


nodes = []
edges = []

for key, value in mapping_data.items():
    message = value.get("message", {})
    content = message.get("content", {}) if message else {}
    content_parts = content.get("parts", []) if content else []
    label = content_parts[0] if content_parts else ""
    
    nodes.append({
        "data": {
            "id": key,
            "label": label,
            "author": message["author"]["role"] if message else "unknown"
        }
    })
    
    if "parent" in value and value["parent"]:
        edges.append({
            "data": {
                "source": value["parent"],
                "target": key
            }
        })

graph_data = {
    "nodes": nodes,
    "edges": edges
}


cyto.load_extra_layouts()


app = dash.Dash(__name__)
app.title = "ChatGPT Conversation Visualization"


for node in graph_data["nodes"]:
    label_length = len(node["data"]["label"])
    node_width = 500
    node_height = max(10, 20 * (label_length ** 0.5))
    node["data"]["width"] = node_width
    node["data"]["height"] = node_height

stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'text-align': 'justify',
            'text-valign': 'center',
            'background-color': '#0074D9',
            'color': '#FFFFFF',
            'font-size': '8px',
            'text-wrap': 'wrap',
            'text-max-height': '90%',
            'text-max-width': '450px',  
            'shape': 'round-rectangle',
            'width': 'data(width)',
            'height': 'data(height)'
        }
    },
    {
        'selector': '[author = "user"]',
        'style': {'background-color': '#2ECC40'}
    },
    {
        'selector': '[author = "system"]',
        'style': {'background-color': '#FFDC00'}
    },
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'line-color': '#AAAAAA',
            'target-arrow-color': '#AAAAAA'
        }
    }
]

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=[
            *graph_data["nodes"],
            *graph_data["edges"]
        ],
        layout={'name': 'dagre'},
        style={'width': '100%', 'height': '100vh'},
        stylesheet=stylesheet,
        boxSelectionEnabled=False,
        zoomingEnabled=True,
        panningEnabled=True,
        zoom=1,
        minZoom=0.05,
        maxZoom=5,
        responsive=True,
        autolock=False,
        autoungrabify=True,
        autounselectify=True,
    )
])


app.run(debug=True)
