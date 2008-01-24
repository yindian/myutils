#include<stdio.h>
#include<stdlib.h>
#include<math.h>
double average_result;
//	Macro AVERAGE below is used as: AVERAGE(0, n, x[i]*y[i])
#define AVERAGE(lo, hi, expr) do{\
	int i;\
	average_result = 0;\
	for (i = lo; i < hi; ++i)\
		average_result += expr;\
	average_result = average_result / (double)(hi-lo);\
}while(0)
int main(int argc, char *argv[])
{
	if (argc != 2)
	{
		puts("Usage: aver num");
		return 0;
	}
	int n = atoi(argv[1]);
	double x[n], aver;
	int i;
	for (i = 0; i < n; ++i)
		scanf("%lf", &x[i]);

	AVERAGE(0, n, x[i]);
	aver = average_result;
	printf("Average = %le\n", aver);
	AVERAGE(0, n, (x[i] - aver) * (x[i] - aver) / (n-1.));
	printf("Stderr = %le\n", sqrt(average_result));
	return 0;
}
