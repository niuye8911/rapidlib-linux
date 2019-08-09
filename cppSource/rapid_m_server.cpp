#include <curl/curl.h>
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include "rapid_m_server.h"

namespace RAPIDS_SERVER{

	// Function declarations
	std::string readFile(FILE* file);
	std::string queryServer(std::string path, std::string getParams, std::string postParams);
	int strToInt(std::string str);

	// Function implementations

	/*
	 *
	 */
	bool init(std::string machineID, std::string appID, FILE* buckets, FILE* pModel){
		std::string bucketsFileText 	= readFile(buckets);
		std::string pModelFileText		= readFile(pModel);

		std::string getParams 	= "machine=" + machineID + "&app=" + appID;
		std::string postParams 	= "buckets=" + bucketsFileText + "&p_model=" + pModelFileText;

		std::string result = queryServer(std::string("init.php"), getParams, postParams);

		return result.empty();
	}

	/*
	 *
	 */
	std::string start(std::string machineID, std::string appID, int budget){

		std::string getParams 	= "machine=" + machineID + "&app=" + appID;
		std::string postParams 	= "budget=" + std::to_string(budget);

		std::string result = queryServer(std::string("start.php"), getParams, postParams);

		return result;
	}

	/*
	 *
	 */
	std::string get(std::string machineID, std::string appID, int budget){
		std::string getParams 	= "machine=" + machineID + "&app=" + appID;
		std::string postParams 	= "budget=" + budget;

		std::string result = queryServer(std::string("get.php"), getParams, postParams);

		return result;
	}

	/*
	 *
	 */
	bool end(std::string machineID, std::string appID){
		std::string getParams 	= "machine=" + machineID + "&app=" + appID;
		std::string postParams 	= "budget=" + 0;

		std::string result = queryServer(std::string("end.php"), getParams, postParams);

		return result.empty();
	}

	int strToInt(std::string str){
		bool isOnlyDigits = str.find_first_not_of("0123456789") == std::string::npos;

		if(isOnlyDigits) return std::stoi(str);
		else return -1;
	}

	std::string readFile(FILE* file){
		fseek(file, 0, SEEK_END);
		size_t size = ftell(file);

		char* arr = new char[size];

		rewind(file);
		fread(arr, sizeof(char), size, file);

		std::string str = std::string(arr);

		delete[] arr;

		return str;
	}

	size_t WriteCallback(char *contents, size_t size, size_t nmemb, void *userp){
 	   ((std::string*)userp)->append((char*)contents, size * nmemb);
 	   return size * nmemb;
 	}

	std::string queryServer(std::string path, std::string getParams, std::string postParams){
		// Fist, we build the whole url
		std::string url = "http://algaesim.cs.rutgers.edu/rapid_server/" + path;
		if(!getParams.empty()) url += "?" + getParams;

		curl_global_init(CURL_GLOBAL_ALL);

		CURL* curl = curl_easy_init();
		std::string readBuffer;

		curl_easy_setopt(curl, CURLOPT_URL, url.c_str()); //"/init.php?machine=123&app=5&budget=10&buckets=10,11,12,13&p_model=1.0,2.0,3.0");

		if(!postParams.empty()){
			curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postParams.c_str());
		}

		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

		curl_easy_perform(curl);

		return readBuffer;
	}

}
