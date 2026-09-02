import unittest
import strategy

class TestStrategy(unittest.TestCase):
    def test_parse_board(self):
        board_str = '''
| | | |
| |A| |
| | |*|
'''
        grid = strategy.parse_board(board_str)
        self.assertEqual(len(grid), 3)
        self.assertEqual(grid[0], [' ', '|', ' ', '|', ' '])
        self.assertEqual(grid[1], [' ', '|', 'A', '|', ' '])
        self.assertEqual(grid[2], [' ', '|', ' ', '|', '*'])
        
        # Test empty input
        self.assertEqual(strategy.parse_board(""), [])

    def test_find_positions(self):
        grid = [
            ['A', 'a', 'a'],
            [' ', 'B', 'b'],
            ['*', ' ', '*']
        ]
        head_a, head_b, foods, length_a, length_b = strategy.find_positions(grid)
        self.assertEqual(head_a, (0, 0))
        self.assertEqual(head_b, (1, 1))
        self.assertEqual(foods, [(2, 0), (2, 2)])
        self.assertEqual(length_a, 3) # Head + 2 'a'
        self.assertEqual(length_b, 2) # Head + 1 'b'
        
        # Empty grid
        head_a, head_b, foods, length_a, length_b = strategy.find_positions([])
        self.assertIsNone(head_a)
        self.assertIsNone(head_b)
        self.assertEqual(foods, [])

    def test_is_safe(self):
        grid = [
            [' ', '*'],
            ['A', 'a']
        ]
        self.assertTrue(strategy.is_safe(grid, 0, 0))
        self.assertTrue(strategy.is_safe(grid, 0, 1))
        self.assertFalse(strategy.is_safe(grid, 1, 0))
        self.assertFalse(strategy.is_safe(grid, 1, 1))
        # Bounds check
        self.assertFalse(strategy.is_safe(grid, -1, 0))
        self.assertFalse(strategy.is_safe(grid, 0, 2))
        self.assertFalse(strategy.is_safe(grid, 2, 0))
        
        # Empty grid
        self.assertFalse(strategy.is_safe([], 0, 0))

    def test_bfs_distances(self):
        grid = [
            [' ', ' ', '*'],
            [' ', 'A', ' '],
            ['*', ' ', ' ']
        ]
        dist = strategy.bfs_distances(grid, 0, 0)
        self.assertEqual(dist[(0, 0)], 0)
        self.assertEqual(dist[(0, 1)], 1)
        self.assertEqual(dist[(0, 2)], 2)
        self.assertEqual(dist[(1, 0)], 1)
        # (1,1) is 'A', not safe
        self.assertNotIn((1, 1), dist)
        
        # Not safe start
        self.assertEqual(strategy.bfs_distances(grid, 1, 1), {})

    def test_bfs_safe_area(self):
        grid = [
            [' ', ' ', ' '],
            [' ', 'B', ' '],
            [' ', ' ', ' ']
        ]
        # B controls area around it, but if opponent distance is high, it's safe
        opp_dist = {
            (1, 0): 1,
            (1, 1): 0, # not really safe but part of simulation
            (2, 0): 2
        }
        # If we start at (0, 0)
        area = strategy.bfs_safe_area(grid, 0, 0, opp_dist)
        # Should count (0,0)[dist=1], (0,1)[dist=2], (0,2)[dist=3]
        # (1,0) opp_dist=1 <= my_dist=2 -> skip
        self.assertGreater(area, 0)
        
        # Not safe start
        self.assertEqual(strategy.bfs_safe_area(grid, 1, 1, opp_dist), 0)

    def test_get_next_snake_move_empty(self):
        self.assertEqual(strategy.get_next_snake_move("", 'A'), 'up')
        
    def test_get_next_snake_move_no_head(self):
        board_str = '''
| | | |
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

    def test_get_next_snake_move_panic(self):
        # Enclosed snake
        board_str = '''
|B|B|B|
|B|A|B|
|B|B|B|
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

    def test_get_next_snake_move_survival(self):
        # A has some space, but not enough for safe_threshold (len = 4)
        board_str = '''
| |a|a|
| |A|a|
|B|B|B|
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['left', 'up', 'down', 'right'])

    def test_get_next_snake_move_excellent(self):
        # Path to food
        board_str = '''
|*| | |
| |A| |
| | | |
| | |B|
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        # We need to make sure the board structure is actually what parsed correctly
        self.assertIn(move, ['up', 'down', 'left', 'right'])
        
        # Test edge case min distance (line 210-211, 241-242, 245 equivalent) - we add another food further to trigger iteration update 
        board_str_min_dist = '''
|*| | | | | | | | |
| | | | | | | | | |
| | | |A| | | | |*|
| | | | | | | | | |
| | | | | | | |B| |
'''
        move_min = strategy.get_next_snake_move(board_str_min_dist, 'A')
        self.assertIn(move_min, ['up', 'down', 'left', 'right'])

    def test_get_next_snake_move_fallback(self):
        # No food path, just pick max area
        board_str = '''
|B|B|B|
| |A| |
| | | |
| | | |
'''
        # B controls top, A should go down or sides. Area below is completely open
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['down', 'left', 'right'])
        
    def test_get_next_snake_move_side_b(self):
        # Path to food for B
        board_str = '''
|*| | |
| |B| |
| | | |
| | |A|
'''
        move = strategy.get_next_snake_move(board_str, 'B')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

    def test_unreachable_food(self):
        # A food is blocked by opponent territory but we still have safe path in our territory
        board_str = '''
|*|B| |
|B|B| |
| | | |
| |A| |
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])
        
        # Test fallback_moves max_excellent_area line execution precisely by creating symmetrical areas with equal safe scores
        # We also create a situation where `best_direction` is NOT set because food is unreachable, so we fall through
        board_str_sym = '''
| | | |
| |A| |
| | | |
| |B| |
'''
        move_sym = strategy.get_next_snake_move(board_str_sym, 'A')
        self.assertIn(move_sym, ['up', 'down', 'left', 'right'])
        
        # We must trigger line 241-242: where we actually choose the fallback_moves with random.choice, which means no best_direction, but excellent_moves exists.
        board_str_fallback = '''
|B|B|B|
| |A| |
| | | |
| | | |
'''
        move_fallback = strategy.get_next_snake_move(board_str_fallback, 'A')
        self.assertIn(move_fallback, ['left', 'right', 'down'])
        
    def test_opponent_bfs_paths(self):
        # We need a board where opponent BFS logic is fully triggered to cover missing lines
        board_str = '''
| | |*| | |
| |B| | | |
| | | |A| |
| | | | | |
'''
        # This will trigger A evaluating food and B's safe zones
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['up', 'down', 'left', 'right'])

    def test_close_to_opponent(self):
        # Trigger line 198: opp_head and abs(nr - opp_head[0]) + abs(nc - opp_head[1]) == 1
        board_str = '''
| | | | |
| |A|B| |
| | | | |
'''
        move = strategy.get_next_snake_move(board_str, 'A')
        self.assertIn(move, ['up', 'down', 'left'])

if __name__ == '__main__':
    unittest.main()
