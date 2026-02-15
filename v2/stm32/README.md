# STM32 道闸控制器使用说明

## 硬件连接
- **串口1 (USART1)**: PA9(TX), PA10(RX) - 连接到上位机（树莓派/门卫电脑串口转USB模块）
- **舵机信号线**: PA8 (TIM1_CH1) - 通过PWM控制舵机角度
- **红外传感器**: PA0 - 检测车辆通过（低电平表示有车）
- **板载LED**: PC13 - 500ms闪烁表示运行中

## 舵机角度调整
根据实际安装，修改 `servo.h` 中的角度定义：
```c
#define SERVO_ANGLE_CLOSE 0     // 落杆角度
#define SERVO_ANGLE_OPEN  90    // 抬杆角度