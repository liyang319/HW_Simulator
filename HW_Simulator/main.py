import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import json
import time
import threading
from datetime import datetime


class HardwareSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("硬件仿真系统 v1.0.0")
        self.root.geometry("900x700")

        # 全局变量
        self.model_running = False
        self.start_time = None
        self.timer_thread = None
        self.is_connected = False

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="硬件仿真系统 v1.0.0",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 创建主容器
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 第一行：目标机区域
        target_frame = tk.Frame(main_container)
        target_frame.pack(fill=tk.X, pady=5)

        tk.Label(target_frame, text="目标机:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.target_entry = tk.Entry(target_frame, width=30, font=("Arial", 10))
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "192.168.1.100")

        self.connect_button = tk.Button(target_frame, text="连接", width=8,
                                        font=("Arial", 10), command=self.toggle_connection)
        self.connect_button.pack(side=tk.LEFT, padx=5)

        # 第二行：模型操作区域
        model_ops_frame = tk.Frame(main_container)
        model_ops_frame.pack(fill=tk.X, pady=5)

        # 左侧按钮组
        left_ops_frame = tk.Frame(model_ops_frame)
        left_ops_frame.pack(side=tk.LEFT, fill=tk.X)

        self.select_model_btn = tk.Button(left_ops_frame, text="选择模型", width=10,
                                          font=("Arial", 10), command=self.select_model)
        self.select_model_btn.pack(side=tk.LEFT, padx=5)

        self.model_file_label = tk.Label(left_ops_frame, text="未选择文件",
                                         width=20, relief=tk.SUNKEN, bg="white", font=("Arial", 10))
        self.model_file_label.pack(side=tk.LEFT, padx=5)

        self.download_model_btn = tk.Button(left_ops_frame, text="模型下载", width=10,
                                            font=("Arial", 10), command=self.download_model)
        self.download_model_btn.pack(side=tk.LEFT, padx=5)

        # 右侧状态组
        right_ops_frame = tk.Frame(model_ops_frame)
        right_ops_frame.pack(side=tk.RIGHT, fill=tk.X)

        self.download_status_label = tk.Label(right_ops_frame, text="模型下载状态: 未下载",
                                              relief=tk.SUNKEN, width=20, bg="white", font=("Arial", 10))
        self.download_status_label.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(right_ops_frame, text="模型运行", width=10,
                                    font=("Arial", 10), command=self.toggle_model_run)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.time_label = tk.Label(right_ops_frame, text="00:00:00",
                                   font=("Arial", 10), width=10, relief=tk.SUNKEN, bg="white")
        self.time_label.pack(side=tk.LEFT, padx=5)

        # 中间部分：参数表格和监视表格
        middle_frame = tk.Frame(main_container)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 左侧：模型参数输入
        params_container = tk.Frame(middle_frame)
        params_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        params_header = tk.Frame(params_container)
        params_header.pack(fill=tk.X, pady=5)

        tk.Label(params_header, text="模型参数输入", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        self.param_send_btn = tk.Button(params_header, text="参数下发", width=10,
                                        font=("Arial", 10), command=self.send_parameters)
        self.param_send_btn.pack(side=tk.RIGHT)

        # 参数表格
        self.setup_params_table(params_container)

        # 右侧：变量监视
        watch_container = tk.Frame(middle_frame)
        watch_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        watch_header = tk.Frame(watch_container)
        watch_header.pack(fill=tk.X, pady=5)

        tk.Label(watch_header, text="变量监视", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # 变量监视表格
        self.setup_watch_table(watch_container)

        # 底部：系统日志
        bottom_frame = tk.Frame(main_container)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(bottom_frame, text="系统日志:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.log_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD,
                                                  width=80, height=12, font=("Arial", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 初始日志
        self.add_log("系统启动成功...")

    def setup_params_table(self, parent):
        """设置参数输入表格"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ("索引", "输入参数", "参数数值")
        self.params_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        # 设置列属性
        self.params_table.heading("索引", text="索引")
        self.params_table.heading("输入参数", text="输入参数")
        self.params_table.heading("参数数值", text="参数数值")

        self.params_table.column("索引", width=60, anchor=tk.CENTER)
        self.params_table.column("输入参数", width=150, anchor=tk.CENTER)
        self.params_table.column("参数数值", width=150, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.params_table.yview)
        self.params_table.configure(yscrollcommand=scrollbar.set)

        self.params_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_watch_table(self, parent):
        """设置变量监视表格"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ("索引", "变量名称", "参数数值", "波形")
        self.watch_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        # 设置列属性
        self.watch_table.heading("索引", text="索引")
        self.watch_table.heading("变量名称", text="变量名称")
        self.watch_table.heading("参数数值", text="参数数值")
        self.watch_table.heading("波形", text="波形")

        self.watch_table.column("索引", width=60, anchor=tk.CENTER)
        self.watch_table.column("变量名称", width=120, anchor=tk.CENTER)
        self.watch_table.column("参数数值", width=120, anchor=tk.CENTER)
        self.watch_table.column("波形", width=80, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.watch_table.yview)
        self.watch_table.configure(yscrollcommand=scrollbar.set)

        self.watch_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定波形按钮点击事件
        self.watch_table.bind("<Button-1>", self.on_waveform_click)

    def load_initial_data(self):
        """加载初始数据"""
        try:
            # 加载参数数据
            with open("input_params.json", "r", encoding="utf-8") as f:
                self.params_data = json.load(f)
            self.update_params_table()
        except FileNotFoundError:
            self.params_data = []
            self.add_log("警告: input_params.json 文件未找到")

        try:
            # 加载监视变量数据
            with open("watch_variables.json", "r", encoding="utf-8") as f:
                self.watch_data = json.load(f)
            self.update_watch_table()
        except FileNotFoundError:
            self.watch_data = []
            self.add_log("警告: watch_variables.json 文件未找到")

    def update_params_table(self):
        """更新参数表格"""
        # 清空表格
        for item in self.params_table.get_children():
            self.params_table.delete(item)

        # 添加数据（只显示param和val，隐藏type）
        for idx, param in enumerate(self.params_data, 1):
            self.params_table.insert("", tk.END, values=(
                idx,
                param.get("param", ""),
                param.get("val", "")
            ))

    def update_watch_table(self):
        """更新监视变量表格"""
        # 清空表格
        for item in self.watch_table.get_children():
            self.watch_table.delete(item)

        # 添加数据（只显示variable和val，隐藏type）
        for idx, var in enumerate(self.watch_data, 1):
            self.watch_table.insert("", tk.END, values=(
                idx,
                var.get("variable", ""),
                var.get("val", ""),
                "波形"
            ))

    def toggle_connection(self):
        """切换连接状态"""
        current_text = self.connect_button.cget("text")
        target = self.target_entry.get()

        if current_text == "连接":
            self.connect_button.config(text="断开")
            self.is_connected = True
            self.add_log(f"已连接到目标机: {target}")
        else:
            self.connect_button.config(text="连接")
            self.is_connected = False
            self.add_log(f"已断开与目标机 {target} 的连接")

    def select_model(self):
        """选择模型文件"""
        file_path = filedialog.askopenfilename(
            title="选择模型文件",
            filetypes=[("模型文件", "*.mdl *.model *.bin"), ("所有文件", "*.*")]
        )

        if file_path:
            filename = file_path.split("/")[-1]
            self.model_file_label.config(text=filename)
            self.add_log(f"选择了模型文件: {filename}")

    def download_model(self):
        """下载模型"""
        if not self.is_connected:
            self.add_log("错误: 请先连接目标机")
            return

        self.download_status_label.config(text="模型下载状态: 下载中...")
        self.add_log("开始下载模型...")

        # 模拟下载过程
        def simulate_download():
            time.sleep(2)
            self.root.after(0, lambda: self.download_status_label.config(
                text="模型下载状态: 已完成"))
            self.root.after(0, lambda: self.add_log("模型下载完成"))

        threading.Thread(target=simulate_download, daemon=True).start()

    def send_parameters(self):
        """下发参数"""
        if not self.is_connected:
            self.add_log("错误: 请先连接目标机")
            return

        self.add_log("参数下发中...")

        # 模拟参数下发过程
        def simulate_send():
            time.sleep(1)
            self.root.after(0, lambda: self.add_log("参数下发完成"))

        threading.Thread(target=simulate_send, daemon=True).start()

    def toggle_model_run(self):
        """切换模型运行状态"""
        if not self.is_connected:
            self.add_log("错误: 请先连接目标机")
            return

        if not self.model_running:
            # 开始运行
            self.model_running = True
            self.run_button.config(text="模型停止")
            self.start_time = time.time()
            self.add_log("模型开始运行")

            # 启动计时器线程
            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()

            # 启动模拟数据更新线程
            self.data_update_thread = threading.Thread(target=self.simulate_data_update, daemon=True)
            self.data_update_thread.start()

        else:
            # 停止运行
            self.model_running = False
            self.run_button.config(text="模型运行")
            self.time_label.config(text="00:00:00")
            self.add_log("模型停止运行")

    def update_timer(self):
        """更新运行时间"""
        while self.model_running:
            elapsed_time = int(time.time() - self.start_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            self.root.after(0, lambda ts=time_str: self.time_label.config(text=ts))
            time.sleep(1)

    def simulate_data_update(self):
        """模拟数据更新"""
        import random

        while self.model_running:
            if self.watch_data:
                # 随机更新一个变量的值
                idx = random.randint(0, len(self.watch_data) - 1)
                var_type = self.watch_data[idx].get("type", "int")

                if var_type == "int":
                    new_val = str(random.randint(0, 100))
                elif var_type == "float":
                    new_val = f"{random.uniform(0, 100):.2f}"
                else:
                    new_val = f"val_{random.randint(100, 999)}"

                self.watch_data[idx]["val"] = new_val
                self.root.after(0, self.update_watch_table)

            time.sleep(2)

    def on_waveform_click(self, event):
        """波形按钮点击事件"""
        item = self.watch_table.identify_row(event.y)
        column = self.watch_table.identify_column(event.x)

        if item and column == "#4":  # 波形列
            values = self.watch_table.item(item, "values")
            variable_name = values[1]  # 变量名称在第二列
            self.add_log(f"点击了变量 '{variable_name}' 的波形按钮")

    def add_log(self, message):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.update()


def create_sample_json_files():
    """创建示例JSON文件"""
    # 创建输入参数示例文件
    input_params = [
        {"param": "采样频率", "type": "int", "val": "1000"},
        {"param": "仿真时长", "type": "float", "val": "10.5"},
        {"param": "模型名称", "type": "string", "val": "test_model"},
        {"param": "参数A", "type": "int", "val": "50"},
        {"param": "参数B", "type": "float", "val": "3.14"},
        {"param": "参数C", "type": "string", "val": "default"}
    ]

    with open("input_params.json", "w", encoding="utf-8") as f:
        json.dump(input_params, f, ensure_ascii=False, indent=2)

    # 创建监视变量示例文件
    watch_variables = [
        {"variable": "温度", "type": "float", "val": "25.5"},
        {"variable": "压力", "type": "float", "val": "101.3"},
        {"variable": "转速", "type": "int", "val": "1500"},
        {"variable": "状态", "type": "string", "val": "正常"},
        {"variable": "电流", "type": "float", "val": "12.5"},
        {"variable": "电压", "type": "float", "val": "220.0"}
    ]

    with open("watch_variables.json", "w", encoding="utf-8") as f:
        json.dump(watch_variables, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 创建示例JSON文件
    create_sample_json_files()

    # 创建主窗口
    root = tk.Tk()
    app = HardwareSimulator(root)
    root.mainloop()