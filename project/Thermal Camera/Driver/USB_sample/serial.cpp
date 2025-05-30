#include "serial.h"
#include <chrono>
HANDLE hSerial;
bool keepReading = true;
std::vector<int64_t> data;
int64_t serial_time;
std::vector<std::vector<int64_t>> csvData;
int64_t timeStamp;
std::mutex dataMutex;

void InitSerialPort(const wchar_t* portName) {
	hSerial = CreateFileW(portName, GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);

	if (hSerial == INVALID_HANDLE_VALUE) {
		if (GetLastError() == ERROR_FILE_NOT_FOUND) {
			std::cerr << "Serial port does not exist.\n";
		}
		std::cerr << "Error opening serial port.\n";
	}

	DCB dcbSerialParams = { 0 };
	dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
	if (!GetCommState(hSerial, &dcbSerialParams)) {
		std::cerr << "Getting state error.\n";
	}

	dcbSerialParams.BaudRate = CBR_115200;
	dcbSerialParams.ByteSize = 8;
	dcbSerialParams.StopBits = ONESTOPBIT;
	dcbSerialParams.Parity = NOPARITY;
	if (!SetCommState(hSerial, &dcbSerialParams)) {
		std::cerr << "Error setting serial port state.\n";
	}

	COMMTIMEOUTS timeouts = { 0 };
	timeouts.ReadIntervalTimeout = 50;
	timeouts.ReadTotalTimeoutConstant = 1000;
	timeouts.ReadTotalTimeoutMultiplier = 10;
	timeouts.WriteTotalTimeoutConstant = 50;
	timeouts.WriteTotalTimeoutMultiplier = 10;
	if (!SetCommTimeouts(hSerial, &timeouts)) {
		std::cerr << "Error setting timeouts.\n";
	}

	// 设置串口缓冲区大小
	if (!SetupComm(hSerial, 1024, 1024)) {  // 1024字节接收和发送缓冲区
		std::cerr << "Error setting up serial buffer size.\n";
	}
}

void sendHexData(HANDLE hSerial, const char* data, size_t size) {
	DWORD bytesWritten;
	if (!WriteFile(hSerial, data, size, &bytesWritten, NULL)) {
		std::cerr << "Error writing to serial port\n";
	}
}
bool receiveInt64(HANDLE hSerial, int64_t& receivedData) {
	DWORD bytesRead;
	char buffer[8]; // 64位整数的大小为8字节
	BOOL result = ReadFile(hSerial, buffer, sizeof(buffer), &bytesRead, NULL);

	if (!result) {
		std::cerr << "Error reading from serial port\n";
		return false;
	}
	if (bytesRead != sizeof(buffer)) {
		std::cerr << "Incomplete data received\n";
		return false;
	}

	// 将接收到的字节数组直接转换为 int64_t
	memcpy(&receivedData, buffer, sizeof(receivedData));
	return true;
}

int64_t readMcuTime() {
	// 发送两个十六进制数
	char data[] = { 0xA3, 0x0D };
	sendHexData(hSerial, data, sizeof(data));
	int64_t receivedData;
	if (receiveInt64(hSerial, receivedData)) {
		//std::cout << "Received int64_t data: " << receivedData << "\n";
		return receivedData;
	}
	return -1;
}

void serialAppInit() {
	const wchar_t* portName = L"\\\\.\\COM6";  // 替换为实际的串口名称
	InitSerialPort(portName);
}


void main_() {
	const wchar_t* portName = L"\\\\.\\COM6";  // 替换为实际的串口名称
	InitSerialPort(portName);
	// 发送两个十六进制数
	char data[] = { 0xA3, 0x0D };
	while (true) {
		sendHexData(hSerial, data, sizeof(data));
		int64_t receivedData;
		if (receiveInt64(hSerial, receivedData)) {
			std::cout << "Received int64_t data: " << receivedData << "\n";
		}
		
		Sleep(40); // 间隔1000毫秒
	}
}
