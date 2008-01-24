iterator findRecord(string pattern, int type, iterator from)	// type=1:byname 2:bytel
{
	for (iterator it = from; it != end(); ++it)
		if ((type == 1 && it->name.find(pattern, 0) < it->name.size()) ||
				(type == 2 && it->tel.find(pattern, 0) < it->tel.size()))
			return it;
	return end();
}

