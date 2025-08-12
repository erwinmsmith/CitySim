"""
动态日志记录器 - 实时保存模拟过程
"""
import json
import os
import datetime
import logging

logger = logging.getLogger(__name__)

class SimulationLogger:
    """实时模拟日志记录器"""
    
    def __init__(self, city: str, filename: str = None):
        """
        初始化日志记录器
        
        Args:
            city: 城市名称
            filename: 自定义文件名
        """
        self.city = city
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if filename:
            self.log_filepath = os.path.join('output', f"{filename}.json")
        else:
            self.log_filepath = os.path.join('output', f"simulation_log_{city}_{timestamp}.json")
        
        self.log_data = {
            "city": city,
            "timestamp": timestamp,
            "rounds": [],
            "summary": {},
            "errors": []
        }
        self._initialize_log_file()
        logger.info(f"Dynamic simulation log initialized: {self.log_filepath}")

    def _initialize_log_file(self):
        """初始化日志文件"""
        os.makedirs('output', exist_ok=True)
        with open(self.log_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)

    def log_round_start(self, round_num: int, agent_counts: dict):
        """记录轮次开始"""
        round_entry = {
            "round": round_num,
            "start_time": datetime.datetime.now().isoformat(),
            "agent_counts": agent_counts,
            "decisions": [],
            "interactions": [],
            "environment_state": {},
            "status": "in_progress"
        }
        self.log_data["rounds"].append(round_entry)
        self._save_current_state()

    def log_agent_decision(self, round_num: int, agent_type: str, agent_id: str, decision: dict, is_fallback: bool = False, error: str = None):
        """记录agent决策"""
        if round_num >= 0 and round_num < len(self.log_data["rounds"]):
            decision_entry = {
                "agent_type": agent_type,
                "agent_id": agent_id,
                "decision": decision,
                "is_fallback": is_fallback,
                "error": error,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.log_data["rounds"][round_num]["decisions"].append(decision_entry)
            self._save_current_state()

    def log_interactions(self, round_num: int, interactions: list):
        """记录交互过程"""
        if round_num >= 0 and round_num < len(self.log_data["rounds"]):
            self.log_data["rounds"][round_num]["interactions"] = interactions
            self._save_current_state()

    def log_environment_update(self, round_num: int, env_state: dict):
        """记录环境更新"""
        if round_num >= 0 and round_num < len(self.log_data["rounds"]):
            self.log_data["rounds"][round_num]["environment_state"] = env_state
            self._save_current_state()

    def log_round_complete(self, round_num: int):
        """记录轮次完成"""
        if round_num >= 0 and round_num < len(self.log_data["rounds"]):
            self.log_data["rounds"][round_num]["status"] = "completed"
            self.log_data["rounds"][round_num]["end_time"] = datetime.datetime.now().isoformat()
            self._save_current_state()

    def log_error(self, round_num: int, error_message: str, error_type: str = "general"):
        """记录错误"""
        error_entry = {
            "round": round_num,
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.log_data["errors"].append(error_entry)
        self._save_current_state()

    def log_simulation_complete(self, metrics: dict):
        """记录模拟完成"""
        self.log_data["summary"]["metrics"] = metrics
        self.log_data["summary"]["status"] = "completed"
        self.log_data["summary"]["end_time"] = datetime.datetime.now().isoformat()
        self._save_current_state()

    def interrupt_simulation(self, reason: str = "User interrupted"):
        """记录模拟中断"""
        self.log_data["summary"]["status"] = "interrupted"
        self.log_data["summary"]["interruption_reason"] = reason
        self.log_data["summary"]["end_time"] = datetime.datetime.now().isoformat()
        self._save_current_state()

    def get_current_status(self) -> dict:
        """获取当前状态"""
        last_round = self.log_data["rounds"][-1] if self.log_data["rounds"] else None
        return {
            "current_round": last_round["round"] if last_round else -1,
            "summary": f"Round {last_round['round'] if last_round else 'N/A'} - {last_round['status'] if last_round else 'Not started'}",
            "errors_count": len(self.log_data["errors"])
        }

    def _save_current_state(self):
        """保存当前状态到文件"""
        try:
            with open(self.log_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save log state: {e}")


def create_logger(city: str, filename: str = None) -> SimulationLogger:
    """创建日志记录器实例"""
    return SimulationLogger(city, filename)
