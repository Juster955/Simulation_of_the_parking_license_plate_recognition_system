#ifndef __UART_H
#define __UART_H

#include "main.h"

// 串口初始化
void MX_USART1_UART_Init(void);

// 发送字符串
void UART_SendString(char *str);

// 发送字节数组
void UART_SendData(uint8_t *data, uint16_t len);

// 获取接收缓冲区数据
uint8_t UART_GetRxBuffer(uint8_t **data, uint16_t *len);

// 清空接收缓冲区
void UART_ClearRxBuffer(void);

// 串口接收回调（在中断中调用）
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);

#endif