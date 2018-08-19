int main() {
    while (1) {
        long long a, d;
        asm volatile("rdtsc" : "=a" (a), "=d" (d));
        printf("Cycles: %llu\n", (a | (d << 32)));
    }
}