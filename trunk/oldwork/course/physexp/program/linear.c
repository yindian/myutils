#include<stdio.h>
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
int main()
{
	int n;
	fputs("Please input n:",stderr);
	scanf("%d",&n);

	double xx[n], yy[n];
	int i;
	fputs("Please input x:", stderr);
	for (i = 0; i < n; ++i)
		scanf("%lf", &xx[i]);
	fputs("Please input y:", stderr);
	for (i = 0; i < n; ++i)
		scanf("%lf", &yy[i]);

	double lxx, lxy, lyy, r;
	double xybar, xbar, ybar, xsqrbar, ysqrbar;

	AVERAGE(0, n, yy[i]); ybar = average_result;
	AVERAGE(0, n, xx[i]); xbar = average_result;
	AVERAGE(0, n, xx[i]*xx[i]); xsqrbar = average_result;
	AVERAGE(0, n, xx[i]*yy[i]); xybar = average_result;
	AVERAGE(0, n, yy[i]*yy[i]); ysqrbar = average_result;

	lxy = (xybar - xbar * ybar) * (double)n;
	lxx = (xsqrbar - xbar * xbar) * (double)n;
	lyy = (ysqrbar - ybar * ybar) * (double)n;
	r = lxy / sqrt(lxx * lyy);

	printf("\nlxy = %.10le\nlxx = %.10le\nlyy = %.10le\nr = %.10le\n", lxy, lxx, lyy, r);

	double m, b, sm, sb;
	m = lxy / lxx;
	b = ybar - m*xbar;
	sm = sqrt((1/r/r-1)/((double)n-2.)) * m;
	sb = sqrt(xsqrbar) *sm;
	printf("\nm = %.10le\nb = %.10le\nsm = %.10le\nsb = %.10le\n", m, b, sm, sb);

	return 0;
}
