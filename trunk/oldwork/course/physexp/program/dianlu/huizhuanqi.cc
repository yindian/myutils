#include<stdio.h>
#define PRINTARRAY(ar, n, fmt) do{\
	 int i;\
	 printf(#fmt, ar[0]);\
	 for (i = 1; i < n; ++i)\
	  printf(" "#fmt, ar[i]);\
	 printf("\n");\
}while(0)
int cedianzu()
{
	int n = 9;
	double R = 1,
	Rl[]={
	    0.5,
	    1,
	    2,
	    4,
	    8,
	    16,
	    32,
	    50,
	    1.0/0
	},
	U1[]={
	    0.673,
	    0.506,
	    0.343,
	    0.206,
	    0.115,
	    0.061,
	    0.032,
	    0.021,
	    0
	},
	Ur[]={
	    0.336,
	    0.500,
	    0.667,
	    0.802,
	    0.894,
	    0.949,
	    0.968,
	    0.989,
	    1.007
	},
	U2[]={
	    0.322,
	    0.510,
	    0.681,
	    0.823,
	    0.897,
	    0.968,
	    1.003,
	    1.000,
	    1.003
	},
	I1[n], I2[n], r1[n], r2[n], ra[n];

	int i;

	for (i = 0; i < n; ++i)
	{
		I1[i] = Ur[i] / R;
		I2[i] = -U2[i]/Rl[i];
		r1[i] = U2[i]/I1[i];
		r2[i] = -U1[i]/I2[i];
		ra[i] = (r1[i]+r2[i])/2.;
	}
	PRINTARRAY(Rl, n, %7.3lf);
	PRINTARRAY(U1, n, %7.3lf);
	PRINTARRAY(Ur, n, %7.3lf);
	PRINTARRAY(U2, n, %7.3lf);
	printf("------------------------------------\n");
	PRINTARRAY(I1, n, %7.3lf);
	PRINTARRAY(I2, n, %7.3lf);
	PRINTARRAY(r1, n, %7.3lf);
	PRINTARRAY(r2, n, %7.3lf);
	PRINTARRAY(ra, n, %7.3lf);

	ra[n-1] = r1[n-1];

	double r = 0; 
	for (i = 0; i < n; ++i)
		r += ra[i];
	r /= n;
	printf("%lf\n", r);
	return 0;
}
void yanxianxing()
{
	int n = 6;
	double R= 1, Rl = 2,
	       U1[]={
		       1.961,
		       1.402,
		       0.506,
		       -0.423,
		       -1.008,
		       -1.503
	       },
	       Ur[] = {
		       2.972,
		       2.004,
		       0.998,
		       -0.989,
		       -1.993,
		       -2.987
	       },
	       I1[n], Rin[n];

	int i;
	for (i = 0; i < n; ++i)
	{
		I1[i] = Ur[i] / R;
		Rin[i] = U1[i] / I1[i];
	}

	PRINTARRAY(U1, n, %7.3lf);
	PRINTARRAY(Ur, n, %7.3lf);
	printf("---------------------\n");
	PRINTARRAY(I1, n, %7.3lf);
	PRINTARRAY(Rin, n, %7.3lf);


}
int main()
{
	yanxianxing();
	return 0;
}
