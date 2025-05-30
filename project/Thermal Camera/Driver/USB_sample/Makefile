TARGET_SRC_DIR=.
TARGET_INC_DIR=.
TARGET_OUT_DIR=.
ISP_INC_DIR=$(TARGET_SRC_DIR)/include

OPENCV_LIB_DIR="/usr/lib/x86_64-linux-gnu"

CPPFLAGS=-I $(TARGET_INC_DIR)  -I $(ISP_INC_DIR)  -Wl,-rpath=./libs

sample:$(TARGET_SRC_DIR)/*.cpp
	g++ $(CPPFLAGS) -o $(TARGET_OUT_DIR)/$@ $^  -L ./libs  -L $(OPENCV_LIB_DIR) \
	-lpthread -liruvc -lirtemp -lirprocess -lirparse -lm \
	-lopencv_highgui -lopencv_imgcodecs  -lopencv_imgproc -lopencv_core
.PHONY:clean
clean:
	@rm -f sample
