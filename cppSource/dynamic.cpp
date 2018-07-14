#include <fstream>
#include <iostream>
#include <map>
#include <math.h>
#include <sstream>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

#define END ";"
using namespace std;

ofstream report;
ifstream f;
ifstream g;
map<string, vector<int>> fact;
map<string, vector<double>> guess;
vector<pair<string, string>> ctrs;
vector<string> bounds;

int totNum;
double maxerr;
void readObserved() {
  ifstream constraints;
  constraints.open("observed");
  while (!constraints.eof()) {
    string ctr1, ctr2;
    getline(constraints, ctr1);
    if (ctr1 == "")
      getline(constraints, ctr1);
    getline(constraints, ctr2);
    ctrs.push_back(make_pair(ctr1, ctr2));
  }
}

void genProblem(vector<int> &comb) {
  ifstream orig;
  orig.open("factorig.lp");
  ofstream prob;
  prob.open("factgen.lp");
  prob << orig.rdbuf();

  for (int i = 0; i < comb.size(); i++) {
    prob << ctrs[comb[i]].first << endl;
    prob << ctrs[comb[i]].second << endl;
  }
  ifstream end;
  end.open("factend.lp");
  prob << end.rdbuf();
  prob.close();
  string cmd = "gurobi_cl ResultFile=max.sol ";
  cmd += "factgen.lp";
  system(cmd.c_str());
}

void readGuess() {
  ifstream gg;
  gg.open("max.sol");
  string name;
  int level;
  string tmp;
  while (!gg.eof()) {
    gg >> tmp;
    level = tmp[tmp.size() - 1] - '0' - 1;
    tmp = tmp.substr(0, tmp.size() - 1);
    if (fact.find(tmp) == fact.end())
      continue;
    guess[tmp].resize(fact[tmp].size());
    gg >> guess[tmp][level];
  }
  // add in specific known value
  /*	guess["GPS"].push_back(298);
          guess["SYS"].push_back(375);
          guess["comm"].push_back(109);*/
}

void readFact() {
  string name;
  int level;
  while (!f.eof()) {
    f >> name;
    if (name == "#")
      break;
    f >> level;
    fact[name].resize(level);
  }
}

double checkRate() {
  int num = 0;
  double diff = 0;
  maxerr = -1;
  while (!f.eof()) {
    string s1, s2, s3, s4;
    int l1, l2, l3, l4;
    double v;
    f >> s1;
    f >> l1;
    f >> s2;
    f >> l2;
    f >> s3;
    f >> l3;
    f >> s4;
    f >> l4;
    f >> v;
    if (s1 == "")
      continue;
    double gvalue = guess[s1][l1 - 1] + guess[s2][l2 - 1] + guess[s3][l3 - 1] +
                    guess[s4][l4 - 1] + 782;
    if (l3 > 3)
      gvalue -= 298;
    cout << guess[s1][l1 - 1] << " " << guess[s2][l2 - 1] << " "
         << guess[s3][l3 - 1] << " " << guess[s4][l4 - 1] << " " << gvalue
         << "->" << v << endl;
    double dif = (gvalue - v) / v;
    dif = dif > 0 ? dif : -dif;
    diff += dif;
    maxerr = max(maxerr, dif);
    num++;
  }
  totNum = num;
  double errC = diff / num;
  return errC;
}

int main() {
  report.open("report");
  g.open("max.sol");
  readObserved();
  vector<int> repSet;
  repSet.push_back(0);
  double errtot = 99999999;
  int count = 1;
  map<int, bool> visited;

  while (errtot >= 0.1 || maxerr >= 0.15) {
    double errcur = 999999;
    int repcur = -1;
    for (int i = 1; i < ctrs.size(); i++) {
      if (visited.find(i) == visited.end())
        repSet.push_back(i);
      else
        continue;
      f.open("fact");
      readFact();
      genProblem(repSet);
      readGuess();
      double errtmp = checkRate();
      if (errtmp < errcur) {
        repcur = i;
        errcur = errtmp;
      }
      f.close();
      repSet.pop_back();
    }
    if (repcur == -1)
      break;
    repSet.push_back(repcur);
    errtot = errcur;
    visited[repcur] = true;
    count++;
    cout << "added" << repcur << endl;
    report << "added " << repcur << "->" << errtot << "max:" << maxerr << endl;
  }
  cout << "With error = " << errtot << " in " << totNum << " combinations"
       << endl;
  cout << "Max error = " << maxerr << endl;
  cout << "count=" << count << endl;
  report.close();
  return 1;
}
