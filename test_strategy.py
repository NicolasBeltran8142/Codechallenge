import unittest
import strategy

class TestStrategy(unittest.TestCase):

    def test_parse_board(self):
        board_str = '''
|       |
|  *    |
|  A    |
|       |
'''
        grid = strategy.parse_board(board_str)
        self.assertEqual(len(grid), 4)
        self.assertEqual(len(grid[0]), 7)
        self.assertEqual(grid[1][2], '*')
        self.assertEqual(grid[2][2], 'A')

    def test_find_positions(self):
        grid = [
            [' ', 'a', 'a'],
            [' ', 'A', '*'],
            ['B', 'b', ' ']
        ]
        head_a, head_b, foods, length_a, length_b = strategy.find_positions(grid)
        self.assertEqual(head_a, (1, 1))
        self.assertEqual(head_b, (2, 0))
        self.assertEqual(foods, [(1, 2)])
        # head + 2 bodies = 3
        self.assertEqual(length_a, 3)
        # head + 1 body = 2
        self.assertEqual(length_b, 2)

    def test_is_safe(self):
        grid = [
            [' ', '*', 'b'],
            [' ', 'A', 'B'],
            ['a', ' ', ' ']
        ]

        # Out of bounds
        self.assertFalse(strategy.is_safe(grid, -1, 0))
        self.assertFalse(strategy.is_safe(grid, 0, 3))

        # Safe spaces
        self.assertTrue(strategy.is_safe(grid, 0, 0)) # Empty space
        self.assertTrue(strategy.is_safe(grid, 0, 1)) # Food

        # Unsafe spaces (bodies/heads)
        self.assertFalse(strategy.is_safe(grid, 1, 1)) # A
        self.assertFalse(strategy.is_safe(grid, 0, 2)) # b
        self.assertFalse(strategy.is_safe(grid, 2, 0)) # a

    def test_flood_fill(self):
        # A simple grid representing a U-shaped dead end
        # The space at (1, 1) is only connected to (0, 1) and (0, 2)
        grid = [
            ['A', ' ', ' ', 'B'],
            ['A', ' ', 'B', 'B'],
            ['A', 'B', 'B', '*']
        ]

        # Flood fill starting inside the pocket
        area = strategy.flood_fill(grid, 1, 1)
        # Should count (1,1), (0,1), (0,2) = 3
        self.assertEqual(area, 3)

        # Flood fill starting on food (which is safe)
        area2 = strategy.flood_fill(grid, 2, 3)
        self.assertEqual(area2, 1) # Trapped in the corner

    def test_get_next_snake_move_seeks_food(self):
        board_str = '''
|       |
|   *   |
|   A   |
|       |
|       |
|       |
|       |
|       |
|       |
'''
        # Head is at (2, 3), Food is at (1, 3). Best move is 'up'.
        # Needs to be a bit bigger to pass the "safe threshold" (30).
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertEqual(move, 'up')

    def test_get_next_snake_move_avoids_dead_end(self):
        # A is at (1, 1).
        # The space around it:
        # up/left are walls/out of bounds.
        # right leads to a dead end (enclosed by a).
        # down leads to open space.
        board_str = '''
| aaaa  |
| aA a  |
| a aa  |
| a     |
| a     |
'''
        # The flood fill for right gives 1 (the single space inside)
        # The flood fill for down gives > 1 (the rest of the board)
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertEqual(move, 'down')

    def test_get_next_snake_move_eats_in_safe_space(self):
        # Even if right has slightly less space than down,
        # if both are > safe_threshold, it should prioritize the food (at right)
        board_str = '''
|       |
|       |
|       |
|       |
|       |
|       |
|       |
|       |
|       |
|       |
|       |
|       |
| A *   |
| a     |
| a     |
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertEqual(move, 'right')


if __name__ == '__main__':
    unittest.main()
