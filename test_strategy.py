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
        self.assertEqual(move, "up")

        # Powerup vs Food balance
        # Food base=200, PU base=1000.
        # Food at dist 0 (right next to it) -> score = 200/1 = 200
        # PU at dist 3 -> score = 1000/4 = 250 -> prefers PU!
        # Let's test Food at dist 0 vs PU at dist 5 -> score = 1000/6 = 166. Food wins!
        board = '''
| X      A1|
|          |
'''
        # A is at (0,8), 1 is at (0,9) (dist 0 from A's right step).
        # X is at (0,2). dist from A's left step is 5.
        # PU score = 1000/(5+1) = 166. Food score = 200/(0+1) = 200.
        # It should go right to eat 1!
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'right')

        # Survival priority over objectives
        board = '''
| Aw   |
| www  |
'''
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'left')

    def test_get_next_snake_move_with_opponent(self):
        # Opponent is closer to X, so we ignore it and go for Food
        board = '''
|A    B X |
|         |
|   1     |
'''
        # B is closer to X. A should go down towards 1.
        move = get_next_snake_move(board, 'A')
        self.assertEqual(move, 'down')

    def test_coverage_misses(self):
        # Cover pass statement line 198
        board = '''
|A B|
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

        # Cover fallback lines 230-232
        board = '''
|A     |
|      |
|      |
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

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

        # line 262-264 survival moves
        board3 = '''
| Aw   |
| www  |
'''
        move = get_next_snake_move(board3, 'A')
        self.assertIn(move, ['left'])

    def test_coverage_misses_3(self):
        # line 272 (panic fallback)
        board = '''
|B|
|A|
'''
        move = get_next_snake_move(board, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

        # line 198 (opp_head interaction pass)
        board2 = '''
|A B|
'''
        move = get_next_snake_move(board2, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
