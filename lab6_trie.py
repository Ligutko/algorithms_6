"""Лабораторна робота № 6. Просунуті структури для оптимізації та пошуку.

Завдання 2. Розширення класу Trie (префіксне дерево).
Базові методи: count_words_with_suffix(pattern), has_prefix(prefix).
Варіант 2: longest_common_prefix(), count_words_starting_with(prefix).

Базовий клас Trie (файл trie.py) взято з репозиторію прикладів курсу
https://github.com/zhukov-vntu/mlta-lr6 без змін.

Запуск: python lab6_trie.py [template | variant | errors | check]
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
    if mode in ("variant", "all"):
        run_variant()
    if mode in ("errors", "all"):
        run_errors()
    if mode in ("check", "all"):
        run_check()
