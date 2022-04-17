#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#define N_THREADS 100
int counter;
void *thread_code (void *arg) {
    counter = counter + 1;
    pthread_exit(0);
}
void start_threads() {
    int i;
    pthread_t threads[N_THREADS];
    counter = 0;
    for (i = 0; i < N_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_code, NULL);
    }
    for (i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    printf("Counter value: %d\n", counter);
}
void test(int nums){
    int pass = 0;
    for(int i = 0; i < nums; i++) {
        counter = 0;
        start_threads();
        if(counter == N_THREADS) {
            pass++;
            printf("test %d out of %d PASSED\n", i + 1, nums);
        } else {
            printf("test %d out of %d FAILED\n", i + 1, nums);
        }
    }
    printf("passed %d tests out of %d tests\n", pass, nums);
}
int main() {
    test(1000);
    return EXIT_SUCCESS;
}