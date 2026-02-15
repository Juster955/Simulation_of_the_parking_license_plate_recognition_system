#include "main.h"
#include "uart.h"
#include "servo.h"
#include "infrared.h"
#include "gate.h"
#include <string.h>
#include <stdio.h>

// 全局变量定义
GateState currentGateState = GATE_IDLE;
uint8_t vehiclePassedFlag = 0;
uint32_t gateOpenStartTime = 0;
uint32_t gateCloseStartTime = 0;

// 接收缓冲区
uint8_t rxBuffer[64];
uint16_t rxLen = 0;

// 系统时钟初始化
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;  // 8MHz * 9 = 72MHz
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

// GPIO初始化
static void MX_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    // LED指示灯（PC13 - 板载LED）
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
}

// 解析串口指令
void ParseCommand(char *cmd) {
    if (strcmp(cmd, "OPEN_GATE") == 0) {
        Gate_OpenCommand();
        UART_SendString("CMD:OPEN_GATE OK\r\n");
    }
    else if (strcmp(cmd, "CLOSE_GATE") == 0) {
        Gate_CloseCommand();
        UART_SendString("CMD:CLOSE_GATE OK\r\n");
    }
    else if (strcmp(cmd, "GET_STATUS") == 0) {
        char status[32];
        sprintf(status, "STATUS:%s\r\n", Gate_GetStateString());
        UART_SendString(status);
    }
    else {
        UART_SendString("CMD:UNKNOWN\r\n");
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();

    // 初始化各模块
    MX_USART1_UART_Init();
    Servo_Init();
    Infrared_Init();
    Gate_Init();

    UART_SendString("STM32 Gate Controller Ready\r\n");

    uint32_t lastTick = HAL_GetTick();

    while (1) {
        // 处理道闸状态机（每10ms调用一次）
        if (HAL_GetTick() - lastTick >= 10) {
            Gate_Process();
            lastTick = HAL_GetTick();
        }

        // 处理串口接收
        uint8_t *rxData;
        if (UART_GetRxBuffer(&rxData, &rxLen)) {
            if (rxLen > 0 && rxData[rxLen-1] == '\n') {
                // 将接收数据转为字符串（去掉\r\n）
                char cmd[32] = {0};
                memcpy(cmd, rxData, rxLen > 31 ? 31 : rxLen);
                // 去掉换行符
                char *p = cmd;
                while (*p) {
                    if (*p == '\r' || *p == '\n') *p = '\0';
                    p++;
                }
                if (strlen(cmd) > 0) {
                    ParseCommand(cmd);
                }
                UART_ClearRxBuffer();
            }
        }

        // LED闪烁表示运行中
        static uint32_t ledTick = 0;
        if (HAL_GetTick() - ledTick >= 500) {
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
            ledTick = HAL_GetTick();
        }
    }
}

// 硬件错误处理
void Error_Handler(void) {
    while (1) {
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        HAL_Delay(100);
    }
}