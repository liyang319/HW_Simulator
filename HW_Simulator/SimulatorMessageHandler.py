import logging
import json
from TCPMessageHandler import TCPMessageHandler


class CtrlMessageHandler(TCPMessageHandler):
    """控制链路消息处理器 - 处理系统控制消息"""

    def __init__(self, host, port=9001, message_callback=None):
        super().__init__(host, port, "CtrlHandler")
        self.message_callback = message_callback

    def _process_received_data(self, data):
        """处理控制链路接收到的数据 - 系统控制消息"""
        try:
            message = data.decode('utf-8') if isinstance(data, bytes) else str(data)
            self.logger.info(f"控制链路收到系统消息: {message}")

            # 如果有回调函数，传递系统消息
            if self.message_callback:
                message_info = {
                    'type': 'system_message',
                    'message': message,
                    'timestamp': self._get_timestamp(),
                    'source': 'control_link'
                }
                self.message_callback(message_info)

            # 根据消息内容执行具体控制逻辑
            if "HEARTBEAT" in message:
                self._handle_heartbeat()
            elif "CONNECTED" in message:
                self._handle_connected()
            elif "ERROR" in message:
                self._handle_error(message)
            elif "MODEL_START" in message:
                self._handle_model_start()
            elif "MODEL_STOP" in message:
                self._handle_model_stop()
            elif "PARAM_UPDATE" in message:
                self._handle_param_update(message)
            else:
                self._handle_unknown_message(message)

        except Exception as e:
            self.logger.error(f"处理控制链路数据失败: {e}")
            if self.message_callback:
                self.message_callback({
                    'type': 'error',
                    'message': f"控制链路处理错误: {e}",
                    'timestamp': self._get_timestamp(),
                    'source': 'control_link'
                })

    def _handle_heartbeat(self):
        """处理心跳消息"""
        self.logger.debug("收到心跳消息，连接正常")

    def _handle_connected(self):
        """处理连接成功消息"""
        self.logger.info("服务器确认连接成功")

    def _handle_error(self, message):
        """处理错误消息"""
        self.logger.error(f"服务器报告错误: {message}")

    def _handle_model_start(self):
        """处理模型启动指令"""
        self.logger.info("执行模型启动处理")

    def _handle_model_stop(self):
        """处理模型停止指令"""
        self.logger.info("执行模型停止处理")

    def _handle_param_update(self, message):
        """处理参数更新确认"""
        self.logger.info(f"参数更新确认: {message}")

    def _handle_unknown_message(self, message):
        """处理未知控制消息"""
        self.logger.warning(f"收到未知控制消息: {message}")

    def send_heartbeat(self):
        """发送心跳消息"""
        heartbeat_msg = "HEARTBEAT from client"
        self.send_message(heartbeat_msg)

    def send_model_control(self, command):
        """发送模型控制命令"""
        control_msg = f"MODEL_{command.upper()}"
        self.send_message(control_msg)

    def _get_timestamp(self):
        """获取时间戳"""
        import time
        return time.strftime("%H:%M:%S", time.localtime())


class StatusMessageHandler(TCPMessageHandler):
    """状态链路消息处理器 - 专门处理变量数据"""

    def __init__(self, host, port=9000, variable_callback=None):
        super().__init__(host, port, "StatusHandler")
        self.variable_callback = variable_callback

    def _process_received_data(self, data):
        """处理状态链路接收到的数据 - 专门处理变量数据"""
        try:
            message = data.decode('utf-8') if isinstance(data, bytes) else str(data)
            self.logger.info(f"状态链路收到数据: {message[:100]}...")

            # 解析变量数据
            variable_data = self._parse_variable_data(message)
            if variable_data:
                # 通过回调函数传递变量数据
                if self.variable_callback:
                    self.variable_callback(variable_data)
            else:
                # 如果不是变量数据，记录到日志
                self.logger.warning(f"无法解析为变量数据: {message[:50]}...")

        except Exception as e:
            self.logger.error(f"处理状态链路数据失败: {e}")
            if self.variable_callback:
                self.variable_callback({
                    'type': 'error',
                    'message': f"状态链路处理错误: {e}",
                    'timestamp': self._get_timestamp(),
                    'source': 'status_link'
                })

    def _parse_variable_data(self, message):
        """
        解析变量数据
        期望的消息格式：JSON或键值对
        """
        try:
            # 尝试解析为JSON
            if message.strip().startswith('{') and message.strip().endswith('}'):
                data = json.loads(message)
                if isinstance(data, dict):
                    # 验证是否为变量数据（包含数值型数据）
                    if self._is_variable_data(data):
                        return data

            # 尝试解析为键值对
            elif '=' in message and ';' in message:
                data = {}
                pairs = message.split(';')
                for pair in pairs:
                    if '=' in pair and pair.strip():
                        key_value = pair.split('=', 1)
                        if len(key_value) == 2:
                            key, value = key_value
                            key = key.strip()
                            value = value.strip()
                            if key:  # 确保key不为空
                                # 尝试转换为数值
                                try:
                                    if '.' in value:
                                        value = float(value)
                                    else:
                                        value = int(value)
                                except ValueError:
                                    pass  # 保持为字符串
                                data[key] = value
                # 只有包含有效数据时才返回
                return data if data and self._is_variable_data(data) else None

        except Exception as e:
            self.logger.debug(f"解析变量数据失败: {e}")

        return None

    def _is_variable_data(self, data):
        """判断是否为有效的变量数据"""
        if not isinstance(data, dict):
            return False

        # 检查是否包含数值型数据（温度、压力、转速等）
        numeric_count = 0
        for value in data.values():
            if isinstance(value, (int, float)):
                numeric_count += 1

        # 如果包含数值类型数据，认为是变量数据
        return numeric_count > 0

    def _get_timestamp(self):
        """获取时间戳"""
        import time
        return time.strftime("%H:%M:%S", time.localtime())