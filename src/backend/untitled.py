from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import math


@dataclass
class Task:
    """Represents a task with an ID and a work duration."""
    id: int
    name: str
    duration: float  # time to complete the task itself


class ScheduleSolver:
    """
    Finds an order of visiting tasks that minimizes:
        total_travel_time + sum(task.duration)
    using Held–Karp dynamic programming (TSP on travel times).

    Assumes:
        - You start at task with index 0 (e.g. 'home' or first place).
        - You don't need to return to the start.
    """
    def __init__(self, tasks: List[Task], move_time: List[List[float]]):
        """
        :param tasks: list of Task objects; index in this list = node index
        :param move_time: square matrix move_time[i][j] = time to move from i to j
        """
        self.tasks = tasks
        self.move_time = move_time
        self.n = len(tasks)
        self._dp_cache: Optional[Dict[Tuple[int, int], float]] = None
        self._parent_cache: Optional[Dict[Tuple[int, int], int]] = None

    def update_move_time(self, i: int, j: int, new_time: float) -> None:
        """
        Update moving time from task i to task j and invalidate DP cache.
        This is how the scheduler 'reacts' to changing moving times.
        """
        if not (0 <= i < self.n and 0 <= j < self.n):
            raise IndexError("Invalid task index for move time update.")
        self.move_time[i][j] = new_time
        # Invalidate previous optimal-schedule computation
        self._dp_cache = None
        self._parent_cache = None

    def _run_held_karp(self) -> Tuple[float, List[int]]:
        """
        Run Held–Karp DP to find minimal travel time and corresponding path.
        Returns:
            (min_travel_time, path_as_list_of_indices)
        """
        n = self.n
        if n == 0:
            return 0.0, []

        # For small n only (n up to ~18–20 is realistic)
        # start at node 0
        start = 0
        ALL_MASK = (1 << n) - 1

        # dp[(mask, j)] = minimal travel time to start at 'start', visit all nodes in 'mask',
        # and end at node j.
        dp: Dict[Tuple[int, int], float] = {}
        parent: Dict[Tuple[int, int], int] = {}

        # Initialization: only start node visited, cost 0 to be at start.
        dp[(1 << start, start)] = 0.0

        # Iterate over all subsets that include the start node
        for mask in range(1 << n):
            if not (mask & (1 << start)):
                continue  # must include the start

            for j in range(n):
                state = (mask, j)
                if j not in self._nodes_in_mask(mask):
                    continue
                if state not in dp:
                    continue

                current_cost = dp[state]

                # Try to go from j to k, where k is not yet visited
                for k in range(n):
                    if mask & (1 << k):  # already visited
                        continue
                    new_mask = mask | (1 << k)
                    new_state = (new_mask, k)
                    new_cost = current_cost + self.move_time[j][k]
                    if new_state not in dp or new_cost < dp[new_state]:
                        dp[new_state] = new_cost
                        parent[new_state] = j

        # Find best endpoint (no need to return to start).
        best_cost = math.inf
        best_end = None
        for j in range(n):
            state = (ALL_MASK, j)
            if state in dp and dp[state] < best_cost:
                best_cost = dp[state]
                best_end = j

        if best_end is None:
            # Should not happen if the graph is connected and n > 0
            raise RuntimeError("No valid tour found. Check move_time connectivity.")

        # Reconstruct path backward from (ALL_MASK, best_end)
        path_indices: List[int] = []
        mask = ALL_MASK
        j = best_end
        while True:
            path_indices.append(j)
            if mask == (1 << start) and j == start:
                break
            state = (mask, j)
            i = parent[state]  # previous node
            mask = mask ^ (1 << j)  # remove j from visited set
            j = i

        path_indices.reverse()  # now from start to end

        self._dp_cache = dp
        self._parent_cache = parent
        return best_cost, path_indices

    @staticmethod
    def _nodes_in_mask(mask: int) -> List[int]:
        """Return indices of nodes that are in 'mask' (helper for clarity)."""
        nodes = []
        i = 0
        while mask:
            if mask & 1:
                nodes.append(i)
            i += 1
            mask >>= 1
        return nodes

    def compute_optimal_schedule(self) -> Tuple[List[Task], float, float, float]:
        """
        Compute optimal visiting order under current move_time.

        Returns:
            (ordered_tasks, total_travel_time, total_work_time, total_schedule_time)
        """
        if self.n == 0:
            return [], 0.0, 0.0, 0.0

        min_travel_time, path_indices = self._run_held_karp()
        ordered_tasks = [self.tasks[i] for i in path_indices]
        total_work_time = sum(t.duration for t in ordered_tasks)
        total_schedule_time = min_travel_time + total_work_time
        return ordered_tasks, min_travel_time, total_work_time, total_schedule_time


def example_usage():
    """
    Example:
        - 4 tasks (0..3).
        - Task 0 is 'Home' (duration 0).
        - The program computes optimal order and then recomputes after you change move times.
    """

    # Define tasks
    tasks = [
        Task(id=0, name="Home", duration=0.0),
        Task(id=1, name="Task A", duration=1.5),
        Task(id=2, name="Task B", duration=2.0),
        Task(id=3, name="Task C", duration=0.5),
    ]

    # Move-time matrix (symmetric here, but it doesn't have to be)
    # move_time[i][j] = time to go from i to j
    INF = 1e9
    move_time = [
        [0.0, 10.0, 15.0, 20.0],  # from 0
        [10.0, 0.0, 35.0, 25.0],  # from 1
        [15.0, 35.0, 0.0, 30.0],  # from 2
        [20.0, 25.0, 30.0, 0.0],  # from 3
    ]

    solver = ScheduleSolver(tasks, move_time)

    # First computation
    ordered_tasks, travel_t, work_t, total_t = solver.compute_optimal_schedule()
    print("=== Initial optimal schedule ===")
    print("Order:", " -> ".join(f"{t.id}:{t.name}" for t in ordered_tasks))
    print(f"Total travel time: {travel_t}")
    print(f"Total work time:   {work_t}")
    print(f"Total schedule time (travel+work): {total_t}")
    print()

    # React to change in moving time: suppose road from 0 to 1 becomes faster
    print("Updating move time: 0 -> 1 from 10.0 to 3.0 (and 1 -> 0 as well)...")
    solver.update_move_time(0, 1, 3.0)
    solver.update_move_time(1, 0, 3.0)

    ordered_tasks2, travel_t2, work_t2, total_t2 = solver.compute_optimal_schedule()
    print("=== New optimal schedule after move-time change ===")
    print("Order:", " -> ".join(f"{t.id}:{t.name}" for t in ordered_tasks2))
    print(f"Total travel time: {travel_t2}")
    print(f"Total work time:   {work_t2}")
    print(f"Total schedule time (travel+work): {total_t2}")


if __name__ == "__main__":
    example_usage()
