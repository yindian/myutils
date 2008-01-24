SRC=	addrbook.cpp	\
    	addrbook.h
OFILES=addrbook.o
EXEC=addrbook.exe
CXX=g++
FLAGS=-Wall -g

all:$(EXEC)

$(EXEC):$(OFILES) Makefile
	$(CXX) $(FLAGS) -o $(EXEC) $(OFILES)
%.o:%.cpp %.h Makefile
	$(CXX) $(FLAGS) -c $<
