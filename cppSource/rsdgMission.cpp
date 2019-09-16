#include "rsdgMission.h"
#include "rapid_m_server.h"
#include "rsdgService.h"
#include "stdlib.h"
#include "string.h"
#include <ctime>
#include <curl/curl.h>
#include <iostream>
#include <math.h>
#include <signal.h>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>

/////rsdgMission////
rsdgMission::rsdgMission(string name) {
  RS_fact.open("observed.csv");
  app_name = name;
  numThreads = 0;
  budget = 0;
  curBudget = 0;
  rapidm_started = false;
  string test = "test";
  string log_name = "./mission_" + name + "_log.csv";
  string input_dep_file = "./input_" + name + "_log.txt";
  logfile.open(log_name);
  inputDepFile.open(input_dep_file);
  logfile << "Selection,RC_by_budget,RC_by_result,Real_Cost,RC_Time,"
             "RC_Num,Budget,Exec,SUCCESS\n";
}

rsdgService *rsdgMission::getService(string name) {
  if (serviceMap.find(name) != serviceMap.end())
    return serviceMap[name];
  else {
    return NULL;
  }
}

void rsdgMission::regService(string sName, string bName, void *(*func)(void *),
                             bool single, pair<rsdgPara *, int> para) {
  if (func == NULL) {
    basicToService[bName] = sName;
    threadPref[sName] = 0;
  }
  runnableList.push_back(func);
  runnableID[bName] = runnableList.size() - 1;

  if (getService(sName) == NULL) {
    rsdgService *s = new rsdgService(sName);
    s->setSingle(single);
    serviceList.push_back(s);
    threadPref[sName] = 0;
    threadID[sName] = serviceList.size() - 1;
    numThreads++;
    basicToService[bName] = sName;
    serviceMap[sName] = s;
  } else {
    basicToService[bName] = sName;
  }
  if (para.first != NULL) {
    paraList[bName] = para;
  }
  getService(sName)->addNode(bName);
}

void rsdgMission::regContService(string sName, string bName,
                                 void *(*func)(void *), rsdgPara *para) {
  regService(sName, bName, func, true);
  // register the value for parameter
  contParaList[bName] = para;
  CONT = true;
}

void rsdgService::addNode(string nodeName) {
  node_lists.push_back(nodeName);
  logDebug("Pushing back node : " + nodeName);
}

vector<string> &rsdgService::getList() { return node_lists; }
void rsdgMission::regService(string sName, string bName, void *(*func)(void *),
                             bool single) {
  if (func == NULL) {
    basicToService[bName] = sName;
    threadPref[sName] = 0;
  }
  runnableList.push_back(func);
  runnableID[bName] = runnableList.size() - 1;

  if (getService(sName) == NULL) {
    rsdgService *s = new rsdgService(sName);
    s->setSingle(single);
    serviceList.push_back(s);
    threadPref[sName] = 0;
    threadID[sName] = serviceList.size() - 1;
    numThreads++;
    basicToService[bName] = sName;
    serviceMap[sName] = s;
  } else {
    basicToService[bName] = sName;
  }
  getService(sName)->addNode(bName);
  // cout<<"registered imp:"<<bName<<"in service:"<<sName<<endl;
}

void rsdgMission::setupSolverFreq(int freq) { this->freq = freq; }

void rsdgMission::setUnit(int u) { unit.set(u); }

void rsdgMission::finish_one_unit() {
  checkPoint(1);
  double elapsed = timeSinceLastCheckPoints[1];
  inputDepFile << elapsed << " ";
  (unit.set(unit.get() - 1));
  if (unit.get() == 0) {
    // mission is finished
    fact.close();
  }
  checkPoint(1);
}

// helper func for libcurl
string data;
size_t writeCallback(char *buf, size_t size, size_t nmemb, void *up) {
  for (int c = 0; c < (int)(size * nmemb); c++) {
    data.push_back(buf[c]);
  }
  return size * nmemb; // tell curl how many bytes we handled
}
// parsing server response to vector
void rsdgMission::getRes(vector<string> &holder, string response) {
  // cout<<"response="<<response<<endl;
  int l = 1, r = 1;
  if (response[1] == 'o') {
    double obj = atof(&response[5]);
    objValue = obj;
    logDebug("objValue = " + to_string(obj));
  }
  while (r <= (int)response.size()) {
    if (response[r] != '\\') {
      r++;
      continue;
    }
    holder.push_back(response.substr(l, r - l));
    l = r + 2;
    r = l;
  }
  return;
}

void rsdgMission::consultServer_M() {
  // consult the server with RAPID_M option
  if (!rapidm_started) {
    string register_result =
        RAPIDS_SERVER::start("algaesim", app_name, curBudget);
    if (register_result != "1") {
      cout << "app cannot be registered to be started, msg:" << register_result
           << endl;
    };
  }
  string response = RAPIDS_SERVER::get("algaesim", app_name, curBudget);
  cout << response << std::endl;
  RAPIDS_SERVER::Response result = RAPIDS_SERVER::parse_response(response);
  updateSelection(result.configs);
  slowdown = result.slowdown;
  bucket = result.bucket;
}

void rsdgMission::consultServer() {
  if (offline_search) {
    vector<string> res = searchProfile();
    updateSelection(res);
    res.clear();
    return;
  }
  //#TO BE DONE
  if (local) {
    // cfgse local solver
    vector<string> res = localSolve();
    updateSelection(res);
    res.clear();
    return;
  }
  CURL *curl;
  CURLcode responseCode;
  vector<string> res;
  // init http options
  struct curl_httppost *formpost = NULL;
  struct curl_httppost *lastptr = NULL;
  struct curl_slist *headerlist = NULL;
  static const char buffer[] = "Expect:";
  string name =
      (graph->minmax) ? (outfileName + "MAX.lp") : (outfileName + "MIN.lp");
  curl_formadd(&formpost, &lastptr, CURLFORM_COPYNAME, "uploaded_file[]",
               CURLFORM_FILE, name.c_str(), CURLFORM_END);
  curl = curl_easy_init();
  headerlist = curl_slist_append(headerlist, buffer);

  // consult server
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL,
                     "http://algaesim.cs.rutgers.edu/solver/index.php");
    curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &writeCallback);
    responseCode = curl_easy_perform(curl);
    if (responseCode != CURLE_OK)
      logWarning("Server Failed");
    getRes(res, data);
    data = ""; // reset the data
    curl_easy_cleanup(curl);
    updateSelection(res);
    res.clear();
  }
}

void rsdgMission::updateSelection(vector<string> &result) {
  if (result.size() == 0) {
    // no solution
    logWarning("no solution found");
    solvable = false;
    if (!TRAINING_MODE) {
      logWarning("Mission Failed");
      finish(false);
      exit(0);
    }
    return;
  }
  int i;
  // clear the current selected
  for (map<string, string>::iterator it = selected.begin();
       it != selected.end(); it++) {
    it->second = "";
  }
  for (map<string, vector<string>>::iterator it2 = depChain.begin();
       it2 != depChain.end(); it2++) {
    it2->second.clear();
  }
  // iterating throught he result and fetch the returned result
  for (i = 0; i < (int)result.size(); i++) {
    string currentNode = result[i];
    string curNode = currentNode;
    logDebug("getting node : " + currentNode);
    std::size_t found = curNode.find(" ");
    // this might be a cont service
    if (found != std::string::npos) {
      string nodeName = "";
      int i = 0;
      while (currentNode[i] != ' ')
        nodeName += currentNode[i++];
      double value = stof(currentNode.substr(i));
      contServiceValue[nodeName] = value;
      curNode = nodeName;
    }

    string s = basicToService[curNode];
    rsdgService *svc = serviceMap[s];
    if (svc == NULL) { // could be edge or could be something wrong
      // get the edge
      size_t deli = curNode.find_last_of("$");
      if (deli != string::npos) {
        // found
        string sink = curNode.substr(0, deli);
        string source = curNode.substr(deli + 1);
        depChain[sink].push_back(source);
      }
      // get the objective cost
      size_t equalSign = curNode.find_last_of("=");
      if (equalSign != string::npos) {
        int expectCost = stoi(curNode.substr(equalSign + 1));
        predictedCost = expectCost;
        //                cout<<RSDG_TAG+"EXPECTED COST = "<<expectCost<<endl;
      }
      continue;
    }
    svc->setStatus(false);
    selected[s] = curNode;
    // special case where the cont service value is set to 1
    if (contParaList.find(curNode) != contParaList.end() &&
        contServiceValue.find(curNode) == contServiceValue.end()) {
      contServiceValue[curNode] = 1;
    }
  }
}

bool rsdgMission::applyResult() {
  bool reconfiged = false;
  for (map<string, string>::iterator it = selected.begin();
       it != selected.end(); it++) {
    string service = it->first;
    string basic = it->second;
    rsdgService *s = getService(service);
    if (s == NULL)
      continue;
    if (contParaList.find(basic) != contParaList.end()) {
      // this is a continuous service
      bool updated = updateThread(s, basic, contServiceValue[basic]);
      reconfiged = reconfiged || updated;
    } else
      updateThread(s, basic, 0.0);
  }
  // sleep for a few moment to let all config takes effect
  usleep(10000);
  logDebug("*Reconfiguration Finished*");
  return reconfiged;
}

bool rsdgMission::updateThread(rsdgService *s, string basic, double value) {
  if (basic == "") { // turn this service off
    /*pthread_t curThread = s->getThread();
    if (pthread_kill(curThread, 0) == 0) {
      pthread_cancel(curThread);
      s->setStatus(false);
      pthread_join(curThread, NULL);
    }
    return;*/
    value = 0.0;
  }
  void *(*f)(void *) = runnableList[runnableID[basic]];
  if (paraList.find(basic) != paraList.end()) {
    rsdgPara *p = paraList[basic].first;
    if (p != NULL) {
      int pValue = paraList[basic].second;
      p->intPara = pValue;
      return true;
    }
  } else if (contParaList.find(basic) != contParaList.end()) {
    // only change if change is greater than 1%
    double origin_value = contParaList[basic]->intPara;
    if (fabs(value - origin_value) / origin_value <= 0.01) {
      logDebug("Insignificant Change Ignored");
      return false;
    }

    contParaList[basic]->intPara = value;
    s->updateNode(f, basic);
    return true;
  }
  return true;
}

double rsdgMission::getObj() { return objValue; }

void rsdgMission::printToLog(int status, bool rc_by_budget, bool rc_by_result) {
  if (status != 0) {
    // in the middle of execution or has ended, write the real cost
    logfile << ',' << realCost << ",,,,," << endl;
    if (status == 1) {
      // end
      return;
    }
  }
  // write the current config
  for (map<string, string>::iterator it = selected.begin();
       it != selected.end(); it++) {
    string basic = it->second;
    string service = basicToService[basic];
    vector<string> &nodelist = getService(service)->getList();
    int lvl = 0;
    for (; lvl < nodelist.size(); lvl++) {
      if (nodelist[lvl] == basic) {
        break;
      }
    }
    lvl++;
    if (CONT && contServiceValue.find(basic) != contServiceValue.end()) {
      // check if this service is a cont service
      lvl = contServiceValue[basic];
    }
    logfile << service << "-" << lvl;
    if (next(it) != selected.end()) {
      logfile << "-";
    }
  }
  logfile << ',' << rc_by_budget << ',' << rc_by_result;
  logfile.flush();
}

void rsdgMission::genFact() {
  for (map<string, string>::iterator it = selected.begin();
       it != selected.end(); it++) {
    string basic = it->second;
    fact << basic << ",";
  }
  fact << realCost << endl;
  fact.flush();
}

void rsdgMission::genAllConfigs(int curSvcId, vector<string> tmp_result) {
  if (curSvcId == serviceList.size()) {
    // get a copy of the result
    vector<string> *result = new vector<string>();
    *result = tmp_result;
    all_configs.push_back(*result);
    return;
  }
  // dfs through all the nodes
  vector<string> &node_list = serviceList[curSvcId]->getList();
  for (int i = 0; i < node_list.size(); i++) {
    string curNode = node_list[i];
    tmp_result.push_back(curNode);
    genAllConfigs(curSvcId + 1, tmp_result);
    tmp_result.pop_back();
  }
}

void rsdgMission::filterConfigs() {
  for (int i = 0; i < all_configs.size(); i++) {
    if (!validate(all_configs[i])) {
      all_configs.erase(all_configs.begin() + i);
      i--;
      solvable = true; // reset the solvable
      continue;
    }
  }
}

void rsdgMission::reconfig_training() {
  // a procedure that gives all combinations of service selections for training
  vector<string> fake_results;
  if (all_configs.size() == 0) {
    // first time caling, need to generate the entire search space
    vector<string> tmp;
    tmp.clear();
    genAllConfigs(0, tmp);
    logDebug("Training Configs generated with total size = " +
             to_string(all_configs.size()));
    filterConfigs();
    // print all configs to a file
    ofstream valid_config;
    valid_config.open("validConfig.csv");
    for (auto config : all_configs) {
      for (auto node : config) {
        valid_config << node << " ";
      }
      valid_config << endl;
    }
    valid_config.close();
    logDebug("Training Configs generated with reduced size = " +
             to_string(all_configs.size()));
  }
  curTrainingId++;
  if (curTrainingId == all_configs.size()) {
    logInfo("Training done");
    fact.close();
  } else {
    fake_results = all_configs[curTrainingId];
    updateSelection(fake_results);
    string res = "";
    for (string sel : fake_results) {
      res += sel + " ";
    }
    logDebug("TRAINING: " + res);
  }
}

void rsdgMission::finalizeRSDG(vector<int> &preference) {
  // use user-provided preference to finalize RSDG MV weights
  string cmd = "python " + rapidScript + " -m finalize -xml " + xml_path;
  system(cmd.c_str());
}

void rsdgMission::updateRSDG() {
  // execute the python scrip
  string cmd =
      "python " + pythonScript + " -m consrsdg -o observed.csv -f fact.csv";
  system(cmd.c_str());
  // now that we have a file "rsdg" which contains a new rsdg
  // it's time to update the internal rsdg
  ifstream rsdgfile;
  rsdgfile.open("rsdg");
  string svc;
  vector<vector<string>> configs;
  while (getline(rsdgfile, svc)) {
    istringstream nodes(svc);
    string svcname = "";
    nodes >> svcname;
    logDebug("Updating RSDG weight for service: " + svcname);
    int curlevel = 0;
    double cost;
    while (nodes >> cost) {
      rsdgService *svc = getService(svcname);
      vector<string> &node_list = svc->getList();
      if (svc != NULL) {
        string nodename = node_list[curlevel++];
        updateWeight(nodename, cost);
        logDebug("Updating node weight " + nodename + " to " + to_string(cost));
      }
    }
  }
  logDebug("Updating RSDG COMPLETE");
}

void rsdgMission::reconfig_updating() {
  curUpdatingId++;
  if (curUpdatingId == RS.size()) {
    logDebug("Updating Model Done");
    RS_fact.close();
    // now we have the observation file, update the model
    updateRSDG();
    update = false;

  } else {
    updateSelection(RS[curUpdatingId]);
  }
}

void rsdgMission::reconfig() {
  logDebug("*Reconfiguration Start*");
  // updateModel(unitBetweenCheckPoints);
  checkPoint();
  updateModel(unitBetweenCheckPoints);
  bool update_by_budget = updateBudget();
  bool update_by_result = false;
  if (startTime == -1 || update_by_budget) {
    // first time or need to reconfig
    if (offline_search) {
      // offline reconfig
      consultServer();
    } else {
      // rsdg reconfig
      graph->minmax = MAX;
      printProb(outfileName);
      if (rapidm)
        consultServer_M();
      else
        consultServer();
    }
    // apply result
    update_by_result = applyResult();
    // check point again to ignore the overhead by RSDG
    checkPoint();
    total_reconfig_time += timeSinceLastCheckPoints[0];
    if (update_by_result)
      num_of_reconfig++;
  }
  int status = startTime == -1 ? 0 : 2;
  printToLog(status, update_by_budget, update_by_result);
  if (startTime == -1)
    startTime = getCurrentTimeInMilli();
}

double rsdgMission::genProductProfile() {
  ofstream myfile;
  myfile.open("./productProfile.csv");
  myfile << "missionValue, minEnergy, Selections \n";
  vector<double> profile;
  double initBudget = budget;
  while (solvable) {
    reconfig();
    if (!solvable)
      break;
    profile.push_back(maxMV * (budget - minEnergy));
    setBudget(minEnergy - 0.1);
    myfile << maxMV << ", " << minEnergy << ", ";
    for (map<string, string>::iterator it = selected.begin();
         it != selected.end(); it++) {
      string basic = it->second;
      myfile << basic << ", ";
    }
    myfile << endl;
  }
  myfile.close();
  double total = 0;
  for (int i = 0; i < profile.size(); i++) {
    total += profile[i];
  }
  return total / (initBudget - minEnergy);
}

void rsdgMission::start() {
  /*dummy code to start */
  reconfig();
  if (freq == 0)
    return;
  pthread_create(&monitor, NULL, startSolver, this);
}

void rsdgMission::stopSolver() {
  pthread_cancel(monitor);
  pthread_join(monitor, NULL);
  return;
}

void *startSolver(void *arg) {
  while (1) {
    pthread_testcancel();
    rsdgMission *rsdg = (rsdgMission *)arg;
    sleep(rsdg->getFreq());
    rsdg->reconfig();
  }
  return NULL;
}

double rsdgMission::getFreq() { return freq; }
void rsdgMission::setBudget(int b) {
  if (budget == 0)
    budget = b;
  curBudget = b;
  if (graph == NULL) {
    logWarning("RSDG has not been generated yet");
    return;
  }
  graph->setBudget((double)curBudget);
  return;
}

void rsdgMission::updateMV(string serviceName, int value, bool exp) {
  if (graph == NULL) {
    logWarning("RSDG has not been generated yet");
    return;
  }
  graph->updateMissionValue(serviceName, value, exp);
}

void rsdgMission::updateWeight(string b_name, double cost) {
  if (graph == NULL) {
    logWarning("RSDG has not been generated yet");
    return;
  }
  graph->updateCost(b_name, cost);
}

void rsdgMission::updateWeight(string sink, string source, double cost) {
  if (graph == NULL) {
    logWarning("RSDG has not been generated yet");
    return;
  }
  graph->updateEdgeCost(sink, source, cost);
}

int rsdgMission::getBudget() { return budget; }

int rsdgMission::getNumThreads() { return numThreads; }

void rsdgMission::generateProb(string input) {
  xml_path = input;
  graph = rsdgGen(input);
}

void rsdgMission::setOutput(string name) { outfileName = name; }

void rsdgMission::printProb(string outfile) {
  string name = outfile;
  if (graph->minmax)
    name += "MAX.lp";
  else
    name += "MIN.lp";
  graph->writeXMLLp(name, lpsolve);
}

void rsdgMission::setSolver(bool LP, bool LC, bool RM) {
  lpsolve = LP;
  local = LC;
  rapidm = RM;
}

void rsdgMission::cancel() {
  for (int i = 0; i < (int)serviceList.size(); i++) {
    rsdgService *s = serviceList[i];
    pthread_t sT = s->getThread();
    if (sT == 0)
      continue;
    if (pthread_kill(sT, 0) == 0) {
      pthread_cancel(sT);
      pthread_join(sT, NULL);
    }
  }
  return;
}

// The default impl uses the work unit left and time left to calculate the
// budget per unit User could re-define this method to their own needs
// return true if reconfig is needed, else false
bool rsdgMission::updateBudget() {
  int unit_left = unit.get();
  long long current_time = getCurrentTimeInMilli();
  long long usedMilli = startTime == -1 ? 0 : current_time - startTime;
  curBudget = budget - usedMilli;
  logDebug("currentBudget = " + to_string(curBudget));
  double new_budget_per_unit = (double)curBudget / (double)unit_left;
  logDebug("Used budget in Milli = " + to_string(usedMilli));
  logDebug("Unit left = " + to_string(unit_left));
  logDebug("New Budget per Unit = " + to_string(new_budget_per_unit));
  setBudget(new_budget_per_unit);
  if (abs(new_budget_per_unit - cur_budget_per_unit) / cur_budget_per_unit <=
      0.05) {
    return false;
  }
  cur_budget_per_unit = new_budget_per_unit;
  return true;
}

long long getCurrentTimeInMilli() {
  struct timeval tp;
  gettimeofday(&tp, NULL);
  long long mslong = (long long)tp.tv_sec * 1000L + tp.tv_usec / 1000;
  return mslong;
}

// keep the current timestamp to calculate new budget or monitor usage
void rsdgMission::checkPoint(int index) {
  long long curTime = getCurrentTimeInMilli();
  // check if last checkpoint exists
  if (lastCheckPoints.size() < index + 1) {
    lastCheckPoints.resize(index+1,startTime);
    timeSinceLastCheckPoints.resize(index+1,startTime);
  }
  timeSinceLastCheckPoints[index] = curTime - lastCheckPoints[index];
  lastCheckPoints[index] = curTime;
}

void rsdgMission::setUnitBetweenCheckpoints(int unit) {
  unitBetweenCheckPoints = unit;
}

double newCost(double real, double pred) {
  if (real > pred)
    return (real - pred) / 2 + pred;
  return pred - (pred - real) / 2;
}

bool rsdgMission::validate(vector<string> &sel) {
  int curBudgetBackup = curBudget;
  for (string i : sel) {
    graph->addTmpOn(i);
  }
  // generate new problem
  graph->minmax = MAX;
  graph->setBudget((double)10000); // more than enough budget
  printProb(outfileName);
  consultServer();
  // solvable will be set at this moment
  // recover the budget
  graph->setBudget((double)curBudgetBackup);
  graph->resetTmpOn();
  return solvable;
}

// update the model when actual usage is way off expected
void rsdgMission::updateModel(int unitSinceLastCheckPoint) {
  if (startTime == -1) {
    realCost = 0.0;
    return;
  }
  realCost = (double)timeSinceLastCheckPoints[0] / (double)unitSinceLastCheckPoint;
}

vector<string> rsdgMission::getDep(string s) {
  vector<string> dummy;
  if (depChain.find(s) != depChain.end()) {
    return depChain[s];
  } else
    return dummy;
}

void rsdgMission::addConstraint(string name, bool on) {
  if (on)
    graph->addOn(name);
  else
    graph->addOff(name);
}

void rsdgMission::addConstraint(string sink, string source, bool on) {
  string edge = sink + "$" + source;
  if (on)
    graph->addOn(edge);
  else
    graph->addOff(edge);
}

vector<string> rsdgMission::localSolve() {
  vector<string> result;
  string filename = "";
  if (graph->minmax)
    filename = outfileName + "MAX.lp";
  else
    filename = outfileName + "MIN.lp";
  string cmd = "";
  if (lpsolve) {
    cmd = "lp_solve <" + filename + " >max.sol";
  } else {
    cmd = "gurobi_cl ResultFile=max.sol LogFile=gurobi.log OutputFlag=0 " +
          filename + ">licenseInfo";
  }
  system(cmd.c_str());
  logDebug("executing solver");
  FILE *sol = fopen("max.sol", "r");
  if (!sol) {
    logWarning("no solution file found");
    return result;
  }
  char line[256];
  char res[50];

  while (fgets(line, sizeof(line), sol)) {
    char *pch, *pch_obj, *pch_energy;
    char *node;
    // getting the VARs
    // pch = strstr(line, " 0\n");
    // if (pch != NULL)
    //  continue; // current line represents a value that's not chosen

    pch_energy = strstr(line, "energy ");
    if (lpsolve)
      pch_obj = strstr(line, "Value of objective function:");
    else
      pch_obj = strstr(line, " Objective value");

    if (pch_obj != NULL) {
      char *s;
      if (lpsolve)
        s = strstr(line, ":");
      else
        s = strstr(line, "=");
      s += 1;
      // cout<<"objective value"<<s<<endl;
      std::stringstream ss;
      ss.str(s);
      ss >> objValue;
      continue; // proceed to next line
    }

    if (pch_energy != NULL) {
      // record the energy cost, proceed
      continue;
    }

    // this is a line with a selection
    if ((node = strstr(line, " 1\n"))) {
      int i = 0;
      while (line[i] != ' ') {
        res[i] = line[i];
        i++;
      }
      res[i] = '\0';
      result.push_back(res);
      continue;
    } else {
      // this is a line with continuous service value
      /*stringstream ss(line);
       string name; double value;
       ss>>name;
       ss>>value;
       result.push_back(name);
       result.push_back(to_string(value));*/
      result.push_back(line);
    }
  }
  return result;
}

void rsdgMission::setTraining() {
  TRAINING_MODE = true;
  logDebug("In TRAINING MODE");
  fact.open("fact.csv");
}

bool rsdgMission::isFailed() { return !solvable; }

void rsdgMission::readRS(string input) {
  ifstream rs_file(input);
  string config;
  vector<vector<string>> configs;
  while (getline(rs_file, config)) {
    vector<string> cur_config;
    istringstream nodes(config);
    while (!nodes.eof()) {
      string tmp;
      nodes >> tmp; // now tmp is in the form of svc_lvl
      // convert the format to node name
      string servicename;
      int lvl;
      for (int i = 0; i < tmp.length(); i++) {
        if (tmp[i] == '_') {
          servicename = tmp.substr(0, i);
          lvl = stoi(tmp.substr(i + 1));
          break;
        }
      }
      rsdgService *svc = getService(servicename);
      if (svc != NULL) {
        vector<string> &node_list = svc->getList();
        string nodename = node_list[lvl - 1];
        cur_config.push_back(nodename);
      }
    }
    configs.push_back(cur_config);
  }
  RS = configs;
}

void rsdgMission::setUpdate(bool up) { update = up; }

void rsdgMission::resetTimer() { startTime = getCurrentTimeInMilli(); }

void rsdgMission::setLogger() { LOGGER = true; }
void rsdgMission::readMVProfile() {
  ifstream offline_profile;
  offline_profile.open("factmv.csv");
  string line;
  double mv;
  string svcname;
  int svclvl;
  if (CONT) {
    while (getline(offline_profile, line)) {
      istringstream nodes(line);
      string finalconfig = "";
      vector<string> lines;
      string itm;
      while (nodes >> itm) {
        lines.push_back(itm);
      }
      // get the result
      for (int i = 0; i < lines.size() - 1; i++) {
        finalconfig += lines[i] + " ";
      }
      finalconfig = finalconfig.substr(0, finalconfig.size() - 1);
      // get the cost
      mv = stod(lines.back());
      offlineMV[finalconfig] = mv;
      logDebug(finalconfig + " with mv" + to_string(mv));
    }
    return;
  }

  while (getline(offline_profile, line)) {
    istringstream nodes(line);
    nodes >> mv;
    string finalConfig = "";
    while (nodes >> svcname) {
      nodes >> svclvl;
      rsdgService *svc = getService(svcname);
      vector<string> &node_list = svc->getList();
      if (svc != NULL) {
        string nodename = node_list[svclvl - 1];
        finalConfig += nodename;
        finalConfig += " ";
      }
    }
    offlineMV[finalConfig] = mv;
    logDebug(finalConfig + " with mv" + to_string(mv));
  }
}

/**
 * Read the offline profile for exhaustive search
 */
void rsdgMission::readCostProfile() {
  ifstream offline_profile;
  offline_profile.open("factcost.csv");
  string line;
  double cost;
  string svcname;
  int svclvl;
  if (CONT) {
    while (getline(offline_profile, line)) {
      istringstream nodes(line);
      string finalconfig = "";
      vector<string> lines;
      string itm;
      while (nodes >> itm) {
        lines.push_back(itm);
      }
      // get the result
      for (int i = 0; i < lines.size() - 1; i++) {
        finalconfig += lines[i] + " ";
      }
      finalconfig = finalconfig.substr(0, finalconfig.size() - 1);
      // get the cost
      cost = stod(lines.back());
      offlineCost[finalconfig] = cost;
      logDebug(finalconfig + " with cost" + to_string(cost));
    }
    return;
  }

  while (getline(offline_profile, line)) {
    istringstream nodes(line);
    nodes >> cost;
    string finalConfig = "";
    while (nodes >> svcname) {
      nodes >> svclvl;
      rsdgService *svc = getService(svcname);
      vector<string> &node_list = svc->getList();
      if (svc != NULL) {
        string nodename = node_list[svclvl - 1];
        finalConfig += nodename;
        finalConfig += " ";
      }
    }
    offlineCost[finalConfig] = cost;
  }
}

/**
 * Search through the offline profile
 */
vector<string> rsdgMission::searchProfile() {
  vector<string> resultConfig;
  double curMaxMV = -100;
  string maxConfig = "";
  for (auto it = offlineCost.begin(); it != offlineCost.end(); it++) {
    double curcost = it->second;
    if (curcost > curBudget) {
      continue;
    }
    string curconfig = it->first;
    // this config is valid
    if (offlineMV[curconfig] > curMaxMV) {
      maxConfig = curconfig;
      curMaxMV = offlineMV[curconfig];
    }
  }
  if (maxConfig == "")
    return resultConfig;
  // construct the result
  istringstream configs(maxConfig);
  string tmp;
  if (CONT) {
    string node = "";
    while (configs >> node) {
      node += " ";
      string val = "";
      configs >> val;
      resultConfig.push_back(node + val);
      node = "";
    }
    return resultConfig;
  }
  while (configs >> tmp)
    resultConfig.push_back(tmp);
  return resultConfig;
}

void rsdgMission::setOfflineSearch() { offline_search = true; }

/**
 * Training a continuous RSDG
 */
void rsdgMission::readContTrainingSet() {
  ifstream trainingSet;
  trainingSet.open("trainingset");
  string line;
  while (getline(trainingSet, line)) {
    vector<string> singleConfig;
    istringstream configs(line);
    string curSVC;
    string curSVCval;
    while (configs >> curSVC) {
      configs >> curSVCval;
      string singleSelect = curSVC + " " + curSVCval;
      singleConfig.push_back(singleSelect);
    }
    all_configs.push_back(singleConfig);
  }
}

void rsdgMission::setDebug() { DEBUG = true; }

void rsdgMission::logWarning(string msg) { cout << "RAPID-WARNING!:" + msg; }

void rsdgMission::logDebug(string msg) {
  if (DEBUG)
    cout << "RAPID-DEBUG:" + msg << endl;
}

void rsdgMission::logInfo(string msg) { cout << "RAPID-INFO:" + msg; }

/*
 void rsdgMission::scaleup(string service, int scale){
 rsdgService* svc = getService(service);
 if(svc!=NULL){
 for(auto
 }
 }*/
void rsdgMission::finish(bool FINISH) {
  printToLog(1, false, false);                                // finish
  long long total_used = getCurrentTimeInMilli() - startTime; // second
  logfile << ",,,," << to_string((double)total_reconfig_time) << ','
          << to_string(num_of_reconfig) << "," << budget << "," << total_used
          << ',' << FINISH << endl;
  logfile.close();
  inputDepFile.close();
  RAPIDS_SERVER::end("algaesim", app_name);
}
