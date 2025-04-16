import serial
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import time
from matplotlib.widgets import Button
import pandas as pd
from matplotlib.widgets import TextBox
from datetime import datetime
import winsound

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 查询所有串口并输出
def list_serial_ports():
    ports = ['COM%s' % (i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# 输出所有串口
serial_ports = list_serial_ports()
if serial_ports:
    print("可用串口:")
    for port in serial_ports:
        print(port)

# 配置串口 - 使用异常处理
try:
    # 如果有可用串口，使用第一个可用串口，否则使用COM8
    default_port = serial_ports[0] if serial_ports else 'COM8'
    ser = serial.Serial(default_port, 115200, timeout=1)
    print(f"成功连接到串口: {default_port}")
except (OSError, serial.SerialException) as e:
    print(f"串口连接错误: {e}")


# 创建图表和布局
fig = plt.figure(figsize=(14, 10))
gs = plt.GridSpec(3, 1, height_ratios=[5, 5, 1.5], hspace=0.6)

# 设置全局样式
plt.style.use('ggplot')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# 配置子图
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
line1, = ax1.plot([], [], 'r-', linewidth=1.5)
line2, = ax2.plot([], [], 'b-', linewidth=1.5)

# 设置图表属性
ax1.set_title('心电图信号', pad=10, fontsize=12, fontweight='bold')
ax2.set_title('呼吸波形', pad=10, fontsize=12, fontweight='bold')
ax1.set_xlabel('采样点')
ax2.set_xlabel('采样点')
ax1.set_ylabel('幅值')
ax2.set_ylabel('幅值')

ax1.set_xlim(0, 500)
ax1.grid(True, alpha=0.3)
ax2.set_xlim(0, 500)
ax2.grid(True, alpha=0.3)

# 启用自动缩放
ax1.set_autoscale_on(True)
ax2.set_autoscale_on(True)

# 数据缓冲区
data_buffer1 = np.zeros(500)
data_buffer2 = np.zeros(500)

# 添加按钮区域
button_ax = fig.add_subplot(gs[2])
button_ax.axis('off')

# 自定义按钮样式
button_style = {'color': 'white',
               'hovercolor': '#0056b3'}

# 设置按钮位置和样式
ax_start = plt.axes([0.35, 0.1, 0.1, 0.05])
ax_pause = plt.axes([0.45, 0.1, 0.1, 0.05])
ax_export = plt.axes([0.55, 0.1, 0.1, 0.05])

# 创建美化后的按钮
btn_start = Button(ax_start, '开始', color='#007bff', hovercolor='#0056b3')
btn_pause = Button(ax_pause, '暂停', color='#6c757d', hovercolor='#545b62')
btn_export = Button(ax_export, '导出', color='#28a745', hovercolor='#218838')

# 设置按钮文本颜色
for btn in [btn_start, btn_pause, btn_export]:
    btn.label.set_color('white')
    btn.label.set_fontsize(8)  # 设置按钮文字大小

# 动画控制变量
is_running = True

# 警报控制变量
last_alarm_time = 0
ALARM_INTERVAL = 3  # 警报间隔时间（秒）

runtime_data = {}


def export_data(event):
    try:
        from ecg_export import show_export_window
        show_export_window(runtime_data)
    except Exception as e:
        print(f"导出错误: {e}")

def start(event):
    global is_running, ani
    if not is_running:
        ani.event_source.start()
        is_running = True


def pause(event):
    global is_running, ani
    if is_running:
        ani.event_source.stop()
        is_running = False

btn_start.on_clicked(start)
btn_pause.on_clicked(pause)
btn_export.on_clicked(export_data)

def update(frame): 
    global data_buffer1, data_buffer2, last_alarm_time
 
    if ser.in_waiting:
        try:
            # 读取一行数据，尝试多种编码方式
            raw_data = ser.readline()
            try:
                line_data = raw_data.decode('utf-8').strip()
            except UnicodeDecodeError:
                try:
                    line_data = raw_data.decode('gbk').strip()
                except UnicodeDecodeError:
                    line_data = raw_data.decode('latin1').strip()
            
            values = line_data.split(',')
            
            if len(values) >= 3:
                # 获取心电信号和呼吸波数据
                ecg_value = float(values[0])
                resp_value = float(values[1])
                bpm_value = float(values[2])

                # 在bpm < 40 或者 > 120 时，嘀嘀嘀 警报
                if bpm_value < 40 or bpm_value > 120:
                    current_time = time.time()
                    if current_time - last_alarm_time >= ALARM_INTERVAL:
                        winsound.Beep(1000, 500)
                        last_alarm_time = current_time

    

                runtime_data[time.time()] = {
                    'ECG': ecg_value,
                    'Respiration': resp_value,
                    'BPM': bpm_value
                }
                
                # 更新数据缓冲区
                data_buffer1 = np.roll(data_buffer1, -1)
                data_buffer1[-1] = ecg_value
                data_buffer2 = np.roll(data_buffer2, -1)
                data_buffer2[-1] = resp_value
                
                # 更新图表
                line1.set_data(np.arange(len(data_buffer1)), data_buffer1)
                line2.set_data(np.arange(len(data_buffer2)), data_buffer2)
                # 更新y轴范围
                ax1.relim()
                ax1.autoscale_view()
                ax2.relim()
                ax2.autoscale_view()
                
                # 强制重绘以更新坐标轴
                fig.canvas.draw_idle()
        except Exception as e:
            print(f"数据处理错误: {e}")
    
    return [line1, line2]

ani = FuncAnimation(fig, update, frames=500, interval=10)

# 设置窗口标题
root = plt.get_current_fig_manager().window
#root.title("心电图实时监测")

# 调整布局，但不使用tight_layout
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

plt.show()