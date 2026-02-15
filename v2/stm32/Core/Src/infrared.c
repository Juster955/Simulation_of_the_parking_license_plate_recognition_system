#include "infrared.h"

static uint8_t lastInfraredState = 0;
static uint8_t vehicleEnterEvent = 0;
static uint8_t vehicleExitEvent = 0;

void Infrared_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitStruct.Pin = INFRARED_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;  // 根据模块实际输出电平调整
    HAL_GPIO_Init(INFRARED_PORT, &GPIO_InitStruct);

    // 读取初始状态
    lastInfraredState = HAL_GPIO_ReadPin(INFRARED_PORT, INFRARED_PIN);
}

uint8_t Infrared_Read(void) {
    return HAL_GPIO_ReadPin(INFRARED_PORT, INFRARED_PIN);
}

uint8_t Infrared_GetVehicleEvent(void) {
    uint8_t currentState = HAL_GPIO_ReadPin(INFRARED_PORT, INFRARED_PIN);

    // 检测下降沿（有车进入）- 假设有车时输出低电平
    if (lastInfraredState == 1 && currentState == 0) {
        vehicleEnterEvent = 1;
    }
    // 检测上升沿（有车离开）
    if (lastInfraredState == 0 && currentState == 1) {
        vehicleExitEvent = 1;
    }

    lastInfraredState = currentState;

    if (vehicleEnterEvent) {
        vehicleEnterEvent = 0;
        return 1;  // 车辆进入
    }
    if (vehicleExitEvent) {
        vehicleExitEvent = 0;
        return 2;  // 车辆离开
    }
    return 0;  // 无事件
}

void Infrared_ClearEvent(void) {
    vehicleEnterEvent = 0;
    vehicleExitEvent = 0;
}