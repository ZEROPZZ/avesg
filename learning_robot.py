from typing import Optional, Dict, Any, Tuple, List
import numpy as np # type: ignore
import time
import tensorflow as tf  # type: ignore # 添加这行
from models.autonomous_learning import AutonomousLearner

class Memory:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.memory: List[Tuple] = []
        self.position = 0
        
    def store(self, experience: Tuple):
        """存储经验 (state, action, reward, next_state)"""
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.position] = experience
        self.position = (self.position + 1) % self.capacity
        
    def sample(self, batch_size: int) -> List[Tuple]:
        """随机采样经验"""
        if len(self.memory) >= batch_size:
            indices = np.random.choice(len(self.memory), batch_size, replace=False)
            return [self.memory[i] for i in indices]
        return self.memory

class AutonomousLearningRobot:
    def __init__(self, state_space: int = 10, action_space: int = 4):
        self.learner = AutonomousLearner()
        self.state_space = state_space
        self.action_space = action_space
        self.current_state = np.zeros(state_space)
        self.memory = Memory()
        self.learning_history = []
        self.epsilon = 0.1  # 探索率
        
    def choose_action(self, state: np.ndarray) -> int:
        """
        根据当前状态选择动作
        使用 epsilon-greedy 策略
        """
        if np.random.random() < self.epsilon:
            # 探索：随机选择动作
            action = np.random.randint(0, self.action_space)
        else:
            # 利用：选择最优动作
            action = self.learner.predict_action(state)
            
        # 更新当前状态
        self.current_state = state
        return action
        
    def learn(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """学习过程"""
        if not isinstance(state, np.ndarray):
            state = np.array(state)
        if not isinstance(next_state, np.ndarray):
            next_state = np.array(next_state)
        if state.shape != (self.state_space,):
            raise ValueError(f"状态维度不匹配: 期望 {self.state_space}, 实际 {state.shape}")
        if not 0 <= action < self.action_space:
            raise ValueError(f"动作值出范围: {action}")
            
        self.memory.store((state, action, reward, next_state))
        self.current_state = next_state
        self.learning_history.append({
            'state': state.tolist(),
            'action': action,
            'reward': reward,
            'next_state': next_state.tolist(),
            'timestamp': time.time()
        })
        
        # 从记忆中学习
        if len(self.memory.memory) >= 32:  # 批量大小为32
            experiences = self.memory.sample(32)
            self.learner.train_on_batch(experiences)
    
    def get_learning_statistics(self) -> Dict:
        """获取学习统计信息"""
        if not self.learning_history:
            return {"error": "No learning history available"}
            
        recent_rewards = [h['reward'] for h in self.learning_history[-100:]]
        return {
            "average_reward": np.mean(recent_rewards),
            "total_experiences": len(self.memory.memory),
            "exploration_rate": self.epsilon
        }
    
    def save_state(self, filepath: str):
        """保存模型状态"""
        self.learner.save_model(filepath)