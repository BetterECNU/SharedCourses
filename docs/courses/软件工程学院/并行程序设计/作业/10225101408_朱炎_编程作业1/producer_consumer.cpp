#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <queue>
#include <omp.h>
#include <chrono>
#include <thread>

std::queue<std::string> shared_queue;
int producers_done = 0;
omp_lock_t queue_lock;
omp_lock_t output_lock;
int n;

void producer(int file_index, const char *filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
    {
#pragma omp critical
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    std::string line;
    while (std::getline(file, line))
    {
        omp_set_lock(&queue_lock);
        shared_queue.push(line);
        omp_unset_lock(&queue_lock);
    }
    omp_set_lock(&queue_lock);
    producers_done++;
    omp_unset_lock(&queue_lock);
}

void consumer()
{
    while (true)
    {
        std::string line;
        bool should_exit = false;

        omp_set_lock(&queue_lock);
        if (!shared_queue.empty())
        {
            line = shared_queue.front();
            shared_queue.pop();
            omp_unset_lock(&queue_lock);

            std::istringstream iss(line);
            std::string word;
            while (iss >> word)
            {
                omp_set_lock(&output_lock);
                std::cout << word << std::endl;
                omp_unset_lock(&output_lock);
            }
        }
        else
        {
            if (producers_done == n)
                should_exit = true;
            omp_unset_lock(&queue_lock);
            if (should_exit)
                break;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }
}

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        std::cerr << "Usage: " << argv[0] << " n file1 file2 ... filen" << std::endl;
        return 1;
    }
    n = std::stoi(argv[1]);
    if (argc != n + 2)
    {
        std::cerr << "Expected " << n << " files, got " << (argc - 2) << std::endl;
        return 1;
    }

    omp_init_lock(&queue_lock);
    omp_init_lock(&output_lock);

#pragma omp parallel num_threads(2 * n)
    {
        int tid = omp_get_thread_num();
        if (tid < n)
        {
            producer(tid, argv[2 + tid]);
        }
        else
        {
            consumer();
        }
    }

    omp_destroy_lock(&queue_lock);
    omp_destroy_lock(&output_lock);

    std::cout << std::endl
              << "All producers and consumers have finished." << std::endl;
    return 0;
}

// g++ -o producer_consumer -fopenmp producer_consumer.cpp -std=c++11
// .\producer_consumer 4 1.txt 2.txt 3.txt 4.txt