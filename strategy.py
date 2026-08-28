import random

def parse_board(board_str):
    """
    [TEORIA] Representación del Tablero
    El servidor nos envía el tablero como un bloque de texto gigante. 
    Para una computadora es difícil analizar un solo texto largo, por lo que convertimos
    este texto en una "Grilla Bidimensional" o Matriz (una lista de listas).
    Imagina que es como una hoja cuadriculada. Cada fila es una lista, y cada celda
    tiene una coordenada (r, c) donde 'r' es la fila (row) y 'c' es la columna (col).
    """
    lines = board_str.strip().split('\n')
    grid = []
    for line in lines:
        # Solo procesamos las líneas que empiezan y terminan con '|' (los bordes)
        if line.startswith('|') and line.endswith('|'):
            # Quitamos los '|' de los extremos para quedarnos solo con el contenido
            row = list(line[1:-1])
            grid.append(row)
    return grid

def find_positions(grid):
    """
    [TEORIA] Escaneo de la Grilla
    Una vez que tenemos nuestra "hoja cuadriculada" (grid), la recorremos celda por celda
    usando dos bucles (uno para filas, otro para columnas). 
    Anotamos las coordenadas de todo lo que nos importa:
    - 'A' y 'B': Las cabezas de las serpientes.
    - 'a' y 'b': Los cuerpos de las serpientes (para saber qué tan largos somos).
    - '*': Las comidas.
    Las posiciones se guardan como "tuplas" (r, c).
    """
    head_a = None
    head_b = None
    length_a = 1
    length_b = 1
    foods = []
    
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell == 'A':
                head_a = (r, c)
            elif cell == 'B':
                head_b = (r, c)
            elif cell == 'a':
                length_a += 1
            elif cell == 'b':
                length_b += 1
            elif cell == '*':
                foods.append((r, c))
                
    return head_a, head_b, foods, length_a, length_b

def is_safe(grid, r, c):
    """
    [TEORIA] Validación de Movimiento
    Antes de movernos a una coordenada (r, c), debemos verificar:
    1. Que no nos caigamos del mapa (que 'r' y 'c' estén dentro de los límites de la matriz).
    2. Que la celda esté vacía (' ') o tenga comida ('*'). Si tiene letras, es un cuerpo y moriremos.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # 1. Límites del mapa
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
        
    cell = grid[r][c]
    # 2. Obstáculos
    if cell not in (' ', '*'):
        return False
        
    return True

from collections import deque

def bfs_distances(grid, start_r, start_c):
    """
    [TEORIA] Búsqueda en Anchura (BFS - Breadth-First Search)
    Calcula la distancia real (en cantidad de pasos) desde (start_r, start_c)
    hasta todas las casillas alcanzables en el mapa, esquivando obstáculos.
    Devuelve un diccionario {(r, c): distancia}.
    """
    if not is_safe(grid, start_r, start_c):
        return {}

    distances = {(start_r, start_c): 0}
    queue = deque([(start_r, start_c)])
    
    while queue:
        curr_r, curr_c = queue.popleft()
        curr_dist = distances[(curr_r, curr_c)]

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc) and (nr, nc) not in distances:
                distances[(nr, nc)] = curr_dist + 1
                queue.append((nr, nc))

    return distances

def bfs_safe_area(grid, start_r, start_c, opponent_distances):
    """
    [TEORIA] Control de Territorio y Área Segura
    Calcula cuántas casillas de espacio libre real tenemos si empezamos a caminar
    desde (start_r, start_c), pero ¡OJO! descontando las casillas a las que el
    oponente puede llegar antes o al mismo tiempo que nosotros.
    Esto evita que nos encierren.
    """
    if not is_safe(grid, start_r, start_c):
        return 0

    visited = {(start_r, start_c)}
    queue = deque([(start_r, start_c, 1)]) # (fila, columna, nuestra_distancia_pasos)
    area = 0
    
    while queue:
        curr_r, curr_c, my_dist = queue.popleft()

        # Verificamos si esta casilla está en peligro por el oponente
        opp_dist = opponent_distances.get((curr_r, curr_c), float('inf'))
        # Si el oponente llega antes o en el mismo turno, descartamos seguir por acá (territorio enemigo)
        if opp_dist <= my_dist:
            continue

        area += 1
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, my_dist + 1))
                
    return area

def get_next_snake_move(board_str, side):
    """
    [TEORIA] El "Cerebro" de la Serpiente Mejorado
    1. Parseamos el tablero.
    2. Calculamos las distancias del oponente a todo el mapa mediante BFS.
    3. Evaluamos nuestros movimientos seguros (inmediatos).
    4. Para cada movimiento seguro, calculamos el "Territorio Seguro" usando BFS,
       esquivando las zonas que el enemigo domina.
    5. Evaluamos si el movimiento nos acerca a una comida (usando distancias BFS reales, no Manhattan),
       siempre y cuando nos deje suficiente espacio de vida.
    """
    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, foods, length_a, length_b = find_positions(grid)
    
    my_head = head_a if side == 'A' else head_b
    my_length = length_a if side == 'A' else length_b
    
    opp_head = head_b if side == 'A' else head_a

    if not my_head:
        return random.choice(['up', 'down', 'left', 'right'])
        
    r, c = my_head
    
    # Pre-calculamos qué zonas controla el oponente.
    # Si no hay oponente en el mapa, sus distancias serán infinitas.
    opp_distances = {}
    if opp_head:
        # Iniciamos un BFS falso desde los vecinos del oponente para simular su movimiento
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = opp_head[0] + dr, opp_head[1] + dc
            if is_safe(grid, nr, nc):
                sub_dists = bfs_distances(grid, nr, nc)
                for pos, dist in sub_dists.items():
                    # Su distancia real es 1 (el primer paso) + la distancia desde allí
                    actual_dist = dist + 1
                    if pos not in opp_distances or actual_dist < opp_distances[pos]:
                        opp_distances[pos] = actual_dist

    moves = {
        'up': (r - 1, c),
        'down': (r + 1, c),
        'left': (r, c - 1),
        'right': (r, c + 1)
    }
    
    safe_moves_data = {}

    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc):
            # [TEORIA] Evitar Choques de Cabeza
            # Si el movimiento es adyacente a la cabeza del oponente, es muy riesgoso
            if opp_head and abs(nr - opp_head[0]) + abs(nc - opp_head[1]) == 1:
                # Si somos mucho más cortos, es una muerte segura
                # Por ahora, simplemente penalizaremos ir allí dándole área 0 si no es el último recurso
                pass # Podemos mejorar esto luego

            # Calculamos área controlada si vamos en esta dirección
            area = bfs_safe_area(grid, nr, nc, opp_distances)

            # Calculamos las distancias reales (BFS) a toda la grilla desde este paso
            my_dists = bfs_distances(grid, nr, nc)
            
            # Distancia a la comida más cercana
            closest_food_dist = float('inf')
            for fr, fc in foods:
                if (fr, fc) in my_dists:
                    if my_dists[(fr, fc)] < closest_food_dist:
                        closest_food_dist = my_dists[(fr, fc)]

            safe_moves_data[direction] = {
                'area': area,
                'food_dist': closest_food_dist
            }

    if not safe_moves_data:
        # Pánico total
        return random.choice(['up', 'down', 'left', 'right'])
        
    # Necesitamos un espacio mínimo para no morir enrollados.
    # Dado que ahora el BFS descuenta zonas enemigas, seremos un poco conservadores.
    safe_threshold = my_length
    
    excellent_moves = [d for d, data in safe_moves_data.items() if data['area'] >= safe_threshold]
    
    if not excellent_moves:
        # Supervivencia estricta: tomar el que nos de más área libre.
        max_area = max(data['area'] for data in safe_moves_data.values())
        survival_moves = [d for d, data in safe_moves_data.items() if data['area'] == max_area]
        return random.choice(survival_moves)
        
    # De los movimientos seguros, elegimos el que nos acerque más a la comida
    best_direction = None
    min_dist = float('inf')

    for direction in excellent_moves:
        data = safe_moves_data[direction]
        if data['food_dist'] < min_dist:
            min_dist = data['food_dist']
            best_direction = direction

    if best_direction:
        return best_direction
        
    # Si no hay ruta a la comida pero estamos a salvo (por ej. manzanas bloqueadas por el enemigo),
    # elegimos el que nos de mayor territorio
    max_excellent_area = max(safe_moves_data[d]['area'] for d in excellent_moves)
    fallback_moves = [d for d in excellent_moves if safe_moves_data[d]['area'] == max_excellent_area]

    return random.choice(fallback_moves)
