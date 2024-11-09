import numpy as np # type: ignore
from typing import Dict, List, Tuple
import tensorflow as tf # type: ignore
from collections import deque
import random

class ReinforcementLearner:
    def __init__(self):
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # 折扣因子
        self.epsilon = 1.0   # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self) -> tf.keras.Model:
        """构建DQN模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, input_dim=4, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(2, activation='linear')
        ])
        
        model.compile(
            loss='mse',
            optimizer=tf.keras.optimizers.Adam(lr=self.learning_rate)
        )
        
        return model
        
    def remember(self, state: np.ndarray, action: int, reward: float, 
                next_state: np.ndarray, done: bool):
        """记忆经验"""
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state: np.ndarray) -> int:
        """选择动作"""
        if np.random.rand() <= self.epsilon:
            return random.randrange(2)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])
        
    def replay(self, batch_size: int):
        """经验回放"""
        if len(self.memory) < batch_size:
            return
            
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay 