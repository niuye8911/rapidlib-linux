#include<iostream>
#include <unistd.h>
#include <sstream>
#include <fstream>

using namespace std;

ofstream observe;

ifstream file; 

int main(){
	observe.open("observed_rob");
	file.open("robotraw");
	while(!file.eof()){
		int s;
		int b;

		double v;

		file>>s;
		file>>b;
		file>>v;

		observe<<"s"<<s<<" "<<"+ "<<"b"<<b<<" + SYS + comm >= "<<v<<endl;
		observe<<"s"<<s<<" "<<"+ "<<"b"<<b<<" + SYS + comm - "<<v<<" err <= "<<v<<endl;
	}

	file.close();
	observe.close();
}
