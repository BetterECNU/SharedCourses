#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int compare(const void *a, const void *b)
{
    return (*(int *)a - *(int *)b);
}

void merge(int *a, int *b, int *merged, int size)
{
    int i = 0, j = 0, k = 0;
    while (i < size && j < size)
    {
        if (a[i] < b[j])
        {
            merged[k++] = a[i++];
        }
        else
        {
            merged[k++] = b[j++];
        }
    }
    while (i < size)
        merged[k++] = a[i++];
    while (j < size)
        merged[k++] = b[j++];
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);
    int my_rank, comm_sz;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    const int LOCAL_SIZE = 1250; // 共排序10000个元素，用8个进程，每个进程1250个元素

    int *full_data = NULL;
    if (my_rank == 0)
    {
        FILE *fp = fopen("input.txt", "r");
        if (fp == NULL)
        {
            fprintf(stderr, "Failed to open input file\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        int total_size = comm_sz * LOCAL_SIZE;
        full_data = malloc(total_size * sizeof(int));
        for (int i = 0; i < total_size; i++)
        {
            if (fscanf(fp, "%d", &full_data[i]) != 1)
            {
                fprintf(stderr, "Invalid input format\n");
                MPI_Abort(MPI_COMM_WORLD, 1);
            }
        }
        fclose(fp);
    }

    int *local_data = malloc(LOCAL_SIZE * sizeof(int));
    if (local_data == NULL)
    {
        fprintf(stderr, "Memory allocation failed!\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    MPI_Scatter(full_data, LOCAL_SIZE, MPI_INT,
                local_data, LOCAL_SIZE, MPI_INT,
                0, MPI_COMM_WORLD);

    // 本地排序
    qsort(local_data, LOCAL_SIZE, sizeof(int), compare);

    // 奇偶阶段排序
    for (int phase = 0; phase < comm_sz; phase++)
    {
        int partner;
        // 计算partner
        if (phase % 2 == 0)
        {
            partner = my_rank + 1;
        }
        else
        {
            partner = my_rank - 1;
        }

        // 检查partner是否有效
        if (partner < 0 || partner >= comm_sz)
        {
            continue;
        }

        // 准备发送和接收缓冲区
        int *received_data = malloc(LOCAL_SIZE * sizeof(int));
        int *merged_data = malloc(2 * LOCAL_SIZE * sizeof(int));

        // 使用阻塞式通信交换数据
        MPI_Sendrecv(local_data, LOCAL_SIZE, MPI_INT, partner, 0,
                     received_data, LOCAL_SIZE, MPI_INT, partner, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        // 合并两个有序数组
        merge(local_data, received_data, merged_data, LOCAL_SIZE);

        // 保留前一半或后一半
        if (my_rank < partner)
        {
            // 保留较小的一半
            for (int i = 0; i < LOCAL_SIZE; i++)
            {
                local_data[i] = merged_data[i];
            }
        }
        else
        {
            // 保留较大的一半
            for (int i = 0; i < LOCAL_SIZE; i++)
            {
                local_data[i] = merged_data[LOCAL_SIZE + i];
            }
        }

        free(received_data);
        free(merged_data);
    }

    // 排序完成后收集结果到0号进程
    int *global_data = NULL;
    if (my_rank == 0)
    {
        global_data = malloc(comm_sz * LOCAL_SIZE * sizeof(int));
    }

    MPI_Gather(local_data, LOCAL_SIZE, MPI_INT,
               global_data, LOCAL_SIZE, MPI_INT,
               0, MPI_COMM_WORLD);

    if (my_rank == 0)
    {
        FILE *fout = fopen("output.txt", "w");
        if (fout == NULL)
        {
            fprintf(stderr, "Failed to open output file\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        for (int i = 0; i < comm_sz * LOCAL_SIZE; i++)
        {
            fprintf(fout, "%d ", global_data[i]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }

    free(local_data);
    free(full_data);
    free(global_data);
    MPI_Finalize();
    return 0;
}