#include "rsdgMission.h"
#include <unistd.h>
#include <signal.h>
#include <iostream>
#include <string>
#include "string.h"
#include "stdlib.h"
#include <curl/curl.h>
#include <ctime>
#include <vector>
#include <sstream>

vector<string> localSolve();

string RSDG_TAG = "[RAPID DEBUG]:";

void rsdgUnit::set(int u){
        unit = u;
}

int rsdgUnit::get(){
        return unit;
}

//////rsdgService////

rsdgService::rsdgService(std::string serviceName){
        name = serviceName;
        READY = true;
        bufferReady = 2;
        unit = new rsdgUnit();
        parents.resize(10);
}

string rsdgService::getName(){return name;}

int rsdgService::getUnit(){return unit->get();}

vector<rsdgService*> rsdgService::getParents(){
        return parents;
}

void* rsdgService::get(pthread_t getter){
        while(bufferReady!=1){
                sleep(1000);
        }
        cout<<"buffer ready to be taken"<<endl;
        setBufferUsed();
        return buffer;
}

void rsdgService::set(pthread_t setter, void* obj){
        buffer = obj;
        setBufferReady();
        cout<<"buffer changed"<<endl;
}

void rsdgService::run(string name, void *f(void*)){
        curNode = name;
        pthread_create(&sThread, NULL, f,NULL);

        return;
}

void rsdgService::updateNode(void* (*f)(void*),string name){
	if(name==curNode){
		cout<<RSDG_TAG+"same config:"<<curNode<<"->"<<name<<endl;
		return;
	}
	cout<<RSDG_TAG+"change config:"<<curNode<<"->"<<name<<endl;
        if(name!=curNode && f!=NULL){
		if(single){
			f(NULL);
			curNode = name;
			return;
		}
		if(sThread!=0){
                	pthread_cancel(sThread);
                	setStatus(false);
                	pthread_join(sThread,NULL);
		}
                pthread_create(&sThread, NULL,f, NULL);
		
		curNode = name;
		//cout<<"created thread"<<endl;
        }
}
pthread_t rsdgService::getThread(){return sThread;}
/////rsdgMission////
rsdgMission::rsdgMission(){
	RS_fact.open("observed.csv");
	numThreads = 0;
	budget = 0;
	curBudget = 0;
	string test = "test";
	logfile.open ("./mission.log");
        logfile<<"selection, ExpectedEnergy, MV \n";

}

rsdgService* rsdgMission::getService(string name){
	if(serviceMap.find(name)!=serviceMap.end()) return serviceMap[name];
	else {
		return NULL;
	}
}

void rsdgMission::regService(string sName, string bName, void*(*func)(void*), bool single,pair<rsdgPara*, int> para){
	if(func==NULL){
		basicToService[bName] = sName;
		threadPref[sName] = 0;
	}
	runnableList.push_back(func);
	runnableID[bName] = runnableList.size()-1;
	
	if(getService(sName) == NULL){
		rsdgService* s = new rsdgService(sName);
		s->single = single;
		serviceList.push_back(s);	
		threadPref[sName] = 0;
		threadID[sName] = serviceList.size()-1;
		numThreads++;
		basicToService[bName] = sName;
		serviceMap[sName] = s;
	}else{
		basicToService[bName] = sName;
	}
	if(para.first != NULL){
		paraList[bName] = para;
	}
	getService(sName)->addNode(bName);
}

void rsdgMission::regContService(string sName, string bName, void*(*func)(void*)){
	regService(sName, bName, func, false);	
}

void rsdgService::addNode(string nodeName){
	node_lists.push_back(nodeName);
	cout<<"Pushing back node "<<nodeName<<endl;
}

void rsdgMission::regService(string sName, string bName, void*(*func)(void*),bool single){
        if(func==NULL){                                            
                basicToService[bName] = sName;                     
                threadPref[sName] = 0;
        }                                                          
        runnableList.push_back(func);
        runnableID[bName] = runnableList.size()-1;
                
        if(getService(sName) == NULL){                             
                rsdgService* s = new rsdgService(sName);
		s->single = single;           
                serviceList.push_back(s);                          
                threadPref[sName] = 0;
                threadID[sName] = serviceList.size()-1;            
                numThreads++;                                      
                basicToService[bName] = sName;                     
                serviceMap[sName] = s;                             
        }else{
                basicToService[bName] = sName;                     
        }                                                          
	getService(sName)->addNode(bName);
        //cout<<"registered imp:"<<bName<<"in service:"<<sName<<endl;         
}

void rsdgMission::setupSolverFreq(int freq){ this->freq = freq;}

void rsdgMission::setUnit(int u){unit.set(u);}

void rsdgMission::finish_one_unit(){
	(unit.set(unit.get()-1));
	if(unit.get()==0){
		// mission is finished
		fact.close();
		logfile.close();
	}
}

//helper func for libcurl
string data;
size_t writeCallback(char* buf, size_t size, size_t nmemb, void* up)
{
    for (int c = 0; c<(int)(size*nmemb); c++)
    {
        data.push_back(buf[c]);
    }
    return size*nmemb; //tell curl how many bytes we handled
}
//parsing server response to vector
void rsdgMission::getRes(vector<string>& holder, string response){
	//cout<<"response="<<response<<endl;
        int l = 1, r = 1;
	if(response[1]=='o'){
		double obj = atof(&response[5]);
		objValue = obj;
		cout<<"objValue"<<obj<<endl;
	}
        while(r<=(int)response.size()){
                if(response[r]!='\\'){r++;continue;}
                holder.push_back(response.substr(l,r-l));
                l = r+2;
                r = l;
        }
        return;
}
void rsdgMission::consultServer(){
	//#TO BE DONE
	if(local){
		//cfgse local solver
		vector<string> res = localSolve();
		updateSelection(res);
		res.clear();
		return;
	}
	if(offline_search){
		vector<string> res = searchProfile();
		updateSelection(res);
		res.clear();
		return; 
	}
	CURL *curl;
	CURLcode responseCode;
	vector<string> res;
	//init http options
	struct curl_httppost *formpost=NULL;
        struct curl_httppost *lastptr = NULL;
        struct curl_slist *headerlist=NULL;
        static const char buffer[] = "Expect:";
	string name = (graph->minmax)?(outfileName+"MAX.lp"):(outfileName+"MIN.lp");
        curl_formadd(&formpost,&lastptr,CURLFORM_COPYNAME, "uploaded_file[]",CURLFORM_FILE, name.c_str(),CURLFORM_END);
        curl = curl_easy_init();
        headerlist = curl_slist_append(headerlist,buffer);

	//consult server
	if(curl){
                curl_easy_setopt(curl, CURLOPT_URL, "http://algaesim.cs.rutgers.edu/solver/index.php");
                curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
                curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &writeCallback);
                responseCode = curl_easy_perform(curl);
       		if(responseCode!=CURLE_OK)cout<<RSDG_TAG+"Server Failed"<<endl;
		getRes(res,data);
		data = "";//reset the data
		cout<<endl;
		curl_easy_cleanup(curl);
			updateSelection(res);
			res.clear();
	}
}

void rsdgMission::updateSelection(vector<string>& result){
	if(result.size()==0){
		//no solution
		cout<<RSDG_TAG+"no solution found"<<endl;
		solvable = false;
		if(!TRAINING_MODE){
			cout<<RSDG_TAG+"Misison Failed"<<endl;
			exit(0);	
		}
		return;
	}
	int i;
	//clear the current selected
	for (map<string,string>::iterator it = selected.begin(); it!=selected.end(); it++){
		it->second = "";
	}
	for(map<string,vector<string> >::iterator it2 = depChain.begin(); it2!=depChain.end(); it2++){
		it2->second.clear();
	}
	//iterating throught he result and fetch the returned result
	for(i = 0; i<(int)result.size(); i++){
		string s = basicToService[result[i]];	
		rsdgService* svc = serviceMap[s];
		if(svc==NULL){//could be edge or could be something wrong
			//get the edge
			size_t deli = result[i].find_last_of("$");
			if(deli != string::npos){
				//found
				string sink = result[i].substr(0,deli);
				string source = result[i].substr(deli+1);
				depChain[sink].push_back(source);
			}	
			//get the objective cost
			size_t equalSign = result[i].find_last_of("=");
			if(equalSign != string::npos){
				int expectCost = stoi(result[i].substr(equalSign+1));
				predictedCost = expectCost;
//				cout<<RSDG_TAG+"EXPECTED COST = "<<expectCost<<endl;
			}
			continue;
		}
		svc->setStatus(false);
		selected[s] = result[i]; 
	}	
}

void rsdgMission::applyResult(){
	for (map<string, string>::iterator it = selected.begin(); it!=selected.end(); it++){
		string service = it->first;
		string basic = it->second;
		rsdgService* s = getService(service);
		if(s==NULL)continue;
		updateThread(s,basic);		
	}	
	//sleep for a few moment to let all config takes effect
	usleep(10000);
	cout<<RSDG_TAG+"*Reconfiguration Finished*"<<endl<<endl;
}

void rsdgMission::updateThread(rsdgService* s, string basic){
	if(basic == ""){//turn this service off
		pthread_t curThread = s->getThread();
		if(pthread_kill(curThread,0)==0){
			pthread_cancel(curThread);
			s->setStatus(false);
			pthread_join(curThread,NULL);			
		}
		return;
	}
	void*(*f)(void*) = runnableList[runnableID[basic]];
	if(paraList.find(basic)!=paraList.end()){
		rsdgPara* p = paraList[basic].first;
		if(p!=NULL){
			int pValue = paraList[basic].second;
			p->intPara = pValue;
		}
	}
	s->updateNode(f,basic);
}

double rsdgMission::getObj(){
	return objValue;
}

void rsdgMission::printToLog(){
	//print selection to log file
	for (map<string, string>::iterator it = selected.begin(); it!=selected.end(); it++){
		string basic = it->second;
		string service = basicToService[basic];
		vector<string>& nodelist = getService(service)->node_lists;
		int lvl =0;
		for(;lvl<nodelist.size(); lvl++){
			if(nodelist[lvl]==basic){
				break;	
			}
		} 
	        logfile<<service<<","<<lvl+1<<",";
		if(TRAINING_MODE)fact<<service<<","<<lvl+1<<",";
		if(update)RS_fact<<service<<","<<lvl+1<<",";
        }
	logfile<<predictedCost<<",";
	logfile<<realCost<<endl;
	logfile.flush();
	if(TRAINING_MODE){
		fact<<realCost<<endl;
		fact.flush();
	}
	if(update){
		RS_fact<<realCost<<endl;
		RS_fact.flush();
	}
}

void rsdgMission::genFact(){
	for(map<string, string>::iterator it = selected.begin(); it!=selected.end(); it++){
		string basic = it->second;
		fact<<basic<<",";
	}
	fact<<realCost<<endl;
	fact.flush();
}

void rsdgMission::genAllConfigs(int curSvcId, vector<string> tmp_result){
	if(curSvcId==serviceList.size()){
		//get a copy of the result
		vector<string> *result = new vector<string>();
		*result = tmp_result;
		for(int i = 0; i<tmp_result.size(); i++){
			cout<<tmp_result[i]<<" ";
		}
		cout<<endl;
		all_configs.push_back(*result);
		return;
	}
	// dfs through all the nodes
	for(int i = 0; i<(serviceList[curSvcId]->node_lists).size(); i++ ){
		string curNode = serviceList[curSvcId]->node_lists[i];
		tmp_result.push_back(curNode);
		genAllConfigs(curSvcId+1, tmp_result);
		tmp_result.pop_back();
        }
}

void rsdgMission::filterConfigs(){
	for(int i = 0; i<all_configs.size(); i++){
		                        for(auto cfg:all_configs[i]){
                                cout<<cfg<<" ";
                        }  
		if(!validate(all_configs[i])){
			all_configs.erase(all_configs.begin()+i);
			i--;
			cout<<"erased"<<endl;
			solvable = true;//reset the solvable
			continue;
		}
		cout<<"valid"<<endl;
	}
}

void rsdgMission::reconfig_training(){
	// a procedure that gives all combinations of service selections for training
	vector<string> fake_results;
	if(all_configs.size()==0){
		// first time caling, need to generate the entire search space
		vector<string> tmp;
		tmp.clear();
		genAllConfigs(0,tmp);
		cout<<RSDG_TAG+"Training Configs generated with total size = "<<all_configs.size()<<endl;
		filterConfigs();
		// print all configs to a file
		ofstream valid_config;
		valid_config.open("validConfig.csv");
		for(auto config: all_configs){
			for (auto node:config){
				valid_config<<node<<" ";
			}
			valid_config<<endl;
		}
		valid_config.close();
		cout<<RSDG_TAG+"Training Configs generated with reduced size = "<<all_configs.size()<<endl;
	}
	curTrainingId++;
	if(curTrainingId == all_configs.size()){
		cout<<RSDG_TAG<<"Training done"<<endl;
		fact.close();
	}else{
		fake_results = all_configs[curTrainingId];
		updateSelection(fake_results);
		cout<<RSDG_TAG+"TRAINING:";
		for (string sel:fake_results){  
			cout<<sel<<" "; 
		}
		cout<<endl;
	}
}

void rsdgMission::updateRSDG(){
	//execute the python scrip
	string cmd = "python "+pythonScript + " -m consrsdg -o observed.csv -f fact.csv";
	system(cmd.c_str());
	// now that we have a file "rsdg" which contains a new rsdg
	// it's time to update the internal rsdg
	ifstream rsdgfile;
	rsdgfile.open("rsdg");

	string svc;
        vector<vector<string>> configs;
        while(getline(rsdgfile, svc)){
                istringstream nodes(svc);
		string svcname="";
		nodes >> svcname;
		cout<<RSDG_TAG + "Updating RSDG weight for service: " + svcname<<endl;
		int curlevel = 0;
		double cost;
                while(nodes>>cost){
                        rsdgService* svc = getService(svcname);
                        if(svc!=NULL){
                                string nodename = svc->node_lists[curlevel++];
				updateWeight(nodename, cost);
				cout<<RSDG_TAG + "Updating node weight " + nodename + " to "<<cost<<endl;
                        }
                }
        }
	cout<<RSDG_TAG+"Updating RSDG COMPLETE"<<endl;	
}

void rsdgMission::reconfig_updating(){
	curUpdatingId ++;
	if(curUpdatingId == RS.size()){
		cout<<RSDG_TAG + "Updating Model Done"<<endl;
		RS_fact.close();
		//now we have the observation file, update the model
		updateRSDG();
		update = false;
		
	}else{
		
		updateSelection(RS[curUpdatingId]);
		cout<<RSDG_TAG + "UPDATING: ";
		for (string i:RS[curUpdatingId]){
			cout<<i<<" ";
		}
		cout<<endl;
	}
}

void rsdgMission::reconfig(){
	cout<<RSDG_TAG+"*Reconfiguration Start*"<<endl;
	//first check if the model is corrected
	checkPoint();
	updateModel(unitBetweenCheckPoints);
	updateBudget();
        if(startTime!=-1){
		cout<<RSDG_TAG+"logging info"<<endl;
		if(LOGGER)printToLog();
	}
	// get the result
	if(TRAINING_MODE){
		reconfig_training();
	}else if(!TRAINING_MODE && update){
	// updating RSDG
		if(RS.size()==0)readRS("RS");	// read in representative set
		reconfig_updating();
	}else if(offline_search){
		consultServer();
	}else{
	// phase1, max MV
		graph->minmax = MAX;
		printProb(outfileName);
		cout<<RSDG_TAG<<"problem created"<<endl;
		consultServer();
		cout<<RSDG_TAG<<"result returned"<<endl;
	// phase2 and set the new MV
		graph->minmax = MIN;
		graph->targetMV = objValue;
		maxMV=objValue==0?-1:objValue;
		printProb(outfileName);
		consultServer();
		minEnergy=objValue;
	}
	applyResult();
	//check point again to ignore the overhead by RSDG
	checkPoint();
	total_reconfig_time += timeSinceLastCheckPoint;
	num_of_reconfig ++;
	cout<<RSDG_TAG+"reconfig overhead = "<<timeSinceLastCheckPoint<<endl;
	cout<<RSDG_TAG+"AVG reconfig overhead = "<<(double)total_reconfig_time / (double)num_of_reconfig<<"ms"<<endl;
	if(startTime==-1)startTime = getCurrentTimeInMilli();
}

double rsdgMission::genProductProfile(){
	ofstream myfile;
	myfile.open ("./productProfile.csv");
	myfile<<"missionValue, minEnergy, Selections \n";
	vector<double> profile;
	double initBudget = budget;
	while(solvable){
		reconfig();
		if(!solvable)break;
		profile.push_back(maxMV*(budget-minEnergy));
		setBudget(minEnergy-0.1);
		myfile<<maxMV<<", "<<minEnergy<<", ";
		for (map<string, string>::iterator it = selected.begin(); it!=selected.end(); it++){
			string basic = it->second;
			myfile<<basic<<", ";
		}
		myfile<<endl;
	}	
	myfile.close();
	double total = 0;
	for(int i = 0; i<profile.size(); i++){
		total+=profile[i];
	}
	return total / (initBudget-minEnergy); 
}

void rsdgMission::start(){
	/*dummy code to start */
	reconfig();
	if(freq==0)return;
	pthread_create(&monitor,NULL,startSolver,this);
}

void rsdgMission::stopSolver(){
	pthread_cancel(monitor);
	pthread_join(monitor,NULL);
	return;
}

void* startSolver(void* arg){
	while(1){
		pthread_testcancel();
		rsdgMission* rsdg = (rsdgMission*)arg;
		sleep(rsdg->freq);
		rsdg->reconfig();
	}
	return NULL;
}
void rsdgMission::setBudget(int b){
	if(budget==0)budget = b;
	curBudget = b;
	if(graph==NULL){cout<<RSDG_TAG+"RSDG has not been generated yet"<<endl;return;}
	graph->setBudget((double)curBudget);
	return;
}

void rsdgMission::updateMV(string serviceName, int value, bool exp){
	if(graph==NULL){
		cout<<"RSDG has not been generated yet"<<endl;
		return;
	}
	graph->updateMissionValue(serviceName,value,exp);
}

void rsdgMission::updateWeight(string b_name, double cost){
	if(graph==NULL){
		cout<<"RSDG has not been generated yet"<<endl;
		return;
	}
	graph->updateCost(b_name,cost);
}

void rsdgMission::updateWeight(string sink, string source, double cost){
	if(graph==NULL){
		cout<<"RSDG has not been generated yet"<<endl;
		return;
	}
	graph->updateEdgeCost(sink,source,cost);
}

int rsdgMission::getBudget(){return budget;}

int rsdgMission::getNumThreads(){return numThreads;}

void rsdgMission::generateProb(string input){
	graph = rsdgGen(input); 
}

void rsdgMission::setOutput(string name){
	outfileName = name;
}

void rsdgMission::printProb(string outfile){
	string name = outfile;
	if(graph->minmax)
		name+="MAX.lp";
	else
		name+="MIN.lp";
	graph->writeXMLLp(name,lpsolve);
}

void rsdgMission::setSolver(bool LP, bool LC){
	lpsolve=LP;
	local = LC;
}

void rsdgMission::cancel(){
	for(int i = 0; i<(int)serviceList.size(); i++){
		rsdgService* s = serviceList[i];
		pthread_t sT = s->getThread();
		if(sT==0)continue;
		if(pthread_kill(sT,0)==0){
			pthread_cancel(sT);
			pthread_join(sT,NULL);
		}
	}
	return;
}

// The default impl uses the work unit left and time left to calculate the budget per unit
// User could re-define this method to their own needs
void rsdgMission::updateBudget(){
	int unit_left = unit.get();
	long long current_time = getCurrentTimeInMilli();
	long long usedMilli = startTime==-1?0:current_time-startTime; 
	curBudget = budget - usedMilli;
	cout<<RSDG_TAG+"currentBudget = "<<curBudget<<endl;
	double new_budget_per_unit = (double)curBudget / (double)unit_left;
	cout<<RSDG_TAG+"Used budget in Milli = "<<usedMilli<<"; Unit left = "<<unit_left<<" ; New Budget per unit = "<<new_budget_per_unit<<endl;
	setBudget(new_budget_per_unit);
	return;
}

long long getCurrentTimeInMilli(){
    struct timeval tp; 
    gettimeofday(&tp, NULL);
    long long mslong = (long long) tp.tv_sec * 1000L + tp.tv_usec / 1000;
    return mslong;
}

// keep the current timestamp to calculate new budget or monitor usage
void rsdgMission::checkPoint(){
	long long curTime = getCurrentTimeInMilli();
	if(lastCheckPoint==0){
		lastCheckPoint = curTime;
		cout<<RSDG_TAG+"Skipping checkpoint for first invocation"<<endl;
		return;
	}
	timeSinceLastCheckPoint = curTime-lastCheckPoint;
	lastCheckPoint = curTime;
}

void rsdgMission::setUnitBetweenCheckpoints(int unit){
	unitBetweenCheckPoints = unit;
}

double newCost(double real, double pred){
	if(real>pred)return (real-pred)/2+pred;
	return pred-(pred-real)/2;
}

bool rsdgMission::validate(vector<string> &sel){
	int curBudgetBackup = curBudget;
	for(string i: sel){
		graph->addTmpOn(i);
	}
	//generate new problem
	graph->minmax = MAX;
	graph->setBudget((double)10000);//more than enough budget
	printProb(outfileName);
	consultServer();
	// solvable will be set at this moment
	// recover the budget
	graph->setBudget((double)curBudgetBackup);
	graph->resetTmpOn();
	return solvable;
}

// update the model when actual usage is way off expected
void rsdgMission::updateModel(int unitSinceLastCheckPoint){
	if(startTime==-1){
		cout<<RSDG_TAG+"first reconfig()"<<endl;
		return;
	}
	realCost = (double)timeSinceLastCheckPoint / (double)unitSinceLastCheckPoint;	
	cout<<"timesincelastCheckpoint"<<timeSinceLastCheckPoint<<"   unitsince"<<unitSinceLastCheckPoint<<endl;
	cout<<RSDG_TAG+"REAL="<<realCost<<"   PREDICTED="<<predictedCost<<endl;
	string targetNode = "";
	//get the current selected nodes
	//TODO: currently only support 1-node situation
/*	for (map<string,string>::iterator it = selected.begin(); it!=selected.end();it++){
		if(it->second == "")continue;
		targetNode = it->second;
	}
	double error = (realCost - predictedCost) / realCost;
	double updatedCost = newCost(realCost, predictedCost);	
	error = error<0?-1*error:error;//get the absolute error
	if(error>=THRESHOLD){
		cout<<RSDG_TAG+"OFF BY REAL CONSUMPTION BY "<<error;
		cout<<" GREATER THAN THRESHOLD, MODEL NEEDS TO BE UPDATED"<<endl;
		updateWeight(targetNode, updatedCost);	
	}*/
}

vector<string> rsdgMission::getDep(string s){
	vector<string> dummy;
	if(depChain.find(s)!=depChain.end()){
		return depChain[s];
	}
	else return dummy;
}

void rsdgMission::addConstraint(string name, bool on){
	if(on)graph->addOn(name);
	else graph->addOff(name);
}

void rsdgMission::addConstraint(string sink, string source, bool on){
	string edge = sink+"$"+source;
	if(on)graph->addOn(edge);
	else graph->addOff(edge);
}

vector<string>  rsdgMission::localSolve(){
	string filename = "";
	if(graph->minmax)
		filename=outfileName+"MAX.lp";
	else
		filename = outfileName+"MIN.lp";
	string cmd = "";
	if(lpsolve){
		cmd="lp_solve <" + filename + " >max.sol";
	}else{
		cmd="gurobi_cl ResultFile=max.sol LogFile=gurobi.log OutputFlag=0 "+filename + ">licenseInfo";
	}		
	system(cmd.c_str());
	cout<<"executing solver"<<endl;
	FILE *sol = fopen("max.sol","r");                                                  
	vector<string> result;
        if(!sol){
                cout<<"no solution file found\n"; 
		return result;
	}                                                                
        char line[256];                                                                    
        char res[50];                                                                      
        
        while(fgets(line,sizeof(line),sol)){                                               
                char *pch,*pch_obj,pch_energy;                                                                 
                char *node;                                                                
		//getting the VARs
                pch = strstr(line," 1\n");                                                 
		//pch_energy = strstr(line, "energy ");
		if(lpsolve)pch_obj = strstr(line, "Value of objective function:");
		else pch_obj = strstr(line," Objective value");

                if(!pch && !pch_energy && !pch_obj){//none found
                       // pch = strstr(line, "9.9");                                         
                        continue;
                }

		if(pch_obj !=NULL){
			char * s;
			if(lpsolve)s = strstr(line,":");
			else s = strstr(line,"=");
			s +=1;
			//cout<<"objective value"<<s<<endl;
			std::stringstream ss;
			ss.str (s);
			ss>>objValue;
			
		}
	
                if(pch !=NULL){
                        if((node = strstr(line," "))){                                       
                                //get the selected service 
                                int i = 0;                                                 
                                while(line[i]!=' '){                                       
                                        res[i] = line[i];
                                        i++;                                               
                                }                                                          
                                res[i] = '\0';                                             
                        }
                }
		//getting the budget/MV                                                                          
                result.push_back(res);
        }       
	return result;
}

void rsdgMission::setTraining(){
	TRAINING_MODE = true;
	cout<<RSDG_TAG + "In TRAINING MODE"<<endl;
	fact.open("fact.csv");
}

bool rsdgMission::isFailed(){
	return !solvable;
}

void rsdgMission::readRS(string input){	
	ifstream rs_file(input);
	string config;
	vector<vector<string>> configs;
	while(getline(rs_file, config)){
		vector<string> cur_config;
		istringstream nodes(config);
		while(!nodes.eof()){
			string tmp;
			nodes >> tmp;// now tmp is in the form of svc_lvl
			// convert the format to node name
			string servicename;
			int lvl;
			for(int i = 0; i<tmp.length(); i++){
				if(tmp[i]=='_'){
					servicename = tmp.substr(0,i);	
					lvl= stoi(tmp.substr(i+1));
					break;
				}
			}
			rsdgService* svc = getService(servicename);
			if(svc!=NULL){
				string nodename = svc->node_lists[lvl-1];
				cur_config.push_back(nodename);
			}
		}
		configs.push_back(cur_config);
	}
	RS = configs;
	cout<<RSDG_TAG + "representative set read in with "<<configs.size()<<" configs"<<endl;
}

void rsdgMission::setUpdate(bool up){
	update = up;
}

void rsdgMission::resetTimer(){
	startTime = getCurrentTimeInMilli();
}

void rsdgMission::setLogger(){
	LOGGER = true;
}
void rsdgMission::readMVProfile(){
        ifstream offline_profile;
        offline_profile.open("factmv.csv");
	string line;
	double mv;
	string svcname;
	int svclvl;
        while(getline(offline_profile, line)){
                istringstream nodes(line);
		nodes >> mv;
		string finalConfig = "";
                while(nodes>>svcname){
			nodes>>svclvl;
                        rsdgService* svc = getService(svcname);
                        if(svc!=NULL){
                                string nodename = svc->node_lists[svclvl-1];
				finalConfig+=nodename;
				finalConfig+=" ";
                        }
                }
		offlineMV[finalConfig] = mv;
		cout<<finalConfig<<" with mv"<<mv<<endl;
        }
}

/**
 * Read the offline profile for exhaustive search
 */
void rsdgMission::readCostProfile(){
        ifstream offline_profile;
        offline_profile.open("factcost.csv");
        string line;
        double cost;
        string svcname;
        int svclvl;
        while(getline(offline_profile, line)){
                istringstream nodes(line);
                nodes >> cost;
		string finalConfig="";
                while(nodes>>svcname){
                        nodes>>svclvl;
                        rsdgService* svc = getService(svcname);
                        if(svc!=NULL){
                                string nodename = svc->node_lists[svclvl-1];
				finalConfig+=nodename;
				finalConfig+=" ";
                        }
			
                }
		offlineCost[finalConfig] = cost;
        }
}

/**
 * Search through the offline profile
 */
vector<string> rsdgMission::searchProfile(){
	vector<string> resultConfig;
	double curMaxMV = -1;
	string maxConfig = "";
	for(auto it = offlineCost.begin(); it!=offlineCost.end(); it++){
		double curcost = it->second;
		cout<<"cur cost"<<curcost<<" ";
		cout<<it->first<<" ";
		if(curcost > curBudget){
			continue;
		}
		string curconfig = it->first;
		// this config is valid
		cout<<offlineMV[curconfig]<<endl;
		if(offlineMV[curconfig]>curMaxMV){
			maxConfig = curconfig;
			curMaxMV = offlineMV[curconfig];
			cout<<"changed to "<<curMaxMV<<endl;
		}
	}
	if(maxConfig=="")return resultConfig;
	// construct the result
	istringstream configs(maxConfig);
	string tmp;
	while(configs>>tmp)resultConfig.push_back(tmp);	
	return resultConfig;
}

void rsdgMission::setOfflineSearch(){
	offline_search = true;
}
/*
void rsdgMission::scaleup(string service, int scale){
	rsdgService* svc = getService(service);
	if(svc!=NULL){
		for(auto 
	}
}*/
