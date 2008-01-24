#include<iostream>
#include<string>
#include"bignum.h"
#include"ydtiming.h"
using namespace std;
using namespace yd_algorithm;
int main()
{
	BigNum a, b, quot, rem;
	int i;
	try
	{
//		a += 4;/*{{{*/
//		cout<<a.to_str()<<endl;
//		a += 4000000000000LL;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//		UBigNum b=a;
//		cout<<b.to_str()<<endl;
//		cout<<b.get_low_8_byte()<<endl;
//		a = a+b;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//		a += a;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//
//		cout<<endl;
//		a -= b;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//		a -= b;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//		a -= 9;
//		cout<<a.to_str()<<endl;
//		cout<<a.get_low_8_byte()<<endl;
//
//		cout<<endl;
//		a *= a; 
//		cout<<a.to_str()<<endl;
//		a = a*a - a; 
//		cout<<a.to_str()<<endl;
//
//		cout<<"================"<<endl;
//		a = 5;
//		a = a - 3;
//		cout<<a.to_str()<<endl;
//	//	a = a - 3;
//	//	cout<<a.to_str()<<endl;
//		a = 188888888;
//		cout<<a.to_str()<<endl;
//		a = a >> 22;
//		cout<<a.to_str()<<endl;
//		cout<<"================"<<endl;
//
//		a = 1;
//		cout<<a.to_str()<<endl;
//		a = (a << 200) * 37;
//		cout<<a.to_str()<<endl;
//		a >>= 190;
//		cout<<a.to_str()<<endl;
//		cout<<"================"<<endl;
//		
//		a = a *a * a + a * 41 + 49999999;
//		cout<<a.to_str()<<"	|	"<<a.getsize()<<endl;
//		a /= 100;
//		cout<<a.to_str()<<"	|	"<<a.getsize()<<endl;
//		a %= 31;
//		cout<<a.to_str()<<"	|	"<<a.getsize()<<endl;
//		////////////////////////////////////////////
		cout<<"Please input two positive integers\n";
		begintiming();
		cin>>a>>b;
		endtiming();
		begintiming();
		cout<<"a="<<a<<endl;
		endtiming();
		begintiming();
		cout<<"b="<<b<<endl;
		endtiming();
		begintiming();
		cout<<"a+b="<<a+b<<endl;
		endtiming();
		begintiming();
		cout<<"a-b="<<a-b<<endl;
		endtiming();
		begintiming();
		cout<<"a*b="<<a*b<<endl;
		endtiming();
		begintiming();
		a.divide(b, quot, rem);
		endtiming();
		begintiming();
		cout<<"a/b="<<quot<<endl;
		endtiming();
		begintiming();
		cout<<"a\%b="<<rem<<endl;
		endtiming();
		cout<<a.getsize()<<' '<<b.getsize()<<' '<<quot.getsize()<<' '<<rem.getsize()<<endl;/*}}}*/
		/*
		begintiming();
		b = 31;
		for (i = 0; i < 6000; ++i)
			b *= 31;
		a = 37;
		for (i = 0; i < 6000; ++i)
			a *= 37;
		a = -a;
		endtiming();
		begintiming();
		cout<<"a="<<a<<endl;
		endtiming();
		begintiming();
		cout<<"b="<<b<<endl;
		endtiming();
		begintiming();
		cout<<"a+b="<<a+b<<endl;
		endtiming();
		begintiming();
		cout<<"a-b="<<a-b<<endl;
		endtiming();
		begintiming();
		cout<<"a*b="<<a*b<<endl;
		endtiming();
		begintiming();
		cout<<"a/b="<<a/b<<endl;
		endtiming();
		begintiming();
		cout<<"a\%b="<<a%b<<endl;
		endtiming();
		*/
	}
	catch (base_exception &e)
	{
		e.print();
		return 3;
	}
	return 0;
}
