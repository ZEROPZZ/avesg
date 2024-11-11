import tensorflow as tf # type: ignore
import numpy as np # type: ignore
from typing import Optional, Dict, List, Tuple

class AutonomousLearner:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._build_model()
        self.loss_fn = tf.compat.v1.losses.sparse_softmax_cross_entropy
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        
    def _build_model(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(4, activation='softmax')
        ])
        
    def predict_action(self, state: np.ndarray) -> int:
        if state.ndim == 1:
            state = state[np.newaxis, ...]
        logits = self.model(state)
        return np.argmax(logits.numpy())
        
    def train_on_batch(self, experiences: List[Tuple]):
        """批量训练"""
        states = np.array([exp[0] for exp in experiences])
        actions = np.array([exp[1] for exp in experiences])
        rewards = np.array([exp[2] for exp in experiences])
        next_states = np.array([exp[3] for exp in experiences])
        
        with tf.GradientTape() as tape:
            logits = self.model(states)
            # 计算每个样本的损失
            losses = self.loss_fn(actions, logits)
            # 应用奖励权重并计算平均损失
            weighted_losses = losses * tf.cast(rewards, tf.float32)
            loss = tf.reduce_mean(weighted_losses)  # 添加这行，计算平均损失
            
        # 计算梯度并应用
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
        
        # 返回标量损失值
        return float(loss.numpy())  # 现在 loss 是一个标量