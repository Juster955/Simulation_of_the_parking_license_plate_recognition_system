#include "servo.h"
#include "main.h"

TIM_HandleTypeDef htim2;
uint8_t currentAngle = 90;  // 默认90度

void Servo_Init(void) {
    __HAL_RCC_TIM2_CLK_ENABLE();

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 72 - 1;          // 72MHz/72 = 1MHz，计数周期1us
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 20000 - 1;          // 20ms周期（50Hz）
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_PWM_Init(&htim2);

    TIM_OC_InitTypeDef sConfigOC = {0};
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 1500;                 // 1.5ms对应90度（理论值）
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1);

    // 启动PWM
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);

    // 设置初始角度
    Servo_SetAngle(90);
}

void Servo_SetAngle(uint8_t angle) {
    if (angle > 180) angle = 180;
    currentAngle = angle;
    // 角度转脉宽：0度=0.5ms，180度=2.5ms，对应计数值500-2500
    uint32_t pulse = 500 + (angle * 2000 / 180);  // 500 + angle*11.11
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse);
}

uint8_t Servo_GetAngle(void) {
    return currentAngle;
}