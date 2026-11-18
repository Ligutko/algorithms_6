"""Лабораторна робота № 6. Просунуті структури для оптимізації та пошуку.

Завдання 2. Розширення класу Trie (префіксне дерево).
Базові методи: count_words_with_suffix(pattern), has_prefix(prefix).
Варіант 2: longest_common_prefix(), count_words_starting_with(prefix).

Базовий клас Trie (файл trie.py) взято з репозиторію прикладів курсу
https://github.com/zhukov-vntu/mlta-lr6 без змін.

Запуск: python lab6_trie.py [template | suffix | variant | errors | check | scale]
Без аргументу виконуються всі розділи.
"""
import os
import random
import sys

from trie import Trie

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class Homework(Trie):

    @staticmethod
    def _check(text, name):
        """Перевірка аргументу: тільки непорожній рядок."""
        if not isinstance(text, str):
            raise TypeError(f"{name} має бути рядком, отримано {type(text).__name__}")
        if not text:
            raise ValueError(f"{name} не може бути порожнім рядком")

    def _find_node(self, prefix):
        """Вузол, у якому закінчується prefix, або None, якщо такого шляху немає."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    @staticmethod
    def _count_words(node):
        """Кількість слів у піддереві вузла (вузли з value, відмінним від None)."""
        count = 0
        stack = [node]
        while stack:
            current = stack.pop()
            if current.value is not None:
                count += 1
            stack.extend(current.children.values())
        return count

    def count_words_with_suffix(self, pattern) -> int:
        """Кількість слів, що закінчуються на pattern (з урахуванням регістру)."""
        self._check(pattern, "pattern")
        count = 0
        for word in self.keys():
            if word.endswith(pattern):
                count += 1
        return count

    def has_prefix(self, prefix) -> bool:
        """True, якщо в дереві є хоча б одне слово з префіксом prefix."""
        self._check(prefix, "prefix")
        node = self._find_node(prefix)
        if node is None:
            return False
        stack = [node]
        while stack:
            current = stack.pop()
            if current.value is not None:
                return True
            stack.extend(current.children.values())
        return False

    def longest_common_prefix(self) -> str:
        """Найдовший спільний префікс усіх слів дерева; '' для порожнього дерева."""
        if self._count_words(self.root) == 0:
            return ""
        node = self.root
        prefix = []
        while len(node.children) == 1 and node.value is None:
            char, node = next(iter(node.children.items()))
            prefix.append(char)
        return "".join(prefix)

    def count_words_starting_with(self, prefix) -> int:
        """Кількість слів, що починаються з prefix (з урахуванням регістру)."""
        self._check(prefix, "prefix")
        node = self._find_node(prefix)
        if node is None:
            return 0
        return self._count_words(node)


def make_trie(words):
    trie = Homework()
    for i, word in enumerate(words):
        trie.put(word, i)
    return trie


def show(call, expected, got):
    status = "OK" if expected == got else "ПОМИЛКА"
    print(f"  {call:<48} очікується {expected!r:<9} отримано {got!r:<9} {status}")
    assert expected == got, call


def run_template():
    """Тести з шаблону програми методичних вказівок."""
    print("=" * 78)
    print("Базові методи: тести з шаблону")
    print("=" * 78)
    words = ["apple", "application", "banana", "cat"]
    trie = make_trie(words)
    print(f"Слова: {words}")
    for pattern, exp in [("e", 1), ("ion", 1), ("a", 1), ("at", 1), ("E", 0), ("p", 0)]:
        show(f'count_words_with_suffix("{pattern}")', exp, trie.count_words_with_suffix(pattern))
    for prefix, exp in [("app", True), ("bat", False), ("ban", True), ("ca", True),
                        ("App", False), ("applications", False)]:
        show(f'has_prefix("{prefix}")', exp, trie.has_prefix(prefix))
    print()


SUFFIX_WORDS = ["ion", "lion", "onion", "nation", "Nation", "station", "NATION",
                "apple"]


def run_suffix():
    """Базові методи на наборі, де суфікс має кілька слів, збігається з
    цілим словом, відрізняється регістром і довший за слова."""
    print("=" * 78)
    print("Базові методи: кілька слів з одним закінченням, регістр, ціле слово")
    print("=" * 78)
    trie = make_trie(SUFFIX_WORDS)
    print(f"Слова: {SUFFIX_WORDS}")
    for pattern, exp in [("ion", 6), ("ation", 3), ("Nation", 1), ("ION", 1),
                         ("onion", 1), ("stations", 0)]:
        show(f'count_words_with_suffix("{pattern}")', exp,
             trie.count_words_with_suffix(pattern))
    for prefix, exp in [("ion", True), ("Na", True), ("nA", False),
                        ("stations", False)]:
        show(f'has_prefix("{prefix}")', exp, trie.has_prefix(prefix))
    print()


def best_time(fn, repeat):
    """Найменший час одного виклику fn() у мікросекундах із repeat запусків."""
    import time
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        result = fn()
        best = min(best, time.perf_counter() - t0)
    return result, best * 1_000_000


def run_scale(n_words=100_000, seed=6, prefix="abc", suffix="abc"):
    """Час методів на дереві з n_words випадкових слів (a-z, довжина 3-10)
    порівняно з переглядом списку слів. Повертає словник результатів."""
    rng = random.Random(seed)
    letters = "abcdefghijklmnopqrstuvwxyz"
    words = sorted({"".join(rng.choice(letters) for _ in range(rng.randint(3, 10)))
                    for _ in range(n_words)})
    trie = make_trie(words)
    rows = [
        ("count_words_starting_with", f'"{prefix}"',
         *best_time(lambda: trie.count_words_starting_with(prefix), 200)),
        ("has_prefix", f'"{prefix}"', *best_time(lambda: trie.has_prefix(prefix), 200)),
        ("список: startswith", f'"{prefix}"',
         *best_time(lambda: sum(w.startswith(prefix) for w in words), 15)),
        ("count_words_with_suffix", f'"{suffix}"',
         *best_time(lambda: trie.count_words_with_suffix(suffix), 5)),
        ("список: endswith", f'"{suffix}"',
         *best_time(lambda: sum(w.endswith(suffix) for w in words), 15)),
    ]
    assert rows[0][2] == rows[2][2] and rows[3][2] == rows[4][2]
    assert rows[1][2] == (rows[0][2] > 0)
    print("=" * 78)
    print(f"Масштаб: дерево з {len(words)} випадкових слів (a-z, довжина 3-10)")
    print("=" * 78)
    print(f"  {'Метод':<28}{'Аргумент':<10}{'Результат':>10}{'Час, мкс':>12}")
    for name, arg, res, us in rows:
        shown = f"{us:.1f}" if us < 100 else f"{us:.0f}"
        print(f"  {name:<28}{arg:<10}{str(res):>10}{shown:>12}")
    print()
    return {"n_words": len(words), "rows": rows}


def run_variant():
    """Тести методів варіанта 2."""
    print("=" * 78)
    print("Варіант 2: longest_common_prefix()")
    print("=" * 78)
    cases = [
        (["flower", "flow", "flight"], "fl"),
        (["interspecies", "interstellar", "interstate"], "inters"),
        (["dog", "racecar", "car"], ""),
        (["car", "card", "cards"], "car"),
        (["Apple", "apple"], ""),
        (["banana"], "banana"),
        ([], ""),
    ]
    for words, exp in cases:
        show(f"{words}", exp, make_trie(words).longest_common_prefix())
    print()
    print("=" * 78)
    print("Варіант 2: count_words_starting_with(prefix)")
    print("=" * 78)
    words = ["app", "apple", "application", "apply", "band", "banana", "Bandit"]
    trie = make_trie(words)
    print(f"Слова: {words}")
    for prefix, exp in [("app", 4), ("appl", 3), ("apple", 1), ("ban", 2),
                        ("Ban", 1), ("b", 2), ("cat", 0), ("applications", 0)]:
        show(f'count_words_starting_with("{prefix}")', exp,
             trie.count_words_starting_with(prefix))
    print()


def run_errors():
    """Обробка некоректних вхідних даних."""
    print("=" * 78)
    print("Некоректні вхідні дані")
    print("=" * 78)
    trie = make_trie(["apple", "banana"])
    calls = [
        ("has_prefix(123)", lambda: trie.has_prefix(123)),
        ("has_prefix('')", lambda: trie.has_prefix("")),
        ("count_words_with_suffix(None)", lambda: trie.count_words_with_suffix(None)),
        ("count_words_with_suffix('')", lambda: trie.count_words_with_suffix("")),
        ("count_words_starting_with(['a'])", lambda: trie.count_words_starting_with(["a"])),
        ("count_words_starting_with('')", lambda: trie.count_words_starting_with("")),
    ]
    for name, fn in calls:
        try:
            fn()
            print(f"  {name:<36} виняток не виникнув  ПОМИЛКА")
            raise AssertionError(name)
        except (TypeError, ValueError) as e:
            print(f"  {name:<36} {type(e).__name__}: {e}")
    print()


def run_check(trials=1000, seed=6):
    """Порівняння методів із прямим перебором списку слів на випадкових наборах."""
    print("=" * 78)
    print(f"Перевірка на {trials} випадкових наборах слів (алфавіт 'a', 'b', 'A')")
    print("=" * 78)
    rng = random.Random(seed)
    calls = 0
    for _ in range(trials):
        words = sorted({"".join(rng.choice("abA") for _ in range(rng.randint(1, 6)))
                        for _ in range(rng.randint(0, 8))})
        trie = make_trie(words)
        assert trie.longest_common_prefix() == os.path.commonprefix(words)
        calls += 1
        for _ in range(5):
            p = "".join(rng.choice("abA") for _ in range(rng.randint(1, 4)))
            assert trie.count_words_starting_with(p) == sum(w.startswith(p) for w in words)
            assert trie.has_prefix(p) == any(w.startswith(p) for w in words)
            assert trie.count_words_with_suffix(p) == sum(w.endswith(p) for w in words)
            calls += 3
    print(f"  Перевірено викликів: {calls}, розбіжностей: 0")
    print()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("template", "all"):
        run_template()
    if mode in ("suffix", "all"):
        run_suffix()
    if mode in ("variant", "all"):
        run_variant()
    if mode in ("errors", "all"):
        run_errors()
    if mode in ("check", "all"):
        run_check()
    if mode in ("scale", "all"):
        run_scale()
