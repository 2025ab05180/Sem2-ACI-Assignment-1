# Assignment 1 – PS12 – Optimal Planner

**Group ID:** G108  
**Algorithm:** Local Beam Search  
**Language:** Python 3  

---

## Team Members

| Name | Registration Number |
|---|---|
| ARTHIKA G. | — |
| SRINEVEDA R S. | — |
| ASWATHY H. | — |
| AMIYA PALAI. | — |
| KUTAREKAR NISHCHAL AJAY. | — |

---

## Problem Statement

A delivery robot must find the optimal route in a 5×5 warehouse grid from **Start S = (0,0)** to **Goal G = (4,4)** while avoiding blocked cells marked `X`. Movement is restricted to **Up, Down, Left, Right** (no diagonals). Each valid move costs **1 unit**.

### Grid Layout

```
     0    1    2    3    4
0:   S    0    0    X    0
1:   0    X    0    X    0
2:   0    X    0    0    0
3:   0    0    X    X    0
4:   0    0    0    0    G
```

Blocked cells: `(0,3)`, `(1,1)`, `(1,3)`, `(2,1)`, `(3,2)`, `(3,3)`

---

## Algorithm

**Local Beam Search** with beam width **k = 2**.

### Heuristic Function
Manhattan Distance:
```
h(n) = |goal_row - current_row| + |goal_col - current_col|
```

### Cost Function
```
g(n) = number of moves from Start to node n  (each move costs 1)
```

---

## Files

| File | Description |
|---|---|
| `optimal_planner_PS12.py` | Main Python implementation |
| `inputPS12.txt` | Input grid file |
| `outputPS12.txt` | Generated output trace |
| `designPS12_G108.md` | Design document (PEAS, algorithm, complexity) |
| `README_RUN.txt` | Quick-run instructions |

---

## How to Run

### Prerequisites
- Python 3.x installed

### Default Run
```bash
py optimal_planner_PS12.py
```
Reads `inputPS12.txt` and writes `outputPS12.txt` in the same folder.

### Custom Arguments
```bash
py optimal_planner_PS12.py --input inputPS12.txt --output outputPS12.txt --k 2
```

| Argument | Default | Description |
|---|---|---|
| `--input` | `inputPS12.txt` | Path to the input grid file |
| `--output` | `outputPS12.txt` | Path to write the output trace |
| `--k` | `2` | Beam width |

---

## Input File Format

```
# comments are allowed
<rows> <columns>
<grid rows using S, G, X, 0>
```

Example (`inputPS12.txt`):
```
5 5
S 0 0 X 0
0 X 0 X 0
0 X 0 0 0
0 0 X X 0
0 0 0 0 G
```

---

## Sample Output

```
Iteration 0:
  Current Beam: (0,0)  h=8  cost=0
  Selected Best 2 Beam States: (0,1) h=7, (1,0) h=7
...
Final Path from Start to Goal:
(0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2) -> (2,3) -> (2,4) -> (3,4) -> (4,4)

Total Path Cost: 8
```

The found path cost **8** equals the Manhattan lower bound — the path is **optimal**.

---

## Complexity Analysis

| | Complexity |
|---|---|
| **Time** | O(d × k × b × log(k·b)) |
| **Space** | O(k × d) |

Where **k** = beam width, **b** ≤ 4 (branching factor), **d** = solution depth.

---

## Data Structure

`BeamFringe` — a bounded queue-like structure with capacity `k`.
- `insert()` raises `OverflowError` when the fringe is full.
- `delete()` raises `IndexError` when the fringe is empty.

---

## Submission Checklist

- [ ] `designPS12_G108.pdf`
- [ ] `G108_Contribution.xlsx`
- [ ] `inputPS12.txt`
- [ ] `outputPS12.txt`
- [ ] `optimal_planner_PS12.py`
- [ ] Zip file named: `G108_A1_PS12_XXXXXXXXXX.zip`
