#ifndef RAPIDS_M_SERVER
#define RAPIDS_M_SERVER

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>

namespace RAPIDS_SERVER {
typedef struct {
  std::vector<std::string> configs;
  std::string bucket;
  std::vector<std::string> best_config;
  double slowdown;
  bool found;
} Response;

bool init(std::string machineID, std::string appID, FILE *buckets,
          FILE *pModel);
Response start(std::string machineID, std::string appID, int budget);
Response get(std::string machineID, std::string appID, int budget);
std::tuple<bool, Response> check(std::string machineID, std::string appID,
                                 std::string bucket_name, int budget);
bool end(std::string machineID, std::string appID);
Response parse_response(std::string response);
} // namespace RAPIDS_SERVER

#endif
