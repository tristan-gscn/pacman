from .MazeUtils import MazeUtils


class FindPath:
    """
    Solver class that implements the A* algorithm to find the shortest path
    from the start to the end in a maze.

    Attributes:
        maze (list[list[int]]): The maze represented as a 2D grid of integers
        start (tuple[int, int]): The starting coordinates in the maze
        end (tuple[int, int]): The ending coordinates in the maze
        is_42 (list[tuple[int, int]]): List of coordinates representing 42
            obstacles in the maze
    """

    def __init__(
        self,
        maze: list[list[int]]
    ):
        """Initialize the pathfinder with a maze.

        Args:
            maze (list[list[int]]): The maze represented as a 2D grid of
                integers.
        """
        self.maze = maze

    def get_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """Get accessible neighboring cells from the current cell.

        Args:
            cell (tuple[int, int]): The current (row, col) coordinate.

        Returns:
            list[tuple[int, int]]: A list of accessible (row, col) neighbors.
        """
        row, col = cell
        cell_walls = MazeUtils.unpack_cell(self.maze[row][col])
        neighbors: list[tuple[int, int]] = []

        # If no NORTH wall -> there's a NORTH neighbor (checking diff 0001)
        if not cell_walls["N"]:
            neighbors.append((row - 1, col))

        # If no SOUTH wall -> there's a SOUTH neighbor (checking diff 0010)
        if not cell_walls["S"]:
            neighbors.append((row + 1, col))

        # If no WEST wall -> there's a WEST neighbor (checking diff 0100)
        if not cell_walls["W"]:
            neighbors.append((row, col - 1))

        # If no EAST wall -> there's a EAST neighbor (checking diff 1000)
        if not cell_walls["E"]:
            neighbors.append((row, col + 1))
        return neighbors

    @staticmethod
    def h(cell1: tuple[int, int], cell2: tuple[int, int]) -> int:
        """Heuristic function for A* (Manhattan Distance).

        Args:
            cell1 (tuple[int, int]): The first coordinate (row, col).
            cell2 (tuple[int, int]): The second coordinate (row, col).

        Returns:
            int: The Manhattan distance between the two cells.
        """
        y1, x1 = cell1
        y2, x2 = cell2
        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(
        self, node: tuple[int, int], came_from: dict[tuple[int, int],
                                                     tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """Reconstruct the path from start to end using the came_from map.

        Args:
            node (tuple[int, int]): The end node to start reconstruction from.
            came_from (dict): Map of nodes to their preceding node.

        Returns:
            list[tuple[int, int]]: The reconstructed path from start to end.
        """
        path = [node]
        while node in came_from:
            node = came_from[node]
            path.append(node)
        # reverse result to get from beginning to end
        path.reverse()
        return path

    def a_star_algorithm(self, start: tuple[int, int],
                         end: tuple[int, int]) -> list[tuple[int, int]]:
        """Find the shortest path between start and end using A* algorithm.

        Args:
            start (tuple[int, int]): Starting (row, col) coordinate.
            end (tuple[int, int]): Target (row, col) coordinate.

        Returns:
            list[tuple[int, int]]: The shortest path as a list of coordinates,
                or an empty list if no path exists.
        """

        # open_paths: list[(f_score, node)] is the list of cells path opened to
        # explore, sorted by priority (f_score)
        open_paths: list[tuple[int,
                               tuple[int,
                                     int]]] = [(self.h(start, end), start)]

        # Register the precedent node of each newly accessed node
        came_from: dict[tuple[int, int], tuple[int, int]] = {}

        # Register the "cost" or progress already made g(n)
        # for each cell visited
        path_cost: dict[tuple[int, int], int] = {start: 0}

        while len(open_paths) > 0:
            # get the best next cell to visit: the one with the lowest priority
            open_paths.sort(reverse=True)
            _, curr_node = open_paths.pop()
            if curr_node == end:
                goal_path = self.reconstruct_path(end, came_from)
                return goal_path
            neighbors = self.get_neighbors(curr_node)

            # Check all possible neighbors of the current cell
            # and register new ones
            for neighbor in neighbors:
                new_cost = path_cost.get(curr_node, 10000) + 1
                if neighbor not in path_cost or new_cost < path_cost[neighbor]:
                    path_cost[neighbor] = new_cost
                    # f(n)-> priority = g(n)-> new_cost + h(n)-> estimated_cost
                    priority = new_cost + self.h(neighbor, end)
                    open_paths.append((priority, neighbor))
                    came_from[neighbor] = curr_node
        return []
