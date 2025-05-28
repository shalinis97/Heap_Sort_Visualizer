# Visual Sorting Tool - Min & Max Heap Sort Only
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import networkx as nx

# Global counter for operations
class Counter:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    def reset(self):
        self.comparisons = 0
        self.swaps = 0

counter = Counter()

# Max Heapify
def max_heapify(arr, n, i):
    smallest = i
    l = 2 * i + 1
    r = 2 * i + 2

    counter.comparisons += 1
    if l < n and arr[l] < arr[smallest]:
        smallest = l
    counter.comparisons += 1
    if r < n and arr[r] < arr[smallest]:
        smallest = r

    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        counter.swaps += 1
        yield arr.copy(), (i, smallest), f"Swapped {i} and {smallest}"
        yield from max_heapify(arr, n, smallest)
    else:
        yield arr.copy(), (i, i), f"Checked {i}"

# Min Heapify
def min_heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    counter.comparisons += 1
    if l < n and arr[l] > arr[largest]:
        largest = l
    counter.comparisons += 1
    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        counter.swaps += 1
        yield arr.copy(), (i, largest), f"Swapped {i} and {largest}"
        yield from min_heapify(arr, n, largest)
    else:
        yield arr.copy(), (i, i), f"Checked {i}"

# Heap Sort - Max
def heap_sort_max(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        yield from max_heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        counter.swaps += 1
        yield arr.copy(), (0, i), f"Swapped 0 and {i}"
        yield from max_heapify(arr, i, 0)

# Heap Sort - Min
def heap_sort_min(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        yield from min_heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        counter.swaps += 1
        yield arr.copy(), (0, i), f"Swapped 0 and {i}"
        yield from min_heapify(arr, i, 0)

# Plot Function
def draw_plot(plot_spot, arr, highlight=None, algorithm="Heap Sort"):
    fig, ax = plt.subplots(figsize=(10, 5))
    arr = arr[:400]
    arr_for_plot = np.log1p(arr) if (max(arr) - min(arr)) > 100 else arr
    x = np.arange(len(arr))

    colors = ['blue'] * len(arr)
    if highlight:
        for idx in highlight:
            if idx < len(colors):
                colors[idx] = 'red' if highlight.index(idx) == 0 else 'green'

    bars = ax.bar(x, arr_for_plot, color=colors, edgecolor='black', linewidth=0.3)
    ax.set_title(f"{algorithm} Visualizer", fontsize=14)
    plot_spot.pyplot(fig)
    plt.close(fig)

# Heap Tree
def draw_heap_tree(plot_spot, arr, highlight=None):
    G = nx.DiGraph()
    labels = {}
    for i in range(len(arr)):
        G.add_node(i)
        labels[i] = arr[i]
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(arr):
            G.add_edge(i, left)
        if right < len(arr):
            G.add_edge(i, right)

    def hierarchy_pos(G, root=0, width=1.5, vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = {}
        def _hierarchy_pos(G, root, leftmost, width, vert_gap, vert_loc, xcenter, pos, parent=None):
            pos[root] = (xcenter, vert_loc)
            children = list(G.neighbors(root))
            if len(children) != 0:
                dx = width / 2
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    _hierarchy_pos(G, child, leftmost, width / 2, vert_gap, vert_loc - vert_gap, nextx, pos, root)
            return pos
        return _hierarchy_pos(G, root, 0, width, vert_gap, vert_loc, xcenter, pos)

    pos = hierarchy_pos(G)

    node_colors = []
    for node in G.nodes():
        if highlight and node in highlight:
            node_colors.append('red' if highlight.index(node) == 0 else 'green')
        else:
            node_colors.append('skyblue')

    fig, ax = plt.subplots(figsize=(10, 5))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=800, node_color=node_colors, font_size=10, ax=ax)
    plot_spot.pyplot(fig)
    plt.close(fig)

# App Setup
st.set_page_config(page_title="Heap Sort Visualizer", layout="wide")
st.title("🔢 Heap Sort Visualizer")

# Sidebar
st.sidebar.header("Configuration")
algorithm = st.sidebar.selectbox("Choose Sorting Algorithm", ["Heap Sort - Min Heap", "Heap Sort - Max Heap"])
speed_option = st.sidebar.selectbox("Select Visualization Speed", ["0.5x", "0.75x", "1x", "1.5x", "1.75x"])
speed_map = {"0.5x": 0.10, "0.75x": 0.075, "1x": 0.05, "1.5x": 0.033, "1.75x": 0.028}
input_type = st.sidebar.radio("Input Type", ["Random", "Manual"])

if input_type == "Random":
    array_size = st.sidebar.slider("Array Size", 5, 400, 10)
    arr = np.random.randint(1, 1000, size=array_size).tolist()
else:
    user_input = st.sidebar.text_area("Enter comma-separated integers", "1000, 3, 15000, 7, 22")
    try:
        arr = list(map(int, user_input.strip().split(",")))
        arr = arr[:400]
    except:
        st.sidebar.error("Invalid input. Enter integers separated by commas.")
        st.stop()

with st.sidebar.expander("🔍 View Input Array"):
    st.write(arr)

# Sort map
sort_map = {
    "Heap Sort - Min Heap": heap_sort_min,
    "Heap Sort - Max Heap": heap_sort_max
}

if st.button("▶️ Start Sorting"):
    counter.reset()
    sort_gen = sort_map[algorithm](arr.copy())
    plot_placeholder = st.empty()
    text_placeholder = st.empty()
    tree_placeholder = st.empty()

    for step in sort_gen:
        curr_arr, highlight, message = step
        draw_plot(plot_placeholder, curr_arr, highlight=highlight, algorithm=algorithm)
        text_placeholder.markdown(f"🧠 **Step Info:** {message}  ")
        draw_heap_tree(tree_placeholder, curr_arr, highlight=highlight)
        time.sleep(speed_map[speed_option])

    st.success("✅ Sorting Complete!")
    st.write("### Final Sorted Array")
    st.write(curr_arr)

    st.subheader("📊 Time & Space Complexity")
    st.markdown("- Time: O(n log n)  \n- Space: O(1)")

    st.subheader("🧠 Operations Summary")
    st.write(f"Comparisons: `{counter.comparisons}`")
    st.write(f"Swaps: `{counter.swaps}`")

    st.markdown("---")
    st.caption("Developed with 💡 in Streamlit | Heap Sort Visualizer")
