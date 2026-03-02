
#include <stdio.h>

int main()
{
    int size, i;
    double sum=0;

    printf("Нийт нэмэх тоо: ");
    scanf("%d", &size);

    double array[size];
    printf("%d тоог оруулна уу?:\n", size);

    for (i = 0; i < size; i++) {
        scanf("%lf", &array[i]);
        sum += array[i];
    }

    printf("Нийлбэр: %lf ", sum);
    return 0;
}