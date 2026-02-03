"""
信号配置信息类
用于存储和管理信号配置的相关属性
"""

from typing import Optional, List, Any
import json
from dataclasses import dataclass, asdict, field


@dataclass
class SignalConfigInfo:
    """信号配置信息类"""

    # 基本配置
    node_ip: str = ""  # 节点IP地址
    signal_id: str = ""  # 信号ID，格式如: 01_01_01_PO_01

    # 信号参数配置
    signal_value_lower: float = 0.0  # 信号值下限
    signal_value_upper: float = 100.0  # 信号值上限
    dimension: str = ""  # 量纲
    signal_source: str = ""  # 信号源
    unit: str = ""  # 单位
    calibration_value: float = 0.0  # 校准值

    # 信号值配置
    signal_value1: float = 0.0  # 信号值1
    signal_value2: float = 0.0  # 信号值2
    signal_value3: float = 0.0  # 信号值3

    def __post_init__(self):
        """初始化后处理，确保数据有效性"""
        # 确保信号值下限小于等于上限
        if self.signal_value_lower > self.signal_value_upper:
            self.signal_value_lower, self.signal_value_upper = self.signal_value_upper, self.signal_value_lower

    def to_dict(self) -> dict:
        """将对象转换为字典"""
        return asdict(self)

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'SignalConfigInfo':
        """从字典创建对象"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'SignalConfigInfo':
        """从JSON字符串创建对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> List[str]:
        """验证配置的有效性，返回错误信息列表"""
        errors = []

        # 验证IP地址格式
        if not self._is_valid_ip(self.node_ip):
            errors.append(f"无效的IP地址: {self.node_ip}")

        # 验证信号ID格式
        if not self.signal_id or '_' not in self.signal_id:
            errors.append(f"无效的信号ID格式: {self.signal_id}")

        # 验证数值范围
        if self.signal_value_lower >= self.signal_value_upper:
            errors.append("信号值下限必须小于信号值上限")

        # 验证校准值在合理范围内
        if self.calibration_value < -1000 or self.calibration_value > 1000:
            errors.append(f"校准值超出合理范围: {self.calibration_value}")

        return errors

    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        if not ip:
            return False

        parts = ip.split('.')
        if len(parts) != 4:
            return False

        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False

        return True

    def get_signal_values(self) -> List[float]:
        """获取所有信号值"""
        return [self.signal_value1, self.signal_value2, self.signal_value3]

    def update_signal_values(self, values: List[float]) -> None:
        """更新信号值"""
        if len(values) >= 1:
            self.signal_value1 = values[0]
        if len(values) >= 2:
            self.signal_value2 = values[1]
        if len(values) >= 3:
            self.signal_value3 = values[2]

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        return f"信号ID: {self.signal_id}, IP: {self.node_ip}, 范围: [{self.signal_value_lower}, {self.signal_value_upper}], 单位: {self.unit}"

    def clone(self) -> 'SignalConfigInfo':
        """创建对象的副本"""
        return SignalConfigInfo(
            node_ip=self.node_ip,
            signal_id=self.signal_id,
            signal_value_lower=self.signal_value_lower,
            signal_value_upper=self.signal_value_upper,
            dimension=self.dimension,
            signal_source=self.signal_source,
            unit=self.unit,
            calibration_value=self.calibration_value,
            signal_value1=self.signal_value1,
            signal_value2=self.signal_value2,
            signal_value3=self.signal_value3
        )