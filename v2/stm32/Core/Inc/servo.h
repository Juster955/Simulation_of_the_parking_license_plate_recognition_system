#ifndef __SERVO_H
#define __SERVO_H

#include "main.h"

// 舵机角度定义
#define SERVO_ANGLE_CLOSE 0     // 落杆角度（根据实际安装调整）
#define SERVO_ANGLE_OPEN  90    // 抬杆角度（根据实际安装调整）

// 舵机PWM定时器配置
#define SERVO_TIM         &htim2
#define SERVO_TIM_CHANNEL TIM_CHANNEL_1

// 舵机初始化
void Servo_Init(void);

// 设置舵机角度（0-180度）
void Servo_SetAngle(uint8_t angle);

// 获取当前角度
uint8_t Servo_GetAngle(void);

#endif