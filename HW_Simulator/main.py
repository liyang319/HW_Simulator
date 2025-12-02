import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import threading
from datetime import datetime


class HardwareSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("硬件仿真系统 v1.0.0")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        # 状态变量
        self.model_file = None
        self.is_running = False
        self.start_time = None
        self.timer_thread = None
        self.stop_timer = False
        self.is_connected = False

        # 加载参数和变量数据
        self.input_params = self.load_json_file("input_params.json")
        self.watch_variables = self.load_json_file("watch_variables.json")

        self.create_widgets()
        self.add_log("系统启动成功...")

    def load_json_file(self, filename):
        """加载JSON文件，如果文件不存在则返回空列表"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 文件 {filename} 不存在")
            return []
        except json.JSONDecodeError:
            print(f"错误: 文件 {filename} JSON格式错误")
            return []

    def create_widgets(self):
        # 主标题
        title_label = tk.Label(self.root, text="硬件仿真系统 v1.0.0",
                               font=("Arial", 16, "bold"), bg='white')
        title_label.pack(pady=10)

        # 创建主容器
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 1. 目标机区域（第一行）
        target_frame = tk.Frame(main_container, bg='white')
        target_frame.pack(fill=tk.X, pady=(0, 10), anchor='w')

        tk.Label(target_frame, text="目标机:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))

        self.target_entry = tk.Entry(target_frame, width=20, font=("Arial", 10))
        self.target_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.target_entry.insert(0, "192.168.1.100")

        self.connect_button = tk.Button(target_frame, text="连接", width=8, font=("Arial", 10),
                                        command=self.toggle_connection)
        self.connect_button.pack(side=tk.LEFT)

        # 2. 模型操作区域（第二行）
        model_ops_frame = tk.Frame(main_container, bg='white')
        model_ops_frame.pack(fill=tk.X, pady=(0, 15), anchor='w')

        # 选择模型按钮和文件名显示
        self.select_model_btn = tk.Button(model_ops_frame, text="选择模型", width=10, font=("Arial", 10),
                                          command=self.select_model)
        self.select_model_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 模型文件名显示（去掉"模型文件名"文字，直接显示文件名）
        self.model_file_label = tk.Label(model_ops_frame, text="未选择文件", font=("Arial", 10), bg='white')
        self.model_file_label.pack(side=tk.LEFT, padx=(0, 20))

        # 模型下载按钮和状态显示
        self.download_model_btn = tk.Button(model_ops_frame, text="模型下载", width=10, font=("Arial", 10),
                                            command=self.download_model)
        self.download_model_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 模型下载状态显示（去掉"模型下载状态"文字，直接显示状态）
        self.download_status_label = tk.Label(model_ops_frame, text="未下载", font=("Arial", 10), bg='white')
        self.download_status_label.pack(side=tk.LEFT, padx=(0, 20))

        # 模型运行按钮和时间显示
        self.run_button = tk.Button(model_ops_frame, text="模型运行", width=10, font=("Arial", 10),
                                    command=self.toggle_model_run)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        # 运行时间显示
        self.time_label = tk.Label(model_ops_frame, text="00:00:00", font=("Arial", 10), bg='white')
        self.time_label.pack(side=tk.LEFT)

        # 3. 中间区域：参数表格和监视表格
        middle_frame = tk.Frame(main_container, bg='white')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 表格标题行
        table_titles_frame = tk.Frame(middle_frame, bg='white')
        table_titles_frame.pack(fill=tk.X, pady=(0, 5))

        # 左侧：模型参数输入标题 + 参数下发按钮
        left_title_frame = tk.Frame(table_titles_frame, bg='white')
        left_title_frame.pack(side=tk.LEFT, anchor='w')

        tk.Label(left_title_frame, text="模型参数输入", font=("Arial", 10, "bold"), bg='white').pack(side=tk.LEFT,
                                                                                                     padx=(0, 10))

        self.param_send_btn = tk.Button(left_title_frame, text="参数下发", width=10, font=("Arial", 10),
                                        command=self.send_parameters)
        self.param_send_btn.pack(side=tk.LEFT)

        # 右侧：变量监视标题（与列表左对齐）
        right_title_frame = tk.Frame(table_titles_frame, bg='white')
        right_title_frame.pack(side=tk.LEFT, anchor='w', padx=(50, 0))

        tk.Label(right_title_frame, text="变量监视", font=("Arial", 10, "bold"), bg='white').pack(side=tk.LEFT)

        # 表格容器
        tables_container = tk.Frame(middle_frame, bg='white')
        tables_container.pack(fill=tk.BOTH, expand=True)

        # 左侧参数表格
        params_frame = tk.Frame(tables_container, bg='white')
        params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.setup_params_table(params_frame)

        # 右侧监视表格
        watch_frame = tk.Frame(tables_container, bg='white')
        watch_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.setup_watch_table(watch_frame)

        # 4. 底部：系统日志
        bottom_frame = tk.Frame(main_container, bg='white')
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(bottom_frame, text="系统日志:", font=("Arial", 10, "bold"), bg='white').pack(anchor='w', pady=(0, 5))

        # 日志文本框
        log_frame = tk.Frame(bottom_frame, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Arial", 10), height=8)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_params_table(self, parent):
        """设置参数输入表格"""
        # 创建表格框架
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview表格
        self.params_tree = ttk.Treeview(table_frame, columns=("索引", "输入参数", "参数数值"),
                                        show="headings", height=6)

        # 设置列属性 - 索引列宽度缩小
        self.params_tree.heading("索引", text="索引")
        self.params_tree.heading("输入参数", text="输入参数")
        self.params_tree.heading("参数数值", text="参数数值")

        self.params_tree.column("索引", width=40, anchor=tk.CENTER)  # 缩小索引列宽度
        self.params_tree.column("输入参数", width=120, anchor=tk.CENTER)
        self.params_tree.column("参数数值", width=120, anchor=tk.CENTER)

        # 设置表格样式，增加分隔线
        style = ttk.Style()
        style.configure("Treeview",
                        rowheight=25,
                        font=('Arial', 10),
                        borderwidth=1,
                        relief='solid')
        style.configure("Treeview.Heading",
                        font=('Arial', 10, 'bold'),
                        background='lightgray')

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.params_tree.yview)
        self.params_tree.configure(yscrollcommand=scrollbar.set)

        self.params_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定双击编辑事件
        self.params_tree.bind("<Double-1>", self.on_param_double_click)

        # 填充数据
        self.update_params_table()

    def setup_watch_table(self, parent):
        """设置变量监视表格"""
        # 创建表格框架
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview表格
        self.watch_tree = ttk.Treeview(table_frame, columns=("索引", "变量名称", "参数数值", "波形"),
                                       show="headings", height=6)

        # 设置列属性 - 索引列宽度缩小
        self.watch_tree.heading("索引", text="索引")
        self.watch_tree.heading("变量名称", text="变量名称")
        self.watch_tree.heading("参数数值", text="参数数值")
        self.watch_tree.heading("波形", text="波形")

        self.watch_tree.column("索引", width=40, anchor=tk.CENTER)  # 缩小索引列宽度
        self.watch_tree.column("变量名称", width=100, anchor=tk.CENTER)
        self.watch_tree.column("参数数值", width=100, anchor=tk.CENTER)
        self.watch_tree.column("波形", width=60, anchor=tk.CENTER)

        # 设置表格样式，增加分隔线
        style = ttk.Style()
        style.configure("Treeview",
                        rowheight=25,
                        font=('Arial', 10),
                        borderwidth=1,
                        relief='solid')

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.watch_tree.yview)
        self.watch_tree.configure(yscrollcommand=scrollbar.set)

        self.watch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定波形按钮点击事件
        self.watch_tree.bind("<Button-1>", self.on_waveform_click)

        # 填充数据
        self.update_watch_table()

    def update_params_table(self):
        """更新参数表格"""
        # 清空表格
        for item in self.params_tree.get_children():
            self.params_tree.delete(item)

        # 添加数据
        for idx, param in enumerate(self.input_params, 1):
            self.params_tree.insert("", tk.END, values=(
                idx,
                param.get("param", ""),
                param.get("val", "")
            ))

    def update_watch_table(self):
        """更新监视变量表格"""
        # 清空表格
        for item in self.watch_tree.get_children():
            self.watch_tree.delete(item)

        # 添加数据
        for idx, var in enumerate(self.watch_variables, 1):
            self.watch_tree.insert("", tk.END, values=(
                idx,
                var.get("variable", ""),
                var.get("val", ""),
                "波形"
            ))

    def on_param_double_click(self, event):
        """参数数值双击编辑事件"""
        item = self.params_tree.selection()
        if not item:
            return

        item = item[0]
        column = self.params_tree.identify_column(event.x)

        # 只允许编辑"参数数值"列（第3列）
        if column == "#3":
            # 获取当前值
            current_values = self.params_tree.item(item, "values")
            current_value = current_values[2]

            # 获取单元格位置
            bbox = self.params_tree.bbox(item, column)
            if not bbox:
                return

            # 创建编辑框
            edit_frame = tk.Frame(self.params_tree, borderwidth=1, relief="solid")
            edit_frame.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

            entry = tk.Entry(edit_frame, font=("Arial", 10))
            entry.insert(0, current_value)
            entry.pack(fill=tk.BOTH, expand=True)
            entry.focus_set()
            entry.select_range(0, tk.END)

            def save_edit(event=None):
                new_value = entry.get()
                # 更新表格数据
                new_values = (current_values[0], current_values[1], new_value)
                self.params_tree.item(item, values=new_values)

                # 更新内存中的数据
                idx = int(current_values[0]) - 1
                if 0 <= idx < len(self.input_params):
                    self.input_params[idx]["val"] = new_value

                edit_frame.destroy()
                self.add_log(f"修改参数 {current_values[1]} 的值为: {new_value}")

            def cancel_edit(event=None):
                edit_frame.destroy()

            entry.bind("<Return>", save_edit)
            entry.bind("<Escape>", cancel_edit)
            entry.bind("<FocusOut>", lambda e: save_edit())

    def on_waveform_click(self, event):
        """波形按钮点击事件"""
        item = self.watch_tree.identify_row(event.y)
        column = self.watch_tree.identify_column(event.x)

        if item and column == "#4":  # 点击的是波形列
            values = self.watch_tree.item(item, "values")
            variable_name = values[1]  # 变量名称在第二列
            self.add_log(f"点击了变量 '{variable_name}' 的波形按钮")
            messagebox.showinfo("波形显示", f"显示变量 {variable_name} 的波形")

    def toggle_connection(self):
        """切换连接状态"""
        target = self.target_entry.get()
        if not self.is_connected:
            self.is_connected = True
            self.connect_button.config(text="断开", bg="lightcoral")
            self.add_log(f"已连接到目标机: {target}")
        else:
            self.is_connected = False
            self.connect_button.config(text="连接", bg="SystemButtonFace")
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
        if not self.model_file_label.cget("text") or self.model_file_label.cget("text") == "未选择文件":
            messagebox.showwarning("警告", "请先选择模型文件")
            return

        self.download_status_label.config(text="下载中...")
        self.add_log("开始下载模型...")

        # 模拟下载过程
        def simulate_download():
            time.sleep(2)
            self.root.after(0, lambda: self.download_status_label.config(text="已完成"))
            self.root.after(0, lambda: self.add_log("模型下载完成"))

        threading.Thread(target=simulate_download, daemon=True).start()

    def send_parameters(self):
        """下发参数"""
        self.add_log("参数下发中...")

        # 模拟参数下发过程
        def simulate_send():
            time.sleep(1)
            self.root.after(0, lambda: self.add_log("参数下发完成"))

        threading.Thread(target=simulate_send, daemon=True).start()

    def toggle_model_run(self):
        """切换模型运行状态"""
        if not self.model_file_label.cget("text") or self.model_file_label.cget("text") == "未选择文件":
            messagebox.showwarning("警告", "请先选择模型文件")
            return

        if not self.is_running:
            # 开始运行
            self.is_running = True
            self.run_button.config(text="模型停止", bg="lightcoral")
            self.start_time = time.time()
            self.stop_timer = False
            self.add_log("模型开始运行")

            # 启动计时器线程
            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()

            # 启动模拟数据更新线程
            self.data_update_thread = threading.Thread(target=self.simulate_data_update, daemon=True)
            self.data_update_thread.start()

        else:
            # 停止运行
            self.is_running = False
            self.run_button.config(text="模型运行", bg="SystemButtonFace")
            self.stop_timer = True
            self.time_label.config(text="00:00:00")
            self.add_log("模型停止运行")

    def update_timer(self):
        """更新运行时间"""
        while self.is_running and not self.stop_timer:
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

        while self.is_running and not self.stop_timer:
            if self.watch_variables:
                # 随机更新一个变量的值
                idx = random.randint(0, len(self.watch_variables) - 1)
                var_type = self.watch_variables[idx].get("type", "int")

                if var_type == "int":
                    new_val = str(random.randint(0, 100))
                elif var_type == "float":
                    new_val = f"{random.uniform(0, 100):.2f}"
                else:
                    new_val = f"val_{random.randint(100, 999)}"

                self.watch_variables[idx]["val"] = new_val
                self.root.after(0, self.update_watch_table)

            time.sleep(2)

    def add_log(self, message):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)


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