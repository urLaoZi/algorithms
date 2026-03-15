import random
import time
from datetime import date, timedelta
from typing import Any, Optional, Iterator


class Node:
    """Узел двусвязного списка"""
    def __init__(self, data: Any):
        self.data = data
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class LinkedListIterator:
    """Итератор для двусвязного списка"""
    def __init__(self, head: Optional[Node]):
        self.current = head
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current is None:
            raise StopIteration
        data = self.current.data
        self.current = self.current.next
        return data


class LinkedList:
    """Двусвязный список"""
    
    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0
    
    def __iter__(self) -> Iterator:
        """Возвращает итератор для for each"""
        return LinkedListIterator(self.head)
    
    def __len__(self) -> int:
        """Возвращает количество элементов"""
        return self._size
    
    def __bool__(self) -> bool:
        """Проверка на пустоту"""
        return self._size > 0
    
    def empty(self) -> bool:
        """Проверка на пустоту"""
        return self._size == 0
    
    def size(self) -> int:
        """Возвращает количество элементов"""
        return self._size
    
    def push_front(self, data: Any) -> None:
        """Добавление в начало"""
        new_node = Node(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
    
    def push_back(self, data: Any) -> None:
        """Добавление в конец"""
        new_node = Node(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1
    
    def insert(self, data: Any, position: int) -> None:
        """Вставка в произвольное место"""
        if position <= 0:
            self.push_front(data)
            return
        
        if position >= self._size:
            self.push_back(data)
            return
        
        current = self.head
        for _ in range(position):
            current = current.next
        
        new_node = Node(data)
        new_node.prev = current.prev
        new_node.next = current
        current.prev.next = new_node
        current.prev = new_node
        self._size += 1
    
    def remove(self, data: Any) -> None:
        """Удаление элемента по значению"""
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
                
                self._size -= 1
            current = current.next
    
    def clear(self) -> None:
        """Очистка списка"""
        self.head = self.tail = None
        self._size = 0
    
    def to_list(self) -> list:
        """Преобразование в список Python (для удобства)"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def shuffle(self) -> None:
        """Перемешивание элементов"""
        if self._size < 2:
            return
        
        # Преобразуем в список, перемешиваем и восстанавливаем
        items = self.to_list()
        random.shuffle(items)
        
        self.clear()
        for item in items:
            self.push_back(item)
    
    def sort(self) -> None:
        """Сортировка элементов"""
        if self._size < 2:
            return
        
        items = self.to_list()
        items.sort()
        
        self.clear()
        for item in items:
            self.push_back(item)


# Класс для теста 3
class Person:
    def __init__(self, surname: str, name: str, patronymic: str, birth_date: str):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.birth_date = birth_date
    
    def __repr__(self) -> str:
        return f"{self.surname} {self.name} {self.patronymic}, {self.birth_date}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Person):
            return False
        return (self.surname == other.surname and
                self.name == other.name and
                self.patronymic == other.patronymic and
                self.birth_date == other.birth_date)


def test1():
    """Тест 1: Работа с числами"""
    print("\n=== Тест 1: Работа с числами ===")
    
    lst = LinkedList()
    
    # Заполнение 1000 случайными числами
    for _ in range(1000):
        lst.push_back(random.randint(-1000, 1000))
    
    # Подсчет статистики
    total = 0
    min_val = float('inf')
    max_val = float('-inf')
    
    for value in lst:  # Используем for each
        total += value
        min_val = min(min_val, value)
        max_val = max(max_val, value)
    
    average = total / len(lst)
    
    print(f"Размер списка: {len(lst)}")
    print(f"Сумма: {total}")
    print(f"Среднее: {average:.2f}")
    print(f"Минимум: {min_val}")
    print(f"Максимум: {max_val}")
    print(f"Список пуст? {'Да' if lst.empty() else 'Нет'}")


def test2():
    """Тест 2: Работа со строками"""
    print("\n=== Тест 2: Работа со строками ===")
    
    lst = LinkedList()
    words = ["яблоко", "банан", "вишня", "дыня", "ежевика",
             "инжир", "киви", "лимон", "манго", "нектарин"]
    
    for word in words:
        lst.push_back(word)
    
    print("Исходный список:")
    print(" ".join(lst))
    
    # Вставка
    lst.push_front("арбуз")
    lst.push_back("апельсин")
    lst.insert("груша", 3)
    
    print("\nПосле вставок:")
    print(" ".join(lst))
    
    # Удаление
    lst.remove("киви")
    lst.remove("манго")
    
    print("\nПосле удалений:")
    print(" ".join(lst))
    
    print(f"\nКоличество элементов: {len(lst)}")


def test3():
    """Тест 3: Работа со структурой Person"""
    print("\n=== Тест 3: Работа со структурой Person ===")
    
    # Подготовка данных
    surnames = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
                "Попов", "Васильев", "Федоров", "Михайлов", "Андреев"]
    names = ["Иван", "Петр", "Сергей", "Алексей", "Дмитрий",
             "Андрей", "Михаил", "Николай", "Владимир", "Павел"]
    patronymics = ["Иванович", "Петрович", "Сергеевич", "Алексеевич", "Дмитриевич",
                   "Андреевич", "Михайлович", "Николаевич", "Владимирович", "Павлович"]
    
    # Генерация случайных дат
    start_date = date(1980, 1, 1)
    end_date = date(2020, 1, 1)
    days_between = (end_date - start_date).days
    
    people = LinkedList()
    
    # Заполнение 100 людьми
    for _ in range(100):
        person = Person(
            random.choice(surnames),
            random.choice(names),
            random.choice(patronymics),
            (start_date + timedelta(days=random.randint(0, days_between))).strftime("%d.%m.%Y")
        )
        people.push_back(person)
    
    print(f"Создано {len(people)} людей")
    
    # Фильтрация
    young = LinkedList()
    middle = LinkedList()
    old = LinkedList()
    
    current_year = 2024
    
    for person in people:
        year = int(person.birth_date.split('.')[-1])
        age = current_year - year
        
        if age < 20:
            young.push_back(person)
        elif age > 30:
            old.push_back(person)
        else:
            middle.push_back(person)
    
    print(f"Младше 20: {len(young)} человек")
    print(f"От 20 до 30: {len(middle)} человек")
    print(f"Старше 30: {len(old)} человек")
    
    # Проверка суммы
    assert len(young) + len(middle) + len(old) == len(people)
    
    # Перемешивание (специфично для списка)
    print("\nПеремешивание списка:")
    people.shuffle()
    
    # Вывод первых 5 для проверки
    count = 0
    for person in people:
        if count >= 5:
            break
        print(person)
        count += 1


def bubble_sort(arr):
    """Пузырьковая сортировка"""
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def quick_sort(arr):
    """Быстрая сортировка"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(arr):
    """Сортировка слиянием"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left, right):
    """Слияние для merge sort"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def test4():
    """Тест 4: Сравнение производительности сортировок"""
    print("\n=== Тест 4: Сравнение производительности сортировки ===")
    
    SIZE = 5000  # Уменьшаем для Python, так как он медленнее
    
    # Подготовка данных
    data = [random.randint(0, 100000) for _ in range(SIZE)]
    linked_list = LinkedList()
    for val in data:
        linked_list.push_back(val)
    
    # Тестирование на списке Python
    print(f"\nСортировка {SIZE} элементов (время в секундах):")
    
    # Bubble sort
    arr_copy = data.copy()
    start = time.time()
    bubble_sort(arr_copy)
    bubble_time = time.time() - start
    print(f"Bubble sort на списке Python: {bubble_time:.3f} сек")
    
    # Quick sort
    arr_copy = data.copy()
    start = time.time()
    quick_sort(arr_copy)
    quick_time = time.time() - start
    print(f"Quick sort на списке Python: {quick_time:.3f} сек")
    
    # Merge sort
    arr_copy = data.copy()
    start = time.time()
    merge_sort(arr_copy)
    merge_time = time.time() - start
    print(f"Merge sort на списке Python: {merge_time:.3f} сек")
    
    # Timsort (встроенная сортировка Python)
    arr_copy = data.copy()
    start = time.time()
    arr_copy.sort()
    timsort_time = time.time() - start
    print(f"Timsort (встроенная) на списке Python: {timsort_time:.3f} сек")
    
    # Тестирование на нашем списке
    start = time.time()
    linked_list.sort()
    list_sort_time = time.time() - start
    print(f"Sort на нашем двусвязном списке: {list_sort_time:.3f} сек")
    
    # Проверка корректности
    sorted_data = sorted(data)
    list_data = linked_list.to_list()
    
    correct = list_data == sorted_data
    print(f"\nРезультат сортировки корректен: {'Да' if correct else 'Нет'}")


def main():
    """Главная функция"""
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запуск всех тестов
    test1()
    test2()
    test3()
    test4()
    
    # Дополнительная демонстрация работы итератора
    print("\n=== Демонстрация работы итератора ===")
    demo_list = LinkedList()
    for i in range(5):
        demo_list.push_back(f"Элемент {i}")
    
    print("Перебор с помощью for each:")
    for item in demo_list:
        print(item)
    
    print("\nРучное использование итератора:")
    iterator = iter(demo_list)
    try:
        while True:
            print(next(iterator))
    except StopIteration:
        pass


if __name__ == "__main__":
    main()