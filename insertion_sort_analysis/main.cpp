#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <fstream>
#include <algorithm>
#include <iomanip>
#include <string>
#include <cmath>
#include <thread>
#include <future>
#include <mutex>
#include <atomic>

using namespace std;
using namespace chrono;

// Мьютекс для защиты вывода в консоль
mutex cout_mutex;

// Структура для хранения результатов одного запуска
struct SortResult {
    long long time_ns;      // время в наносекундах
    long long comparisons;   // количество сравнений
    long long swaps;         // количество обменов
    int size;                // размер массива
    int attempt;             // номер попытки
    
    SortResult() : time_ns(0), comparisons(0), swaps(0), size(0), attempt(0) {}
    SortResult(long long t, long long comp, long long sw, int s, int a) 
        : time_ns(t), comparisons(comp), swaps(sw), size(s), attempt(a) {}
};

// Класс сортировки выбором со счетчиками
class SelectionSorter {
private:
    long long comparisons_;
    long long swaps_;
    
public:
    SelectionSorter() : comparisons_(0), swaps_(0) {}
    
    void reset() {
        comparisons_ = 0;
        swaps_ = 0;
    }
    
    void sort(vector<double>& arr) {
        int n = arr.size();
        
        for (int i = 0; i < n - 1; i++) {
            int min_idx = i;
            
            // Поиск минимального элемента
            for (int j = i + 1; j < n; j++) {
                comparisons_++;
                if (arr[j] < arr[min_idx]) {
                    min_idx = j;
                }
            }
            
            // Обмен при необходимости
            if (min_idx != i) {
                swap(arr[i], arr[min_idx]);
                swaps_++;
            }
        }
    }
    
    long long getComparisons() const { return comparisons_; }
    long long getSwaps() const { return swaps_; }
};

// Генератор случайных массивов (потокобезопасный)
class ArrayGenerator {
private:
    random_device rd;
    mt19937 engine;
    uniform_real_distribution<double> dist;
    mutex gen_mutex;
    
public:
    ArrayGenerator() : engine(rd()), dist(-1.0, 1.0) {}
    
    vector<double> generate(int size) {
        lock_guard<mutex> lock(gen_mutex);
        vector<double> arr(size);
        for (auto& x : arr) x = dist(engine);
        return arr;
    }
};

// Глобальный генератор (один на все потоки)
ArrayGenerator globalGenerator;

// Функция для выполнения одной попытки сортировки
SortResult runSingleAttempt(int size, int attempt_num) {
    // Генерация массива
    vector<double> arr = globalGenerator.generate(size);
    
    // Создание сортировщика
    SelectionSorter sorter;
    
    // Измерение времени
    auto start = high_resolution_clock::now();
    sorter.sort(arr);
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<nanoseconds>(end - start);
    
    // Проверка сортировки (для отладки можно раскомментировать)
    // if (!is_sorted(arr.begin(), arr.end())) {
    //     lock_guard<mutex> lock(cout_mutex);
    //     cout << "Warning: Array not sorted correctly for size " << size << endl;
    // }
    
    return SortResult(duration.count(), 
                     sorter.getComparisons(), 
                     sorter.getSwaps(),
                     size, 
                     attempt_num);
}

// Функция для выполнения всех попыток для одного размера (в одном потоке)
vector<SortResult> runSizeInThread(int size, int attempts, int thread_id) {
    vector<SortResult> results;
    results.reserve(attempts);
    
    for (int i = 0; i < attempts; i++) {
        auto result = runSingleAttempt(size, i + 1);
        results.push_back(result);
        
        // Вывод прогресса (редко, чтобы не засорять консоль)
        if ((i + 1) % 5 == 0 || i == 0) {
            lock_guard<mutex> lock(cout_mutex);
            cout << "    [Thread " << thread_id << "] Size " << size 
                 << ": attempt " << (i + 1) << "/" << attempts 
                 << " completed" << endl;
        }
    }
    
    return results;
}

// Структура для статистики по серии
struct SeriesStats {
    int size;
    double best_time;
    double worst_time;
    double avg_time;
    double avg_swaps;
    double avg_comparisons;
    double big_o;
    
    SeriesStats() : size(0), best_time(0), worst_time(0), avg_time(0), 
                    avg_swaps(0), avg_comparisons(0), big_o(0) {}
};

// Вычисление статистики
SeriesStats computeStats(const vector<SortResult>& results, int size) {
    SeriesStats stats;
    stats.size = size;
    
    if (results.empty()) return stats;
    
    stats.best_time = results[0].time_ns;
    stats.worst_time = results[0].time_ns;
    double time_sum = 0;
    double swaps_sum = 0;
    double comp_sum = 0;
    
    for (const auto& r : results) {
        time_sum += r.time_ns;
        swaps_sum += r.swaps;
        comp_sum += r.comparisons;
        
        if (r.time_ns < stats.best_time) stats.best_time = r.time_ns;
        if (r.time_ns > stats.worst_time) stats.worst_time = r.time_ns;
    }
    
    stats.avg_time = time_sum / results.size();
    stats.avg_swaps = swaps_sum / results.size();
    stats.avg_comparisons = comp_sum / results.size();
    
    // Подбор константы для O(n^2)
    double c = 0;
    if (size > 1000) {
        c = (stats.worst_time / (static_cast<double>(size) * size)) * 1.2;
    } else {
        c = stats.avg_time / (static_cast<double>(size) * size);
    }
    stats.big_o = c * size * size;
    
    return stats;
}

// Сохранение результатов в CSV
void saveToCSV(const vector<SeriesStats>& allStats, 
               const vector<SortResult>& allRawData,
               const vector<int>& sizes) {
    
    // Сохранение статистики
    ofstream stats_file("selection_sort_stats.csv");
    stats_file << "Size,BestTime_ns,WorstTime_ns,AvgTime_ns,AvgSwaps,AvgComparisons,BigO_ns\n";
    
    for (const auto& s : allStats) {
        stats_file << s.size << ","
                   << fixed << setprecision(2)
                   << s.best_time << ","
                   << s.worst_time << ","
                   << s.avg_time << ","
                   << s.avg_swaps << ","
                   << s.avg_comparisons << ","
                   << s.big_o << "\n";
    }
    stats_file.close();
    
    // Сохранение сырых данных
    ofstream raw_file("selection_raw_data.csv");
    raw_file << "Size,Attempt,Time_ns,Comparisons,Swaps\n";
    
    for (const auto& r : allRawData) {
        raw_file << r.size << ","
                 << r.attempt << ","
                 << r.time_ns << ","
                 << r.comparisons << ","
                 << r.swaps << "\n";
    }
    raw_file.close();
    
    cout << "\nResults saved to selection_sort_stats.csv and selection_raw_data.csv\n";
}

// Многопоточное выполнение всех тестов
void runAllTestsMultithreaded(const vector<int>& sizes, int attempts) {
    cout << "=== SELECTION SORT ANALYSIS (MULTITHREADED) ===\n";
    cout << "Array sizes: ";
    for (int s : sizes) cout << s << " ";
    cout << "\nAttempts per size: " << attempts << "\n";
    cout << "Number of CPU cores: " << thread::hardware_concurrency() << "\n\n";
    
    vector<SortResult> allRawData;
    vector<future<vector<SortResult>>> futures;
    
    int thread_id = 0;
    
    // Запускаем по одному потоку на каждый размер
    for (int size : sizes) {
        cout << "Launching thread for size " << size << "...\n";
        futures.push_back(async(launch::async, runSizeInThread, size, attempts, thread_id++));
    }
    
    // Собираем результаты
    vector<vector<SortResult>> allResults;
    for (auto& fut : futures) {
        auto results = fut.get();
        allResults.push_back(results);
        
        // Добавляем в общий вектор для сырых данных
        allRawData.insert(allRawData.end(), results.begin(), results.end());
    }
    
    // Вычисляем статистику
    vector<SeriesStats> allStats;
    for (size_t i = 0; i < sizes.size(); i++) {
        auto stats = computeStats(allResults[i], sizes[i]);
        allStats.push_back(stats);
        
        cout << "\nSize " << stats.size << ":\n";
        cout << "  Best time: " << stats.best_time << " ns\n";
        cout << "  Worst time: " << stats.worst_time << " ns\n";
        cout << "  Avg time: " << stats.avg_time << " ns\n";
        cout << "  Avg comparisons: " << stats.avg_comparisons << "\n";
        cout << "  Avg swaps: " << stats.avg_swaps << "\n";
    }
    
    // Сохраняем результаты
    saveToCSV(allStats, allRawData, sizes);
}

int main() {
    try {
        // Параметры тестирования
        vector<int> sizes = {1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000};
        int attempts = 20;
        
        // Запуск многопоточного тестирования
        runAllTestsMultithreaded(sizes, attempts);
        
        cout << "\nTesting completed successfully!\n";
        cout << "Run plot_graphs.py to generate plots\n";
        
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}