from tkinter import Tk, Frame, Label, Button, StringVar, ttk, messagebox, Toplevel
from pandas.core.frame import console
import tkcalendar
import numpy as np
import pandas as pd
from datetime import datetime
from plot_utils import ECGPlotter

class ECGExportWindow:
    def __init__(self, runtime_data):
        self.runtime_data = runtime_data
        self.start_timestamp = None
        self.end_timestamp = None
        
        # 新增时间戳初始化逻辑
        if runtime_data:
            try:
                # 提取所有时间戳并转换为datetime对象
                timestamps = [datetime.fromtimestamp(float(ts)) for ts in runtime_data.keys()]
                self.start_timestamp = min(timestamps).strftime("%Y-%m-%d %H:%M:%S")
                self.end_timestamp = max(timestamps).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                messagebox.showerror("错误", f"时间戳格式错误: {str(e)}")
                # 设置默认时间戳为当前时间
                now = datetime.now()
                self.start_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                self.end_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            messagebox.showwarning("警告", "没有可用的数据")
            # 设置默认时间戳为当前时间
            now = datetime.now()
            self.start_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            self.end_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        self.setup_window()
        self.setup_ui()
        self.window.mainloop()

    def setup_window(self):
        self.window = Tk()
        self.window.title("心电图数据导出")
        self.window.geometry("1200x200")
        self.window.configure(bg="#f0f0f0")

    def setup_ui(self):
        # 创建主内容框架
        self.main_frame = Frame(self.window, bg="#f0f0f0")
        self.main_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # 创建日期选择器和按钮的容器
        self.content_frame = Frame(self.main_frame, bg="#f0f0f0")
        self.content_frame.pack(fill="both", expand=True)
        
        # 创建水平布局框架
        self.horizontal_frame = Frame(self.content_frame, bg="#f0f0f0")
        self.horizontal_frame.pack(side="top", fill="x", padx=20)
        
        self.setup_date_selection()
        self.setup_plot_frame()
        self.setup_status_bar()
        self.setup_buttons()

    def setup_date_selection(self):
        # 创建日期选择器框架
        date_frame = Frame(self.horizontal_frame, bg="#f0f0f0")
        date_frame.pack(side="left", padx=(0, 20))
        
        # 使用从runtime_data获取的时间戳
        start_date = self.start_timestamp.split()[0]  # 开始日期部分
        start_time = self.start_timestamp.split()[1]  # 开始时间部分
        end_date = self.end_timestamp.split()[0]  # 结束日期部分
        end_time = self.end_timestamp.split()[1]  # 结束时间部分
        
        # 开始日期时间选择
        self.setup_start_datetime(date_frame, start_date, start_time)
        # 结束日期时间选择
        self.setup_end_datetime(date_frame, end_date, end_time)

    def setup_start_datetime(self, date_frame, default_date, default_time):
        start_frame = Frame(date_frame, bg="#f0f0f0")
        start_frame.pack(side="left", padx=10)
        
        # 创建开始日期时间选择框和标签
        Label(start_frame, text="开始时间:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left", padx=5)
        print("default_date", default_date)  # Add this print statement for debugging
        print("default_time", default_time)  # Add this print statement for debugging
        self.start_datetime_var = StringVar(value=f"{default_date} {default_time}")
        self.start_datetime_label = Label(
            start_frame,
            textvariable=self.start_datetime_var,
            font=("Microsoft YaHei", 10),
            bg="#f0f0f0",
            fg="black",
            width=20
        )
        self.start_datetime_label.pack(side="left", padx=5)
        
        # 创建选择按钮
        Button(start_frame, text="选择", command=lambda: self.show_datetime_picker(True),
               bg="#007bff", fg="white", font=("Microsoft YaHei", 9)).pack(side="left", padx=5)

    def setup_end_datetime(self, date_frame, default_date, default_time):
        end_frame = Frame(date_frame, bg="#f0f0f0")
        end_frame.pack(side="left", padx=10)
        
        # 创建结束日期时间选择框和标签
        Label(end_frame, text="结束时间:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.end_datetime_var = StringVar(value=f"{default_date} {default_time}")
        self.end_datetime_label = Label(
            end_frame,
            textvariable=self.end_datetime_var,
            font=("Microsoft YaHei", 10),
            bg="#f0f0f0",
            fg="black",
            width=20
        )
        self.end_datetime_label.pack(side="left", padx=5)
        
        # 创建选择按钮
        Button(end_frame, text="选择", command=lambda: self.show_datetime_picker(False),
               bg="#007bff", fg="white", font=("Microsoft YaHei", 9)).pack(side="left", padx=5)

    def show_datetime_picker(self, is_start):
        # 创建日期时间选择器窗口
        picker = Toplevel(self.window)
        picker.title("选择日期和时间")
        picker.geometry("300x400")
        picker.configure(bg="#f0f0f0")
        
        # 获取当前选择的日期时间
        current_datetime = datetime.strptime(
            self.start_datetime_var.get() if is_start else self.end_datetime_var.get(),
            "%Y-%m-%d %H:%M:%S"
        )
        
        # 创建日历选择器
        cal = tkcalendar.Calendar(
            picker, selectmode='day',
            year=current_datetime.year,
            month=current_datetime.month,
            day=current_datetime.day,
            locale='zh_CN',
            background="#007bff",
            foreground="white",
            selectbackground="#0056b3",
            font=("Microsoft YaHei", 10)
        )
        cal.pack(pady=10, padx=10, fill="x")
        
        # 创建时间选择框架
        time_frame = Frame(picker, bg="#f0f0f0")
        time_frame.pack(pady=10)
        
        # 时间选择器
        hour_var = StringVar()
        minute_var = StringVar()
        second_var = StringVar()
        
        # 设置下拉框默认值
        hour_var.set(current_datetime.strftime("%H"))
        minute_var.set(current_datetime.strftime("%M"))
        second_var.set(current_datetime.strftime("%S"))
        
        # 创建时分秒选择器
        values_h = [f"{i:02d}" for i in range(24)]
        values_m = [f"{i:02d}" for i in range(60)]
        values_s = [f"{i:02d}" for i in range(60)]
        
        # 时间选择下拉框
        ttk.Combobox(time_frame, values=values_h, textvariable=hour_var, width=4,
                    state="readonly", font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
        Label(time_frame, text=":", bg="#f0f0f0", font=("Microsoft YaHei", 10)).pack(side="left")
        
        ttk.Combobox(time_frame, values=values_m, textvariable=minute_var, width=4,
                    state="readonly", font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
        Label(time_frame, text=":", bg="#f0f0f0", font=("Microsoft YaHei", 10)).pack(side="left")
        
        ttk.Combobox(time_frame, values=values_s, textvariable=second_var, width=4,
                    state="readonly", font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
        
        # 确定按钮
        Button(picker, text="确定", command=lambda: self.confirm_datetime_selection(cal, hour_var, minute_var, second_var, is_start, picker),
                bg="#28a745", fg="white", font=("Microsoft YaHei", 10)).pack(pady=10)

    def setup_plot_frame(self):
        # 创建图表框架
        plot_frame = Frame(self.main_frame, bg="#f0f0f0")
        plot_frame.pack(fill="both", expand=True, pady=20)

    def confirm_datetime_selection(self, cal, hour_var, minute_var, second_var, is_start, picker):
        try:
            selected_date = cal.selection_get()
            if not selected_date:
                messagebox.showerror("错误", "请选择日期")
                return

            selected_time = f"{hour_var.get().zfill(2)}:{minute_var.get().zfill(2)}:{second_var.get().zfill(2)}"
            selected_datetime = datetime.strptime(
                f"{selected_date.strftime('%Y-%m-%d')} {selected_time}",
                "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")

            target_var = self.start_datetime_var if is_start else self.end_datetime_var
            target_var.set(selected_datetime)
            self.status_var.set(f"已更新{'开始' if is_start else '结束'}时间: {selected_datetime}")
            picker.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"设置日期时间时出错: {str(e)}")
            self.status_var.set("日期时间设置失败")
            picker.destroy()

    def setup_status_bar(self):
        # 创建状态栏
        status_frame = Frame(self.window, bg="#f0f0f0")
        status_frame.pack(side="bottom", fill="x", padx=20, pady=5)
        
        self.status_var = StringVar(value="就绪")
        status_label = Label(status_frame, textvariable=self.status_var,
                            font=("Microsoft YaHei", 9), bg="#f0f0f0", anchor="w")
        status_label.pack(side="left")

    def setup_buttons(self):
        # 创建按钮框架
        button_frame = Frame(self.horizontal_frame, bg="#f0f0f0")
        button_frame.pack(side="left", padx=(20, 0), pady=(15, 0))
        
        # 创建按钮
        buttons = [
            ("绘制图像", self.plot_data, "#007bff"),
            ("导出Excel", self.export_to_excel, "#28a745")
        ]
        
        for text, command, bg_color in buttons:
            btn = Button(
                button_frame,
                text=text,
                command=command,
                bg=bg_color,
                fg="white",
                font=("Microsoft YaHei", 10),
                padx=15,
                pady=5
            )
            btn.pack(side="left", padx=5)

    def plot_data(self):
        try:
            # 获取用户输入的时间范围
            start_datetime_str = self.start_datetime_var.get()
            end_datetime_str = self.end_datetime_var.get()
            print("start_datetime_str", start_datetime_str)
            print("end_datetime_str", end_datetime_str)
            
            # 转换为datetime格式
            print(f"原始开始时间字符串: {start_datetime_str}")
            print(f"原始结束时间字符串: {end_datetime_str}")
            
            try:
                start_time_obj = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
                end_time_obj = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                messagebox.showerror("格式错误", f"时间格式转换错误: {str(e)}\n请确保使用YYYY-MM-DD HH:MM:SS格式")
                return
            
            # 读取数据
            data_list = self.get_filtered_data(start_time_obj, end_time_obj)
            
            # 使用ECGPlotter创建图表窗口
            plot_window, fig, ax = ECGPlotter.create_plot_window(self.window, data_list)
            if plot_window:
                self.status_var.set("已在新窗口中绘制图表")
                
        except Exception as e:
            messagebox.showerror("错误", f"绘制图表时出错: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")

    def get_filtered_data(self, start_time, end_time):
        try:
            # 验证数据可用性
            if not hasattr(self, 'runtime_data'):
                messagebox.showerror("错误", "runtime_data属性不存在")
                return []
            if not self.runtime_data:
                messagebox.showerror("错误", "没有可用的数据")
                return []
            if not isinstance(self.runtime_data, dict):
                messagebox.showerror("错误", "数据格式错误：runtime_data必须是字典类型")
                return []
            
            # 确保开始时间不晚于结束时间
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            
            # 筛选指定时间范围内的数据
            filtered_data = []
            invalid_format_count = 0
            missing_field_count = 0
            print("start_time", start_time)
            print("end_time", end_time)
            for timestamp_str, data in self.runtime_data.items():
                # 验证数据结构
                if not isinstance(data, dict):
                    continue
                
                if 'ECG' not in data:
                    missing_field_count += 1
                    continue
                
                try:
                    # 将时间戳转换为datetime对象
                    timestamp = float(timestamp_str)
                    data_time = datetime.fromtimestamp(timestamp)
                    
                    if start_time <= data_time <= end_time:
                        # 验证ECG数据
                        if pd.isna(data['ECG']):
                            continue
                        # 构建标准格式的数据记录
                        record = {
                            'Time': data_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'ECG': data['ECG'],
                            'Respiration': data.get('Respiration', None),
                            'BPM': data.get('BPM', None)
                        }
                        filtered_data.append(record)
                except ValueError:
                    invalid_format_count += 1
                    continue
                except Exception as e:
                    self.status_var.set(f"处理数据时出错: {str(e)}")
                    continue
            
            # 设置状态信息
            if not filtered_data:
                error_msg = "未找到指定时间范围内的有效数据\n"
                if invalid_format_count > 0:
                    error_msg += f"发现 {invalid_format_count} 条时间格式错误的数据\n"
                if missing_field_count > 0:
                    error_msg += f"发现 {missing_field_count} 条缺少必要字段的数据"
                messagebox.showwarning("警告", error_msg.strip())
                self.status_var.set("筛选完成，但未找到有效数据")
            else:
                self.status_var.set(f"已找到 {len(filtered_data)} 条有效数据")
            
            return filtered_data
            
        except Exception as e:
            error_msg = f"数据筛选失败: {str(e)}"
            messagebox.showerror("错误", error_msg)
            self.status_var.set(error_msg)
            return []
    
    def export_to_excel(self):
        try:
            # 获取用户输入的时间范围
            start_datetime_str = self.start_datetime_var.get()
            end_datetime_str = self.end_datetime_var.get()
            print("start_datetime_str", start_datetime_str)
            print("end_datetime_str", end_datetime_str)
            # 转换为datetime格式
            print(f"原始开始时间字符串: {start_datetime_str}")
            print(f"原始结束时间字符串: {end_datetime_str}")
            
            try:
                start_time_obj = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
                end_time_obj = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                messagebox.showerror("格式错误", f"时间格式转换错误: {str(e)}\n请确保使用YYYY-MM-DD HH:MM:SS格式")
                return
            
            # 获取筛选后的数据
            data_list = self.get_filtered_data(start_time_obj, end_time_obj)
            if not data_list:
                return
            
            # 创建DataFrame
            df = pd.DataFrame(data_list)
            df = df.sort_values('Time')
            
            # 设置默认文件名
            default_filename = f"ECG数据_{start_datetime_str}_{end_datetime_str}.xlsx"
            
            # 选择保存路径
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if file_path:
                # 导出到Excel
                df.to_excel(file_path, index=False)
                self.status_var.set(f"数据已导出到: {file_path}")
                messagebox.showinfo("成功", "数据导出完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出Excel失败: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")

def show_export_window(runtime_data):
    ECGExportWindow(runtime_data)