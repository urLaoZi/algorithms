import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Настройка стиля
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12

# Проверка наличия файлов
if not os.path.exists('merge_sort_stats.csv'):
    print("Error: merge_sort_stats.csv not found!")
    exit(1)

# Чтение данных
df = pd.read_csv('merge_sort_stats.csv')
raw_df = pd.read_csv('merge_raw_data.csv')

# Создание директории для графиков
os.makedirs('plots', exist_ok=True)

# === ГРАФИК 1: Совмещённый график наихудшего времени и сложности O(n log n) ===
plt.figure(1, figsize=(12, 8))
plt.loglog(df['Size'], df['WorstTime_ns'], 'ro-', linewidth=2, markersize=8, 
           label='Худшее время (эксперимент)')
plt.loglog(df['Size'], df['BigO_ns'], 'b--', linewidth=2, 
           label='Теория: O(n log n) с константой')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время (наносекунды)', fontsize=14)
plt.title('Сортировка слиянием: наихудшее время vs O(n log n)', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3, which='both')
plt.savefig('plots/merge_worst_vs_complexity.png', dpi=150)
plt.close(1)

# === ГРАФИК 2: Совмещенный график среднего, лучшего и худшего времени ===
plt.figure(2, figsize=(12, 8))
plt.loglog(df['Size'], df['BestTime_ns'], 'g-', linewidth=2, marker='o', 
           label='Лучшее время')
plt.loglog(df['Size'], df['AvgTime_ns'], 'b-', linewidth=2, marker='s', 
           label='Среднее время')
plt.loglog(df['Size'], df['WorstTime_ns'], 'r-', linewidth=2, marker='^', 
           label='Худшее время')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время (наносекунды)', fontsize=14)
plt.title('Сортировка слиянием: сравнение времени выполнения', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/merge_time_comparison.png', dpi=150)
plt.close(2)

# === ГРАФИК 3: Совмещенный график глубины рекурсии ===
plt.figure(3, figsize=(12, 8))
plt.loglog(df['Size'], df['BestDepth'], 'g-', linewidth=2, marker='o', 
           label='Лучшая глубина')
plt.loglog(df['Size'], df['AvgDepth'], 'b-', linewidth=2, marker='s', 
           label='Средняя глубина')
plt.loglog(df['Size'], df['WorstDepth'], 'r-', linewidth=2, marker='^', 
           label='Худшая глубина')
# Теоретическая кривая log2(n) для сравнения
plt.loglog(df['Size'], np.log2(df['Size']), 'k--', linewidth=2, 
           label='log₂(n) (теория)')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Глубина рекурсии', fontsize=14)
plt.title('Сортировка слиянием: глубина рекурсии', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/merge_depth_comparison.png', dpi=150)
plt.close(3)

# === ГРАФИК 4: Совмещенный график потребления дополнительной памяти ===
plt.figure(4, figsize=(12, 8))
# Переводим в мегабайты для наглядности
plt.loglog(df['Size'], df['BestMemory']/1024/1024, 'g-', linewidth=2, marker='o', 
           label='Лучшая память')
plt.loglog(df['Size'], df['AvgMemory']/1024/1024, 'b-', linewidth=2, marker='s', 
           label='Средняя память')
plt.loglog(df['Size'], df['WorstMemory']/1024/1024, 'r-', linewidth=2, marker='^', 
           label='Худшая память')
# Теоретическая кривая n * 8 байт
plt.loglog(df['Size'], df['Size']*8/1024/1024, 'k--', linewidth=2, 
           label='n·8 байт (теория)')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Дополнительная память (МБ)', fontsize=14)
plt.title('Сортировка слиянием: потребление дополнительной памяти', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/merge_memory_comparison.png', dpi=150)
plt.close(4)

# === ГРАФИК 5: Количество рекурсивных вызовов ===
plt.figure(5, figsize=(12, 8))
plt.loglog(df['Size'], df['BestCalls'], 'g-', linewidth=2, marker='o', 
           label='Лучшее')
plt.loglog(df['Size'], df['AvgCalls'], 'b-', linewidth=2, marker='s', 
           label='Среднее')
plt.loglog(df['Size'], df['WorstCalls'], 'r-', linewidth=2, marker='^', 
           label='Худшее')
# Теоретическая кривая 2n-1
plt.loglog(df['Size'], 2*df['Size']-1, 'k--', linewidth=2, 
           label='2n-1 (теория)')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Количество рекурсивных вызовов', fontsize=14)
plt.title('Сортировка слиянием: количество рекурсивных вызовов', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/merge_calls_comparison.png', dpi=150)
plt.close(5)

# === ГРАФИК 6: Нормализованное время (проверка сложности) ===
plt.figure(6, figsize=(12, 8))
n = df['Size'].values
normalized_time = df['AvgTime_ns'].values / (n * np.log2(n))

plt.semilogx(n, normalized_time, 'bo-', linewidth=2, markersize=8)
plt.axhline(y=normalized_time.mean(), color='r', linestyle='--', 
            label=f'Средняя константа: {normalized_time.mean():.2e}')
plt.fill_between(n, 
                 normalized_time.mean() - normalized_time.std(),
                 normalized_time.mean() + normalized_time.std(),
                 alpha=0.2, color='gray', label='Стандартное отклонение')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время / (n·log₂(n))', fontsize=14)
plt.title('Сортировка слиянием: нормализованное время', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/merge_normalized.png', dpi=150)
plt.close(6)

print("Все требуемые графики успешно построены!")
print("\nСозданные файлы:")
print("  1. merge_worst_vs_complexity.png  - наихудшее время vs O(n log n)")
print("  2. merge_time_comparison.png      - сравнение времени (best/avg/worst)")
print("  3. merge_depth_comparison.png     - сравнение глубины рекурсии")
print("  4. merge_memory_comparison.png    - сравнение потребления памяти")
print("  5. merge_calls_comparison.png     - количество рекурсивных вызовов")
print("  6. merge_normalized.png           - проверка сложности")

# Анализ результатов
print("\n" + "="*60)
print("АНАЛИЗ СЛОЖНОСТИ СОРТИРОВКИ СЛИЯНИЕМ")
print("="*60)

last = df.iloc[-1]
print(f"\nДля n = {int(last['Size'])}:")
print(f"  Среднее время: {last['AvgTime_ns']/1e9:.2f} с")
print(f"  Глубина рекурсии: {last['AvgDepth']:.0f} (теория: {np.log2(last['Size']):.1f})")
print(f"  Вызовов: {last['AvgCalls']:.0f} (теория: {2*last['Size']-1})")
print(f"  Память: {last['AvgMemory']/1024/1024:.2f} МБ (теория: {last['Size']*8/1024/1024:.2f} МБ)")