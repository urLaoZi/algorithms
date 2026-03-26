import random
import time
from datetime import datetime

# ================= NODE =================
class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


# ================= ITERATOR =================
class DoublyLinkedListIterator:
    def __init__(self, node):
        self.current = node

    def __iter__(self):
        return self

    def __next__(self):
        if not self.current:
            raise StopIteration
        data = self.current.data
        self.current = self.current.next
        return data


# ================= LIST =================
class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __iter__(self):
        return DoublyLinkedListIterator(self.head)

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.size == 0

    def push_front(self, data):
        node = Node(data)
        if self.head:
            self.head.prev = node
            node.next = self.head
        else:
            self.tail = node
        self.head = node
        self.size += 1

    def push_back(self, data):
        node = Node(data)
        if self.tail:
            self.tail.next = node
            node.prev = self.tail
        else:
            self.head = node
        self.tail = node
        self.size += 1

    def insert(self, index, data):
        if index <= 0:
            self.push_front(data)
            return
        if index >= self.size:
            self.push_back(data)
            return

        current = self.head
        for _ in range(index):
            current = current.next

        node = Node(data)
        prev_node = current.prev

        prev_node.next = node
        node.prev = prev_node

        node.next = current
        current.prev = node

        self.size += 1

    def remove(self, data):
        current = self.head

        while current:
            if current.data == data:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                self.size -= 1
                return True
            current = current.next

        return False

    def to_list(self):
        return [x for x in self]


# ================= SORT =================
def selection_sort_list(dll):
    current = dll.head

    while current:
        min_node = current
        runner = current.next

        while runner:
            if runner.data < min_node.data:
                min_node = runner
            runner = runner.next

        current.data, min_node.data = min_node.data, current.data
        current = current.next


def selection_sort_array(arr):
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]


# ================= TEST 1 =================
def test_numbers():
    print("\n=== ТЕСТ 1: ЧИСЛА ===")

    dll = DoublyLinkedList()

    for _ in range(1000):
        dll.push_back(random.randint(-1000, 1000))

    # показать первые 20 элементов
    first_20 = []
    for i, x in enumerate(dll):
        if i >= 20:
            break
        first_20.append(x)

    print("Первые 20 элементов:")
    print(first_20)

    total = 0
    count = 0
    min_val = None
    max_val = None

    for x in dll:
        total += x
        count += 1

        if min_val is None or x < min_val:
            min_val = x
        if max_val is None or x > max_val:
            max_val = x

    print("Количество:", count)
    print("Сумма:", total)
    print("Среднее:", total / count)
    print("Минимум:", min_val)
    print("Максимум:", max_val)


# ================= TEST 2 =================
def test_push_front():
    print("\n=== ТЕСТ: ДОБАВЛЕНИЕ В НАЧАЛО ===")

    dll = DoublyLinkedList()

    #print("До:")
    #print(dll.to_list())

    for i in range(5):
        dll.push_front(i)

    print("После:")
    print(dll.to_list())

# ================= TEST 3 =================
def test_insert():
    print("\n=== ТЕСТ: ВСТАВКА ===")

    dll = DoublyLinkedList()

    for i in range(5):
        dll.push_back(i)

    print("До вставки:")
    print(dll.to_list())

    dll.insert(2, 99)

    print("После вставки 99 на позицию 2:")
    print(dll.to_list())

# ================= TEST 4 =================
def test_push_back():
    print("\n=== ТЕСТ: ДОБАВЛЕНИЕ В КОНЕЦ ===")

    dll = DoublyLinkedList()

    #print("До:")
    #print(dll.to_list())

    for i in range(5):
        dll.push_back(i)

    print("После:")
    print(dll.to_list())

# ================= TEST 5 =================

def test_remove():
    print("\n=== ТЕСТ: УДАЛЕНИЕ ===")

    dll = DoublyLinkedList()

    for i in range(5):
        dll.push_back(i)

    print("До удаления:")
    print(dll.to_list())

    dll.remove(2)

    print("После удаления 2:")
    print(dll.to_list())


# ================= PERSON =================
class Person:
    def __init__(self, last, first, middle, birth):
        self.last = last
        self.first = first
        self.middle = middle
        self.birth = birth

    def age(self):
        return 2025 - self.birth.year


# ================= TEST 3 =================
def test_people():
    print("\n=== ТЕСТ 3: ЛЮДИ ===")

    last_names = ["Ivanov", "Petrov", "Sidorov"]
    first_names = ["Ivan", "Petr", "Alex"]
    middle_names = ["Ivanovich", "Petrovich"]

    dll = DoublyLinkedList()

    for _ in range(100):
        birth = datetime(
            random.randint(1980, 2020),
            random.randint(1, 12),
            random.randint(1, 28)
        )

        person = Person(
            random.choice(last_names),
            random.choice(first_names),
            random.choice(middle_names),
            birth
        )

        dll.push_back(person)

    young = DoublyLinkedList()
    old = DoublyLinkedList()
    other = DoublyLinkedList()

    for p in dll:
        if p.age() < 20:
            young.push_back(p)
        elif p.age() > 30:
            old.push_back(p)
        else:
            other.push_back(p)

    total = len(dll)
    total_split = len(young) + len(old) + len(other)

    print("Всего:", total)
    print("Младше 20:", len(young))
    print("Старше 30:", len(old))
    print("Остальные:", len(other))
    print("Проверка:", "✓" if total == total_split else "✗")


# ================= TEST 4 =================
def test_compare():
    print("\n=== ТЕСТ 4: СОРТИРОВКА ===")

    sizes = [1000, 2000, 4000]

    for size in sizes:
        data = [random.random() for _ in range(size)]

        arr = data.copy()
        start = time.time()
        selection_sort_array(arr)
        t_arr = time.time() - start

        dll = DoublyLinkedList()
        for x in data:
            dll.push_back(x)

        start = time.time()
        selection_sort_list(dll)
        t_list = time.time() - start

        print(f"\nРазмер: {size}")
        print(f"Массив: {t_arr:.5f} сек")
        print(f"Список: {t_list:.5f} сек")


# ================= MAIN =================
if __name__ == "__main__":
    test_numbers()

    test_push_front()
    test_push_back()
    test_insert()
    test_remove()

    #test_strings()
    test_people()
    test_compare()