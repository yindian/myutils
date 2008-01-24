/*
 * 	bignum.h
 * 	C++ Header file for big num maniplation
 * 	Hist:	050627 050628		All except exception and division
 * 		050704			comparison, part of division
 * 		050722			bitwise shift right
 * 		050723			bitwise shift left, equality compare, division & modulo
 * 		050724			Added BNDEBUG output. Fixed bug in multiplication: access out of alloc.
 * 					Fixed bug in divide(). Since shr1() doesn't entighten, so entighten() shd b added.
 * 					Fixed bug in comparison operation. All bullshit I've written!!!
 * 					Refined input/output. Input speed up very obvious.
 * 					Added mul10, add10, sub10.
 * 					Added BigNum, a new class for signed intergers. Modulo is guaranteed to >=0
 * 					Fixed serious bug in operation-= +=: access out of alloc. !!!!!!!
 * 					Adjusted SizeIncrement to 256, so that the increase in speed is apparent.
 */
#ifndef __bignum_h_
#define __bignum_h_
#ifndef DO_NOTHING
#define DO_NOTHING
#endif

#include"ydexception.h"
#include<string>
#include<vector>

namespace yd_algorithm {

static const unsigned int SizeIncrement = 256;

typedef short INT16;
typedef unsigned short UINT16;
typedef long INT32;
typedef unsigned long UINT32;
typedef long long INTBIG;

////////////			Unsigned bignum class
/*
 * 	Notes:
 * 	1. One integer has only one representation which costs least memory (shrinked the leading zeros).
 */
class UBigNum {
	public:
		UBigNum(INTBIG x = 0);
		UBigNum(const UBigNum &b);
		UBigNum &operator=(UBigNum b);
		~UBigNum() {delete[] base;}
		bool isZero();
		int getsize() {return size;}

		UBigNum operator+(UBigNum b);
		UBigNum &operator+=(UBigNum b);
		UBigNum operator++() {*this += 1; return *this;}
		UBigNum operator++(int) {UBigNum t = *this; *this += 1; return t;}

		UBigNum operator-(UBigNum b);
		UBigNum &operator-=(UBigNum b);
		UBigNum operator--() {*this -= 1; return *this;}
		UBigNum operator--(int) {UBigNum t = *this; *this -= 1; return t;}

		UBigNum operator*(UBigNum b);
		UBigNum &operator*=(UBigNum b);

		void divide(UBigNum b, UBigNum &quotient, UBigNum &remainder);
		UBigNum operator/(UBigNum b);
		UBigNum &operator/=(UBigNum b);
		UBigNum operator%(UBigNum b);
		UBigNum &operator%=(UBigNum b);

		UBigNum &operator<<=(unsigned bits);
		UBigNum operator<<(unsigned bits);
		UBigNum &shl1();

		UBigNum &operator>>=(unsigned bits);
		UBigNum operator>>(unsigned bits);
		UBigNum &shr1();

		bool operator<(UBigNum b);
		bool operator<=(UBigNum b);
		bool operator>(UBigNum b);
		bool operator>=(UBigNum b);
		bool operator==(UBigNum b);
		bool operator!=(UBigNum b);

		std::string to_str();
		INTBIG get_low_8_byte();
		int div10(UINT16 deno = 10);
		void mul10(UINT16 mul = 10);
		void add10(UINT16 add = 10);
		void sub10(UINT16 sub = 10);

		friend std::ostream &operator<<(std::ostream &out, UBigNum b);
		friend std::istream &operator>>(std::istream &ins, UBigNum &b);
		void outputhex(std::ostream &out);
	private:
		UINT16 *base;
		int size;
		void enlarge();
		void preserve(int acquireindex);
		void entighten();
};

//////			Implementation of UBigNum
//	Constructors and assignment/*{{{*/
UBigNum::UBigNum(INTBIG x)/*{{{*/
{
	UINT16 *p, *q;
	unsigned int s = SizeIncrement;
	int n;
	while (s < sizeof(INTBIG))
		s += SizeIncrement;
	size = s;
	base = new unsigned short[size];
	n = sizeof(INTBIG)/sizeof(UINT16);
	for (p = base, q = (UINT16*)&x; p-base < n; *p++ = *q++)
		DO_NOTHING;
	for (; p-base < size; *p++ = 0)
		DO_NOTHING;
	entighten();
}
UBigNum::UBigNum(const UBigNum &b)
{
	UINT16 *p, *q;
	size = b.size;
	base = new UINT16[size];
	for (p = base, q = b.base; p-base<size; *p++ = *q++)
		DO_NOTHING;
}
UBigNum &UBigNum::operator=(UBigNum b)
{
	UINT16 *p, *q;
	delete[] base;
	size = b.size;
	base = new UINT16[size];
	for (p = base, q = b.base; p-base<size; *p++ = *q++)
		DO_NOTHING;
	return *this;
}/*}}}*/

//	enlarge and isZero and entighten
void UBigNum::enlarge()/*{{{*/
{
	UINT16 *p, *q, *newbase;
	newbase = new UINT16[size+SizeIncrement];
	for (p = newbase, q = base; q-base<size; *p++ = *q++)
		DO_NOTHING;
	size += SizeIncrement;
	for (; p-newbase<size; *p++ = 0)
		DO_NOTHING;
	delete[] base;
	base = newbase;
}

void UBigNum::preserve(int acquireindex)
{
	if (acquireindex < size)
		return;
	UINT16 *p, *q, *newbase;
	int newsize;
	newsize = (acquireindex / SizeIncrement + 1) * SizeIncrement;
	newbase = new UINT16[newsize];
	for (p = newbase, q = base; q-base<size; *p++ = *q++)
		DO_NOTHING;
	size = newsize;
	for (; p-newbase<size; *p++ = 0)
		DO_NOTHING;
	delete[] base;
	base = newbase;
}

void UBigNum::entighten()	// placed after every operation that can make the number less
{
	UINT16 *p, *q, *newbase;
	int dec_times;
	dec_times = 0;
	for (p = base+size-1; p > base && *p == 0; --p)
		++dec_times;
	dec_times = dec_times / SizeIncrement;
	if (dec_times == 0)
		return;

	size -= dec_times*SizeIncrement;
	newbase = new UINT16[size];
	for (p = newbase, q = base; q-base<size; *p++ = *q++)
		DO_NOTHING;
	delete[] base;
	base = newbase;
}

bool UBigNum::isZero()
{
	for (UINT16 *p = base; p-base < size; ++p)
		if (*p)
			return false;
	return true;
}/*}}}*/

//	operator+ and operator+=
UBigNum UBigNum::operator+(UBigNum b)/*{{{*/
{
	UBigNum t(*this);
	t += b;
	return t;
}
UBigNum &UBigNum::operator+=(UBigNum b)
{
	int i, carry = 0;
	UINT32 t;
	for (i = 0; i < b.size || carry; ++i)
	{
		if (i == size)
			enlarge();
		t = base[i];
		if (i < b.size)
			t += b.base[i]+carry;
		else 
			t += carry;
		base[i] = t & 0xffff;
		carry = t >> 16;
	}
	return *this;
}
/*}}}*/

//	operator- and operator-=
UBigNum UBigNum::operator-(UBigNum b)/*{{{*/
{
	UBigNum t(*this);
	t -= b;
	return t;
}
UBigNum &UBigNum::operator-=(UBigNum b)
{
	int i, carry = 0;
	INT32 t;
#ifdef BNDEBUGSUB
	std::cerr<<"Substraction: \n "<<*this<<"\n-"<<b<<"\n    size="<<size<<"   b.size="<<b.size<<"\n";
#endif
	if (b.size > size)
		throw underflow();
	for (i = 0; i < b.size || carry; ++i)
	{
		if (i == size)
			throw underflow();
		if (i < b.size)
			t = (INT32) base[i] - b.base[i] + carry;
		else
			t = (INT32) base[i] + carry;
		base[i] = t & 0xffff;
		carry = t >> 16;	// carry = 0 or -1
	}
#ifdef BNDEBUGSUB
	std::cerr<<"="<<*this<<"\n";
#endif
	entighten();
#ifdef BNDEBUGSUB
	std::cerr<<"="<<*this<<"\n\n";
#endif
	return *this;
}
/*}}}*/

//	div10 and tostr etc
int UBigNum::div10(UINT16 deno)/*{{{*/
{
	UINT32 mod, tmp;
	UINT16 *p = base + size;
	mod = 0;
	while (p > base && !*--p)			// find the first non-zero offset
		DO_NOTHING;
	while (p >= base)
	{
		tmp = (mod << 16) | *p;
		*p = tmp / deno;
		mod = tmp % deno;
		--p;
	}
	entighten();
	return mod;
}

void UBigNum::mul10(UINT16 mul)
{
	UINT32 carry, tmp;
	int i;
	carry = 0;
	for (i = 0; i < size || carry; ++i)
	{
		if (i == size)
			enlarge();
		tmp = (UINT32) base[i] * mul + carry;
		base[i] = tmp & 0xffff;
		carry = tmp >> 16;
	}
}

void UBigNum::add10(UINT16 add)
{
	UINT32 carry, tmp;
	int i;
	carry = 0;
	if (0 == size)
		enlarge();
	tmp = (UINT32) base[0] + add;
	base[0] = tmp & 0xffff;
	carry = tmp >> 16;
	for (i = 1; carry; ++i)
	{
		if (i == size)
			enlarge();
		tmp = (UINT32) base[i] + carry;
		base[i] = tmp & 0xffff;
		carry = tmp >> 16;
	}
}

void UBigNum::sub10(UINT16 sub)
{
	INT32 carry, t;
	int i;
	carry = 0;
	if (0 == size)
		throw underflow();
	t= (INT32) base[0] - sub;
	base[0] = t & 0xffff;
	carry = t >> 16;	// 0 or -1
	for (i = 1; carry; ++i)
	{
		if (i == size)
			throw underflow();
		t = (INT32) base[i] + carry;
		base[i] = t & 0xffff;
		carry = t >> 16;	// carry = 0 or -1
	}
}

std::string UBigNum::to_str()
{
	std::string str;
	UBigNum t = *this;
	do
	{
		str = char('0'+t.div10()) + str;
	} while (!t.isZero());
	return str;
}
INTBIG UBigNum::get_low_8_byte()
{
	return *((INTBIG *)base);
}/*}}}*/

//	operator* and operator*=
UBigNum UBigNum::operator*(UBigNum b)/*{{{*/
{
	UINT16 *btop = b.base + b.size;
	UINT16 *q;
	UINT32 t, carry;
	UBigNum tmp;
	int i, j;

#ifdef BNDEBUGMUL
	std::cerr<<"Multiplication: \n "<<*this<<"\n*"<<b<<'\n';
#endif
	while (btop > b.base && !*--btop)	// find first non-zero of b
		DO_NOTHING;
	for (q = b.base; q <= btop; ++q)
	{
		carry = 0;
		j = q-b.base;
		for (i=0; i < size; ++i)
		{
			tmp.preserve(i + j);
			t = (UINT32)base[i] * *q;
			t += tmp.base[i + j] + carry;
			tmp.base[i+j] = t & 0xffff;
			carry = t >> 16;
		}
		for (i += j; carry; ++i)
		{
			tmp.preserve(i + j);
			t = tmp.base[i] + carry;
			tmp.base[i] = t & 0xffff;
			carry = t >> 16;
		}
	}
#ifdef BNDEBUGMUL
	std::cerr<<"="<<tmp<<"\n";
#endif
	tmp.entighten();
#ifdef BNDEBUGMUL
	std::cerr<<"="<<tmp<<"\n\n";
#endif
	return tmp;
}
UBigNum &UBigNum::operator*=(UBigNum b)
{
	*this = this->operator*(b);
	return *this;
}
/*}}}*/

//	divide
void UBigNum::divide(UBigNum b, UBigNum &quotient, UBigNum &remainder)/*{{{*/
{
	if (isZero())
	{
		quotient = remainder = 0;
		return;
	}
	if (b.isZero())
		throw division_by_zero();

	UINT16 bitsets[16];
	UINT16 *hi, *bhi, *thi;
	int i, k;
	int tsize, tbit;
	int hibit, bhibit, thibit;
	for (i = 0, k = 1; i < 16; ++i, k <<= 1)
		bitsets[i] = k;
	for (hi = base + size; hi > base && !*--hi; )		//find first non-zero offset in *this
		DO_NOTHING;
	for (bhi = b.base + b.size; bhi > b.base && !*--bhi; )	//find first non-zero offset in b
		DO_NOTHING;
	for (hibit = 15; hibit >= 0 && !(bitsets[hibit] & *hi); --hibit)	// find first non-zero bit in *this
		DO_NOTHING;
	for (bhibit = 15; bhibit >=0 && !(bitsets[bhibit] & *bhi); --bhibit)	// find first non-zero bit in *this
		DO_NOTHING;
//	if (bhi == b.base && bhibit < 0)
//		throw division_by_zero();
//	if (hi == base && hibit < 0)
//		return tmp;				// :*this == 0
	//tsize = (hi - base) - (bhi - b.base);
	tbit = (hi - base) * sizeof(UINT16) * 8 + hibit 
		- (bhi - b.base) * sizeof(UINT16) * 8 - bhibit;
	if (tbit < 0)		// *this < b
	{
		quotient = 0;
		remainder = *this;
		return;
	}
	tsize = (tbit / (sizeof(UINT16) * 8)) + 1;
	quotient = 0;
	remainder = *this;
	quotient.preserve(tsize);
	b <<= tbit;
	thi = quotient.base + tsize - 1;
	thibit = tbit & (sizeof(UINT16) *8 -1);
#ifdef BNDEBUGDIV
				std::cerr<<"Division: \n ";
				outputhex(std::cerr);
				std::cerr<<"\n/";
				b.outputhex(std::cerr);
				std::cerr<<"\n";
#endif
	while (thi >= quotient.base)
	{
		if (remainder >= b)
		{
#ifdef BNDEBUGDIV
				std::cerr<<"Division: \n ";
				remainder.outputhex(std::cerr);
				std::cerr<<"\n-";
				b.outputhex(std::cerr);
				std::cerr<<"\n       r.size="<<remainder.size<<"   b.size="<<b.size<<"\n";
#endif
			*thi |= bitsets[thibit];
			remainder -= b;
		}
		b.shr1();
		b.entighten();
		if (--thibit < 0)
		{
			--thi;
			thibit = sizeof(UINT16) * 8 - 1;
		}
	}
	quotient.entighten();
	remainder.entighten();
}/*}}}*/

//	operator/ and operator/= operator% and operator%=
UBigNum UBigNum::operator/(UBigNum b)/*{{{*/
{
	UBigNum quot, remain;
	divide(b, quot, remain);
	return quot;
}
UBigNum &UBigNum::operator/=(UBigNum b)
{
	*this = this->operator/(b);
	return *this;
}
UBigNum UBigNum::operator%(UBigNum b)
{
	UBigNum quot, remain;
	divide(b, quot, remain);
	return remain;
}
UBigNum &UBigNum::operator%=(UBigNum b)
{
	*this = this->operator%(b);
	return *this;
}/*}}}*/

//	operator< <=
bool UBigNum::operator<(UBigNum b)/*{{{*/
{
	if (size > b.size)
		return false;
	else if (size < b.size)
		return true;
	UINT16 *p, *q;
	p = base + size;
	q = b.base + size;
	while (p > base && *--p == *--q)
		DO_NOTHING;
	return *p < *q;
}

bool UBigNum::operator<=(UBigNum b)
{
	if (size > b.size)
		return false;
	else if (size < b.size)
		return true;
	UINT16 *p, *q;
	p = base + size;
	q = b.base + size;
	while (p > base && *--p == *--q)
		DO_NOTHING;
	return *p <= *q;
}/*}}}*/

//	operator> >=
bool UBigNum::operator>(UBigNum b)/*{{{*/
{
	if (size > b.size)
		return true;
	else if (size < b.size)
		return false;
	UINT16 *p, *q;
	p = base + size;
	q = b.base + size;
	while (p > base && *--p == *--q)
		DO_NOTHING;
	return *p > *q;
}

bool UBigNum::operator>=(UBigNum b)
{
	if (size > b.size)
		return true;
	else if (size < b.size)
		return false;
	UINT16 *p, *q;
	p = base + size;
	q = b.base + size;
	while (p > base && *--p == *--q)
		DO_NOTHING;
	return *p >= *q;
}/*}}}*/

//	operator== !=
bool UBigNum::operator==(UBigNum b)/*{{{*/
{
	if (size != b.size)
		return false;
	for (int i = 0; i < size; ++i)
		if (base[i] != b.base[i])
			return false;
	return true;
}

bool UBigNum::operator!=(UBigNum b)
{
	return !operator==(b);
}/*}}}*/

//	operator>> >>= shr1
UBigNum &UBigNum::shr1()/*{{{*/
{
	UINT16 *p, carry, t;
	for (p = base + size - 1; p > base && *p == 0; --p)
		DO_NOTHING;
	t = carry = 0;
	for (; p >= base; --p)
	{
		t = *p & 1;
		*p = (carry << (sizeof(UINT16)*8-1)) | (*p >> 1);
		carry = t;
	}
	return *this;
}

UBigNum UBigNum::operator>>(unsigned bits)
{
	UBigNum tmp(*this);
	tmp >>= bits;
	return tmp;
}
UBigNum &UBigNum::operator>>=(unsigned bits)
{
	UINT16 *p, *q;
	int i;
	if (isZero())
		return *this;
	if (bits >= size * sizeof(UINT16) * 8)
		*this = 0;
	else
	{
		for (i = 0; i < (int)(bits & (sizeof(UINT16)*8-1)); ++i)
			shr1();
		bits = bits / sizeof(UINT16) / 8;
		if (bits > 0)
		{
			for (p = base, q = p + bits; q < base + size; ++p, ++q)
				*p = *q;
			for (; p < base + size; ++p)
				*p = 0;
		}
	}
	entighten();
	return *this;
}
/*}}}*/

//	operator<< <<= shl1
UBigNum &UBigNum::shl1()/*{{{*/
{
	UINT16 *p, carry, t;
	t = carry = 0;
	for (p = base; p < base + size; ++p)
		if (carry != 0 || *p != 0)	// otherwise nothing needs to be done
		{
			t = (*p & (1 << (sizeof(UINT16)*8-1))) != 0;
			*p = (*p << 1) | carry;
			carry = t;
		}
	if (carry)
	{
		enlarge();
		base[size - SizeIncrement] = 1;
	}
	return *this;
}

UBigNum &UBigNum::operator<<=(unsigned bits)
{
	UINT16 *p, *q;
	int i;
	unsigned leading0;
	if (isZero())
		return *this;
	for (i = 0; i < (int)(bits & (sizeof(UINT16)*8-1)); ++i)
		shl1();
	bits = bits / sizeof(UINT16) / 8;
	if (bits > 0)
	{
		for (p = base + size - 1; p > base && *p == 0; --p)
			DO_NOTHING;
		leading0 = base + size - 1 - p;
		while (leading0 < bits)
		{
			enlarge();
			leading0 += SizeIncrement;
		}
		for (p = base + size - 1, q = p - bits; q >= base; --p, --q)
			*p = *q;
		for (; p >= base; --p)
			*p = 0;
	}
	entighten();
	return *this;
}

UBigNum UBigNum::operator<<(unsigned bits)
{
	UBigNum tmp(*this);
	tmp <<= bits;
	return tmp;
}/*}}}*/

//	input and output
std::ostream &operator<<(std::ostream &out, UBigNum b)/*{{{*/
{
	std::vector<char> S;
	do
	{
		S.push_back('0' + b.div10());
	} while (!b.isZero());
	for (int i = S.size() - 1; i >= 0; --i)
		out.put(S[i]);
	//out<<b.to_str();
	return out;
}

std::istream &operator>>(std::istream &ins, UBigNum &b)
{
	char ch;
	b = 0;
	ins.get(ch);
	while (ins && (ch == ' ' || ch == '\t' || ch == '\n'))
		ins.get(ch);
	while (ins)
	{
		if (ch >= '0' && ch <= '9')
		{
			b.mul10();
			b.add10(ch - '0');
		}
		else
		{
			break;
		}
		ins.get(ch);
	}
	ins.putback(ch);
	return ins;
}

void UBigNum::outputhex(std::ostream &out)
{
	UINT16 *p;
	char hexout[] = "0123456789ABCDEF";
	out<<"0x";
	for (p = base +size - 1; p > base && *p == 0; --p)
		DO_NOTHING;
	for (; p >= base; --p)
		out<<hexout[ *p >> 12 ]<<hexout[ (*p >> 8) & 0xf]<<hexout[ (*p >> 4) & 0xf]<<hexout[*p & 0xf];
}
/*}}}*/
/*}}}*/

////////////			Signed bignum class
/*
 * 	Notes:
 * 	1. Division satisfies:  a = b * q + r;	where r >= 0;
 * 	2. Bitwise shift only multiplies or divides the absolute part of the number.
 * 	3. Zero is with sign = 1.
 */
class BigNum {
	public:
		BigNum(INTBIG x = 0)        :digits(x >= 0 ? x : -x),sign(x >= 0 ? 1 : -1) {}
		BigNum(const BigNum &b)        :digits(b.digits), sign(b.sign) {}
		BigNum(const UBigNum &b)        :digits(b), sign(1) {}
		BigNum &operator=(BigNum b)         { digits = b.digits; sign = b.sign; return *this;}
		~BigNum() {}
		bool isZero()         {return digits.isZero();}
		int getsize()         {return digits.getsize();}
		int getsign()         {if (isZero()) return 0; else return sign;}

		BigNum operator+(BigNum b)        {BigNum tmp = *this; tmp += b; return tmp; }
		BigNum &operator+=(BigNum b) {/*{{{*/
			if (getsign() * b.getsign() >= 0) 
				digits += b.digits;
			else if (b.sign > 0)	// *this < 0, b > 0
				if (digits <= b.digits) {
					sign = -sign;
					digits = b.digits - digits;
				}
				else
					digits -= b.digits;
			else 	// *this > 0, b < 0
				if (digits < b.digits) {
					sign = -sign;
					digits = b.digits - digits;
				}
				else
					digits -= b.digits;
			return *this;
		}/*}}}*/
		BigNum operator++()                {*this += 1; return *this;}
		BigNum operator++(int)             {BigNum t = *this; *this += 1; return t;}

		BigNum operator-()                 {BigNum tmp = *this; if (!tmp.isZero()) tmp.sign = -tmp.sign; return tmp;}
		BigNum operator-(BigNum b)         {BigNum tmp = *this; tmp -= b; return tmp;}
		BigNum &operator-=(BigNum b)       {return *this += -b;}
		BigNum operator--()                {*this -= 1; return *this;}
		BigNum operator--(int)             {BigNum t = *this; *this -= 1; return t;}

		BigNum operator*(BigNum b)        {BigNum tmp = *this; tmp *= b; return tmp;}
		BigNum &operator*=(BigNum b)      {digits *= b.digits; if (isZero()) sign=1; else sign*=b.sign; return *this;}

		void divide(BigNum b, BigNum &quotient, BigNum &remainder) {/*{{{*/
#ifdef BNDEBUGDIV
				std::cerr<<"IDivision: \n "<<*this<<"\n/"<<b<<"\n";
#endif
			digits.divide( b.digits, quotient.digits, remainder.digits);
			if (!quotient.isZero())		// quotient = 0 ==> sign = 1
				quotient.sign = sign * b.sign;
			else 
				quotient.sign = 1;
			if (!remainder.isZero())
				remainder.sign = sign;
			else
				remainder.sign = 1;
			if (remainder.sign < 0)		// *this < 0
			{
#ifdef BNDEBUGDIV
				std::cerr<<"IDivision: \n "<<*this<<"\n="<<b<<"\n*"<<quotient<<"\n+"<<remainder<<"\n";
#endif
				remainder.sign = 1;
				remainder.digits = b.digits - remainder.digits;
				if (!quotient.isZero() || b.sign < 0)
					++quotient.digits;
				else {
					quotient.digits = 1;
					quotient.sign = -1;
				}
#ifdef BNDEBUGDIV
				std::cerr<<"IDivision: \n "<<*this<<"\n="<<b<<"\n*"<<quotient<<"\n+"<<remainder<<"\n";
#endif
			}
		}/*}}}*/
		BigNum operator/(BigNum b)            {BigNum q, r; divide(b, q, r); return q;}
		BigNum &operator/=(BigNum b)          {return *this = *this / b; }
		BigNum operator%(BigNum b)            {BigNum q, r; divide(b, q, r); return r;}
		BigNum &operator%=(BigNum b)          {return *this = *this % b; }

		BigNum &operator<<=(unsigned bits)    {digits <<= bits; return *this;}
		BigNum operator<<(unsigned bits)      {BigNum tmp = *this; return tmp <<= bits; }
		BigNum &shl1()                        {digits.shl1(); return *this;}

		BigNum &operator>>=(unsigned bits)    {digits >>= bits; if (isZero()) sign = 1; return *this;}
		BigNum operator>>(unsigned bits)      {BigNum tmp = *this; return tmp >>= bits; }
		BigNum &shr1()                        {digits.shr1(); return *this;}

		bool operator<(BigNum b) {/*{{{*/
			if (sign < b.sign)
				return true;
			else if (sign > b.sign)
				return false;
			if (sign > 0)
				return digits < b.digits;
			else
				return digits > b.digits;
		}/*}}}*/
		bool operator<=(BigNum b)             {return !(*this > b);}
		bool operator>(BigNum b)              {return b < *this; }
		bool operator>=(BigNum b)             {return !(*this < b);}
		bool operator==(BigNum b)             {return sign == b.sign && digits == b.digits;}
		bool operator!=(BigNum b)             {return !operator==(b);}

		std::string to_str()                  {
			if (sign > 0) return digits.to_str(); else return std::string("-")+digits.to_str();
		}

		friend std::ostream &operator<<(std::ostream &out, BigNum b);
		friend std::istream &operator>>(std::istream &ins, BigNum &b);
		void outputhex(std::ostream &out) {if (sign <0) out<<'-'; digits.outputhex(out);}
	private:
		UBigNum digits;
		int sign;		// sign = -1 or 1
};

//////			Implementation of BigNum
std::ostream &operator<<(std::ostream &out, BigNum b)/*{{{*/
{
	if (b.sign < 0)
		out.put('-');
	return out<<b.digits;
}

std::istream &operator>>(std::istream &ins, BigNum &b)
{
	char ch;
	b = 0;
	ins.get(ch);
	while (ins && (ch == ' ' || ch == '\t' || ch == '\n'))
		ins.get(ch);
	if (ch == '-')
	{
		b.sign = -1;
		ins.get(ch);
	}
	while (ins)
	{
		if (ch >= '0' && ch <= '9')
		{
			b.digits.mul10();
			b.digits.add10(ch - '0');
		}
		else
		{
			break;
		}
		ins.get(ch);
	}
	ins.putback(ch);
	if (b.digits.isZero())
		b.sign = 1;
	return ins;
}/*}}}*/

}// namespace
#endif
