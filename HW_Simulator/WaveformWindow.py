import tkinter as tk
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class WaveformWindow:
    """波形显示窗口"""

    def __init__(self, parent, variable_name, max_points=100):
        """
        初始化波形窗口

        Args:
            parent: 父窗口
            variable_name: 变量名称
            max_points: 最大显示点数
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"波形显示 - {variable_name}")
        self.window.geometry("800x500")
        self.variable_name = variable_name
        self.max_points = max_points

        # 数据存储
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.start_time = time.time()

        # 创建matplotlib图形
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # 设置图形属性
        self.ax.set_title(f"{variable_name} 波形图", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("时间 (秒)", fontsize=12)
        self.ax.set_ylabel(f"{variable_name} 值", fontsize=12)
        self.ax.grid(True, alpha=0.3)

        # 创建初始线条
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label=variable_name)
        self.ax.legend(loc='upper right')

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 信息标签
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.current_value_label = tk.Label(info_frame, text="当前值: --", font=("Arial", 10))
        self.current_value_label.pack(side=tk.LEFT, padx=(0, 20))

        self.max_value_label = tk.Label(info_frame, text="最大值: --", font=("Arial", 10))
        self.max_value_label.pack(side=tk.LEFT, padx=(0, 20))

        self.min_value_label = tk.Label(info_frame, text="最小值: --", font=("Arial", 10))
        self.min_value_label.pack(side=tk.LEFT, padx=(0, 20))

        self.points_label = tk.Label(info_frame, text="点数: 0", font=("Arial", 10))
        self.points_label.pack(side=tk.LEFT)

        # 控制按钮
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.pause_button = tk.Button(control_frame, text="暂停", width=10,
                                      command=self.toggle_pause, bg='#d9d9d9')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = tk.Button(control_frame, text="清除", width=10,
                                      command=self.clear_data, bg='#d9d9d9')
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(control_frame, text="关闭", width=10,
                  command=self.window.destroy, bg='#d9d9d9').pack(side=tk.LEFT)

        # 控制变量
        self.is_paused = False
        self.last_value = None
        self.max_value = None
        self.min_value = None

    def add_data_point(self, value, timestamp=None):
        """
        添加数据点

        Args:
            value: 变量值
            timestamp: 时间戳，None表示使用当前时间
        """
        if self.is_paused:
            return

        try:
            # 尝试转换为浮点数
            float_value = float(value)

            if timestamp is None:
                timestamp = time.time() - self.start_time

            # 添加数据
            self.timestamps.append(timestamp)
            self.values.append(float_value)

            # 更新统计信息
            self.last_value = float_value
            if self.max_value is None or float_value > self.max_value:
                self.max_value = float_value
            if self.min_value is None or float_value < self.min_value:
                self.min_value = float_value

            # 更新图形
            self._update_plot()

        except (ValueError, TypeError):
            # 如果不是数值，忽略
            pass

    def _update_plot(self):
        """更新绘图"""
        if len(self.timestamps) > 0:
            # 更新线条数据
            self.line.set_data(self.timestamps, self.values)

            # 调整坐标轴范围
            if len(self.timestamps) > 1:
                x_padding = (self.timestamps[-1] - self.timestamps[0]) * 0.05
                y_min = min(self.values)
                y_max = max(self.values)
                y_range = y_max - y_min

                if y_range == 0:
                    y_range = 1

                self.ax.set_xlim(self.timestamps[0] - x_padding,
                                 self.timestamps[-1] + x_padding)
                self.ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)

            # 更新标签
            self.current_value_label.config(text=f"当前值: {self.last_value:.2f}")
            self.max_value_label.config(
                text=f"最大值: {self.max_value:.2f}" if self.max_value is not None else "最大值: --")
            self.min_value_label.config(
                text=f"最小值: {self.min_value:.2f}" if self.min_value is not None else "最小值: --")
            self.points_label.config(text=f"点数: {len(self.timestamps)}")

            # 重绘画布
            self.canvas.draw()

    def toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        self.pause_button.config(text="继续" if self.is_paused else "暂停")

    def clear_data(self):
        """清除数据"""
        self.timestamps.clear()
        self.values.clear()
        self.max_value = None
        self.min_value = None
        self._update_plot()

    def is_open(self):
        """检查窗口是否打开"""
        try:
            return self.window.winfo_exists()
        except:
            return False

    def destroy(self):
        """销毁窗口"""
        try:
            self.window.destroy()
        except:
            pass