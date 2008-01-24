/*
 * 	Prog: ydexception.h
 * 	Defines exception classes
 * 	Hist:	050704
 */

namespace yd_algorithm {

class base_exception {
	public:
		virtual void print() = 0;
		virtual void print(int line) = 0;
};

class division_by_zero:public base_exception {
	public:
		void print() {std::cerr<<"Error: Division by Zero.\n";}
		void print(int line) {std::cerr<<"Error: Division by Zero on line "<<line<<".\n";}
};

class underflow:public base_exception {
	public:
		void print() {std::cerr<<"Error: Underflow.\n";}
		void print(int line) {std::cerr<<"Error: Underflow on line "<<line<<".\n";}
};

} // namespace
