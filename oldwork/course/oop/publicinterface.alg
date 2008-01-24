struct Record {
	string name;
	string tel;
	bool operator==(Record &b);
};

class RecordList: public list<Record> {
};

class AddressList {
	public:
		typedef RecordList::iterator iterator;
		iterator findRecord(string pattern, int type, iterator from);
		int addRecord(Record rec);
		iterator removeRecord(iterator it);
		void saveRecords(ostream& os);
		void loadRecords(istream& is);
		const int size() const;
		const bool empty() const;
		void clear();
		iterator begin();
		iterator end();
};

class AddressBook: public AddressList{
	public:
		AddressBook():isModified(false) {}
		void run();
};
