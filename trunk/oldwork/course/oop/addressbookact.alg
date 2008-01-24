void AddressBook::act(AddressBook::Commands cmd)
{
	cout<<left;	// align left
	if (cmd == display)
		if (begin() == end())
			cout<<norecord_display;
		else
		{
			// Code here: Display Record
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
			if (!getline(cin, pattern))
				return;
			if (findRecord(pattern, type, begin()) == end())
				cout<<notfoundtext;
			else
			{
				// Code here: Find all records that match and print
			}
		}
	else if (cmd == addrec)
	{
		cout<<addrectext;
		Record rec;
		while (1)
		{
			cout<<nametext<<": ";
			if (!getline(cin, rec.name))
				break;
			if (rec.name == "0")
				break;
			cout<<teltext<<": ";
			if (!getline(cin, rec.tel))
				break;
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
			// Code here: Input type and pattern. Similar to cmd == query
			if (findRecord(pattern, type, begin()) == end())
				cout<<notfoundtext;
			else
			{
				cout<<setw(20)<<nametext<<setw(20)<<teltext<<endl;
				deleted = 0;
				it = begin();
				for (it = findRecord(pattern, type, it); it != end(); )
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
			if (!getline(cin, filename))
				return;
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
		if (!getline(cin, filename))
			return;
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
		// Code here: the same as cmd == addrec
		isModified = true;
	}
}

