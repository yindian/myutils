#include<stdio.h>
int main()
{
	float a[4] = {0};
	float one = 1.;
	float dy = 0.2;
	int i;
	__asm {
		push edi;
		lea edi, a;
		movss xmm1, one;	// 0 0 0 1.
		movss xmm2, dy;		// 0 0 0 dy
		subss xmm1, xmm2;	// xmm1 = 0 0 0 1-dy
		xorps xmm0, xmm0;	// 0 0 0 0
		unpcklps xmm0, xmm1;	// 0 0 1-dy 0
		addss xmm0, xmm2	// 0 0 1-dy dy
		movlhps xmm0, xmm0;	// 1-dy dy 1-dy dy
		movups [edi], xmm0;
		pop edi;
	}
	for (i = 3; i >= 0; --i)
		printf("%f\t", a[i]);
	printf("\n");
	return 0;
}
