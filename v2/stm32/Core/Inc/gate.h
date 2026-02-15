#ifndef __GATE_H
#define __GATE_H

#include "main.h"

// 抬杆时间（毫秒）- 根据实际道闸物理抬杆时间调整
#define GATE_OPEN_TIME_MS  3000

// 落杆时间（毫秒）
#define GATE_CLOSE_TIME_MS 3000

// 车辆通过检测超时（毫秒）- 如果红外故障，超时后自动落杆
#define VEHICLE_PASS_TIMEOUT_MS 15000

// 道闸控制初始化
void Gate_Init(void);

// 处理道闸状态机（在主循环中定时调用）
void Gate_Process(void);

// 外部指令：开闸
void Gate_OpenCommand(void);

// 外部指令：关闸
void Gate_CloseCommand(void);

// 获取当前状态
GateState Gate_GetState(void);

// 获取状态字符串（用于调试/上报）
char* Gate_GetStateString(void);

#endif