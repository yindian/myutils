#ifndef ADDRBOOK_H_
#define ADDRBOOK_H_

#ifndef DO_NOTHING
#define DO_NOTHING
#endif

#include<iostream>
#include<fstream>
#include<iomanip>
#include<string>
#include<list>
using namespace std;

struct Record {
	string name;
	string tel;
	bool operator==(Record &b)
	{
		return name == b.name && tel == b.tel;
	}
};

class RecordList: public list<Record> {
};

//class Base_Exception {
//	public:
//		virtual void print() = 0;
//};
//
//class Exc_InvalidIterator: public Base_Exception {
//	public:
//		virtual void print() { cerr<<"Invalid Iterator\n";}
//};
//
class AddressList {
	private:
		RecordList recList;
	public:
		typedef RecordList::iterator iterator;
		iterator findRecord(string pattern, int type, iterator from)	// type=1:byname 2:bytel
		{
			for (iterator it = from; it != end(); ++it)
				if ((type == 1 && it->name.find(pattern, 0) < it->name.size()) ||
						(type == 2 && it->tel.find(pattern, 0) < it->tel.size()))
					return it;
			return end();
		}
		int addRecord(Record rec)	// return 0 if duplicate
		{
			for (iterator it = begin(); it != end(); ++it)
				if (*it == rec)
					return 0;
			recList.push_back(rec);
			return 1;
		}
		iterator removeRecord(iterator it) {return recList.erase(it);}	// may cause error if it == end()
		void saveRecords(ostream& os)
		{
			for (iterator it = begin(); it != end(); ++it)
				os<<it->name<<endl<<it->tel<<endl;
		}
		void loadRecords(istream& is)
		{
			//clear();
			Record rec;
			while (getline(is, rec.name) && getline(is, rec.tel))
				addRecord(rec);
		}
		//~AddressList();
		const int size() const {return recList.size();}
		const bool empty() const {return recList.empty();}
		void clear() {recList.clear();}
		iterator begin() {return recList.begin();}
		iterator end() {return recList.end();}
};

const int numberofcommands=8;
#define DEFAULT_FILENAME "sname"
char *querytext = "\
------------\n\
/*@1. 显示记录@*/\n\
/*@2. 查询记录@*/\n\
/*@3. 增加记录@*/\n\
/*@4. 删除记录@*/\n\
/*@5. 保存记录@*/\n\
/*@6. 读取记录@*/\n\
/*@7. 新建通讯录@*/\n\
/*@8. 结束运行@*/\n\
/*@左边数字对应功能选择，请选1-8: @*/";
char *welcometext = "\
**********************\n\
/*@* 欢迎使用简易通讯录@*/ *\n\
**********************\n";
char *farewelltext = "/*@退出操作，再见！@*/\n";
char *reentertext = "/*@输入错误，重选1-8：@*/";
char *nametext = "/*@姓名@*/";
char *teltext = "/*@电话@*/";
char *norecord_display = "/*@没有记录！@*/\n";
char *norecord_query = "/*@记录是空表，退出查询操作@*/\n";
char *norecord_save = "/*@没有记录可存！@*/\n";
char *totalrec_pre = "/*@一共有@*/"; char *totalrec_post = "/*@条记录@*/\n";
char *totalrecfound_pre = "/*@一共找到了@*/";
char *totalrecdeleted_pre = "/*@一共删除了@*/";
char *totalrecremain_pre = "/*@现在还有@*/";
char *choosenameteltext = "\
/*@可以通过姓名或电话号码查找或删除记录@*/\n\
/*@1. 通过姓名@*/\n\
/*@2. 通过电话@*/\n\
/*@请输入你的选择：@*/";
char *notfoundtext = "/*@对不起，没有找到你的记录。@*/\n";
char *pleaseinput = "/*@请输入@*/";
char *pleasereinput = "/*@请重新输入 @*/";
char *addrectext = "/*@输入数据，输入姓名为0时结束。@*/\n";
char *eraseprompttext = "/*@确定要删除这条记录吗？[y/N]@*/";
char *inputfilenameprompttext = "/*@请输入文件名（直接回车选择文件@*/"DEFAULT_FILENAME"/*@）：@*/";
char *writtentofile_post = "/*@条记录已经存入文件，请继续操作。@*/\n";
char *openinputfileerror = "/*@打不开文件！请重新选择@*/\n";
char *openoutputfileerror = "/*@不能打开输出文件@*/\n";
char *saveonquitprompttext = "/*@通讯录已改动，是否保存？(Y/n)@*/";

class AddressBook: public AddressList{
	public:
		AddressBook():isModified(false) {}
		~AddressBook() {}
		void run();

	private:
		bool isModified;

		enum Commands {unknown, display, query, addrec, eraserec, save, load, newbook, abort};
		void clearline()
		{
			char ch;
			while((ch = cin.get()) != '\n' && ch != EOF)
				DO_NOTHING;
			if (ch == EOF)
			{
				cerr<<"Input terminated uncorrectly.\n";
				exit(1);
			}
		}
		Commands readCommand()
		{
			int item;
			cout<<querytext;
			while( !(cin>>item) || item <= 0 || item > numberofcommands)
			{
				cin.clear();
				clearline();
				cout<<reentertext;
			}
			clearline();
			return (Commands) item;
		}
		void act(Commands whatcommand);
};

void AddressBook::run()
{
	Commands cmd;
	cout<<welcometext;
	while ((cmd = readCommand()) != abort)
		act(cmd);
	if (isModified)
	{
		char ch;
		cout<<saveonquitprompttext;
		if (!(cin>>ch))
			return;
		clearline();
		if (ch != 'n' && ch != 'N')
			act(save);
	}
	cout<<farewelltext;
}

void AddressBook::act(AddressBook::Commands cmd)
{
	cout<<left;	// align left
	if (cmd == display)
		if (begin() == end())
			cout<<norecord_display;
		else
		{
			int total = 0;
			cout<<setw(20)<<nametext<<setw(20)<<teltext<<endl;
			for (iterator it = begin(); it != end(); ++it)
			{
				cout<<setw(20)<<it->name<<setw(20)<<it->tel<<endl;
				++total;
			}
			cout<<totalrec_pre<<total<<totalrec_post;
		}
	else if (cmd == query)
		if (begin() == end())
			cout<<norecord_query;
		else
		{
			int type, found; 
			string pattern;
			iterator it;
			cout<<choosenameteltext;
			while( !(cin>>type) || (type != 1 && type != 2))
			{
				cin.clear();
				clearline();
				cout<<choosenameteltext;
			}
			cout<<pleaseinput<<(type == 1 ? nametext : teltext)<<": ";
			clearline();
			while (!getline(cin, pattern) || pattern == "")
				cout<<pleasereinput;
			if (findRecord(pattern, type, begin()) == end())
				cout<<notfoundtext;
			else
			{
				cout<<setw(20)<<nametext<<setw(20)<<teltext<<endl;
				found = 0;
				it = findRecord(pattern, type, begin());
				for (; it != end(); it = findRecord(pattern, type, it))
				{
					cout<<setw(20)<<it->name<<setw(20)<<it->tel<<endl;
					++found;
					++it;
				}
				cout<<totalrecfound_pre<<found<<totalrec_post;
			}
		}
	else if (cmd == addrec)
	{
		cout<<addrectext;
		Record rec;
		while (1)
		{
			cout<<nametext<<": ";
			while (!getline(cin, rec.name) || rec.name == "")
				cout<<pleasereinput;
			if (rec.name == "0")
				break;
			cout<<teltext<<": ";
			while (!getline(cin, rec.tel) || rec.tel == "")
				cout<<pleasereinput;
			addRecord(rec);
		}
		isModified = true;
	}
	else if (cmd == eraserec)
		if (begin() == end())
			cout<<norecord_query;
		else
		{
			int type, deleted; 
			string pattern;
			iterator it;
			char ch;
			cout<<choosenameteltext;
			while( !(cin>>type) || (type != 1 && type != 2))
			{
				cin.clear();
				clearline();
				cout<<choosenameteltext;
			}
			cout<<pleaseinput<<(type == 1 ? nametext : teltext)<<": ";
			clearline();
			while (!getline(cin, pattern) || pattern == "")
				cout<<pleasereinput;
			if (findRecord(pattern, type, begin()) == end())
				cout<<notfoundtext;
			else
			{
				cout<<setw(20)<<nametext<<setw(20)<<teltext<<endl;
				deleted = 0;
				it = findRecord(pattern, type, begin());
				for (; it != end(); it = findRecord(pattern, type, it))
				{
					cout<<setw(20)<<it->name<<setw(20)<<it->tel<<endl;
					cout<<eraseprompttext;
					if (!(cin>>ch))
						return;
					clearline();
					if (ch == 'y' || ch == 'Y')
					{
						it = removeRecord(it);
						++deleted;
					}
					else
						++it;
				}
				cout<<totalrecdeleted_pre<<deleted<<totalrec_post;
				cout<<totalrecremain_pre<<size()<<totalrec_post;
				isModified = true;
			}
		}
	else if (cmd == save)
		if (begin() == end())
			cout<<norecord_save;
		else
		{
			string filename;
			cout<<inputfilenameprompttext;
			while (!getline(cin, filename))
				cout<<pleasereinput;
			if (filename == "") 
				filename = DEFAULT_FILENAME;
			ofstream ofs(filename.c_str());
			if (!ofs)
			{
				cerr<<openoutputfileerror;		// better throw exception
				return;
			}
			saveRecords(ofs);
			ofs.close();
			cout<<size()<<writtentofile_post;
			isModified = false;
		}
	else if (cmd == load)
	{
		string filename;
		cout<<inputfilenameprompttext;
		while (!getline(cin, filename))
			cout<<pleasereinput;
		if (filename == "") 
			filename = DEFAULT_FILENAME;
		ifstream ifs(filename.c_str());
		if (!ifs)
		{
			cerr<<openinputfileerror;
			return;
		}
		loadRecords(ifs);
		ifs.close();
		cout<<totalrec_pre<<size()<<totalrec_post;
		isModified = true;
	}
	else if (cmd == newbook)
	{
		clear();
		cout<<addrectext;
		Record rec;
		while (1)
		{
			cout<<nametext<<": ";
			while (!getline(cin, rec.name) || rec.name == "")
				cout<<pleasereinput;
			if (rec.name == "0")
				break;
			cout<<teltext<<": ";
			while (!getline(cin, rec.tel) || rec.tel == "")
				cout<<pleasereinput;
			addRecord(rec);
		}
		isModified = true;
	}
}

#endif
