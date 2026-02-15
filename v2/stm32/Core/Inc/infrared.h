#ifndef __INFRARED_H
#define __INFRARED_H

#include "main.h"

// 红外传感器引脚定义（根据实际连接修改）
#define INFRARED_PIN       GPIO_PIN_0
#define INFRARED_PORT      GPIOA

// 红外传感器初始化
void Infrared_Init(void);

// 读取红外传感器状态
// 返回值：0-有车遮挡，1-无车（根据实际模块电平调整）
uint8_t Infrared_Read(void);

// 获取车辆通过事件（上升沿/下降沿检测）
uint8_t Infrared_GetVehicleEvent(void);

// 清除事件标志
void Infrared_ClearEvent(void);

#endif