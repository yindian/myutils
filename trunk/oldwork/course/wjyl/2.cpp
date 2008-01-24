#include<stdio.h>
int main()
{
	float one = 1.;
	float dy = 0.2;
	float a[4] = {dy, one-dy, dy, one-dy};
	float result;
	int i;
	__asm {
		push esi;
		push edi;
		lea esi, a;
		lea edi, result;
		movups xmm2, [esi];		// a b c d
		xorps xmm0, xmm0;
		movups xmm1, xmm2;
		shufps xmm1, xmm1, 0x00;	// a a a a
		addss xmm0, xmm1;
		movups xmm1, xmm2;
		shufps xmm1, xmm1, 0x55;	// b b b b
		addss xmm0, xmm1;
		movups xmm1, xmm2;
		shufps xmm1, xmm1, 0xAA;	// c c c c
		addss xmm0, xmm1;
		movups xmm1, xmm2;
		shufps xmm1, xmm1, 0xFF;	// d d d d
		addss xmm0, xmm1;
		movss [edi], xmm0
		pop edi;
		pop esi;
	}
	printf("%g\n", result);
	return 0;
}