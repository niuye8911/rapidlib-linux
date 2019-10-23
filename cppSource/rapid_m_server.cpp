#include "rapid_m_server.h"
#include <curl/curl.h>
#include <fstream>
#include <iostream>
#include <jsoncpp/json/json.h>
#include <jsoncpp/json/value.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>

namespace RAPIDS_SERVER {

// Function declarations
std::string readFile(FILE *file);
std::string queryServer(std::string path, std::string getParams,
                        std::string postParams);
int strToInt(std::string str);

// Function implementations

/*
 * return true if initialization is successed
 */
bool init(std::string machineID, std::string appID, FILE *buckets,
          FILE *pModel) {
  std::string bucketsFileText = readFile(buckets);
  std::string pModelFileText = readFile(pModel);

  std::string getParams = "machine=" + machineID + "&app=" + appID;
  std::string postParams =
      "buckets=" + bucketsFileText + "&p_model=" + pModelFileText;

  std::string response =
      queryServer(std::string("init.php"), getParams, postParams);

  return true;
}

/*
 * return the whole Response including config,bucket,slowdown
 */
RAPIDS_SERVER::Response start(std::string machineID, std::string appID,
                              int budget) {

  std::string getParams = "machine=" + machineID + "&app=" + appID;
  std::string postParams = "budget=" + std::to_string(budget);
  std::string result = "null";
  while (result == "null") {
    result = queryServer(std::string("start.php"), getParams, postParams);
  }
  return parse_response(result);
}

/*
 * return the whole Response including config,bucket,slowdown
 */
RAPIDS_SERVER::Response get(std::string machineID, std::string appID,
                            int budget) {
  std::string getParams = "machine=" + machineID + "&app=" + appID;
  std::string postParams = "budget=" + budget;
  std::string result = "null";
  while (result == "null") {
    result = queryServer(std::string("get.php"), getParams, postParams);
  }
  return parse_response(result);
}

/*
 * return true if config buckets stay the same
 */
std::tuple<bool, Response> check(std::string machineID, std::string appID,
                                 std::string bucket_name) {
  std::string getParams = "machine=" + machineID + "&app=" + appID;
  // std::string postParams = "cur_bucket=" + bucket_name;

  std::string result = queryServer(std::string("check.php"), getParams, "");
  RAPIDS_SERVER::Response r = parse_response(result);
  bool still_valid = r.bucket == bucket_name;
  return std::make_tuple(still_valid, r); // if changed, then check success
}

/*
 *
 */
bool end(std::string machineID, std::string appID) {
  std::string getParams = "machine=" + machineID + "&app=" + appID;
  std::string postParams = "budget=" + 0;

  std::string result =
      queryServer(std::string("end.php"), getParams, postParams);
  return true;
}

int strToInt(std::string str) {
  bool isOnlyDigits = str.find_first_not_of("0123456789") == std::string::npos;

  if (isOnlyDigits)
    return std::stoi(str);
  else
    return -1;
}

std::string readFile(FILE *file) {
  fseek(file, 0, SEEK_END);
  size_t size = ftell(file);

  char *arr = new char[size];

  rewind(file);
  fread(arr, sizeof(char), size, file);

  std::string str = std::string(arr);

  delete[] arr;

  return str;
}

size_t WriteCallback(char *contents, size_t size, size_t nmemb, void *userp) {
  ((std::string *)userp)->append((char *)contents, size * nmemb);
  return size * nmemb;
}

std::string queryServer(std::string path, std::string getParams,
                        std::string postParams) {
  // Fist, we build the whole url
  std::string url = "http://algaesim.cs.rutgers.edu/rapid_server/" + path;
  if (!getParams.empty())
    url += "?" + getParams;

  curl_global_init(CURL_GLOBAL_ALL);

  CURL *curl = curl_easy_init();
  std::string readBuffer;

  curl_easy_setopt(
      curl, CURLOPT_URL,
      url.c_str()); //"/init.php?machine=123&app=5&budget=10&buckets=10,11,12,13&p_model=1.0,2.0,3.0");

  if (!postParams.empty()) {
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postParams.c_str());
  }

  curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
  curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

  curl_easy_perform(curl);

  return readBuffer;
}

std::vector<std::string> process_string(std::string config,
                                        std::string delimiter) {
  std::vector<std::string> result;
  size_t pos = 0;
  std::string token;
  int cur_id = 0;
  while ((pos = config.find(delimiter)) != std::string::npos) {
    cur_id += 1;
    token = config.substr(0, pos);
    result.push_back(token);
    config.erase(0, pos + 1);
  }
  // add the last part
  result.push_back(config);
  return result;
}

// local method to parse the result based on different calling endpoint
Response parse_response(std::string response) {
  Json::Value res;
  Json::Reader reader;
  Response result;
  bool parsingSuccessful = reader.parse(response.c_str(), res);
  if (!parsingSuccessful) {
    std::cout << "Failed to parse JSON response" << std::endl;
    return result;
  }
  std::string bucket = res.get("bucket", "bucket does not exist").asString();
  std::string sd = res.get("slowdown", "slowdown does not exist").asString();
  std::string best_config_str =
      res.get("config", "best config does not exist").asString();
  std::vector<std::string> best_config = process_string(best_config_str, "$");
  std::string config_str =
      res.get("configs", "config does not exist").asString();
  std::vector<std::string> configs = process_string(config_str, "$");
  double slowdown = std::atof(sd.c_str());
  // bool changed = res.get("changed", "true").asString() == "true";
  bool success = res.get("found", "true").asString() == "true";
  result = {configs, bucket, best_config, slowdown, success};
  return result;
}

} // namespace RAPIDS_SERVER
