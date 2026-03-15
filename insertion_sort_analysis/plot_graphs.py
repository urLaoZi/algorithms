import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Настройка стиля
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12

# Проверка наличия файлов
if not os.path.exists('selection_sort_stats.csv'):
    print("Error: selection_sort_stats.csv not found!")
    exit(1)

# Чтение данных
df = pd.read_csv('selection_sort_stats.csv')
raw_df = pd.read_csv('selection_raw_data.csv')

# Создание директории для графиков
os.makedirs('plots', exist_ok=True)

# === ГРАФИК 1: Сравнение с теорией (логарифмический масштаб - для проверки) ===
plt.figure(1, figsize=(12, 8))
plt.loglog(df['Size'], df['WorstTime_ns'], 'ro-', linewidth=2, markersize=8, label='Эксперимент (худшее время)')
plt.loglog(df['Size'], df['BigO_ns'], 'b--', linewidth=2, label='Теория: O(n²) с константой')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время (наносекунды)', fontsize=14)
plt.title('Сортировка выбором: логарифмический масштаб (прямая = степень n²)', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3, which='both')
plt.savefig('plots/selection_loglog.png', dpi=150)
plt.close(1)

# === ГРАФИК 2: Обычный масштаб (видна квадратичная зависимость) ===
plt.figure(2, figsize=(12, 8))
sizes_linear = np.linspace(0, df['Size'].max(), 100)
theory_quadratic = (df['BigO_ns'].iloc[-1] / (df['Size'].iloc[-1]**2)) * sizes_linear**2

plt.plot(df['Size'], df['WorstTime_ns']/1e9, 'ro-', linewidth=2, markersize=8, label='Худшее время')
plt.plot(df['Size'], df['AvgTime_ns']/1e9, 'bo-', linewidth=2, markersize=8, label='Среднее время')
plt.plot(df['Size'], df['BestTime_ns']/1e9, 'go-', linewidth=2, markersize=8, label='Лучшее время')
plt.plot(sizes_linear, theory_quadratic/1e9, 'k--', linewidth=2, label='Теоретическая парабола n²')

plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время (секунды)', fontsize=14)
plt.title('Сортировка выбором: обычный масштаб (видна квадратичная зависимость)', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/selection_linear.png', dpi=150)
plt.close(2)

# === ГРАФИК 3: Нормализованное время (проверка O(n²)) ===
plt.figure(3, figsize=(12, 8))
n = df['Size'].values
normalized_time = df['AvgTime_ns'].values / (n**2)

plt.semilogx(n, normalized_time, 'bo-', linewidth=2, markersize=8)
plt.axhline(y=normalized_time.mean(), color='r', linestyle='--', 
            label=f'Среднее значение: {normalized_time.mean():.2e}')
plt.xlabel('Размер массива (n)', fontsize=14)
plt.ylabel('Время / n² (нормализованное)', fontsize=14)
plt.title('Сортировка выбором: нормализованное время (константа = время/n²)', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('plots/selection_normalized.png', dpi=150)
plt.close(3)

print("Графики для сортировки выбором обновлены!")