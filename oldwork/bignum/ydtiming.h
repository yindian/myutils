/*
 * 	Prog: ydtiming.h
 * 	Provide begintiming(), endtiming();
 * 	Hist:	050724
 */

#include <time.h>

namespace yd_algorithm {

	static int ydtimer;
	void begintiming() {ydtimer = clock();}
	void endtiming() {std::cerr<<"Time elapsed: "<< double(clock()-ydtimer) / CLOCKS_PER_SEC<<'\n';}

} // namespace

