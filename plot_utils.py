from tkinter import Toplevel, Frame, messagebox, Button
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

class ECGPlotter:
    @staticmethod
    def create_plot_window(parent_window, data_list):
        if not data_list:
            ECGPlotter.show_no_data_message()
            return
        
        # 创建新窗口显示图表
        plot_window = Toplevel(parent_window)
        plot_window.title("心电图数据显示")
        plot_window.geometry("1000x600")
        
        # 创建图表框架
        plot_frame = Frame(plot_window, bg="#f0f0f0")
        plot_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建工具栏框架
        toolbar_frame = Frame(plot_window, bg="#e0e0e0")
        toolbar_frame.pack(fill="x", padx=5, pady=5)
        
        # 添加保存按钮
        save_btn = Button(toolbar_frame, text="保存图表", command=lambda: ECGPlotter.save_figure(fig))
        save_btn.pack(side="left", padx=5)
        
        # 创建matplotlib图表
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title('心电图数据', pad=10, fontsize=12, fontweight='bold')
        ax.set_xlabel('时间')
        ax.set_ylabel('幅值')
        ax.grid(True, alpha=0.3)
        
        # 将matplotlib图表嵌入新窗口
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 绘制数据
        df = pd.DataFrame(data_list)
        df = df.sort_values('Time')
        
        if 'ECG' in df.columns and not pd.api.types.is_numeric_dtype(df['ECG']):
            df['ECG'] = pd.to_numeric(df['ECG'], errors='coerce')
        
        ax.plot(range(len(df)), df['ECG'].values, 'r-', linewidth=1)
        
        # 设置x轴刻度
        ECGPlotter.set_x_axis_labels(ax, df)
        
        fig.tight_layout()
        return plot_window, fig, ax
    
    @staticmethod
    def set_x_axis_labels(ax, df):
        num_ticks = min(5, len(df))
        if len(df) > 1:
            tick_positions = np.linspace(0, len(df)-1, num_ticks, dtype=int)
            time_labels = [df['Time'].iloc[i] for i in tick_positions]
            simplified_labels = []
            for label in time_labels:
                if ' ' in label:
                    date_part, time_part = label.split(' ')
                    simplified_labels.append(time_part)
                else:
                    simplified_labels.append(label)
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(simplified_labels, rotation=45)
    
    @staticmethod
    def show_no_data_message():
        messagebox.showinfo("提示", "在指定时间范围内未找到有效数据，请检查时间范围设置是否正确")
        
    @staticmethod
    def save_figure(fig):
        import os
        from tkinter.filedialog import asksaveasfilename
        
        filetypes = [("PNG 文件", "*.png"), ("PDF 文件", "*.pdf"), ("所有文件", "*.*")]
        filename = asksaveasfilename(defaultextension=".png", 
                                  filetypes=filetypes,
                                  title="保存图表")
        if filename:
            try:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", f"图表已保存到: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")