from torch import nn
import torch
from river.anomaly.base import AnomalyDetector
from deep_river import anomaly

from .save import deep_river_model_to_bytes, deep_river_model_from_bytes

class LinearAutoencoder(nn.Module):
    def __init__(self, n_features, latent_dim=1):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_features, latent_dim),
            nn.LeakyReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, n_features),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)
    

class LSTMDecoder(nn.Module):
    def __init__(
        self,
        input_size,
        hidden_size,
        sequence_length=None,
        predict_backward=True,
        num_layers=1,
    ):
        super().__init__()

        self.cell = nn.LSTMCell(input_size, hidden_size)
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.predict_backward = predict_backward
        self.sequence_length = sequence_length
        self.num_layers = num_layers
        self.lstm = (
            None
            if num_layers <= 1
            else nn.LSTM(
                input_size=hidden_size,
                hidden_size=hidden_size,
                num_layers=num_layers - 1,
            )
        )
        self.linear = (
            None
            if input_size == hidden_size
            else nn.Linear(hidden_size, input_size)
        )

    def forward(self, h, sequence_length=None):
        """Computes the forward pass.

        Parameters
        ----------
        x:
            Input of shape (batch_size, input_size)

        Returns
        -------
        Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]
            Decoder outputs (output, (h, c)) where output has the shape (sequence_length, batch_size, input_size).
        """

        c = None
        if sequence_length is None:
            sequence_length = self.sequence_length
        x_hat = torch.empty(sequence_length, h.shape[0], self.hidden_size)
        for t in range(sequence_length):
            if t == 0:
                h, c = self.cell(h)
            else:
                input = h if self.linear is None else self.linear(h)
                h, c = self.cell(input, (h, c))
            t_predicted = -t if self.predict_backward else t
            x_hat[t_predicted] = h

        if self.lstm is not None:
            x_hat = self.lstm(x_hat)

        return x_hat, (h, c)


class LSTMAutoencoderSutskever(nn.Module):
    def __init__(self, n_features, hidden_size=30, n_layers=1):
        super().__init__()
        self.n_features = n_features
        self.hidden_size = hidden_size
        self.n_layers = n_layers
        self.encoder = nn.LSTM(
            input_size=n_features, hidden_size=hidden_size, num_layers=n_layers
        )
        self.decoder = LSTMDecoder(
            input_size=hidden_size,
            hidden_size=n_features,
            predict_backward=True,
            num_layers=n_layers,
        )

    def forward(self, x):
        #print(f"x.shape = {x.shape}")
        _, (h, _) = self.encoder(x)
        # print(f"h.shape = {h.shape}")
        x_hat, _ = self.decoder(h[-1], x.shape[0])
        #print(f"x_hat.shape = {x_hat.shape}")
        return x_hat


class Autoencoder(AnomalyDetector):
    def __init__(self, 
                 n_features : int, 
                 seed : int = 42,
                 hidden_size : int = 4,
                 lr : float = 0.5,
                 warmup_period : int = 0,
                 ):
        self.__ae = anomaly.Autoencoder(
            module=LinearAutoencoder(n_features=n_features,
                                     latent_dim=hidden_size),
            optimizer_fn="adam",
            lr=lr,
            seed=seed,
        )
        self.__learnt_observations = 0
        self.warmup_period = warmup_period

    @property
    def _supervised(self):
        return False
    
    def learn_one(self, 
                  x : dict,
                  y = None, 
                  **kwargs):
        self.__ae.learn_one(x)
        if self.__learnt_observations < self.warmup_period:
            self.__learnt_observations += 1

    def score_one(self, x : dict) -> float:
        if self.__learnt_observations >= self.warmup_period:
            return self.__ae.score_one(x)
        
        return 0
    
    def __getstate__(self) -> dict:
        ae_bytes = deep_river_model_to_bytes(self.__ae)

        state = {
            "__learnt_observations": self.__learnt_observations,
            "warmup_period": self.warmup_period,
            "__ae_bytes": ae_bytes,
        }

        return state
    
    def __setstate__(self, state: dict):
        self.__learnt_observations = state["__learnt_observations"]
        self.warmup_period = state["warmup_period"]

        ae_bytes = state["__ae_bytes"]
        self.__ae = deep_river_model_from_bytes(ae_bytes, anomaly.Autoencoder)
        

    
class LSTMAutoencoder:
    def __init__(self, 
                 window_size : int, 
                 lr : float = 0.05, 
                 seed : int = 42,
                 hidden_size : int = 10,
                 warmup_period: int = 0
                 ):
        self.__rae = anomaly.RollingAutoencoder(
            module=LSTMAutoencoderSutskever(1, hidden_size=hidden_size),
            lr=lr,
            optimizer_fn="adam",
            seed=seed,
            window_size=window_size,
        )
        self.__learnt_observations = 0
        self.warmup_period = warmup_period

    @property
    def _supervised(self):
        return False
    
    def learn_one(self, 
                  x : dict,
                  y = None, 
                  **kwargs):
        self.__rae.learn_one(x)
        if self.__learnt_observations < self.warmup_period:
            self.__learnt_observations += 1

    def score_one(self, x : dict) -> float:
        if self.__learnt_observations >= self.warmup_period:
            return self.__rae.score_one(x)
        
        return 0