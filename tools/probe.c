#include <stdio.h>
int main(void) {
    FILE *f = fopen("build/v0/pk_annexb.bin", "rb");
    printf("f=%p\n", (void *)f);
    if (!f) return 1;
    unsigned n = 0;
    size_t r = fread(&n, 4, 1, f);
    printf("r=%llu n=%u\n", (unsigned long long)r, n);
    unsigned char buf[16];
    size_t r2 = fread(buf, 1, 16, f);
    printf("r2=%llu first=%02x %02x %02x %02x\n", (unsigned long long)r2, buf[0], buf[1], buf[2], buf[3]);
    return 0;
}