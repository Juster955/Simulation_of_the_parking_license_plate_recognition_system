#ifndef __MAIN_H
#define __MAIN_H

#include "stm32f1xx_hal.h"

// 系统时钟定义
#define SYSTEM_TICK_PERIOD_MS 1

// 状态机定义
typedef enum {
    GATE_IDLE = 0,      // 空闲，等待指令
    GATE_OPENING,       // 正在抬杆
    GATE_OPEN,          // 已抬杆，等待车辆通过
    GATE_CLOSING,       // 正在落杆
    GATE_CLOSED         // 已落杆
} GateState;

// 全局变量声明
extern GateState currentGateState;
extern uint8_t vehiclePassedFlag;    // 车辆通过标志（红外触发）
extern uint32_t gateOpenStartTime;   // 抬杆开始时间
extern uint32_t gateCloseStartTime;  // 落杆开始时间

#endif