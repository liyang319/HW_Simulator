import tkinter as tk
import time
from collections import deque


class SimpleWaveformWindow:
    """简单波形显示窗口（不使用matplotlib）"""

    def __init__(self, parent, variable_name, max_points=100):
        """
        初始化简单波形窗口

        Args:
            parent: 父窗口
            variable_name: 变量名称
            max_points: 最大显示点数
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"波形显示 - {variable_name}")
        self.window.geometry("600x400")
        self.variable_name = variable_name
        self.max_points = max_points

        # 数据存储
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.start_time = time.time()

        # 标题
        title_label = tk.Label(self.window, text=f"{variable_name} 波形图",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # 画布用于绘制波形
        self.canvas = tk.Canvas(self.window, bg='white', width=550, height=250)
        self.canvas.pack(padx=10, pady=10)

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

        # 绘图参数
        self.canvas_width = 550
        self.canvas_height = 230
        self.margin_left = 40
        self.margin_right = 20
        self.margin_top = 20
        self.margin_bottom = 30
        self.plot_width = self.canvas_width - self.margin_left - self.margin_right
        self.plot_height = self.canvas_height - self.margin_top - self.margin_bottom

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
            self._draw_waveform()

        except (ValueError, TypeError):
            # 如果不是数值，忽略
            pass

    def _draw_waveform(self):
        """绘制波形"""
        # 清除画布
        self.canvas.delete("all")

        if len(self.timestamps) < 2:
            # 数据不足，显示提示
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2,
                                    text="等待数据...", font=("Arial", 12))
            return

        # 计算数据范围
        time_min = min(self.timestamps)
        time_max = max(self.timestamps)
        value_min = min(self.values)
        value_max = max(self.values)

        # 防止除零
        if time_max - time_min == 0:
            time_max = time_min + 1
        if value_max - value_min == 0:
            value_max = value_min + 1

        # 绘制坐标轴
        # X轴
        self.canvas.create_line(self.margin_left, self.canvas_height - self.margin_bottom,
                                self.canvas_width - self.margin_right, self.canvas_height - self.margin_bottom,
                                width=2)
        # Y轴
        self.canvas.create_line(self.margin_left, self.margin_top,
                                self.margin_left, self.canvas_height - self.margin_bottom,
                                width=2)

        # 绘制刻度
        # X轴刻度
        for i in range(6):
            x = self.margin_left + i * self.plot_width / 5
            time_val = time_min + (time_max - time_min) * i / 5
            self.canvas.create_line(x, self.canvas_height - self.margin_bottom,
                                    x, self.canvas_height - self.margin_bottom + 5,
                                    width=1)
            self.canvas.create_text(x, self.canvas_height - self.margin_bottom + 15,
                                    text=f"{time_val:.1f}s", font=("Arial", 8))

        # Y轴刻度
        for i in range(6):
            y = self.canvas_height - self.margin_bottom - i * self.plot_height / 5
            value_val = value_min + (value_max - value_min) * i / 5
            self.canvas.create_line(self.margin_left - 5, y,
                                    self.margin_left, y,
                                    width=1)
            self.canvas.create_text(self.margin_left - 10, y,
                                    text=f"{value_val:.1f}", font=("Arial", 8),
                                    anchor='e')

        # 绘制波形
        points = []
        for i, (t, v) in enumerate(zip(self.timestamps, self.values)):
            x = self.margin_left + (t - time_min) / (time_max - time_min) * self.plot_width
            y = self.canvas_height - self.margin_bottom - (v - value_min) / (value_max - value_min) * self.plot_height
            points.extend([x, y])

        if len(points) >= 4:
            self.canvas.create_line(*points, fill='blue', width=2)

        # 更新标签
        self.current_value_label.config(text=f"当前值: {self.last_value:.2f}")
        self.max_value_label.config(
            text=f"最大值: {self.max_value:.2f}" if self.max_value is not None else "最大值: --")
        self.min_value_label.config(
            text=f"最小值: {self.min_value:.2f}" if self.min_value is not None else "最小值: --")
        self.points_label.config(text=f"点数: {len(self.timestamps)}")

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
        self._draw_waveform()

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


# 选择使用哪个版本的波形窗口
# 如果有matplotlib，使用高级版本；否则使用简单版本
# try:
#     import matplotlib.pyplot as plt
#     from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#     from matplotlib.figure import Figure
#
#     WaveformWindow = WaveformWindow  # 使用上面的matplotlib版本
# except ImportError:
#     WaveformWindow = SimpleWaveformWindow  # 回退到简单版本