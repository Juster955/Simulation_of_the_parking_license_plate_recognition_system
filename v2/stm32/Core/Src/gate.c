#include "gate.h"
#include "servo.h"
#include "infrared.h"
#include "uart.h"
#include <stdio.h>

void Gate_Init(void) {
    currentGateState = GATE_IDLE;
    vehiclePassedFlag = 0;
    gateOpenStartTime = 0;
    gateCloseStartTime = 0;

    // 确保舵机在初始位置（落杆状态）
    Servo_SetAngle(SERVO_ANGLE_CLOSE);
}

void Gate_Process(void) {
    uint8_t vehicleEvent = Infrared_GetVehicleEvent();
    uint32_t currentTime = HAL_GetTick();

    switch (currentGateState) {
        case GATE_IDLE:
            // 空闲状态，等待指令
            break;

        case GATE_OPENING:
            // 正在抬杆
            if (currentTime - gateOpenStartTime >= GATE_OPEN_TIME_MS) {
                // 抬杆完成
                currentGateState = GATE_OPEN;
                UART_SendString("GATE:OPEN\r\n");
            }
            break;

        case GATE_OPEN:
            // 已抬杆，等待车辆通过
            if (vehicleEvent == 1) {  // 车辆进入
                vehiclePassedFlag = 1;
            }
            if (vehicleEvent == 2) {  // 车辆离开
                // 车辆已通过，准备落杆
                currentGateState = GATE_CLOSING;
                gateCloseStartTime = currentTime;
                Servo_SetAngle(SERVO_ANGLE_CLOSE);  // 开始落杆
                UART_SendString("GATE:CLOSING\r\n");
            }

            // 超时保护（如果红外故障，15秒后自动落杆）
            if (currentTime - gateOpenStartTime >= VEHICLE_PASS_TIMEOUT_MS) {
                currentGateState = GATE_CLOSING;
                gateCloseStartTime = currentTime;
                Servo_SetAngle(SERVO_ANGLE_CLOSE);
                UART_SendString("GATE:CLOSING (TIMEOUT)\r\n");
            }
            break;

        case GATE_CLOSING:
            // 正在落杆
            if (currentTime - gateCloseStartTime >= GATE_CLOSE_TIME_MS) {
                // 落杆完成
                currentGateState = GATE_CLOSED;
                UART_SendString("GATE:CLOSED\r\n");
            }
            break;

        case GATE_CLOSED:
            // 已落杆，准备下一次
            vehiclePassedFlag = 0;
            currentGateState = GATE_IDLE;
            break;
    }
}

void Gate_OpenCommand(void) {
    if (currentGateState == GATE_IDLE || currentGateState == GATE_CLOSED) {
        currentGateState = GATE_OPENING;
        gateOpenStartTime = HAL_GetTick();
        Servo_SetAngle(SERVO_ANGLE_OPEN);  // 抬杆
        UART_SendString("GATE:OPENING\r\n");
    } else {
        UART_SendString("GATE:BUSY\r\n");
    }
}

void Gate_CloseCommand(void) {
    if (currentGateState == GATE_OPEN) {
        currentGateState = GATE_CLOSING;
        gateCloseStartTime = HAL_GetTick();
        Servo_SetAngle(SERVO_ANGLE_CLOSE);  // 落杆
        UART_SendString("GATE:CLOSING\r\n");
    } else {
        UART_SendString("GATE:NOT_OPEN\r\n");
    }
}

GateState Gate_GetState(void) {
    return currentGateState;
}

char* Gate_GetStateString(void) {
    switch (currentGateState) {
        case GATE_IDLE: return "IDLE";
        case GATE_OPENING: return "OPENING";
        case GATE_OPEN: return "OPEN";
        case GATE_CLOSING: return "CLOSING";
        case GATE_CLOSED: return "CLOSED";
        default: return "UNKNOWN";
    }
}