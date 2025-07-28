# -------- Grafo con distancias --------
graph = {
    'Arad': [('Zerind', 75), ('Timisoara', 118), ('Sibiu', 140)],
    'Zerind': [('Arad', 75), ('Oradea', 71)],
    'Oradea': [('Zerind', 71), ('Sibiu', 151)],
    'Timisoara': [('Arad', 118), ('Lugoj', 111)],
    'Lugoj': [('Timisoara', 111), ('Mehadia', 70)],
    'Mehadia': [('Lugoj', 70), ('Dobreta', 75)],
    'Dobreta': [('Mehadia', 75), ('Craiova', 120)],
    'Craiova': [('Dobreta', 120), ('Pitesti', 138), ('Rimnicu Vilcea', 146)],
    'Sibiu': [('Arad', 140), ('Oradea', 151), ('Fagaras', 99), ('Rimnicu Vilcea', 80)],
    'Fagaras': [('Sibiu', 99), ('Bucarest', 211)],
    'Rimnicu Vilcea': [('Sibiu', 80), ('Pitesti', 97), ('Craiova', 146)],
    'Pitesti': [('Rimnicu Vilcea', 97), ('Craiova', 138), ('Bucarest', 101)],
    'Bucarest': [('Fagaras', 211), ('Pitesti', 101), ('Giurgiu', 90), ('Urziceni', 85)],
    'Giurgiu': [('Bucarest', 90)],
    'Urziceni': [('Bucarest', 85), ('Hirsova', 98), ('Vaslui', 142)],
    'Hirsova': [('Urziceni', 98), ('Eforie', 86)],
    'Eforie': [('Hirsova', 86)],
    'Vaslui': [('Urziceni', 142), ('Iasi', 92)],
    'Iasi': [('Vaslui', 92), ('Neamt', 87)],
    'Neamt': [('Iasi', 87)]
}

# -------- Heurísticas --------
heuristics = {
    'Arad': 366, 'Zerind': 374, 'Oradea': 380, 'Timisoara': 329, 'Lugoj': 244,
    'Mehadia': 241, 'Dobreta': 242, 'Craiova': 160, 'Sibiu': 253, 'Fagaras': 176,
    'Rimnicu Vilcea': 193, 'Pitesti': 100, 'Bucarest': 0, 'Giurgiu': 77,
    'Urziceni': 80, 'Hirsova': 151, 'Eforie': 161, 'Vaslui': 199,
    'Iasi': 226, 'Neamt': 234
}

# -------- Nodo --------
class Nodo:
    def __init__(self, estado, padre=None, accion=None, costo=0, f=0):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.costo = costo  # g(n)
        self.f = f          # f(n) = max(g + h, f_padre)

    def expandir(self, problema):
        sucesores = []
        for sucesor, costo in problema.grafo.get(self.estado, []):
            nuevo_costo = self.costo + costo
            h = problema.heuristicas.get(sucesor, float('inf'))
            f = max(nuevo_costo + h, self.f)
            sucesores.append(Nodo(sucesor, self, self.estado, nuevo_costo, f))
        return sucesores

# -------- Problema --------
class Problema:
    def __init__(self, estado_inicial, objetivo, grafo, heuristicas):
        self.estado_inicial = estado_inicial
        self.objetivo = objetivo
        self.grafo = grafo
        self.heuristicas = heuristicas

    def es_objetivo(self, estado):
        return estado == self.objetivo

# -------- BRPM --------
def buscar_rbfs(problema):
    nodo_inicial = Nodo(problema.estado_inicial, costo=0, f=problema.heuristicas[problema.estado_inicial])
    resultado, _ = rbfs(problema, nodo_inicial, float('inf'))
    return resultado

def rbfs(problema, nodo, f_límite):
    if problema.es_objetivo(nodo.estado):
        return nodo, 0

    sucesores = nodo.expandir(problema)
    if not sucesores:
        return None, float('inf')

    while True:
        # Ordenar sucesores por f
        sucesores.sort(key=lambda n: n.f)
        mejor = sucesores[0]

        if mejor.f > f_límite:
            return None, mejor.f

        alternativa = sucesores[1].f if len(sucesores) > 1 else float('inf')
        resultado, mejor.f = rbfs(problema, mejor, min(f_límite, alternativa))
        if resultado is not None:
            return resultado, mejor.f

# -------- Reconstruir solución --------
def reconstruir_camino(nodo):
    camino = []
    while nodo:
        camino.append(nodo.estado)
        nodo = nodo.padre
    return list(reversed(camino))

# -------- Ejecución --------
problema = Problema('Arad', 'Bucarest', graph, heuristics)
solucion = buscar_rbfs(problema)

if solucion:
    camino = reconstruir_camino(solucion)
    print("Camino encontrado:", " → ".join(camino))
    print("Costo total:", solucion.costo)
else:
    print("No se encontró una solución.")
