A dynamic application to visualize and interact with stock-related information.

## Requirements
- `pandas`
- `numpy`
- `pygame`

## Installation

1. Clone the repository:
git clone https://github.com/lordyabu/stockgame.git

2. Navigate to the cloned directory:
cd stockgame

3. Paste your data into folder

4. Run

```python
python main.py --num-vars-table 25 # Adjust the `--num-vars-table` parameter based on your preference.
```

## Features

**Presets**:
- Save and load presets
![output_preset](https://github.com/lordyabu/stockgame/assets/92772420/4ad19ac6-80ae-4209-ae8e-4e4af8551be7)

**Graphs**: 
- Manipulate and customize the graph visualizations according to your preference.
- Personalize the appearance with options for grid, chart type, and color.
- Integrate trading indicators to make the data more insightful.
- Customize the view with a narrowing feature, enabling you to focus on specific portions of the graph.
![output_graph](https://github.com/lordyabu/stockgame/assets/92772420/451ee660-4276-47f7-84a0-2ffb0d45addd)

**Data Table**: 
- Display values present on the graph.
- The data is linked with a point iterator that can traverse across the graph, allowing you to examine specific data points closely.
![output_table (1)](https://github.com/lordyabu/stockgame/assets/92772420/4210ad35-8199-4405-aa31-dae777e2ebcd)
