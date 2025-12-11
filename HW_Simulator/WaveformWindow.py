import tkinter as tk
import time
import os
import sys
from collections import deque
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.font_manager as fm


def get_system_chinese_font():
    """获取系统可用的中文字体"""
    font_paths = []

    if sys.platform == 'win32': #Windows
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        font_paths = [
            os.path.join(windir, 'Fonts', 'msyh.ttc'),
            os.path.join(windir, 'Fonts', 'simhei.ttf'),
            os.path.join(windir, 'Fonts', 'simsun.ttc'),
        ]
    elif sys.platform == 'darwin':  #macOS
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        ]
    else:   #Linux
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path

    return None


def setup_matplotlib_chinese_font():
    """配置matplotlib使用中文字体"""
    try:
        chinese_font_path = get_system_chinese_font()

        if chinese_font_path:
            fm.fontManager.addfont(chinese_font_path)
            font_name = fm.FontProperties(fname=chinese_font_path).get_name()

            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            print(f"已设置matplotlib中文字体: {font_name}")
            return True
        else:
            print("警告: 未找到系统中文字体")
            return False

    except Exception as e:
        print(f"设置中文字体时出错: {e}")
        return False


# 初始化中文字体
setup_matplotlib_chinese_font()


class WaveformWindow:
    """波形显示窗口 - 内部计时版本"""

    def __init__(self, parent, variable_name, max_points=500):
        """
        初始化波形窗口

        Args:
            parent: 父窗口
            variable_name: 变量名称
            max_points: 最大显示点数
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"波形显示 - {variable_name}")
        self.window.geometry("850x550")
        self.variable_name = variable_name
        self.max_points = max_points

        # 数据存储
        self.timestamps = deque(maxlen=max_points)  # 相对时间，从0开始
        self.values = deque(maxlen=max_points)
        self.window_start_time = None  # 第一个数据点到达的时间

        # 显示模式
        self.display_mode = "sliding"
        self.window_size = 10.0  # 滑动窗口大小（秒）

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

        # 禁用科学计数法
        self.ax.ticklabel_format(useOffset=False, style='plain')

        # 初始坐标轴范围
        self.ax.set_xlim(0, self.window_size)
        self.ax.set_ylim(0, 1)

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 控制面板
        self._create_control_panel()

        # 统计信息
        self.last_value = None
        self.max_value = None
        self.min_value = None
        self.is_paused = False
        self.data_count = 0
        self.last_data_time = None

    def _create_control_panel(self):
        """创建控制面板"""
        # 控制框架
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 显示模式
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(mode_frame, text="显示模式:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="sliding")

        sliding_btn = tk.Radiobutton(mode_frame, text="滑动窗口", variable=self.mode_var,
                                     value="sliding", command=self._on_mode_change)
        sliding_btn.pack(side=tk.LEFT, padx=(5, 0))

        fixed_btn = tk.Radiobutton(mode_frame, text="全部显示", variable=self.mode_var,
                                   value="fixed", command=self._on_mode_change)
        fixed_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 窗口大小控制
        window_frame = tk.Frame(control_frame)
        window_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(window_frame, text="窗口(秒):", font=("Arial", 9)).pack(side=tk.LEFT)
        self.window_var = tk.StringVar(value="10.0")
        window_entry = tk.Entry(window_frame, textvariable=self.window_var, width=8)
        window_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 控制按钮
        button_frame = tk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT)

        self.pause_button = tk.Button(button_frame, text="暂停", width=8,
                                      command=self.toggle_pause, bg='#d9d9d9')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = tk.Button(button_frame, text="清除", width=8,
                                      command=self.clear_data, bg='#d9d9d9')
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(button_frame, text="关闭", width=8,
                  command=self.window.destroy, bg='#d9d9d9').pack(side=tk.LEFT)

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

        # 时间信息
        time_frame = tk.Frame(self.window)
        time_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.elapsed_label = tk.Label(time_frame, text="波形时间: 0.0s", font=("Arial", 9))
        self.elapsed_label.pack(side=tk.LEFT, padx=(0, 20))

        self.rate_label = tk.Label(time_frame, text="频率: 0.0 Hz", font=("Arial", 9))
        self.rate_label.pack(side=tk.LEFT)

    def _on_mode_change(self):
        """显示模式改变时的处理"""
        self.display_mode = self.mode_var.get()
        if self.display_mode == "sliding":
            try:
                self.window_size = float(self.window_var.get())
            except:
                self.window_size = 10.0
        self._update_plot()

    def add_data_point(self, value):
        """
        添加数据点

        Args:
            value: 变量值
        """
        if self.is_paused:
            return

        try:
            # 尝试转换为浮点数
            float_value = float(value)

            # 如果是第一个数据点，记录开始时间
            if self.window_start_time is None:
                self.window_start_time = time.time()

            # 计算相对时间（从第一个数据点开始）
            current_time = time.time()
            elapsed_time = current_time - self.window_start_time

            # 记录最后数据时间
            self.last_data_time = current_time

            # 添加数据
            self.timestamps.append(elapsed_time)
            self.values.append(float_value)
            self.data_count += 1

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

            # 调整坐标轴
            self._adjust_axes()

            # 更新标签
            self._update_labels()

            # 重绘画布
            self.canvas.draw()

    def _adjust_axes(self):
        """调整坐标轴范围"""
        if len(self.timestamps) < 2:
            return

        if self.display_mode == "sliding":
            # 滑动窗口模式
            if len(self.timestamps) > 0:
                current_time = self.timestamps[-1]
                window_start = max(0, current_time - self.window_size)
                window_end = current_time

                # 添加5%的边距
                margin = (window_end - window_start) * 0.05
                x_min = window_start - margin
                x_max = window_end + margin
                self.ax.set_xlim(x_min, x_max)
        else:
            # 全部显示模式
            if len(self.timestamps) > 1:
                x_min = min(self.timestamps)
                x_max = max(self.timestamps)

                # 如果只有一个点，设置一个范围
                if x_max - x_min < 0.001:
                    x_mid = x_min
                    x_min = x_mid - 0.5
                    x_max = x_mid + 0.5

                # 添加5%的边距
                margin = (x_max - x_min) * 0.05
                x_min -= margin
                x_max += margin

                self.ax.set_xlim(x_min, x_max)

        # 调整Y轴范围
        if len(self.values) > 0:
            y_min = min(self.values)
            y_max = max(self.values)

            # 如果所有值相同，设置一个范围
            if y_max - y_min < 0.001:
                y_mid = y_min
                y_min = y_mid - 0.5
                y_max = y_mid + 0.5
            else:
                # 添加10%的边距
                y_range = y_max - y_min
                margin = y_range * 0.1
                y_min -= margin
                y_max += margin

            self.ax.set_ylim(y_min, y_max)

    def _update_labels(self):
        """更新信息标签"""
        if self.last_value is not None:
            self.current_value_label.config(text=f"当前值: {self.last_value:.3f}")

        if self.max_value is not None:
            self.max_value_label.config(text=f"最大值: {self.max_value:.3f}")

        if self.min_value is not None:
            self.min_value_label.config(text=f"最小值: {self.min_value:.3f}")

        self.points_label.config(text=f"点数: {len(self.timestamps)}")

        # 更新时间信息
        if self.last_data_time is not None and self.window_start_time is not None:
            elapsed = self.last_data_time - self.window_start_time
            self.elapsed_label.config(text=f"波形时间: {elapsed:.1f}s")

            # 计算数据频率
            if elapsed > 0 and self.data_count > 1:
                frequency = self.data_count / elapsed
                self.rate_label.config(text=f"频率: {frequency:.2f} Hz")

    def toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        self.pause_button.config(text="继续" if self.is_paused else "暂停")

        if not self.is_paused and self.window_start_time is None:
            # 如果从暂停恢复且没有开始时间，重置
            self.window_start_time = time.time()

    def clear_data(self):
        """清除数据"""
        self.timestamps.clear()
        self.values.clear()
        self.max_value = None
        self.min_value = None
        self.last_value = None
        self.window_start_time = None
        self.last_data_time = None
        self.data_count = 0

        # 清除图形
        self.line.set_data([], [])

        # 重置坐标轴
        self.ax.set_xlim(0, self.window_size)
        self.ax.set_ylim(0, 1)

        # 更新标签
        self.current_value_label.config(text="当前值: --")
        self.max_value_label.config(text="最大值: --")
        self.min_value_label.config(text="最小值: --")
        self.points_label.config(text="点数: 0")
        self.elapsed_label.config(text="波形时间: 0.0s")
        self.rate_label.config(text="频率: 0.0 Hz")

        self.canvas.draw()

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