#include "uart.h"

UART_HandleTypeDef huart1;
uint8_t rxByte;
uint8_t rxBuffer[64];
uint16_t rxIndex = 0;
uint8_t rxCompleteFlag = 0;

void MX_USART1_UART_Init(void) {
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart1);

    // 启动接收中断
    HAL_UART_Receive_IT(&huart1, &rxByte, 1);
}

void UART_SendString(char *str) {
    HAL_UART_Transmit(&huart1, (uint8_t*)str, strlen(str), 100);
}

void UART_SendData(uint8_t *data, uint16_t len) {
    HAL_UART_Transmit(&huart1, data, len, 100);
}

uint8_t UART_GetRxBuffer(uint8_t **data, uint16_t *len) {
    if (rxCompleteFlag) {
        *data = rxBuffer;
        *len = rxIndex;
        return 1;
    }
    return 0;
}

void UART_ClearRxBuffer(void) {
    rxIndex = 0;
    rxCompleteFlag = 0;
    memset(rxBuffer, 0, sizeof(rxBuffer));
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        if (rxByte == '\n' || rxIndex >= sizeof(rxBuffer)-1) {
            // 收到换行符或缓冲区满，标记完成
            if (rxIndex < sizeof(rxBuffer)-1) {
                rxBuffer[rxIndex++] = rxByte;
            }
            rxCompleteFlag = 1;
        } else {
            // 继续接收
            rxBuffer[rxIndex++] = rxByte;
        }
        // 重新启动接收
        HAL_UART_Receive_IT(&huart1, &rxByte, 1);
    }
}