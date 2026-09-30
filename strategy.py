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
    [TEORIA] Escaneo de la Grilla (Actualizado v4)
    Anotamos las coordenadas de:
    - 'A', 'a', 'B', 'b': Serpientes
    - '1'-'9': Comidas numéricas
    - 'x': Power-ups (multiplicadores)
    Devuelve las cabezas, los power-ups, todos los dígitos encontrados con su valor, y las longitudes.
    """
    head_a = None
    head_b = None
    length_a = 1
    length_b = 1
    powerups = []
    digits = {} # {(r, c): int_value}
    
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
            elif cell in ('x', 'X'):
                powerups.append((r, c))
            elif cell.isdigit():
                digits[(r, c)] = int(cell)
                
    return head_a, head_b, powerups, digits, length_a, length_b

def get_target_digit(digits_dict):
    """
    [TEORIA] Matemática Modular para la Comida Cíclica
    Si tenemos 5 números consecutivos cíclicos (ej. 8, 9, 1, 2, 3), el "primero"
    (el que hay que comer) siempre es el que está a la derecha del hueco o "salto" más grande
    cuando los ordenamos de menor a mayor.
    En el ejemplo ordenado: 1, 2, 3, 8, 9
    Saltos: 2-1=1, 3-2=1, 8-3=5 (¡Salto grande!), 9-8=1, y 1-9 (cíclico) = (1-9)%9 = 1
    El salto más grande es del 3 al 8. Por ende, la secuencia termina en 3 y empieza en 8.
    """
    if not digits_dict:
        return None
        
    # En la regla v6 hay múltiples copias, por lo que convertimos a set para ordenarlos únicos
    vals = sorted(list(set(digits_dict.values())))
    if len(vals) == 1:
        return vals[0]
        
    max_gap = 0
    target_val = vals[0]
    
    for i in range(len(vals)):
        # Calculamos la distancia al siguiente número único (cíclica)
        # Asumimos que los dígitos válidos son del 1 al 9, módulo 9 (donde 0 equivale a 9)
        v1 = vals[i]
        v2 = vals[(i + 1) % len(vals)]
        
        # Distancia en el ciclo de 1 a 9 avanzando hacia adelante
        gap = (v2 - v1) % 9
        if gap == 0:
            pass
            
        if gap > max_gap:
            max_gap = gap
            target_val = v2
            
    return target_val


def is_safe(grid, r, c, target_digit=None):
    """
    [TEORIA] Validación de Movimiento
    Debemos verificar:
    1. Límites del mapa.
    2. Obstáculos. ' ' y 'x' son seguros siempre.
    3. Si hay un dígito, SOLO es seguro si es exactamente igual a target_digit.
       Cualquier otro número es un veneno (-500 pts) y actuará como un muro.
    4. Los muros '#' también son obstáculos (regla v5).
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
        
    cell = grid[r][c]
    if cell in (' ', 'x', 'X'):
        return True
        
    if cell == '#':
        return False # Muro de regla v5 = PELIGRO

    if cell.isdigit():
        if target_digit is not None and int(cell) == target_digit:
            return True
        return False # Número equivocado = MUERTE
        
    # 'A', 'B', 'a', 'b', etc
    return False

from collections import deque

def bfs_distances(grid, start_r, start_c, target_digit=None):
    """
    [TEORIA] Búsqueda en Anchura (BFS - Breadth-First Search)
    Calcula la distancia real (en cantidad de pasos) desde (start_r, start_c)
    hasta todas las casillas alcanzables en el mapa, esquivando obstáculos.
    Devuelve un diccionario {(r, c): distancia}.
    """
    if not is_safe(grid, start_r, start_c, target_digit):
        return {}
        
    distances = {(start_r, start_c): 0}
    queue = deque([(start_r, start_c)])
    
    while queue:
        curr_r, curr_c = queue.popleft()
        curr_dist = distances[(curr_r, curr_c)]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc, target_digit) and (nr, nc) not in distances:
                distances[(nr, nc)] = curr_dist + 1
                queue.append((nr, nc))
                
    return distances

def bfs_safe_area(grid, start_r, start_c, opponent_distances, target_digit=None):
    """
    [TEORIA] Control de Territorio y Área Segura
    Calcula cuántas casillas de espacio libre real tenemos si empezamos a caminar 
    desde (start_r, start_c), pero ¡OJO! descontando las casillas a las que el 
    oponente puede llegar antes o al mismo tiempo que nosotros.
    Esto evita que nos encierren.
    """
    if not is_safe(grid, start_r, start_c, target_digit):
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
            if is_safe(grid, nr, nc, target_digit) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, my_dist + 1))
                
    return area

def get_next_snake_move(board_str, side, multiplier=1):
    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, powerups, digits_dict, length_a, length_b = find_positions(grid)
    target_digit = get_target_digit(digits_dict)
    
    my_head = head_a if side == 'A' else head_b
    my_length = length_a if side == 'A' else length_b
    opp_head = head_b if side == 'A' else head_a
    opp_length = length_b if side == 'A' else length_a
    
    if not my_head:
        return random.choice(['up', 'down', 'left', 'right'])
        
    r, c = my_head
    
    opp_distances = {}
    if opp_head:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = opp_head[0] + dr, opp_head[1] + dc
            if is_safe(grid, nr, nc, target_digit):
                sub_dists = bfs_distances(grid, nr, nc, target_digit)
                for pos, dist in sub_dists.items():
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
    target_digit_coords = [coord for coord, val in digits_dict.items() if val == target_digit]
    
    # Pre-evaluación de objetivos competitivos
    # Determinamos qué objetivos son "nuestros" (llegamos antes o igual que el rival)
    # y calculamos un "deseo" general para cada objetivo
    
    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc, target_digit):
            penalty = 0
            if opp_head and abs(nr - opp_head[0]) + abs(nc - opp_head[1]) == 1:
                # Si el oponente es más grande o igual, un choque de cabezas nos matará o empatará. Evitar si es posible.
                if opp_length >= my_length:
                    penalty += 5000 # Penalización masiva por riesgo de choque de cabezas

            # Penalización por moverse cerca de muros '#' (para evitar ser aplastados)
            # Chequeamos si hay muros adyacentes
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                wr, wc = nr + dr, nc + dc
                if 0 <= wr < len(grid) and 0 <= wc < len(grid[0]) and grid[wr][wc] == '#':
                    penalty += 100 # Pequeña penalización por estar al lado de un muro que se encoge
                
            area = bfs_safe_area(grid, nr, nc, opp_distances, target_digit)
            my_dists = bfs_distances(grid, nr, nc, target_digit)
            
            # Evaluación equilibrada de objetivos
            best_obj_score = -float('inf')
            
            # Evaluamos Powerups (X)
            # Valor base para priorizar, diluido por la distancia.
            # Si ya tenemos un multiplicador alto, los powerups adicionales valen un poco menos en relación a la comida.
            powerup_base_value = 1000.0 / max(1, (multiplier * 0.5)) 
            for pu in powerups:
                if pu in my_dists:
                    my_dist_to_pu = my_dists[pu]
                    opp_dist_to_pu = opp_distances.get(pu, float('inf'))
                    
                    # Solo lo deseamos si llegamos antes o al mismo tiempo (competimos)
                    if my_dist_to_pu <= opp_dist_to_pu:
                        # Puntuación = valor / (distancia + 1)
                        score = powerup_base_value / (my_dist_to_pu + 1)
                        if score > best_obj_score:
                            best_obj_score = score
                            
            # Evaluamos Comida Regular (Dígito Correcto)
            # La comida se escala directamente con el multiplicador que ya tenemos.
            food_base_value = 200.0 * multiplier
            
            # En v6, el oponente puede comer CUALQUIER copia del dígito y todas desaparecen.
            # Calculamos la distancia mínima del oponente a CUALQUIER copia del target_digit.
            min_opp_dist_to_any_food = float('inf')
            for t_coord in target_digit_coords:
                if t_coord in opp_distances:
                    min_opp_dist_to_any_food = min(min_opp_dist_to_any_food, opp_distances[t_coord])

            for t_coord in target_digit_coords:
                if t_coord in my_dists:
                    my_dist_to_food = my_dists[t_coord]
                    
                    # Comparamos nuestra distancia a esta copia vs. la distancia del oponente a la copia MAS CERCANA a él.
                    # Si él llega a su copia antes de que nosotros a la nuestra, abandonamos este objetivo, porque lo robará.
                    if my_dist_to_food <= min_opp_dist_to_any_food:
                        score = food_base_value / (my_dist_to_food + 1)
                        if score > best_obj_score:
                            best_obj_score = score
            
            # Aplicar la penalización de peligro al obj_score
            final_score = best_obj_score - penalty if best_obj_score != -float('inf') else -penalty

            safe_moves_data[direction] = {
                'area': area,
                'obj_score': final_score
            }
            
    if not safe_moves_data:
        return random.choice(['up', 'down', 'left', 'right'])
        
    safe_threshold = my_length
    excellent_moves = [d for d, data in safe_moves_data.items() if data['area'] >= safe_threshold]
    
    if not excellent_moves:
        max_area = max(data['area'] for data in safe_moves_data.values())
        survival_moves = [d for d, data in safe_moves_data.items() if data['area'] == max_area]
        return random.choice(survival_moves)
        
    # Elegimos el movimiento excelente que nos lleve al objetivo con mayor puntuación
    best_direction = None
    max_score = -float('inf')
    
    for direction in excellent_moves:
        data = safe_moves_data[direction]
        if data['obj_score'] > max_score:
            max_score = data['obj_score']
            best_direction = direction
            
    if best_direction and max_score > -float('inf'):
        return best_direction
        
    # Si no hay rutas a ningún objetivo que podamos ganar, elegimos el que dé más área libre (supervivencia pasiva)
    max_excellent_area = max(safe_moves_data[d]['area'] for d in excellent_moves)
    fallback_moves = [d for d in excellent_moves if safe_moves_data[d]['area'] == max_excellent_area]
    
    return random.choice(fallback_moves)