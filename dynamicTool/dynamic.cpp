#include<iostream>
#include <unistd.h>
#include <sstream>
#include <fstream>
#include <map>
#include <vector>
#include <utility>
#include <math.h>
#include <string>

#define END ";"
using namespace std;

ofstream report;
ifstream f;
ifstream g;
map<string,vector<int>> fact;
map<string,vector<double>> guess;
map<string,vector<double>> finalguess;
vector<pair<string,string>> ctrs;
vector<string> bounds;

string factf = "fact_nav";
string lporig = "factorig.lp";
string lpend = "factend.lp";
string configf = "config";
string observef = "observed_nav";

int totNum;
double maxerr;

void updateGuess(){
	for(auto it = guess.begin(); it!=guess.end(); it++){
		string name = it->first;	
		vector<double> value = it->second;
		for(int i = 0; i<value.size(); i++){
			finalguess[name][i] = value[i];
		}
	}
}

void readObserved(){
	ifstream constraints;
	constraints.open(observef);
	while(!constraints.eof()){
		string ctr1,ctr2;
		getline(constraints,ctr1);
		if(ctr1=="")getline(constraints,ctr1);
		getline(constraints,ctr2);
		ctrs.push_back(make_pair(ctr1,ctr2));
	}
	cout<<"observation read done"<<endl;
}

void genProblem(vector<int> &comb){
	ifstream orig;
	orig.open(lporig);
	ofstream prob;
	prob.open("factgen.lp");
	prob<<orig.rdbuf();
	
	for(int i = 0; i<comb.size(); i++){
		prob<<ctrs[comb[i]].first<<endl;
		prob<<ctrs[comb[i]].second<<endl;
	}
	ifstream end;
	end.open(lpend);
	prob<<end.rdbuf();
	prob.close();		
	string cmd="gurobi_cl ResultFile=max.sol ";
	cmd+="factgen.lp";
	system(cmd.c_str());
}

void readGuess(){
	ifstream gg;
	gg.open("max.sol");
	string name;
	int level;
	string tmp;
	while(!gg.eof()){
		gg>>tmp;
		level = tmp[tmp.size()-1]-'0'-1;
		tmp = tmp.substr(0,tmp.size()-1);
		if(fact.find(tmp)==fact.end())continue;
		guess[tmp].resize(fact[tmp].size());
		finalguess[tmp].resize(fact[tmp].size());
		gg>>guess[tmp][level];
	}
	//add in specific known value
/*	guess["GPS"].push_back(298);
	guess["SYS"].push_back(375);
	guess["comm"].push_back(109);*/
}

void readFact(ifstream & factf){
	string name;
	int level;
	while(!factf.eof()){
		factf>>name;
		if(name=="#")break;
		factf>>level;
		fact[name].resize(level);
	}
	cout<<"fact read done"<<endl;
}

double checkRate(){
	int num = 0;
	double diff = 0;
	maxerr = -1;
	f.open(factf);
	while(!f.eof()){
		string s1,s2,s3;
		int l1,l2,l3;
		double v;
		f>>s1;f>>l1;f>>s2;f>>l2;f>>s3;f>>l3;
		f>>v;
		if(s1=="")continue;
		double gvalue = guess[s1][l1-1]+guess[s2][l2-1]+guess[s3][l3-1];
		if(l1<=3)gvalue+=229;
//		if(l3>3)gvalue-=298;
		cout<<guess[s1][l1-1]<<" "<<guess[s2][l2-1]<<" "<<guess[s3][l3-1]<<" "<<gvalue<<"->"<<v;
		double dif = (gvalue-v)/v;
		cout<<":\t"<<dif<<endl;
		dif=dif>0?dif:-dif;
		diff += dif;
		maxerr = max(maxerr,dif);
		num++;
	}
	f.close();	
	totNum = num;
	double errC = diff/num;
	return errC;
}

double checkRateRob(){
	int num = 0;
	double diff = 0;
	maxerr = -1;
	f.open(factf);
	while(!f.eof()){
		string s,b;
		int ls,lb;
		double v;
		f>>s;f>>ls;f>>b;f>>lb;
		f>>v;
		if(s=="")continue;
		double gvalue = guess[s][ls-1]+guess[b][lb-1];
		cout<<guess[s][ls-1]<<" "<<guess[b][lb-1]<<" "<<gvalue<<"->"<<v<<endl;
		double dif = (gvalue-v)/v;
		dif=dif>0?dif:-dif;
		diff += dif;
		maxerr = max(maxerr,dif);
		num++;
	}
	f.close();	
	totNum = num;
	double errC = diff/num;
	cout<<"totNum:"<<totNum<<"Max:"<<maxerr<<"Mean:"<<errC<<endl;
	return errC;
}

void printGuess(){
	ofstream res;
	res.open("res.csv");
	for(auto it = finalguess.begin(); it!=finalguess.end(); it++){
		res<<it->first<<" ";
		for(int i = 0; i<it->second.size(); i++){
			res<<it->second[i]<<" ";
		}	
		res<<endl;
	}
	int num = 0;
	double diff = 0;
	maxerr = -1;
	f.open(factf);	
		while(!f.eof()){
		string s1,s2,s3,s4;
		int l1,l2,l3,l4;
		double v;
		f>>s1;f>>l1;f>>s2;f>>l2;f>>s3;f>>l3;f>>s4;f>>l4;
		f>>v;
		if(s1=="")continue;
		double gvalue = finalguess[s1][l1-1]+finalguess[s2][l2-1]+finalguess[s3][l3-1]+finalguess[s4][l4-1]+782;
		if(l3>3)gvalue-=298;
		res<<s1<<l1<<" "<<s2<<l2<<" "<<s3<<l3<<" "<<s4<<l4<<" ";
		//res<<finalguess[s1][l1-1]<<"\t"<<finalguess[s2][l2-1]<<"\t"<<finalguess[s3][l3-1]<<"\t"<<finalguess[s4][l4-1]<<"\t"<<v;
		res<<v;
		double dif = (gvalue-v)/v;
		dif=dif>0?dif:-dif;
		res<<"\t"<<dif<<"\t"<<gvalue<<endl;
		diff += dif;
		maxerr = max(maxerr,dif);
		num++;
	}
	f.close();	
	totNum = num;
	double errC = diff/num;
	res<<"mean:"<<errC<<"max:"<<maxerr;
	res.close();
}

int main(){
	report.open("report");
	readObserved();
	vector<int> repSet;
	repSet.push_back(0);
	double errtot=INT_MAX;
	int count = 1;
	map<int,bool> visited;
	
	ifstream factfile;
	factfile.open(configf);
	readFact(factfile);	
	factfile.close();
/*
//check rate only for youtube
	guess["s"].push_back(2915);
	guess["s"].push_back(2279);
	guess["s"].push_back(2198);
	guess["s"].push_back(1796);
	guess["s"].push_back(1796);
	guess["s"].push_back(1675);

	guess["b"].push_back(326);
	guess["b"].push_back(219);
	guess["b"].push_back(3);
	guess["b"].push_back(2);
	guess["b"].push_back(1);

	double mean = checkRateRob();	
	cout<<"mean:"<<mean<<endl;
	return 1;
//end
*/
//check rate only for youtube
	guess["s"].push_back(1913);
	guess["s"].push_back(1726);
	guess["s"].push_back(1410);
	guess["s"].push_back(1409);
	guess["s"].push_back(1408);
	guess["s"].push_back(1407);

	guess["i"].push_back(2);
	guess["i"].push_back(275);
	guess["i"].push_back(1);

	guess["f"].push_back(194);
	guess["f"].push_back(193);
	guess["f"].push_back(192);
	guess["f"].push_back(191);
	guess["f"].push_back(190);
	guess["f"].push_back(1);


	double mean = checkRate();	
	cout<<"mean:"<<mean<<endl;
	return 1;
//end
	
	while(errtot>=0.05 || maxerr>=0.1){
		double errcur=INT_MAX;
		int repcur = -1;
		for(int i = 1;i<ctrs.size(); i++){
			if(visited.find(i)==visited.end())
				repSet.push_back(i);
			else continue;
			genProblem(repSet);
			readGuess();
			double errtmp=checkRate();
			if(errtmp<errcur){
				repcur=i;
				updateGuess();
				errcur = errtmp;
			}
			repSet.pop_back();
		}
		if(repcur==-1)break;
		repSet.push_back(repcur);
		errtot=errcur;
		visited[repcur]=true;
		count++;
		cout<<"added"<<repcur<<"config:"<<ctrs[repcur].first<<endl;
		report<<"added "<<repcur<<"->"<<errtot<<"max:"<<maxerr<<" "<<ctrs[repcur].first<<endl;
	}
	printGuess();
	cout<<"With error = "<<errtot<<" in "<<totNum<<" combinations"<<endl;
	cout<<"Max error = "<<maxerr<<endl;
	cout<<"count="<<count<<endl;
	report.close();	
	return 1;

}
