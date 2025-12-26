import tensorflow as tf
import keras
from collections import deque

class Evaluator:
    def __init__(self, state_size=67, gamma=0.95, epsilon=1.0, epsilon_min=0.05,
                 epsilon_decay=0.99, learning_rate=0.001, buffer_size=10000):
        self.state_size = state_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.replay_buffer = deque(maxlen=buffer_size)
        
        self._build_model()
    
    def _build_model(self):
        self.model = keras.Sequential([
            keras.layers.Input(shape=(self.state_size,0), dtype=("int32")),
        ])
        for _ in range(8):
            self.model.add(keras.layers.Dense(128))
            self.model.add(keras.layers.LeakyReLU(alpha=0.01))
            self.model.add(keras.layers.BatchNormalization())
            self.model.add(keras.layers.Dropout(0.2))
        self.model.add(keras.layers.Dense(1))

        self.model.compile(optimizer="adam", loss="mse", metrics=["mse"])

eva = Evaluator()
