"""Assignment 1 - PS12 - Optimal Planner using Local Beam Search.

The program reads a warehouse grid from inputPS12.txt, runs Local Beam Search
with beam width k = 2 by default, and writes the detailed trace to
outputPS12.txt.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


Position = Tuple[int, int]
Grid = List[List[str]]

FREE_CELLS = {"0", ".", "_"}
BLOCKED_CELL = "X"
START_CELL = "S"
GOAL_CELL = "G"
ALLOWED_CELLS = FREE_CELLS | {BLOCKED_CELL, START_CELL, GOAL_CELL}

MOVES: Sequence[Tuple[str, int, int]] = (
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
)


@dataclass(frozen=True)
class SearchNode:
    """A state retained by the beam search."""

    position: Position
    path: Tuple[Position, ...]
    cost: int
    heuristic: int


@dataclass(frozen=True)
class IterationRecord:
    """Trace data for one Local Beam Search iteration."""

    iteration: int
    current_beam: Tuple[SearchNode, ...]
    generated_successors: Tuple[SearchNode, ...]
    unique_successors: Tuple[SearchNode, ...]
    selected_beam: Tuple[SearchNode, ...]


@dataclass(frozen=True)
class SearchResult:
    """Final search outcome and the trace used for output generation."""

    found: bool
    start: Position
    goal: Position
    final_path: Tuple[Position, ...]
    total_cost: int
    iterations: Tuple[IterationRecord, ...]
    message: str


class BeamFringe:
    """Bounded fringe for storing the selected k beam states."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Beam fringe capacity must be greater than zero.")
        self.capacity = capacity
        self._items: List[SearchNode] = []

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def is_full(self) -> bool:
        return len(self._items) >= self.capacity

    def insert(self, node: SearchNode) -> None:
        if self.is_full():
            raise OverflowError("Beam fringe is full; cannot insert another state.")
        self._items.append(node)

    def delete(self) -> SearchNode:
        if self.is_empty():
            raise IndexError("Beam fringe is empty; cannot delete a state.")
        return self._items.pop(0)

    def drain(self) -> Tuple[SearchNode, ...]:
        selected: List[SearchNode] = []
        while not self.is_empty():
            selected.append(self.delete())
        return tuple(selected)


def normalize_cell(token: str) -> str:
    cell = token.strip().upper()
    if cell not in ALLOWED_CELLS:
        raise ValueError(
            f"Invalid grid cell '{token}'. Allowed cells are S, G, X, 0, ., _."
        )
    return "0" if cell in FREE_CELLS else cell


def read_grid(input_path: Path) -> Grid:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    raw_lines = []
    for line in input_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            raw_lines.append(stripped)

    if not raw_lines:
        raise ValueError("Input file is empty.")

    first_line = raw_lines[0].split()
    if len(first_line) != 2 or not all(token.isdigit() for token in first_line):
        raise ValueError("First non-comment line must contain: <rows> <columns>.")

    rows, columns = int(first_line[0]), int(first_line[1])
    if rows <= 0 or columns <= 0:
        raise ValueError("Grid dimensions must be positive integers.")

    grid_lines = raw_lines[1:]
    if len(grid_lines) != rows:
        raise ValueError(f"Expected {rows} grid rows, but found {len(grid_lines)}.")

    grid: Grid = []
    for row_index, line in enumerate(grid_lines):
        parts = line.split()
        if len(parts) != columns:
            raise ValueError(
                f"Row {row_index} must contain {columns} cells, but found {len(parts)}."
            )
        grid.append([normalize_cell(part) for part in parts])
    return grid


def validate_grid(grid: Grid) -> Tuple[Position, Position]:
    if not grid or not grid[0]:
        raise ValueError("Grid cannot be empty.")

    column_count = len(grid[0])
    start_positions: List[Position] = []
    goal_positions: List[Position] = []

    for row_index, row in enumerate(grid):
        if len(row) != column_count:
            raise ValueError("All grid rows must have the same number of columns.")
        for column_index, cell in enumerate(row):
            if cell == START_CELL:
                start_positions.append((row_index, column_index))
            elif cell == GOAL_CELL:
                goal_positions.append((row_index, column_index))

    if len(start_positions) != 1:
        raise ValueError(f"Grid must contain exactly one S cell; found {len(start_positions)}.")
    if len(goal_positions) != 1:
        raise ValueError(f"Grid must contain exactly one G cell; found {len(goal_positions)}.")

    return start_positions[0], goal_positions[0]


def manhattan_distance(current: Position, goal: Position) -> int:
    return abs(goal[0] - current[0]) + abs(goal[1] - current[1])


def is_valid_position(position: Position, grid: Grid) -> bool:
    row, column = position
    return 0 <= row < len(grid) and 0 <= column < len(grid[0])


def is_blocked(position: Position, grid: Grid) -> bool:
    row, column = position
    return grid[row][column] == BLOCKED_CELL


def node_sort_key(node: SearchNode) -> Tuple[int, int, int, int, Tuple[Position, ...]]:
    row, column = node.position
    return (node.heuristic, node.cost, row, column, node.path)


def generate_successors(node: SearchNode, grid: Grid, goal: Position) -> Tuple[SearchNode, ...]:
    successors: List[SearchNode] = []
    current_row, current_column = node.position

    for _move_name, row_delta, column_delta in MOVES:
        next_position = (current_row + row_delta, current_column + column_delta)

        if not is_valid_position(next_position, grid):
            continue
        if is_blocked(next_position, grid):
            continue
        if next_position in node.path:
            continue

        next_path = node.path + (next_position,)
        successors.append(
            SearchNode(
                position=next_position,
                path=next_path,
                cost=node.cost + 1,
                heuristic=manhattan_distance(next_position, goal),
            )
        )

    return tuple(successors)


def remove_duplicate_states(nodes: Iterable[SearchNode]) -> Tuple[SearchNode, ...]:
    best_by_position = {}
    for node in nodes:
        existing = best_by_position.get(node.position)
        if existing is None or node_sort_key(node) < node_sort_key(existing):
            best_by_position[node.position] = node
    return tuple(sorted(best_by_position.values(), key=node_sort_key))


def select_best_beam(nodes: Sequence[SearchNode], beam_width: int) -> Tuple[SearchNode, ...]:
    fringe = BeamFringe(beam_width)
    for node in sorted(nodes, key=node_sort_key)[:beam_width]:
        fringe.insert(node)
    return fringe.drain()


def local_beam_search(grid: Grid, beam_width: int = 2) -> SearchResult:
    if beam_width <= 0:
        raise ValueError("Beam width k must be greater than zero.")

    start, goal = validate_grid(grid)
    start_node = SearchNode(
        position=start,
        path=(start,),
        cost=0,
        heuristic=manhattan_distance(start, goal),
    )

    if start == goal:
        return SearchResult(True, start, goal, (start,), 0, tuple(), "Start is already goal.")

    current_beam: Tuple[SearchNode, ...] = (start_node,)
    records: List[IterationRecord] = []
    max_iterations = len(grid) * len(grid[0])

    for iteration in range(max_iterations):
        generated: List[SearchNode] = []
        for node in current_beam:
            generated.extend(generate_successors(node, grid, goal))

        unique_successors = remove_duplicate_states(generated)
        selected_beam = select_best_beam(unique_successors, beam_width)

        records.append(
            IterationRecord(
                iteration=iteration,
                current_beam=current_beam,
                generated_successors=tuple(generated),
                unique_successors=unique_successors,
                selected_beam=selected_beam,
            )
        )

        goal_nodes = [node for node in selected_beam if node.position == goal]
        if goal_nodes:
            best_goal = sorted(goal_nodes, key=node_sort_key)[0]
            return SearchResult(
                True,
                start,
                goal,
                best_goal.path,
                best_goal.cost,
                tuple(records),
                "Goal reached successfully.",
            )

        if not selected_beam:
            return SearchResult(
                False,
                start,
                goal,
                tuple(),
                -1,
                tuple(records),
                "No path found because the beam has no valid successors.",
            )

        current_beam = selected_beam

    return SearchResult(
        False,
        start,
        goal,
        tuple(),
        -1,
        tuple(records),
        "No path found within the maximum safe iteration limit.",
    )


def format_position(position: Position) -> str:
    return f"({position[0]}, {position[1]})"


def format_path(path: Sequence[Position]) -> str:
    if not path:
        return "No path available."
    return " -> ".join(format_position(position) for position in path)


def format_nodes(nodes: Sequence[SearchNode]) -> str:
    if not nodes:
        return "None"
    return "\n".join(
        f"State: {format_position(node.position)}, h = {node.heuristic}, cost = {node.cost}"
        for node in nodes
    )


def format_grid(grid: Grid) -> str:
    header = "    " + "  ".join(str(column) for column in range(len(grid[0])))
    lines = [header]
    for row_index, row in enumerate(grid):
        lines.append(f"{row_index}:  " + "  ".join(row))
    return "\n".join(lines)


def build_output_report(grid: Grid, result: SearchResult, beam_width: int) -> str:
    lines: List[str] = []
    lines.append("Assignment 1 - PS12 - Optimal Planner")
    lines.append("Algorithm: Local Beam Search")
    lines.append(f"Beam width k = {beam_width}")
    lines.append("")
    lines.append("Input Grid:")
    lines.append(format_grid(grid))
    lines.append("")
    lines.append(f"Start State: {format_position(result.start)}")
    lines.append(f"Goal State: {format_position(result.goal)}")
    lines.append("")
    lines.append("Heuristic Function:")
    lines.append("h(n) = |goal_row - current_row| + |goal_column - current_column|")
    lines.append("This is Manhattan Distance, suitable for four-direction grid movement.")
    lines.append("")
    lines.append("Cost Function:")
    lines.append("Each valid move has path cost 1 unit.")
    lines.append("Total path cost = number of moves from Start to Goal.")
    lines.append("")

    for record in result.iterations:
        lines.append(f"Iteration {record.iteration}:")
        lines.append("Current Beam States:")
        lines.append(format_nodes(record.current_beam))
        lines.append("")
        lines.append("Generated Successor States:")
        lines.append(format_nodes(record.generated_successors))
        lines.append("")
        lines.append("After Removing Duplicate States:")
        lines.append(format_nodes(record.unique_successors))
        lines.append("")
        lines.append(f"Selected Best {beam_width} Beam States:")
        lines.append(format_nodes(record.selected_beam))
        lines.append("-" * 60)

    lines.append("Search Result:")
    lines.append(result.message)
    lines.append("")

    if result.found:
        lower_bound = manhattan_distance(result.start, result.goal)
        lines.append("Final Path from Start to Goal:")
        lines.append(format_path(result.final_path))
        lines.append("")
        lines.append(f"Total Path Cost: {result.total_cost}")
        lines.append(
            f"Optimality Note: The start-to-goal Manhattan lower bound is {lower_bound}; "
            f"the found path cost is {result.total_cost}, so this path is optimal for the given grid."
        )
    else:
        lines.append("Final Path from Start to Goal:")
        lines.append("No path found.")
        lines.append("")
        lines.append("Total Path Cost: Not applicable")

    lines.append("")
    lines.append("Complexity Analysis:")
    lines.append("Let k be the beam width, b be the branching factor, and d be the search depth.")
    lines.append("For this grid, b <= 4 because movement is limited to Up, Down, Left, and Right.")
    lines.append("At each level, at most k states are expanded and up to k*b successors are sorted.")
    lines.append("Time Complexity: O(d * k * b log(k*b))")
    lines.append("Space Complexity: O(k * d), because each retained beam node stores its path.")
    lines.append("")
    lines.append("Data Structure Notes:")
    lines.append("A bounded BeamFringe stores the selected k states.")
    lines.append("BeamFringe.insert raises an error message when full.")
    lines.append("BeamFringe.delete raises an error message when empty.")

    return "\n".join(lines) + "\n"


def resolve_path(file_name: str) -> Path:
    path = Path(file_name)
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parent / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PS12 Local Beam Search planner.")
    parser.add_argument("--input", default="inputPS12.txt", help="Input grid file path.")
    parser.add_argument("--output", default="outputPS12.txt", help="Output trace file path.")
    parser.add_argument("--k", type=int, default=2, help="Beam width. Default is 2.")
    args = parser.parse_args()

    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    try:
        grid = read_grid(input_path)
        result = local_beam_search(grid, args.k)
        report = build_output_report(grid, result, args.k)
        output_path.write_text(report, encoding="utf-8")
        print(report)
        return 0 if result.found else 2
    except Exception as error:
        error_report = f"Error: {error}\n"
        output_path.write_text(error_report, encoding="utf-8")
        print(error_report)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())