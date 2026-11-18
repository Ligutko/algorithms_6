# Лабораторна робота № 6. Просунуті структури для оптимізації та пошуку

Варіант 2. Мова: Python 3.

- Завдання 1 (`lab6_maxflow.py`): максимальний потік у логістичній мережі
  (2 термінали, 4 склади, 14 магазинів), алгоритм Едмондса-Карпа. Варіант 2:
  пропускна здатність ребер «Склад 4 → Магазини» зменшена на 50%.
  Для перевірки результату використовується бібліотека `networkx`.
- Завдання 2 (`lab6_trie.py`): клас `Homework(Trie)` з методами
  `count_words_with_suffix`, `has_prefix` і методами варіанта 2
  `longest_common_prefix`, `count_words_starting_with`. Базовий клас `Trie`
  (`trie.py`) взято без змін з репозиторію прикладів курсу
  https://github.com/zhukov-vntu/mlta-lr6.

## Запуск

```
python lab6_maxflow.py base      # базова задача і дані для відповідей
python lab6_maxflow.py variant   # варіант 2
python lab6_maxflow.py compare   # порівняння бази і варіанта
python lab6_maxflow.py sens      # потік залежно від зменшення ребер Складу 4
python lab6_maxflow.py check     # перевірка бібліотекою networkx

python lab6_trie.py template     # тести з шаблону
python lab6_trie.py variant      # тести методів варіанта 2
python lab6_trie.py errors       # некоректні вхідні дані
python lab6_trie.py check        # порівняння з прямим перебором
```

Без аргументу кожна програма виконує всі розділи.
