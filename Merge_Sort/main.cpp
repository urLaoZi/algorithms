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

using namespace std;
using namespace chrono;

// Мьютекс для защиты вывода в консоль
mutex cout_mutex;

// Структура для хранения результатов одного запуска
struct SortResult {
    long long time_ns;           // время в наносекундах
    int recursive_calls;          // количество рекурсивных вызовов
    int max_recursion_depth;       // максимальная глубина рекурсии
    long long extra_memory_bytes;  // дополнительная память (в байтах)
    int size;                      // размер массива
    int attempt;                    // номер попытки
    
    SortResult() : time_ns(0), recursive_calls(0), max_recursion_depth(0), 
                   extra_memory_bytes(0), size(0), attempt(0) {}
    
    SortResult(long long t, int calls, int depth, long long memory, int s, int a) 
        : time_ns(t), recursive_calls(calls), max_recursion_depth(depth), 
          extra_memory_bytes(memory), size(s), attempt(a) {}
};

// Класс сортировки слиянием со счетчиками
class MergeSorter {
private:
    int recursive_calls_;         // счетчик рекурсивных вызовов
    int current_depth_;            // текущая глубина рекурсии
    int max_depth_;                // максимальная глубина рекурсии
    long long extra_memory_;       // счетчик дополнительной памяти
    vector<double> temp_buffer;    // временный буфер для слияния
    
    // Рекурсивная функция сортировки слиянием
    void mergeSortRecursive(vector<double>& arr, int left, int right) {
        // Увеличиваем счетчики
        recursive_calls_++;
        current_depth_++;
        max_depth_ = max(max_depth_, current_depth_);
        
        if (left < right) {
            int mid = left + (right - left) / 2;
            
            // Рекурсивно сортируем две половины
            mergeSortRecursive(arr, left, mid);
            mergeSortRecursive(arr, mid + 1, right);
            
            // Слияние отсортированных половин
            merge(arr, left, mid, right);
        }
        
        current_depth_--;
    }
    
    // Функция слияния двух отсортированных подмассивов
    void merge(vector<double>& arr, int left, int mid, int right) {
        int left_size = mid - left + 1;
        int right_size = right - mid;
        
        // Используем временный буфер (уже выделен)
        // Копируем данные во временный буфер
        for (int i = 0; i < left_size; i++) {
            temp_buffer[left + i] = arr[left + i];
        }
        for (int j = 0; j < right_size; j++) {
            temp_buffer[mid + 1 + j] = arr[mid + 1 + j];
        }
        
        // Слияние обратно в исходный массив
        int i = 0, j = 0, k = left;
        
        while (i < left_size && j < right_size) {
            if (temp_buffer[left + i] <= temp_buffer[mid + 1 + j]) {
                arr[k] = temp_buffer[left + i];
                i++;
            } else {
                arr[k] = temp_buffer[mid + 1 + j];
                j++;
            }
            k++;
        }
        
        // Копируем оставшиеся элементы
        while (i < left_size) {
            arr[k] = temp_buffer[left + i];
            i++;
            k++;
        }
        
        while (j < right_size) {
            arr[k] = temp_buffer[mid + 1 + j];
            j++;
            k++;
        }
    }
    
public:
    MergeSorter() : recursive_calls_(0), current_depth_(0), 
                    max_depth_(0), extra_memory_(0) {}
    
    // Основной метод сортировки
    void sort(vector<double>& arr) {
        int n = arr.size();
        
        // Сброс счетчиков
        recursive_calls_ = 0;
        current_depth_ = 0;
        max_depth_ = 0;
        
        // Выделяем временный буфер (дополнительная память)
        if (temp_buffer.size() < n) {
            temp_buffer.resize(n);
        }
        
        // Запоминаем размер временного буфера как дополнительную память
        extra_memory_ = n * sizeof(double);
        
        // Запускаем рекурсивную сортировку
        mergeSortRecursive(arr, 0, n - 1);
    }
    
    // Геттеры
    int getRecursiveCalls() const { return recursive_calls_; }
    int getMaxDepth() const { return max_depth_; }
    long long getExtraMemory() const { return extra_memory_; }
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

// Глобальный генератор
ArrayGenerator globalGenerator;

// Функция для выполнения одной попытки сортировки
SortResult runSingleAttempt(int size, int attempt_num) {
    // Генерация массива
    vector<double> arr = globalGenerator.generate(size);
    
    // Создание сортировщика
    MergeSorter sorter;
    
    // Измерение времени
    auto start = high_resolution_clock::now();
    sorter.sort(arr);
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<nanoseconds>(end - start);
    
    // Проверка сортировки
    if (!is_sorted(arr.begin(), arr.end())) {
        lock_guard<mutex> lock(cout_mutex);
        cerr << "Warning: Array not sorted correctly for size " << size << endl;
    }
    
    return SortResult(duration.count(), 
                     sorter.getRecursiveCalls(),
                     sorter.getMaxDepth(),
                     sorter.getExtraMemory(),
                     size, 
                     attempt_num);
}

// Функция для выполнения всех попыток для одного размера
vector<SortResult> runSizeTests(int size, int attempts, int thread_id) {
    vector<SortResult> results;
    results.reserve(attempts);
    
    for (int i = 0; i < attempts; i++) {
        auto result = runSingleAttempt(size, i + 1);
        results.push_back(result);
        
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
    
    // Время
    double best_time;
    double worst_time;
    double avg_time;
    
    // Рекурсивные вызовы
    int best_calls;
    int worst_calls;
    double avg_calls;
    
    // Глубина рекурсии
    int best_depth;
    int worst_depth;
    double avg_depth;
    
    // Память
    long long best_memory;
    long long worst_memory;
    double avg_memory;
    
    // O-большое
    double big_o;
    
    SeriesStats() : size(0), 
                    best_time(0), worst_time(0), avg_time(0),
                    best_calls(0), worst_calls(0), avg_calls(0),
                    best_depth(0), worst_depth(0), avg_depth(0),
                    best_memory(0), worst_memory(0), avg_memory(0),
                    big_o(0) {}
};

// Вычисление статистики
SeriesStats computeStats(const vector<SortResult>& results, int size) {
    SeriesStats stats;
    stats.size = size;
    
    if (results.empty()) return stats;
    
    // Инициализация
    stats.best_time = results[0].time_ns;
    stats.worst_time = results[0].time_ns;
    stats.best_calls = results[0].recursive_calls;
    stats.worst_calls = results[0].recursive_calls;
    stats.best_depth = results[0].max_recursion_depth;
    stats.worst_depth = results[0].max_recursion_depth;
    stats.best_memory = results[0].extra_memory_bytes;
    stats.worst_memory = results[0].extra_memory_bytes;
    
    double time_sum = 0;
    double calls_sum = 0;
    double depth_sum = 0;
    double memory_sum = 0;
    
    for (const auto& r : results) {
        time_sum += r.time_ns;
        calls_sum += r.recursive_calls;
        depth_sum += r.max_recursion_depth;
        memory_sum += r.extra_memory_bytes;
        
        if (r.time_ns < stats.best_time) stats.best_time = r.time_ns;
        if (r.time_ns > stats.worst_time) stats.worst_time = r.time_ns;
        
        if (r.recursive_calls < stats.best_calls) stats.best_calls = r.recursive_calls;
        if (r.recursive_calls > stats.worst_calls) stats.worst_calls = r.recursive_calls;
        
        if (r.max_recursion_depth < stats.best_depth) stats.best_depth = r.max_recursion_depth;
        if (r.max_recursion_depth > stats.worst_depth) stats.worst_depth = r.max_recursion_depth;
        
        if (r.extra_memory_bytes < stats.best_memory) stats.best_memory = r.extra_memory_bytes;
        if (r.extra_memory_bytes > stats.worst_memory) stats.worst_memory = r.extra_memory_bytes;
    }
    
    stats.avg_time = time_sum / results.size();
    stats.avg_calls = calls_sum / results.size();
    stats.avg_depth = depth_sum / results.size();
    stats.avg_memory = memory_sum / results.size();
    
    // Подбор константы для O(n log n)
    double c = 0;
    if (size > 1000) {
        // c * n * log2(n) > worst_time
        double nlogn = size * log2(size);
        c = (stats.worst_time / nlogn) * 1.2; // +20% запас
    } else {
        double nlogn = size * log2(size);
        c = stats.avg_time / nlogn;
    }
    
    stats.big_o = c * size * log2(size);
    
    return stats;
}

// Сохранение результатов в CSV
void saveToCSV(const vector<SeriesStats>& allStats, 
               const vector<SortResult>& allRawData,
               const vector<int>& sizes) {
    
    // Сохранение статистики
    ofstream stats_file("merge_sort_stats.csv");
    stats_file << "Size,"
               << "BestTime_ns,WorstTime_ns,AvgTime_ns,"
               << "BestCalls,WorstCalls,AvgCalls,"
               << "BestDepth,WorstDepth,AvgDepth,"
               << "BestMemory,WorstMemory,AvgMemory,"
               << "BigO_ns\n";
    
    for (const auto& s : allStats) {
        stats_file << s.size << ","
                   << fixed << setprecision(2)
                   << s.best_time << ","
                   << s.worst_time << ","
                   << s.avg_time << ","
                   << s.best_calls << ","
                   << s.worst_calls << ","
                   << s.avg_calls << ","
                   << s.best_depth << ","
                   << s.worst_depth << ","
                   << s.avg_depth << ","
                   << s.best_memory << ","
                   << s.worst_memory << ","
                   << s.avg_memory << ","
                   << s.big_o << "\n";
    }
    stats_file.close();
    
    // Сохранение сырых данных
    ofstream raw_file("merge_raw_data.csv");
    raw_file << "Size,Attempt,Time_ns,RecursiveCalls,MaxDepth,ExtraMemory\n";
    
    for (const auto& r : allRawData) {
        raw_file << r.size << ","
                 << r.attempt << ","
                 << r.time_ns << ","
                 << r.recursive_calls << ","
                 << r.max_recursion_depth << ","
                 << r.extra_memory_bytes << "\n";
    }
    raw_file.close();
    
    cout << "\nResults saved to merge_sort_stats.csv and merge_raw_data.csv\n";
}

// Многопоточное выполнение всех тестов
void runAllTests(const vector<int>& sizes, int attempts) {
    cout << "=== MERGE SORT ANALYSIS ===\n";
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
        futures.push_back(async(launch::async, runSizeTests, size, attempts, thread_id++));
    }
    
    // Собираем результаты
    vector<vector<SortResult>> allResults;
    for (auto& fut : futures) {
        auto results = fut.get();
        allResults.push_back(results);
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
        cout << "  Avg recursive calls: " << stats.avg_calls << "\n";
        cout << "  Avg recursion depth: " << stats.avg_depth << "\n";
        cout << "  Avg extra memory: " << stats.avg_memory << " bytes\n";
    }
    
    // Сохраняем результаты
    saveToCSV(allStats, allRawData, sizes);
    
    cout << "\nTesting completed successfully!\n";
}

int main() {
    try {
        vector<int> sizes = {1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000};
        int attempts = 20;
        
        runAllTests(sizes, attempts);
        
        cout << "\nRun plot_merge_sort.py to generate plots\n";
        
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}