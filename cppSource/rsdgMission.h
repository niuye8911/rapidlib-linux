#ifndef RSDGMISSION_H
#define RSDGMISSION_H
#include <map>

#include "rsdgService.h"
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

using namespace std;

extern bool verboseRSDG;

void *startSolver(void *);

long long getCurrentTimeInMilli();

extern string RSDG_TAG;

class rsdgMission {
public:
  const static bool LP_SOLVE = true;

public:
  const static bool GUROBI = false;

public:
  const static bool LOCAL = true;

public:
  const static bool REMOTE = false;

public:
  const static bool RAPIDS = false;

public:
  const static bool RAPIDM = true;

  string app_name;
  bool DEBUG = false; // set to true if debug info is needed
  int numThreads;
  const string pythonScript =
      "/home/ubuntu/parsec-3.0/rsdglib/modelConstr/parseData.py";
  const string rapidScript =
      "/home/liuliu/Research/rapidlib-linux/modelConstr/source/rapid.py";
  double predictedCost = 0.0;
  double realCost = 0.0;

  // FACT file for cost
  ofstream fact;
  // Observed FACT file
  ofstream RS_fact;

  map<string, int> runnableID;
  map<string, int> threadID;
  map<string, string> basicToService;
  map<string, rsdgService *> serviceMap;
  map<string, pair<rsdgPara *, int>> paraList;
  map<string, rsdgPara *> contParaList;
  map<string, vector<string>> depChain; // kto a service's dependence
  map<string, int> threadPref;
  map<string, string> selected;
  map<string, double> offlineCost;
  map<string, double> offlineMV;
  map<string, double> contServiceValue;
  vector<vector<string>> all_configs;
  int curTrainingId = -1;
  int curUpdatingId = -1;
  bool lpsolve;
  bool local;
  bool rapidm;
  bool rapidm_started;
  long long lastCheckPoint;
  long long timeSinceLastCheckPoint = 0;
  long long startTime = -1;
  bool TRAINING_MODE = false;
  int unitBetweenCheckPoints = 0;
  bool CONT = false;
  ofstream logfile;
  double cur_budget_per_unit = 0.1;

  // mission related;
  RSDG *graph;
  string outfileName;
  int budgetType;
  rsdgUnit unit;
  long budgetTracker;
  int budget;
  int curBudget;
  double objValue;
  pthread_t monitor;
  int num_of_reconfig = 0;
  double total_reconfig_time = 0;
  vector<vector<string>> RS;
  bool offline_search = false;
  bool LOGGER = false;
  bool update = false;
  long freq;
  string xml_path;

  // result
  double maxMV;
  double minEnergy;
  bool solvable = true;
  //    RAPID_M related
  double slowdown = 0.0;
  string bucket;

  // thread+runnable list
  vector<void *(*)(void *)> runnableList;
  vector<rsdgService *> serviceList;

  void genAllConfigs(int, vector<string>);

public:
  rsdgMission(string name);
  rsdgService *getService(string name);
  void regService(string, string, void *(*)(void *), bool,
                  pair<rsdgPara *, int>);
  void finalizeRSDG(vector<int> &preference);
  void regService(string, string, void *(*)(void *), bool);
  void regContService(string, string, void *(*)(void *), rsdgPara *);
  void setupSolverFreq(int);
  void setUnit(int);
  void consultServer();
  void consultServer_M();
  void updateSelection(vector<string> &result);
  bool applyResult();
  bool updateThread(rsdgService *s, string basicNode, double value);
  void start();
  void generateProb(string);
  void setBudget(int);
  void updateMV(string, int, bool);
  int getBudget();
  void updateWeight(string, double);
  void updateWeight(string, string, double);
  int getNumThreads();
  int printPref(string serviceName);
  void setSolver(bool, bool, bool);
  void finish_one_unit();
  void reconfig();
  void printProb(string);
  void stopSolver();
  void cancel();
  virtual bool updateBudget();
  vector<string> getDep(string);
  void reset() {
    selected.clear();
    for (auto it = serviceMap.begin(); it != serviceMap.end(); it++) {
      if (it->second != NULL)
        it->second->setCurNode("");
    }
  }
  void addConstraint(string, bool);
  void addConstraint(string, string, bool);
  vector<string> localSolve();
  void setOutput(string);
  void getRes(vector<string> &, string);
  double genProductProfile();
  double getObj();
  void checkPoint();
  void
  updateModel(int); // this function will be called everytime before reconfig
  void setUnitBetweenCheckpoints(int);
  void printToLog(int, bool, bool);
  void setTraining();
  void genFact();
  void reconfig_training();
  void reconfig_updating();
  bool validate(vector<string> &);
  void filterConfigs();
  bool isFailed();
  void readRS(string);
  void updateRSDG();
  void setUpdate(bool);
  void resetTimer();
  void setLogger();
  void readMVProfile();
  void readCostProfile();
  vector<string> searchProfile();
  void setOfflineSearch();
  void readContTrainingSet();
  void setDebug();
  void logWarning(string msg);
  void logDebug(string msg);
  void logInfo(string msg);
  void finish(bool FINISH = true);
  double getFreq();
};
#endif
