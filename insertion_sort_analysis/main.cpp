#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <fstream>
#include <algorithm>
#include <iomanip>
#include <string>
#include <cmath>

using namespace std;
using namespace chrono;

// Structure for storing results of one run
struct SortResult {
    long long time_ns;
    long long iterations;
    long long swaps;
    
    SortResult() : time_ns(0), iterations(0), swaps(0) {}
    SortResult(long long t, long long iter, long long sw) 
        : time_ns(t), iterations(iter), swaps(sw) {}
};

// Insertion sort class with counters
class InsertionSorter {
private:
    long long iterations_;
    long long swaps_;
    
public:
    InsertionSorter() : iterations_(0), swaps_(0) {}
    
    void reset() {
        iterations_ = 0;
        swaps_ = 0;
    }
    
    void sort(vector<double>& arr) {
        int n = arr.size();
        
        for (int i = 1; i < n; i++) {
            double key = arr[i];
            int j = i - 1;
            
            iterations_++; // Count outer pass
            
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
                swaps_++; // Count movement
                iterations_++; // Count inner pass
            }
            
            if (j + 1 != i) {
                arr[j + 1] = key;
                swaps_++; // Count insertion
            }
        }
    }
    
    long long getIterations() const { return iterations_; }
    long long getSwaps() const { return swaps_; }
};

// Generate random array
vector<double> generateArray(int size) {
    static random_device rd;
    static mt19937 engine(rd());
    static uniform_real_distribution<double> dist(-1.0, 1.0);
    
    vector<double> arr(size);
    for (auto& x : arr) x = dist(engine);
    return arr;
}

// Run one series of tests
vector<SortResult> runSeries(int size, int attempts) {
    vector<SortResult> results;
    InsertionSorter sorter;
    
    for (int i = 0; i < attempts; i++) {
        // Generate array
        vector<double> arr = generateArray(size);
        
        // Reset counters
        sorter.reset();
        
        // Measure time
        auto start = high_resolution_clock::now();
        sorter.sort(arr);
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<nanoseconds>(end - start);
        
        // Save result
        results.emplace_back(duration.count(), sorter.getIterations(), sorter.getSwaps());
    }
    
    return results;
}

// Structure for series statistics
struct SeriesStats {
    int size;
    double best_time;
    double worst_time;
    double avg_time;
    double avg_swaps;
    double avg_iterations;
    double big_o;
    
    SeriesStats() : size(0), best_time(0), worst_time(0), avg_time(0), 
                    avg_swaps(0), avg_iterations(0), big_o(0) {}
};

// Compute statistics
SeriesStats computeStats(const vector<SortResult>& results, int size) {
    SeriesStats stats;
    stats.size = size;
    
    if (results.empty()) return stats;
    
    // Time statistics
    stats.best_time = results[0].time_ns;
    stats.worst_time = results[0].time_ns;
    double time_sum = 0;
    double swaps_sum = 0;
    double iter_sum = 0;
    
    for (const auto& r : results) {
        time_sum += r.time_ns;
        swaps_sum += r.swaps;
        iter_sum += r.iterations;
        
        if (r.time_ns < stats.best_time) stats.best_time = r.time_ns;
        if (r.time_ns > stats.worst_time) stats.worst_time = r.time_ns;
    }
    
    stats.avg_time = time_sum / results.size();
    stats.avg_swaps = swaps_sum / results.size();
    stats.avg_iterations = iter_sum / results.size();
    
    // Fit constant for O(n^2)
    double c = 0;
    if (size > 1000) {
        c = (stats.worst_time / (static_cast<double>(size) * size)) * 1.2; // +20% margin
    } else {
        c = stats.avg_time / (static_cast<double>(size) * size);
    }
    stats.big_o = c * size * size;
    
    return stats;
}

// Save results to CSV
void saveToCSV(const vector<SeriesStats>& allStats, 
               const vector<vector<SortResult>>& allData,
               const vector<int>& sizes) {
    
    // Save statistics
    ofstream stats_file("sorting_stats.csv");
    stats_file << "Size,BestTime_ns,WorstTime_ns,AvgTime_ns,AvgSwaps,AvgIterations,BigO_ns\n";
    
    for (const auto& s : allStats) {
        stats_file << s.size << ","
                   << fixed << setprecision(2)
                   << s.best_time << ","
                   << s.worst_time << ","
                   << s.avg_time << ","
                   << s.avg_swaps << ","
                   << s.avg_iterations << ","
                   << s.big_o << "\n";
    }
    stats_file.close();
    
    // Save raw data
    ofstream raw_file("raw_data.csv");
    raw_file << "Size,Attempt,Time_ns,Iterations,Swaps\n";
    
    for (size_t i = 0; i < sizes.size(); i++) {
        for (size_t j = 0; j < allData[i].size(); j++) {
            raw_file << sizes[i] << ","
                     << j + 1 << ","
                     << allData[i][j].time_ns << ","
                     << allData[i][j].iterations << ","
                     << allData[i][j].swaps << "\n";
        }
    }
    raw_file.close();
    
    cout << "Results saved to sorting_stats.csv and raw_data.csv\n";
}

// Main function
int main() {
    // Test parameters
    vector<int> sizes = {1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000};
    int attempts = 20;
    
    cout << "=== Insertion Sort Analysis ===\n";
    cout << "Array sizes: ";
    for (int s : sizes) cout << s << " ";
    cout << "\nAttempts per size: " << attempts << "\n\n";
    
    vector<vector<SortResult>> allData;
    vector<SeriesStats> allStats;
    
    // Run tests
    for (int size : sizes) {
        cout << "Testing size " << size << "... ";
        cout.flush();
        
        auto results = runSeries(size, attempts);
        allData.push_back(results);
        
        auto stats = computeStats(results, size);
        allStats.push_back(stats);
        
        cout << "done\n";
        cout << "  Best: " << stats.best_time << " ns\n";
        cout << "  Worst: " << stats.worst_time << " ns\n";
        cout << "  Average: " << stats.avg_time << " ns\n";
    }
    
    // Save results
    saveToCSV(allStats, allData, sizes);
    
    cout << "\nTesting completed!\n";
    cout << "Run plot_graphs.py to generate plots\n";
    
    return 0;
}