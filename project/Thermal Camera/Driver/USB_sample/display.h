#ifndef _DISPALAY_H_
#define _DISPALAY_H_
#define  _CRT_SECURE_NO_WARNINGS
#include <stdint.h>
#include <data.h>
#include "libirparse.h"
#include "libirprocess.h"
#include "cmd.h"
#include "temperature.h"
#include "serial.h"

#define OPENCV_ENABLE
#ifdef OPENCV_ENABLE
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp> 
#include <opencv2/highgui/highgui_c.h> 
//using namespace cv;
#endif

//initial the parameters for displaying
void display_init(StreamFrameInfo_t* stream_frame_info);

//release the parameters
void display_release(void);

//display one frame
void display_one_frame(StreamFrameInfo_t* stream_frame_info);

//display_save
void display_save(StreamFrameInfo_t* stream_frame_info, int frame_idx, int64_t timeStamp, bool save_flag);

//display thread
void* display_function(void* threadarg);


#endif
