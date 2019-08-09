#ifndef RAPIDS_SERVER_WRAPPER
#define RAPIDS_SERVER_WRAPPER

#include <stdlib.h>
#include <string>
#include <stdio.h>

namespace RAPIDS_SERVER{

	bool init(std::string machineID, std::string appID, FILE* buckets, FILE* pModel);
	std::string start(std::string machineID, std::string appID, int budget);
	std::string get(std::string machineID, std::string appID, int budget);
	bool end(std::string machineID, std::string appID);

}

#endif
