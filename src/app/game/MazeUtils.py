class MazeUtils:
    @staticmethod
    def unpack_cell(
            encrypted_int: int
    ) -> dict[str, bool]:
        """
        Unpacks an integer representing a maze cell to reveal the presence of
        walls.

        Args:
            encrypted_int (int): The integer value representing the cell's walls.

        Returns:
            dict[str, bool]: A dictionary mapping directions
            ('N', 'E', 'S', 'W') to boolean values (True if a wall exists,
            False otherwise).
        """
        return {
            "N": bool(encrypted_int & 1),
            "E": bool(encrypted_int & 2),
            "S": bool(encrypted_int & 4),
            "W": bool(encrypted_int & 8)
        }