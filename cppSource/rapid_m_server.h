#ifndef RAPIDS_SERVER_WRAPPER
#define RAPIDS_SERVER_WRAPPER

#include <stdlib.h>
#include <string>
#include <stdio.h>
#include <vector>

namespace RAPIDS_SERVER{
	typedef struct {
		std::vector<std::string> configs;
		std::string bucket;
		double slowdown;
	} Response;
	bool init(std::string machineID, std::string appID, FILE* buckets, FILE* pModel);
	std::string start(std::string machineID, std::string appID, int budget);
	std::string get(std::string machineID, std::string appID, int budget);
	bool end(std::string machineID, std::string appID);
	Response parse_response(std::string response);
}

#endif
