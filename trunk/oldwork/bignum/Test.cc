#include<iostream>
#include<string>
#include"bignum.h"
using namespace std;
int main()
{
	UBigNum b;
	b.enlarge();
	cout<<b.to_str()<<endl;
	return 0;
}
