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

