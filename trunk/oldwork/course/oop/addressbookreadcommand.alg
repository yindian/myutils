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

