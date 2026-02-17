import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Настройка стиля
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12

# Проверка наличия файлов
if not os.path.exists('sorting_stats.csv'):
    print("Error: sorting_stats.csv not found!")
    print("Please run the C++ program first")
    exit(1)

# Чтение данных
df = pd.read_csv('sorting_stats.csv')
raw_df = pd.read_csv('raw_data.csv')

# Создание директории для графиков
os.makedirs('plots', exist_ok=True)

# 1. График: Наихудшее время vs O(n^2)
plt.figure(1)
plt.loglog(df['Size'], df['WorstTime_ns'], 'r-', linewidth=2, label='Worst case')
plt.loglog(df['Size'], df['BigO_ns'], 'b--', linewidth=2, label='O(n^2) with constant')
plt.xlabel('Array size')
plt.ylabel('Time (nanoseconds)')
plt.title('Worst case time vs theoretical complexity O(n^2)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/worst_vs_bigo.png', dpi=150)
plt.close(1)

# 2. График: Сравнение времен
plt.figure(2)
plt.loglog(df['Size'], df['BestTime_ns'], 'g-', linewidth=2, label='Best case')
plt.loglog(df['Size'], df['AvgTime_ns'], 'b-', linewidth=2, label='Average case')
plt.loglog(df['Size'], df['WorstTime_ns'], 'r-', linewidth=2, label='Worst case')
plt.xlabel('Array size')
plt.ylabel('Time (nanoseconds)')
plt.title('Comparison of best, average and worst case times')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/time_comparison.png', dpi=150)
plt.close(2)

# 3. График: Количество обменов
plt.figure(3)
plt.loglog(df['Size'], df['AvgSwaps'], 'm-', marker='o', linewidth=2, label='Average swaps')
plt.xlabel('Array size')
plt.ylabel('Number of swaps')
plt.title('Average number of swap operations')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/swaps.png', dpi=150)
plt.close(3)

# 4. График: Количество проходов
plt.figure(4)
plt.loglog(df['Size'], df['AvgIterations'], 'c-', marker='o', linewidth=2, label='Average iterations')
plt.xlabel('Array size')
plt.ylabel('Number of iterations')
plt.title('Average number of array passes')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/iterations.png', dpi=150)
plt.close(4)

# 5. Дополнительный график: Нормализованное время
plt.figure(5)
n = df['Size'].values
worst_norm = df['WorstTime_ns'].values / (n * n)
avg_norm = df['AvgTime_ns'].values / (n * n)
best_norm = df['BestTime_ns'].values / n

plt.plot(n, worst_norm, 'r-', linewidth=2, label='Worst / n^2')
plt.plot(n, avg_norm, 'b-', linewidth=2, label='Average / n^2')
plt.plot(n, best_norm, 'g-', linewidth=2, label='Best / n')
plt.xlabel('Array size')
plt.ylabel('Normalized time')
plt.title('Normalized time (complexity verification)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xscale('log')
plt.savefig('plots/normalized.png', dpi=150)
plt.close(5)

# 6. Ящик с усами (box plot) для распределения времени - исправлено предупреждение
plt.figure(6)
data_to_plot = []
sizes_for_plot = []

for size in df['Size']:
    times = raw_df[raw_df['Size'] == size]['Time_ns'].values
    data_to_plot.append(times)
    sizes_for_plot.append(str(size))

# Используем правильный параметр tick_labels вместо labels
plt.boxplot(data_to_plot, tick_labels=sizes_for_plot)
plt.xlabel('Array size')
plt.ylabel('Time (nanoseconds)')
plt.title('Time distribution box plot')
plt.yscale('log')
plt.grid(True, alpha=0.3)
plt.savefig('plots/boxplot.png', dpi=150)
plt.close(6)

# 7. График зависимости времени от размера (линейный масштаб)
plt.figure(7)
plt.plot(df['Size'], df['AvgTime_ns'] / 1e9, 'b-', linewidth=2, label='Average time')
plt.plot(df['Size'], df['BestTime_ns'] / 1e9, 'g-', linewidth=2, label='Best time')
plt.plot(df['Size'], df['WorstTime_ns'] / 1e9, 'r-', linewidth=2, label='Worst time')
plt.xlabel('Array size')
plt.ylabel('Time (seconds)')
plt.title('Time dependence on array size (linear scale)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/linear_time.png', dpi=150)
plt.close(7)

# 8. График: Сравнение с теоретическими кривыми
plt.figure(8)
# Аппроксимация
n_log = np.logspace(3, 5.5, 100)
c_best = np.mean(df['BestTime_ns'].values / df['Size'].values)
c_avg = np.mean(df['AvgTime_ns'].values / (df['Size'].values ** 2))
c_worst = np.mean(df['WorstTime_ns'].values / (df['Size'].values ** 2))

plt.loglog(df['Size'], df['BestTime_ns'], 'go', label='Best (experimental)')
plt.loglog(df['Size'], df['AvgTime_ns'], 'bo', label='Average (experimental)')
plt.loglog(df['Size'], df['WorstTime_ns'], 'ro', label='Worst (experimental)')
plt.loglog(n_log, c_best * n_log, 'g--', label='Best fit: O(n)')
plt.loglog(n_log, c_avg * n_log**2, 'b--', label='Average fit: O(n^2)')
plt.loglog(n_log, c_worst * n_log**2, 'r--', label='Worst fit: O(n^2)')
plt.xlabel('Array size')
plt.ylabel('Time (nanoseconds)')
plt.title('Experimental data with theoretical fits')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/theoretical_fits.png', dpi=150)
plt.close(8)

# Сводный график (2x2)
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Верхний левый
axes[0, 0].loglog(df['Size'], df['WorstTime_ns'], 'r-', linewidth=2)
axes[0, 0].loglog(df['Size'], df['BigO_ns'], 'b--', linewidth=2)
axes[0, 0].set_xlabel('Array size')
axes[0, 0].set_ylabel('Time (ns)')
axes[0, 0].set_title('Worst case vs O(n^2)')
axes[0, 0].legend(['Worst', 'O(n^2)'])
axes[0, 0].grid(True, alpha=0.3)

# Верхний правый
axes[0, 1].loglog(df['Size'], df['BestTime_ns'], 'g-', linewidth=2, label='Best')
axes[0, 1].loglog(df['Size'], df['AvgTime_ns'], 'b-', linewidth=2, label='Average')
axes[0, 1].loglog(df['Size'], df['WorstTime_ns'], 'r-', linewidth=2, label='Worst')
axes[0, 1].set_xlabel('Array size')
axes[0, 1].set_ylabel('Time (ns)')
axes[0, 1].set_title('Time comparison')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Нижний левый
axes[1, 0].loglog(df['Size'], df['AvgSwaps'], 'm-', marker='o', linewidth=2)
axes[1, 0].set_xlabel('Array size')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_title('Average swaps')
axes[1, 0].grid(True, alpha=0.3)

# Нижний правый
axes[1, 1].loglog(df['Size'], df['AvgIterations'], 'c-', marker='o', linewidth=2)
axes[1, 1].set_xlabel('Array size')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_title('Average iterations')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/summary.png', dpi=150)
plt.close()

print("\n" + "="*50)
print("GRAPHS GENERATED SUCCESSFULLY!")
print("="*50)
print("\nGenerated files:")
for file in sorted(os.listdir('plots')):
    print(f"  - plots/{file}")

print("\n" + "="*50)
print("TEST RESULTS SUMMARY:")
print("="*50)
print(df.to_string(index=False))

# Вывод теоретической и практической сложности (без спецсимволов)
print("\n" + "="*50)
print("COMPLEXITY ANALYSIS:")
print("="*50)
print("Theoretical complexity of insertion sort:")
print("  - Best case (already sorted): O(n)")
print("  - Average case: O(n^2)")
print("  - Worst case (reverse order): O(n^2)")
print("  - Memory: O(1)")

print("\nExperimental results:")
last_stats = df.iloc[-1]
print(f"  - For n = {int(last_stats['Size'])}:")
print(f"    Time (worst): {last_stats['WorstTime_ns']:.2e} ns = {last_stats['WorstTime_ns']/1e9:.2f} s")
print(f"    Time (average): {last_stats['AvgTime_ns']:.2e} ns = {last_stats['AvgTime_ns']/1e9:.2f} s")
print(f"    Time (best): {last_stats['BestTime_ns']:.2e} ns = {last_stats['BestTime_ns']/1e9:.2f} s")
print(f"    Swaps (average): {last_stats['AvgSwaps']:.2e}")
print(f"    Iterations (average): {last_stats['AvgIterations']:.2e}")

# Проверка соответствия сложности
print("\n" + "="*50)
print("COMPLEXITY VERIFICATION:")
print("="*50)

# Проверяем соотношение времен для разных размеров
for i in range(1, len(df)):
    ratio_size = df['Size'].iloc[i] / df['Size'].iloc[i-1]
    ratio_time_avg = df['AvgTime_ns'].iloc[i] / df['AvgTime_ns'].iloc[i-1]
    ratio_time_worst = df['WorstTime_ns'].iloc[i] / df['WorstTime_ns'].iloc[i-1]
    
    expected_ratio = ratio_size ** 2  # Для O(n^2)
    
    print(f"\nSize {df['Size'].iloc[i-1]} -> {df['Size'].iloc[i]}:")
    print(f"  Size ratio: {ratio_size:.2f}")
    print(f"  Expected time ratio (O(n^2)): {expected_ratio:.2f}")
    print(f"  Actual average time ratio: {ratio_time_avg:.2f}")
    print(f"  Actual worst time ratio: {ratio_time_worst:.2f}")
    
    if 0.8 * expected_ratio <= ratio_time_avg <= 1.2 * expected_ratio:
        print(f"  ✓ Average case matches O(n^2) (within 20%)")
    else:
        print(f"  ✗ Average case deviates from O(n^2)")

# Сохраняем информацию в текстовый файл (используем UTF-8 кодировку)
try:
    with open('plots/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write("INSERTION SORT ANALYSIS REPORT\n")
        f.write("="*50 + "\n\n")
        f.write("Theoretical complexity:\n")
        f.write("  Best case: O(n)\n")
        f.write("  Average case: O(n^2)\n")
        f.write("  Worst case: O(n^2)\n")
        f.write("  Memory: O(1)\n\n")
        
        f.write("Experimental results:\n")
        f.write(df.to_string(index=False))
        f.write("\n\nComplexity verification:\n")
        
        for i in range(1, len(df)):
            ratio_size = df['Size'].iloc[i] / df['Size'].iloc[i-1]
            ratio_time_avg = df['AvgTime_ns'].iloc[i] / df['AvgTime_ns'].iloc[i-1]
            f.write(f"\nSize {df['Size'].iloc[i-1]} -> {df['Size'].iloc[i]}:\n")
            f.write(f"  Size ratio: {ratio_size:.2f}\n")
            f.write(f"  Time ratio: {ratio_time_avg:.2f}\n")
    
    print("\n" + "="*50)
    print(f"Report saved to plots/analysis_report.txt")
    print("="*50)
    
except Exception as e:
    print(f"\nWarning: Could not save report file: {e}")
    # Пробуем сохранить с другой кодировкой
    try:
        with open('plots/analysis_report.txt', 'w', encoding='cp1251') as f:
            f.write("INSERTION SORT ANALYSIS REPORT\n")
            f.write("="*50 + "\n\n")
            f.write("Theoretical complexity:\n")
            f.write("  Best case: O(n)\n")
            f.write("  Average case: O(n^2)\n")
            f.write("  Worst case: O(n^2)\n")
            f.write("  Memory: O(1)\n\n")
            f.write("Experimental results:\n")
            f.write(df.to_string(index=False))
        print(f"Report saved with CP1251 encoding")
    except:
        print("Could not save report file")