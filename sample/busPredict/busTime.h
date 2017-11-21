#include<vector>
#include<utility>

using namespace std;

class Time{
	public:
	int h;
	int m;
	int s;
	Time(){
	}
};

int diff(Time lhs, Time rhs){
	int l = lhs.s+lhs.m*60+lhs.h*3600;
	int r = rhs.s+rhs.m*60+rhs.h*3600;
	return l-r;
}

struct smaller{
	bool operator()(const Time& l, const Time& r){
	 	return diff(l,r)<0;      
	}
};

class Bus{
public:
	void setId(int id){
		this->id = id;
	}
	void setPlate(string s){
		plateID = s;
	}
	void addTraj(double l, double lag){
		traj.push_back(make_pair(l,lag));
	}
	void addTime(Time t){
		timeStamp.push_back(t);
	}
	void sortT(){
		sort(timeStamp.begin(),timeStamp.end(),smaller());
		cout<<"sort done"<<endl;
	}
	void reportStat(){
		int count = 0;
		int tot = 0;
		int mindif = INT_MAX;
		int maxdif = INT_MIN;
		for(int i = 1;i<timeStamp.size(); i++){
			int dif = abs(diff(timeStamp[i],timeStamp[i-1]));
			if(dif>maxdif)maxdif = dif;
			if(dif<mindif)mindif = dif;
			tot+=dif;
			count++;
		}
		cout<<"overall segment"<<count<<endl;
		cout<<"mean"<<tot/count<<endl;
		cout<<"max"<<maxdif<<endl;
		cout<<"min"<<mindif<<endl;
	}
private:
	int id;
	string plateID;
	vector<pair<double,double> > traj;
	vector<Time> timeStamp;
	double curSpeed;

};
