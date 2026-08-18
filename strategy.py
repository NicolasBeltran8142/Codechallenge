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
    - '*': Las comidas.
    Las posiciones se guardan como "tuplas" (r, c).
    """
    head_a = None
    head_b = None
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
            elif cell == '*':
                foods.append((r, c))
                
    return head_a, head_b, foods

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

def flood_fill(grid, r, c):
    """
    [TEORIA] Algoritmo Flood Fill (Relleno por inundación)
    Este algoritmo sirve para responder a la pregunta: "Si doy un paso hacia acá, ¿cuánto espacio libre tendré?"
    Funciona como el balde de pintura en Paint. 
    1. Empezamos en la casilla a la que queremos ir (r, c).
    2. Miramos a nuestros 4 vecinos. Si están vacíos, los marcamos como "visitados" y sumamos +1 al área.
    3. Luego miramos a los vecinos de los vecinos, y así sucesivamente (usando una cola).
    4. Al final, nos devuelve cuántas casillas vacías están conectadas a nuestro punto de partida.
    Esto evita que la serpiente entre en callejones sin salida (áreas muy pequeñas).
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Si la celda inicial no es segura, el área es 0
    if not is_safe(grid, r, c):
        return 0

    visited = set()
    queue = [(r, c)]
    visited.add((r, c))
    area = 0
    
    # Mientras haya casillas por revisar en nuestra cola
    while queue:
        curr_r, curr_c = queue.pop(0)
        area += 1
        
        # Revisamos los 4 vecinos de la casilla actual
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            
            # Si el vecino no fue visitado aún y es un lugar seguro (vacío o comida)
            if (nr, nc) not in visited and is_safe(grid, nr, nc):
                visited.add((nr, nc))
                queue.append((nr, nc))
                
    return area

def get_next_snake_move(board_str, side):
    """
    [TEORIA] El "Cerebro" de la Serpiente
    Aquí juntamos toda la teoría para decidir el mejor movimiento:
    1. Parseamos el tablero.
    2. Buscamos dónde estamos y dónde está la comida.
    3. Miramos a qué casillas inmediatas podemos movernos sin chocar (safe_moves).
    4. Usamos Flood Fill para descartar movimientos que nos lleven a "callejones" (áreas más pequeñas que nuestra serpiente).
    5. De los movimientos seguros restantes, usamos la "Distancia de Manhattan" para elegir el que nos acerque más a la comida.
    """
    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, foods = find_positions(grid)
    
    # Identificamos cuál es nuestra cabeza dependiendo de qué lado nos asignó el servidor
    my_head = head_a if side == 'A' else head_b
    if not my_head:
        return random.choice(['up', 'down', 'left', 'right'])
        
    r, c = my_head
    
    # Direcciones posibles y cómo cambian nuestras coordenadas (fila, columna)
    moves = {
        'up': (r - 1, c),
        'down': (r + 1, c),
        'left': (r, c - 1),
        'right': (r, c + 1)
    }
    
    # Paso 1: Obtener movimientos que no sean chocar inmediatamente (Safe Moves)
    safe_moves = {}
    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc):
            # Paso 2: Usar Flood Fill para ver qué tan grande es el espacio si vamos por allí
            area = flood_fill(grid, nr, nc)
            safe_moves[direction] = area
            
    if not safe_moves:
        # Estamos completamente atrapados, solo podemos elegir al azar y morir con honor
        return random.choice(['up', 'down', 'left', 'right'])
        
    # Paso 3: Filtrar movimientos que nos lleven a espacios muy cerrados.
    # Si un espacio tiene menos de, digamos, 15 casillas conectadas, es probablemente un callejón mortal.
    # Encontramos cuál es el área máxima a la que podemos acceder.
    max_area = max(safe_moves.values())
    
    # Solo consideramos movimientos que nos lleven a un área decente (evita callejones tontos)
    # Para no ser tan estrictos, pedimos que el área sea al menos el 80% del área más grande que encontramos.
    viable_moves = [dir for dir, area in safe_moves.items() if area >= max_area * 0.8]
    
    # Si de alguna forma todos son malos, volvemos a la lista completa
    if not viable_moves:
        viable_moves = list(safe_moves.keys())
        
    # Paso 4: De los movimientos viables (no suicidas y no callejones), buscar la comida
    if foods:
        best_direction = None
        min_distance = float('inf')
        
        for direction in viable_moves:
            nr, nc = moves[direction]
            for fr, fc in foods:
                # [TEORIA] Distancia de Manhattan
                # Como en el juego no podemos movernos en diagonal, la distancia real
                # entre dos puntos no es una línea recta. Es la suma de la distancia horizontal
                # y la distancia vertical. ¡Como contar cuadras en una ciudad (Manhattan)!
                dist = abs(nr - fr) + abs(nc - fc)
                if dist < min_distance:
                    min_distance = dist
                    best_direction = direction
                    
        if best_direction:
            return best_direction

    # Si no hay comida (o algo falló), elegimos uno de los movimientos viables al azar
    return random.choice(viable_moves)
