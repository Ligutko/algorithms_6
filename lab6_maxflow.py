"""Лабораторна робота № 6. Просунуті структури для оптимізації та пошуку.

Завдання 1. Логістична мережа (Max Flow), алгоритм Едмондса-Карпа.
Варіант 2: пропускну здатність ребер "Склад 4 -> Магазини" зменшено на 50%.

Запуск: python lab6_maxflow.py [base | variant | compare | sens | check]
Без аргументу виконуються всі розділи.
"""
import sys
from collections import deque

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TERMINALS = ["Термінал 1", "Термінал 2"]
WAREHOUSES = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
STORES = [f"Магазин {i}" for i in range(1, 15)]

SOURCE_NAME = "Суперджерело"
SINK_NAME = "Суперстік"

# Пропускна здатність допоміжних ребер; перевищує суму всіх ребер мережі.
INF = 10 ** 9

# Ребра мережі (від, до, пропускна здатність) за таблицею методичних вказівок.
BASE_EDGES = [
    ("Термінал 1", "Склад 1", 25),
    ("Термінал 1", "Склад 2", 20),
    ("Термінал 1", "Склад 3", 15),
    ("Термінал 2", "Склад 3", 15),
    ("Термінал 2", "Склад 4", 30),
    ("Термінал 2", "Склад 2", 10),
    ("Склад 1", "Магазин 1", 15),
    ("Склад 1", "Магазин 2", 10),
    ("Склад 1", "Магазин 3", 20),
    ("Склад 2", "Магазин 4", 15),
    ("Склад 2", "Магазин 5", 10),
    ("Склад 2", "Магазин 6", 25),
    ("Склад 3", "Магазин 7", 20),
    ("Склад 3", "Магазин 8", 15),
    ("Склад 3", "Магазин 9", 10),
    ("Склад 4", "Магазин 10", 20),
    ("Склад 4", "Магазин 11", 10),
    ("Склад 4", "Магазин 12", 15),
    ("Склад 4", "Магазин 13", 5),
    ("Склад 4", "Магазин 14", 10),
]


def fmt(x) -> str:
    """Число без зайвого '.0': 15.0 -> '15', 7.5 -> '7.5'."""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def reduce_warehouse(edges, warehouse="Склад 4", percent=50):
    """Зменшує пропускну здатність усіх ребер від складу до магазинів на percent %."""
    result = []
    for u, v, c in edges:
        if u == warehouse and v in STORES:
            c = round(c * (100 - percent) / 100, 6)
        result.append((u, v, c))
    return result


def build_network(edges):
    """Матриця пропускної здатності 22 x 22: 20 вершин мережі,
    суперджерело (до обох терміналів) і суперстік (від усіх магазинів)."""
    nodes = [SOURCE_NAME] + TERMINALS + WAREHOUSES + STORES + [SINK_NAME]
    index = {name: i for i, name in enumerate(nodes)}
    capacity = [[0] * len(nodes) for _ in nodes]
    for terminal in TERMINALS:
        capacity[index[SOURCE_NAME]][index[terminal]] = INF
    for u, v, c in edges:
        capacity[index[u]][index[v]] += c
    for store in STORES:
        capacity[index[store]][index[SINK_NAME]] = INF
    return nodes, index, capacity


def bfs(capacity_matrix, flow_matrix, source, sink, parent):
    """Пошук збільшуючого шляху в залишковій мережі; шлях записується в parent."""
    visited = [False] * len(capacity_matrix)
    queue = deque([source])
    visited[source] = True
    while queue:
        current_node = queue.popleft()
        for neighbor in range(len(capacity_matrix)):
            residual = capacity_matrix[current_node][neighbor] \
                - flow_matrix[current_node][neighbor]
            if not visited[neighbor] and residual > 0:
                parent[neighbor] = current_node
                visited[neighbor] = True
                if neighbor == sink:
                    return True
                queue.append(neighbor)
    return False


def edmonds_karp(capacity_matrix, source, sink):
    """Максимальний потік. Повертає величину потоку, матрицю потоку
    і список кроків (шлях, потік шляху, сумарний потік)."""
    n = len(capacity_matrix)
    flow_matrix = [[0] * n for _ in range(n)]
    parent = [-1] * n
    max_flow = 0
    steps = []
    while bfs(capacity_matrix, flow_matrix, source, sink, parent):
        path_flow = float("inf")
        path = [sink]
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            path_flow = min(path_flow, capacity_matrix[previous_node][current_node]
                            - flow_matrix[previous_node][current_node])
            path.append(previous_node)
            current_node = previous_node
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            flow_matrix[previous_node][current_node] += path_flow
            flow_matrix[current_node][previous_node] -= path_flow
            current_node = previous_node
        max_flow += path_flow
        steps.append((path[::-1], path_flow, max_flow))
    return max_flow, flow_matrix, steps


def decompose(nodes, index, flow_matrix):
    """Розкладає підсумковий потік на шляхи 'термінал -> склад -> магазин'.
    Повертає словник {(термінал, магазин): потік}."""
    rest = [row[:] for row in flow_matrix]
    result = {}
    for terminal in TERMINALS:
        t = index[terminal]
        for warehouse in WAREHOUSES:
            w = index[warehouse]
            for store in STORES:
                s = index[store]
                amount = min(rest[t][w], rest[w][s])
                if amount > 0:
                    rest[t][w] -= amount
                    rest[w][s] -= amount
                    key = (terminal, store)
                    result[key] = result.get(key, 0) + amount
    return result


def min_cut(capacity_matrix, flow_matrix, source):
    """Мінімальний розріз: вершини, досяжні з source у залишковій мережі,
    і ребра з них до недосяжних вершин."""
    n = len(capacity_matrix)
    reachable = [False] * n
    queue = deque([source])
    reachable[source] = True
    while queue:
        u = queue.popleft()
        for v in range(n):
            if not reachable[v] and capacity_matrix[u][v] - flow_matrix[u][v] > 0:
                reachable[v] = True
                queue.append(v)
    cut = [(u, v) for u in range(n) for v in range(n)
           if reachable[u] and not reachable[v] and capacity_matrix[u][v] > 0]
    return reachable, cut


def solve(edges):
    """Повний розрахунок для одного набору ребер."""
    nodes, index, capacity = build_network(edges)
    source, sink = index[SOURCE_NAME], index[SINK_NAME]
    max_flow, flow, steps = edmonds_karp(capacity, source, sink)
    _, cut = min_cut(capacity, flow, source)
    return {
        "edges": edges, "nodes": nodes, "index": index, "capacity": capacity,
        "max_flow": max_flow, "flow": flow, "steps": steps, "cut": cut,
        "pairs": decompose(nodes, index, flow),
    }


def edge_flow(res, u, v):
    return res["flow"][res["index"][u]][res["index"][v]]


def received(res, store):
    """Скільки одиниць отримав магазин."""
    return sum(edge_flow(res, w, store) for w in WAREHOUSES)


def short_path(res, path):
    """Шлях без допоміжних вершин: 'Термінал 1 -> Склад 1 -> Магазин 1'."""
    names = [res["nodes"][i] for i in path[1:-1]]
    return " -> ".join(names)


def print_report(title, res):
    print("=" * 70)
    print(title)
    print("=" * 70)
    print("Збільшуючі шляхи (алгоритм Едмондса-Карпа):")
    print(f"{'Крок':>4}  {'Шлях':<40} {'Потік шляху':>11} {'Сумарний':>9}")
    for k, (path, pf, total) in enumerate(res["steps"], 1):
        print(f"{k:>4}  {short_path(res, path):<40} {fmt(pf):>11} {fmt(total):>9}")
    print(f"Максимальний потік: {fmt(res['max_flow'])}")
    print()
    print("Фактичні потоки 'термінал -> магазин':")
    for (t, s), amount in sorted(res["pairs"].items(),
                                 key=lambda kv: (kv[0][0], int(kv[0][1].split()[1]))):
        print(f"  {t} -> {s:<11} {fmt(amount):>5}")
    print()
    print("Мінімальний розріз:")
    names = res["nodes"]
    total = 0
    for u, v in res["cut"]:
        c = res["capacity"][u][v]
        total += c
        print(f"  {names[u]} -> {names[v]}: {fmt(c)}")
    print(f"  Сума пропускних здатностей розрізу: {fmt(total)}")
    print()


def print_answers(res):
    """Дані для відповідей на чотири запитання методичних вказівок."""
    mf = res["max_flow"]
    print("Запитання 1. Потік від терміналів:")
    for t in TERMINALS:
        sent = sum(edge_flow(res, t, w) for w in WAREHOUSES)
        cap = sum(c for u, _, c in res["edges"] if u == t)
        print(f"  {t}: {fmt(sent)} з {fmt(cap)} ({100 * sent / mf:.1f}% потоку)")
    print("Запитання 2. Найменші пропускні здатності:")
    smallest = sorted(res["edges"], key=lambda e: e[2])[:7]
    for u, v, c in smallest:
        print(f"  {u} -> {v}: {fmt(c)}, потік {fmt(edge_flow(res, u, v))}")
    print("Запитання 3. Магазини (отримано / можливо):")
    for s in STORES:
        cap = sum(c for _, v, c in res["edges"] if v == s)
        print(f"  {s:<11} {fmt(received(res, s)):>5} / {fmt(cap)}")
    print("Запитання 4. Завантаження складів:")
    for w in WAREHOUSES:
        cap_in = sum(c for _, v, c in res["edges"] if v == w)
        cap_out = sum(c for u, _, c in res["edges"] if u == w)
        got = sum(edge_flow(res, t, w) for t in TERMINALS)
        print(f"  {w}: отримано {fmt(got)} з {fmt(cap_in)}, "
              f"може віддати {fmt(cap_out)}")
    print()


def print_compare(base, var):
    region = STORES[9:]
    print("=" * 70)
    print("Порівняння: базова задача і варіант 2")
    print("=" * 70)
    print(f"{'Показник':<38}{'База':>10}{'Варіант 2':>12}")
    rows = [
        ("Максимальний потік", base["max_flow"], var["max_flow"]),
        ("Кількість збільшуючих шляхів", len(base["steps"]), len(var["steps"])),
        ("Вихід Складу 4 (сума ребер)",
         sum(c for u, _, c in base["edges"] if u == "Склад 4"),
         sum(c for u, _, c in var["edges"] if u == "Склад 4")),
        ("Вхід Складу 4 (Термінал 2 -> Склад 4)",
         edge_flow(base, "Термінал 2", "Склад 4"), edge_flow(var, "Термінал 2", "Склад 4")),
    ]
    for name, a, b in rows:
        print(f"{name:<38}{fmt(a):>10}{fmt(b):>12}")
    print("Магазини 10-14 (отримано / пропускна здатність):")
    for s in region:
        cb = sum(c for _, v, c in base["edges"] if v == s)
        cv = sum(c for _, v, c in var["edges"] if v == s)
        print(f"  {s:<11}{fmt(received(base, s)):>6} / {fmt(cb):<4}"
              f"{fmt(received(var, s)):>10} / {fmt(cv)}")
    print()


def sensitivity(steps=range(0, 101, 10)):
    """Максимальний потік залежно від відсотка зменшення ребер Склад 4 -> Магазини."""
    return [(p, solve(reduce_warehouse(BASE_EDGES, percent=p))["max_flow"]) for p in steps]


def print_sensitivity():
    print("=" * 70)
    print("Максимальний потік залежно від зменшення 'Склад 4 -> Магазини'")
    print("=" * 70)
    print(f"{'Зменшення, %':>13}{'Вихід Складу 4':>16}{'Макс. потік':>13}")
    for p, mf in sensitivity():
        out = sum(c for u, _, c in reduce_warehouse(BASE_EDGES, percent=p) if u == "Склад 4")
        print(f"{p:>13}{fmt(out):>16}{fmt(mf):>13}")
    print()


def print_check():
    """Незалежна перевірка: networkx.maximum_flow на тих самих ребрах."""
    import networkx as nx
    print("=" * 70)
    print("Перевірка бібліотекою networkx")
    print("=" * 70)
    for title, edges in [("База", BASE_EDGES), ("Варіант 2", reduce_warehouse(BASE_EDGES))]:
        g = nx.DiGraph()
        for u, v, c in edges:
            g.add_edge(u, v, capacity=c)
        for t in TERMINALS:
            g.add_edge(SOURCE_NAME, t, capacity=INF)
        for s in STORES:
            g.add_edge(s, SINK_NAME, capacity=INF)
        value, _ = nx.maximum_flow(g, SOURCE_NAME, SINK_NAME)
        own = solve(edges)["max_flow"]
        print(f"  {title}: networkx = {fmt(value)}, Едмондс-Карп = {fmt(own)}, "
              f"{'збігається' if value == own else 'НЕ збігається'}")
    print()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    base = solve(BASE_EDGES)
    var = solve(reduce_warehouse(BASE_EDGES))
    if mode in ("base", "all"):
        print_report("БАЗОВА ЗАДАЧА", base)
        print_answers(base)
    if mode in ("variant", "all"):
        print_report("ВАРІАНТ 2: Склад 4 -> Магазини, пропускна здатність -50%", var)
    if mode in ("compare", "all"):
        print_compare(base, var)
    if mode in ("sens", "all"):
        print_sensitivity()
    if mode in ("check", "all"):
        print_check()
