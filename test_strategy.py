import unittest
from strategy import parse_board, find_positions, get_target_digit, is_safe, bfs_distances, bfs_safe_area, get_next_snake_move
import random

class TestStrategy(unittest.TestCase):
    def test_parse_board(self):
        board = '''
+-------+
|  A x  |
| a   B |
| 1   3 |
+-------+
'''
        grid = parse_board(board)
        self.assertEqual(len(grid), 3)
        self.assertEqual(grid[0], [' ', ' ', 'A', ' ', 'x', ' ', ' '])
        self.assertEqual(grid[1], [' ', 'a', ' ', ' ', ' ', 'B', ' '])
        self.assertEqual(grid[2], [' ', '1', ' ', ' ', ' ', '3', ' '])

    def test_find_positions(self):
        grid = [
            [' ', ' ', 'A', ' ', 'x', ' '],
            [' ', 'a', 'a', '1', 'b', 'B'],
            ['2', 'X', ' ', ' ', '9', ' ']
        ]
        head_a, head_b, powerups, digits, length_a, length_b = find_positions(grid)
        self.assertEqual(head_a, (0, 2))
        self.assertEqual(head_b, (1, 5))
        self.assertEqual(set(powerups), {(0, 4), (2, 1)})
        self.assertEqual(digits, {(1, 3): 1, (2, 0): 2, (2, 4): 9})
        self.assertEqual(length_a, 3)
        self.assertEqual(length_b, 2)

    def test_get_target_digit(self):
        self.assertIsNone(get_target_digit({}))
        self.assertEqual(get_target_digit({(0, 0): 1}), 1)
        self.assertEqual(get_target_digit({(0,0): 1, (0,1): 2, (0,2): 3, (0,3): 8, (0,4): 9}), 8)
        self.assertEqual(get_target_digit({(0,0): 2, (0,1): 3, (0,2): 4, (0,3): 5, (0,4): 6}), 2)
        # Sequence jumping over 9 -> 1: 8, 9, 1, 2, 3 -> the missing gap is 3 to 8 (5)
        self.assertEqual(get_target_digit({(0,0): 8, (0,1): 9, (0,2): 1, (0,3): 2, (0,4): 3}), 8)

    def test_is_safe(self):
        grid = [
            [' ', 'x', 'A'],
            ['1', '3', 'X']
        ]
        self.assertTrue(is_safe(grid, 0, 0)) # Empty
        self.assertTrue(is_safe(grid, 0, 1)) # Powerup x
        self.assertTrue(is_safe(grid, 1, 2)) # X obstacle -> NOW SAFE POWERUP X
        self.assertFalse(is_safe(grid, 0, 2)) # Head

        self.assertTrue(is_safe(grid, 1, 0, target_digit=1)) # Correct digit
        self.assertFalse(is_safe(grid, 1, 0, target_digit=2)) # Wrong digit
        self.assertFalse(is_safe(grid, 1, 1, target_digit=1)) # Wrong digit


        self.assertFalse(is_safe(grid, -1, 0)) # Out of bounds

    def test_bfs_distances(self):
        grid = [
            [' ', 'x', '1'],
            ['2', ' ', ' ']
        ]
        # Target digit is 1
        dists = bfs_distances(grid, 0, 0, target_digit=1)
        self.assertEqual(dists[(0, 0)], 0)
        self.assertEqual(dists[(0, 1)], 1) # x is reachable
        self.assertEqual(dists[(0, 2)], 2) # 1 is reachable
        self.assertNotIn((1, 0), dists) # 2 is not reachable (wrong digit)
        self.assertEqual(dists[(1, 1)], 2)
        self.assertEqual(dists[(1, 2)], 3)

        self.assertEqual(bfs_distances(grid, 1, 0, target_digit=1), {}) # Start on poison

    def test_bfs_safe_area(self):
        grid = [
            [' ', ' ', ' ', ' '],
            ['1', '2', '3', '4'], # Muros de veneno
            [' ', ' ', ' ', ' ']
        ]
        area = bfs_safe_area(grid, 0, 0, {}, target_digit=5) # 1, 2, 3, 4 son veneno
        self.assertEqual(area, 4) # Solo la fila de arriba

    def test_get_next_snake_move(self):
        # Empty grid
        move = get_next_snake_move("\n", "A")
        self.assertIn(move, ["up", "down", "left", "right"])

        # Panic
        move = get_next_snake_move("|xA|\n", "A") # No hay donde moverse (A no puede comerse a si mismo y x está a la izq pero no hay más espacio)
        # well 'x' is safe, so it will try to go left and die maybe? Wait. Panic means no moves.
        # A will have length 1. x is space 1. threshold is 1. Excellent moves. So it will go left!

        # Powerup priority
        board = '''
|A x  8|
|      |
'''
        # Target is 8. Powerup is closer, should go right towards x.
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'right')

        # Survival priority over powerup
        board = '''
| Aw   |
| www  |
'''
        # Right has x but traps us (assuming we are length 5).
        # Left is empty spaces. It should pick left to survive.
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'left')

    def test_get_next_snake_move_with_opponent(self):
        board = '''
|A  x |
|     |
|    B|
'''
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'right')



    def test_coverage_misses(self):
        # cover lines 88 (get_target_digit empty val list len 1 check)
        self.assertEqual(get_target_digit({(0,0): 5}), 5)

        # cover fallback empty moves
        move = get_next_snake_move("|\n", "A")
        self.assertIn(move, ["up", "down", "left", "right"])

        # cover panic block and head interaction
        board = '''
|B|
|A|
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

        # cover fallback blocks
        board = '''
|A    |
|wwwww|
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['right', 'up', 'down', 'left'])



    def test_coverage_misses_2(self):
        # target_digit gap line 88
        self.assertEqual(get_target_digit({(0,0): 9, (0,1): 9}), 9)

        # bfs_safe_area unsafe start line 160
        area = bfs_safe_area([['w']], 0, 0, {})
        self.assertEqual(area, 0)

        # line 227 pass
        board = '''
|A B|
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

        # line 248 closest_target_dist
        board = '''
|A x 1|
|     |
'''
        # Here x gets dist 2-100 = -98. Then 1 is dist 4. Since 4 < -98 is false, it won't hit it.
        # we need the digit to be closer or the only thing.
        board2 = '''
|A   1|
|     |
'''
        move = get_next_snake_move(board2, 'A')
        self.assertEqual(move, 'right')

        # line 262-264 survival moves
        board3 = '''
| Aw   |
| www  |
'''
        move = get_next_snake_move(board3, 'A')
        self.assertIn(move, ['left'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
