import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import threading
from datetime import datetime
from TCPClient import TCPClient


class HardwareSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("硬件仿真系统 v1.0.0")
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"{screen_width}x{screen_height}")

        # 设置窗口为屏幕大小，并定位到左上角
        self.root.geometry(f"{screen_width}x{screen_height}")

        # 设置整体背景色为灰色
        self.root.configure(bg='#d9d9d9')

        # 状态变量
        self.model_file = None
        self.is_running = False
        self.start_time = None
        self.timer_thread = None
        self.stop_timer = False
        self.is_connected = False

        # 创建TCPClient对象 - 新增代码
        self.data_tcpclient = None  # 数据链路TCP客户端（端口9000）
        self.cmd_tcpclient = None  # 控制链路TCP客户端（端口9001）

        # 创建示例JSON文件（如果不存在）
        self.create_sample_json_files()

        # 加载参数和变量数据
        self.input_params = self.load_json_file("input_params.json")
        self.watch_variables = self.load_json_file("watch_variables.json")

        # 存储表格行引用
        self.param_rows = []
        self.watch_rows = []

        self.create_widgets()
        self.add_log("系统启动成功...")

    def create_sample_json_files(self):
        """创建示例JSON文件"""
        try:
            # 检查文件是否已存在
            with open("input_params.json", "r", encoding="utf-8") as f:
                json.load(f)  # 尝试读取
        except (FileNotFoundError, json.JSONDecodeError):
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
            print("创建了 input_params.json 文件")

        try:
            with open("watch_variables.json", "r", encoding="utf-8") as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
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
            print("创建了 watch_variables.json 文件")

    def load_json_file(self, filename):
        """加载JSON文件，如果文件不存在则返回空列表"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功加载 {filename}: {len(data)} 条数据")
                return data
        except FileNotFoundError:
            print(f"警告: 文件 {filename} 不存在")
            return []
        except json.JSONDecodeError as e:
            print(f"错误: 文件 {filename} JSON格式错误: {e}")
            return []

    def create_widgets(self):
        # 主标题
        title_label = tk.Label(self.root, text="硬件仿真系统 v1.0.0",
                               font=("Arial", 16, "bold"), bg='#d9d9d9')
        title_label.pack(pady=10)

        # 创建主容器 - 背景色设置为灰色
        main_container = tk.Frame(self.root, bg='#d9d9d9')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 1. 基础设置区域
        basic_settings_frame = tk.LabelFrame(main_container, text="基础设置", font=("Arial", 11, "bold"),
                                           bg='#d9d9d9', fg='#333333', bd=2, relief=tk.GROOVE)
        basic_settings_frame.pack(fill=tk.X, pady=(0, 15))

        # 目标机区域（第一行）
        target_frame = tk.Frame(basic_settings_frame, bg='#d9d9d9')
        target_frame.pack(fill=tk.X, pady=(10, 5), anchor='w', padx=10)

        tk.Label(target_frame, text="目标机:", font=("Arial", 10), bg='#d9d9d9').pack(side=tk.LEFT, padx=(0, 5))

        self.target_entry = tk.Entry(target_frame, width=20, font=("Arial", 10), bg='white',
                                     highlightthickness=0, bd=3, relief='flat',
                                     highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.target_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.target_entry.insert(0, "192.168.3.83")

        self.connect_button = tk.Button(target_frame, text="连接", width=8, font=("Arial", 10),
                                        command=self.toggle_connection, bg='#d9d9d9',
                                        highlightthickness=0, bd=0, relief='flat',
                                        highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.connect_button.pack(side=tk.LEFT)

        # 模型操作区域（第二行）
        model_ops_frame = tk.Frame(basic_settings_frame, bg='#d9d9d9')
        model_ops_frame.pack(fill=tk.X, pady=(5, 10), anchor='w', padx=10)

        # 选择模型按钮和文件名显示
        self.select_model_btn = tk.Button(model_ops_frame, text="选择模型", width=10, font=("Arial", 10),
                                          command=self.select_model, bg='#d9d9d9',
                                          highlightthickness=0, bd=0, relief='flat',
                                          highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.select_model_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 模型文件名显示
        self.model_file_label = tk.Label(model_ops_frame, text="未选择文件", font=("Arial", 10),
                                         bg='#d9d9d9', width=15, anchor='w')
        self.model_file_label.pack(side=tk.LEFT, padx=(0, 20))

        # 模型下载按钮和状态显示
        self.download_model_btn = tk.Button(model_ops_frame, text="模型下载", width=10, font=("Arial", 10),
                                            command=self.download_model, bg='#d9d9d9',
                                            highlightthickness=0, bd=0, relief='flat',
                                            highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.download_model_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 模型下载状态显示
        self.download_status_label = tk.Label(model_ops_frame, text="未下载", font=("Arial", 10),
                                              bg='#d9d9d9', width=12, anchor='w')
        self.download_status_label.pack(side=tk.LEFT, padx=(0, 20))

        # 模型运行按钮和时间显示
        self.run_button = tk.Button(model_ops_frame, text="模型运行", width=10, font=("Arial", 10),
                                    command=self.toggle_model_run, bg='#d9d9d9',
                                    highlightthickness=0, bd=0, relief='flat',
                                    highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        # 运行时间显示
        self.time_label = tk.Label(model_ops_frame, text="00:00:00", font=("Arial", 10),
                                   bg='#d9d9d9', width=10, anchor='center')
        self.time_label.pack(side=tk.LEFT)

        # 2. 参数变量区域
        params_vars_frame = tk.LabelFrame(main_container, text="参数变量", font=("Arial", 11, "bold"),
                                        bg='#d9d9d9', fg='#333333', bd=2, relief=tk.GROOVE)
        params_vars_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 表格标题行
        table_titles_frame = tk.Frame(params_vars_frame, bg='#d9d9d9')
        table_titles_frame.pack(fill=tk.X, pady=(10, 5), padx=10)

        # 左侧：模型参数输入标题 + 参数下发按钮
        left_title_frame = tk.Frame(table_titles_frame, bg='#d9d9d9')
        left_title_frame.pack(side=tk.LEFT, anchor='w')

        tk.Label(left_title_frame, text="模型参数输入", font=("Arial", 10, "bold"), bg='#d9d9d9').pack(side=tk.LEFT,
                                                                                                     padx=(0, 10))

        self.param_send_btn = tk.Button(left_title_frame, text="参数下发", width=10, font=("Arial", 10),
                                        command=self.send_parameters, bg='#d9d9d9',
                                        highlightthickness=0, bd=0, relief='flat',
                                        highlightbackground='#d9d9d9', highlightcolor='#d9d9d9')
        self.param_send_btn.pack(side=tk.LEFT)

        # 右侧：变量监视标题
        right_title_frame = tk.Frame(table_titles_frame, bg='#d9d9d9')
        right_title_frame.pack(side=tk.RIGHT, anchor='w')

        tk.Label(right_title_frame, text="变量监视", font=("Arial", 10, "bold"), bg='#d9d9d9').pack(side=tk.LEFT)

        # 表格容器
        tables_container = tk.Frame(params_vars_frame, bg='#d9d9d9')
        tables_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 左侧参数表格
        params_frame = tk.Frame(tables_container, bg='#d9d9d9')
        params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.setup_params_table(params_frame)

        # 右侧监视表格
        watch_frame = tk.Frame(tables_container, bg='#d9d9d9')
        watch_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.setup_watch_table(watch_frame)

        # 3. 底部：系统日志区域
        system_log_frame = tk.LabelFrame(main_container, text="系统日志", font=("Arial", 11, "bold"),
                                         bg='#d9d9d9', fg='#333333', bd=2, relief=tk.GROOVE)
        system_log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))  # 增加上边距

        # 日志文本框容器（直接放在LabelFrame中，去掉标题行）
        log_container = tk.Frame(system_log_frame, bg='#d9d9d9')
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # 增加内边距

        # 日志文本框
        log_frame = tk.Frame(log_container, bg='#d9d9d9')
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Arial", 10), height=8, bg='white')
        log_scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview, width=3)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_params_table(self, parent):
        """设置参数输入表格 - 使用Frame和Label创建真实表格"""
        # 创建带边框的表格框架
        table_frame = tk.Frame(parent, bg='black', bd=1, relief='solid')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表头
        header_frame = tk.Frame(table_frame, bg='lightgray')
        header_frame.pack(fill=tk.X)

        # 表头标签 - 使用固定宽度
        headers = ["索引", "输入参数", "参数数值"]
        # 设置字符宽度 - 增加列宽确保对齐
        widths = [10, 48, 48]  # 字符宽度

        header_labels = []
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'),
                             bg='lightgray', width=width, relief='solid', bd=1,
                             anchor=tk.CENTER)
            if i == len(headers) - 1:  # 最后一列填充剩余空间
                label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            else:
                label.pack(side=tk.LEFT, fill=tk.BOTH)
            header_labels.append(label)

        # 存储表头宽度信息
        self.param_header_widths = widths

        # 创建表格内容框架（带滚动条）
        content_frame = tk.Frame(table_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Canvas和Scrollbar用于滚动
        canvas = tk.Canvas(content_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=canvas.yview, width=3)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 存储表格行引用
        self.param_rows = []

        # 配置画布滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.params_content_frame = scrollable_frame
        self.params_canvas = canvas

        # 填充数据
        self.update_params_table()

    def setup_watch_table(self, parent):
        """设置变量监视表格 - 使用Frame和Label创建真实表格"""
        # 创建带边框的表格框架
        table_frame = tk.Frame(parent, bg='black', bd=1, relief='solid')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表头
        header_frame = tk.Frame(table_frame, bg='lightgray')
        header_frame.pack(fill=tk.X)

        # 表头标签 - 使用固定宽度
        headers = ["索引", "变量名称", "参数数值", "波形"]
        # 调整列宽：增加变量名称和参数数值列宽，缩小波形列宽
        widths = [10, 50, 50, 7]  # 字符宽度 - 调整后的宽度

        header_labels = []
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'),
                             bg='lightgray', width=width, relief='solid', bd=1,
                             anchor=tk.CENTER)
            if i == len(headers) - 1:  # 最后一列填充剩余空间
                label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            else:
                label.pack(side=tk.LEFT, fill=tk.BOTH)
            header_labels.append(label)

        # 存储表头宽度信息
        self.watch_header_widths = widths

        # 创建表格内容框架（带滚动条）
        content_frame = tk.Frame(table_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Canvas和Scrollbar用于滚动
        canvas = tk.Canvas(content_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=canvas.yview, width=3)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 存储表格行引用
        self.watch_rows = []

        # 配置画布滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.watch_content_frame = scrollable_frame
        self.watch_canvas = canvas

        # 填充数据
        self.update_watch_table()

    def update_params_table(self):
        """更新参数表格"""
        # 清空现有行
        for widget in self.params_content_frame.winfo_children():
            widget.destroy()

        self.param_rows = []

        print(f"正在更新参数表格，数据条数: {len(self.input_params)}")

        # 添加数据行 - 使用与表头相同的宽度
        for idx, param in enumerate(self.input_params, 1):
            param_name = param.get("param", f"参数{idx}")
            param_value = param.get("val", "")
            print(f"添加参数: {idx}, {param_name}, {param_value}")

            # 创建一行 - 增加行高度
            row_frame = tk.Frame(self.params_content_frame, bg='white')
            row_frame.pack(fill=tk.X)

            # 索引列 - 使用表头相同的宽度，增加行高度
            index_label = tk.Label(row_frame, text=str(idx), font=('Arial', 10),
                                   bg='white', width=self.param_header_widths[0],
                                   height=2, relief='solid', bd=1, anchor=tk.CENTER)
            index_label.pack(side=tk.LEFT, fill=tk.BOTH)

            # 参数名列 - 使用表头相同的宽度，增加行高度
            name_label = tk.Label(row_frame, text=param_name, font=('Arial', 10),
                                  bg='white', width=self.param_header_widths[1],
                                  height=2, relief='solid', bd=1, anchor=tk.CENTER)
            name_label.pack(side=tk.LEFT, fill=tk.BOTH)

            # 参数值列 - 使用表头相同的宽度，增加行高度，最后一列填充剩余空间
            value_label = tk.Label(row_frame, text=param_value, font=('Arial', 10),
                                   bg='white', width=self.param_header_widths[2],
                                   height=2, relief='solid', bd=1, anchor=tk.CENTER, cursor="hand2")
            value_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 绑定双击编辑事件
            value_label.bind("<Double-1>",
                             lambda e, idx=idx - 1, label=value_label:
                             self.edit_param_value(idx, label))

            # 存储行引用
            self.param_rows.append({
                'frame': row_frame,
                'index': index_label,
                'name': name_label,
                'value': value_label
            })

        # 更新滚动区域
        self.params_content_frame.update_idletasks()
        self.params_canvas.configure(scrollregion=self.params_canvas.bbox("all"))

    def update_watch_table(self):
        """更新监视变量表格"""
        # 清空现有行
        for widget in self.watch_content_frame.winfo_children():
            widget.destroy()

        self.watch_rows = []

        print(f"正在更新监视表格，数据条数: {len(self.watch_variables)}")

        # 添加数据行 - 使用与表头相同的宽度
        for idx, var in enumerate(self.watch_variables, 1):
            var_name = var.get("variable", f"变量{idx}")
            var_value = var.get("val", "")
            print(f"添加变量: {idx}, {var_name}, {var_value}")

            # 创建一行 - 增加行高度
            row_frame = tk.Frame(self.watch_content_frame, bg='white')
            row_frame.pack(fill=tk.X)

            # 索引列 - 使用表头相同的宽度，增加行高度
            index_label = tk.Label(row_frame, text=str(idx), font=('Arial', 10),
                                   bg='white', width=self.watch_header_widths[0],
                                   height=2, relief='solid', bd=1, anchor=tk.CENTER)
            index_label.pack(side=tk.LEFT, fill=tk.BOTH)

            # 变量名列 - 使用表头相同的宽度，增加行高度
            name_label = tk.Label(row_frame, text=var_name, font=('Arial', 10),
                                  bg='white', width=self.watch_header_widths[1],
                                  height=2, relief='solid', bd=1, anchor=tk.CENTER)
            name_label.pack(side=tk.LEFT, fill=tk.BOTH)

            # 变量值列 - 使用表头相同的宽度，增加行高度
            value_label = tk.Label(row_frame, text=var_value, font=('Arial', 10),
                                   bg='white', width=self.watch_header_widths[2],
                                   height=2, relief='solid', bd=1, anchor=tk.CENTER)
            value_label.pack(side=tk.LEFT, fill=tk.BOTH)

            # 波形按钮列 - 使用表头相同的宽度，增加行高度
            wave_button = tk.Label(row_frame, text="＿/￣", font=('Arial', 8),
                                   bg='lightblue', width=self.watch_header_widths[3],
                                   height=2, relief='raised', bd=1, anchor=tk.CENTER, cursor="hand2")
            wave_button.pack(side=tk.LEFT, fill=tk.BOTH)

            # 绑定波形按钮点击事件
            wave_button.bind("<Button-1>",
                             lambda e, name=var_name: self.on_waveform_click_new(name))

            # 存储行引用
            self.watch_rows.append({
                'frame': row_frame,
                'index': index_label,
                'name': name_label,
                'value': value_label,
                'wave': wave_button
            })

        # 更新滚动区域
        self.watch_content_frame.update_idletasks()
        self.watch_canvas.configure(scrollregion=self.watch_canvas.bbox("all"))

    def edit_param_value(self, idx, label):
        """编辑参数值"""
        current_value = label.cget("text")

        # 创建编辑窗口
        edit_win = tk.Toplevel(self.root)
        edit_win.title("编辑参数值")
        edit_win.geometry("300x100")
        edit_win.transient(self.root)
        edit_win.grab_set()

        tk.Label(edit_win, text="输入新值:").pack(pady=5)

        entry = tk.Entry(edit_win, width=30)
        entry.insert(0, current_value)
        entry.pack(pady=5)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def save_edit():
            new_value = entry.get()
            label.config(text=new_value)

            # 更新内存中的数据
            if 0 <= idx < len(self.input_params):
                self.input_params[idx]["val"] = new_value

            self.add_log(f"修改参数值为: {new_value}")
            edit_win.destroy()

        tk.Button(edit_win, text="确定", command=save_edit).pack(pady=5)
        entry.bind("<Return>", lambda e: save_edit())

    def on_waveform_click_new(self, variable_name):
        """波形按钮点击事件"""
        self.add_log(f"点击了变量 '{variable_name}' 的波形按钮")
        messagebox.showinfo("波形显示", f"显示变量 {variable_name} 的波形")

    def toggle_connection(self):
        """切换连接状态"""
        target = self.target_entry.get()
        if not self.is_connected:
            # 连接操作
            self.connect_button.config(text="连接中...", state="disabled")

            def connect_thread():
                # 创建TCPClient对象
                self.data_tcpclient = TCPClient(target, 9000, timeout=5.0)
                self.cmd_tcpclient = TCPClient(target, 9001, timeout=5.0)
                # 同时连接两个客户端
                data_connected = self.data_tcpclient.connect()
                cmd_connected = self.cmd_tcpclient.connect()
                # 更新UI
                self.root.after(0, self._update_connection_status, target, data_connected, cmd_connected)
            threading.Thread(target=connect_thread, daemon=True).start()
        else:
            # 断开连接操作
            self._disconnect_connections()
            self.is_connected = False
            self.connect_button.config(text="连接", bg="SystemButtonFace")
            self.add_log(f"已断开与目标机 {target} 的连接")

    def _update_connection_status(self, target, data_connected, cmd_connected):
        """更新连接状态"""
        if data_connected and cmd_connected:
            self.is_connected = True
            self.connect_button.config(text="断开", bg="lightcoral", state="normal")
            self.add_log(f"数据链路(9000)连接成功 - 目标机: {target}")
            self.add_log(f"控制链路(9001)连接成功 - 目标机: {target}")
            self.add_log(f"已连接到目标机: {target}")
        else:
            self.is_connected = False
            self.connect_button.config(text="连接", bg="SystemButtonFace", state="normal")

            if not data_connected and not cmd_connected:
                self.add_log(f"连接失败: 数据链路(9000)和控制链路(9001)都无法连接到目标机 {target}")
            elif not data_connected:
                self.add_log(f"连接失败: 数据链路(9000)无法连接到目标机 {target}")
                self.add_log(f"控制链路(9001)连接成功 - 目标机: {target}")
                if self.cmd_tcpclient:
                    self.cmd_tcpclient.disconnect()
            else:
                self.add_log(f"数据链路(9000)连接成功 - 目标机: {target}")
                self.add_log(f"连接失败: 控制链路(9001)无法连接到目标机 {target}")
                if self.data_tcpclient:
                    self.data_tcpclient.disconnect()

            self.data_tcpclient = None
            self.cmd_tcpclient = None

    def _disconnect_connections(self):
        """断开所有连接"""
        if self.data_tcpclient:
            self.data_tcpclient.disconnect()
            self.data_tcpclient = None
        if self.cmd_tcpclient:
            self.cmd_tcpclient.disconnect()
            self.cmd_tcpclient = None

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

        def simulate_download():
            time.sleep(2)
            self.root.after(0, lambda: self.download_status_label.config(text="已完成"))
            self.root.after(0, lambda: self.add_log("模型下载完成"))

        threading.Thread(target=simulate_download, daemon=True).start()

    def send_parameters(self):
        """下发参数"""
        self.add_log("参数下发中...")

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
        self.log_text.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = HardwareSimulator(root)
    root.mainloop()