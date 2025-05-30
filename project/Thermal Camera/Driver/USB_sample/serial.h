#ifndef _SERIAL_H_
#define _SERIAL_H_
#include <string>
#include <windows.h>
#include <iostream>
#include <thread>
#include <sstream>
#include <vector>
#include <string>
#include <mutex>
#include <fstream>
#include "data.h"
void serialAppInit();
int64_t readMcuTime();
#endif


