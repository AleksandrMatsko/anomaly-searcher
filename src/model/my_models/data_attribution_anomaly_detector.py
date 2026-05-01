from typing import Any, Callable, Union
from collections import deque

import io
import warnings

import numpy as np
import pandas as pd
import torch
from river.anomaly.base import AnomalyDetector
from torch import nn

from deep_river.base import DeepEstimator

class LinearWrapper(nn.Module):
    def __init__(self, to_wrap : nn.Module, out_features : int):
        super().__init__()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            self.linear = nn.LazyLinear(
                out_features=out_features
            )
        self.wrapped = to_wrap

    def forward(self, x):
        self.w_output = self.wrapped(x)
        # print(f"w_output shape: {self.w_output.shape}")
        l_out = self.linear(self.w_output)
        # print(f"linear_output shape: {l_out.shape}")
        return l_out

class DataAttributionAnomalyDetector(DeepEstimator, AnomalyDetector):
    """
    Attributes
    ----------
    is_feature_incremental : bool
        Indicates whether the model is designed to increment features dynamically.
    module : torch.nn.Module
        The PyTorch model representing the autoencoder architecture.
    out_features : int
        Amount of features must be returned by module after call.
    loss_fn : Union[str, Callable]
        Specifies the loss function to compute the reconstruction error.
    optimizer_fn : Union[str, Callable]
        Specifies the optimizer to be used for training the autoencoder.
    lr : float
        The learning rate for optimization.
    device : str
        The device on which the model is loaded and trained (e.g., "cpu",
        "cuda").
    seed : int
        Random seed for ensuring reproducibility.
    """

    def __init__(
        self,
        module: torch.nn.Module,
        out_features: int,
        #loss_fn: Union[str, Callable] = "mse",
        optimizer_fn: Union[str, Callable] = "sgd",
        checkpoints_count: int = 5,
        step_between_checkpoints: int = 1,
        warmup_period : int = 0,
        lr: float = 1e-3,
        device: str = "cpu",
        seed: int = 42,
        **kwargs,
    ):
        self.__lwrapper = LinearWrapper(
            to_wrap=module, 
            out_features=out_features,
            )
        super().__init__(
            module=self.__lwrapper,
            loss_fn="mse",
            optimizer_fn=optimizer_fn,
            lr=lr,
            is_feature_incremental=False,
            device=device,
            seed=seed,
            **kwargs,
        )
        # print(f"self.module: {self.module}")
        self.is_feature_incremental = False
        self.__checkpoints = deque([], maxlen=checkpoints_count)
        self.__cur_step_state = 0
        self.step_between_checkpoints = step_between_checkpoints
        self.warmup_period = warmup_period
        self.__warmup_state = 0
    
    @property
    def _supervised(self):
        return False

    def learn_one(self, x: dict, y: Any = None, **kwargs) -> None:
        """
        Performs one step of training with a single example.

        Parameters
        ----------
        x
            Input example.

        **kwargs
        """
        self._update_observed_features(x)
        x_t = self._dict2tensor(x)
        # print(f"learn_one x_t.shape = {x_t.shape}")
        # sometimes x_t may be padded
        # if x_t.shape[1] > 1:
        #     x_t = x_t[:, 0].reshape((1, 1))
        # print(f"learn_one (after reshape) x_t.shape = {x_t.shape}")

        self._learn(x_t)
        if self.__cur_step_state == self.step_between_checkpoints:
            buf = io.BytesIO()
            torch.save(self.module, buf)
            self.__checkpoints.append(buf.getvalue())
            self.__cur_step_state = 0
        else:
            self.__cur_step_state += 1
        self.__warmup_state = self.__warmup_state + 1 if self.__warmup_state < self.warmup_period else self.warmup_period 

    def score_one(self, x: dict) -> float:
        """
        Returns an anomaly score for the provided example in the form of
        the autoencoder's reconstruction error.

        Parameters
        ----------
        x
            Input example.

        Returns
        -------
        float
            Anomaly score for the given example. Larger values indicate
            more anomalous examples.

        """

        #print(f"x = {x}")
        self._update_observed_features(x)
        #print(f"observed features: {self.observed_features}")
        x_t = self._dict2tensor(x)
        #print(f"x_t = {x_t}")
        # sometimes x_t may be padded
        # if x_t.shape[1] > 1:
        #     x_t = x_t[:, 0].reshape((1, 1))
        #print(f"(after reshape) x_t = {x_t}")

        if self.__warmup_state < self.warmup_period:
            return 0

        # self.module.eval()
        # with torch.inference_mode():
        #     x_pred = self.module(x_t)
        # loss = self.loss_func(x_pred, x_t)

        # gradients = torch.autograd.grad(
        #     outputs=loss,
        #     inputs=self.__lwrapper.w_output,
        #     retain_graph=True,
        #     create_graph=True,
        # )
        checkpoint_models = [torch.load(io.BytesIO(chp)) for chp in list(self.__checkpoints)]
        if len(checkpoint_models) == 0:
            return 0
        
        #print(f"checkpoint_models[0]: {checkpoint_models[0]}")

        with torch.inference_mode():
            # calculate TracIn: https://fabrice.popineau.net/ox-hugo/files/20183/Thimonier%20et%20al.%20-%202022%20-%20TracInAD%20Measuring%20Influence%20for%20Anomaly%20Detectio.pdf

            # applies only to mse, because
            # d(y_pred - y_true)**2/dw = 2 * (y_pred - y_true) * d(y_pred)/dw
            # for linear layer: d(y_pred)/dw = x  

            # so TracIn would be:
            # lr * sum[for each checkpoint]( (d(y_pred - y_true)**2/dw) ** 2 )
            def calc(m : nn.Module):
                #print(f"calc model: {m}")
                m.eval()
                x_pred = m(x_t)
                #print(f"x_pred = {x_pred}")
                doubled_diff = 2 * (x_pred - x_t)
                #print(f"doubled_diff = {doubled_diff}")
                squared_diff = doubled_diff ** 2
                #print(f"squared_diff = {squared_diff}")
                return squared_diff

            # to_sum = list(map(lambda m: (2 * (m(x_t) - x_t))**2, checkpoint_models))
            to_sum = list(map(calc, checkpoint_models))
            #print(f"to_sum[0]: {to_sum[0]}")

            influence = self.lr * (x_t**2) * sum(to_sum)
            influence = influence / len(checkpoint_models)

        return torch.sum(influence).item()

    # def learn_many(self, X: pd.DataFrame) -> None:
    #     """
    #     Performs one step of training with a batch of examples.

    #     Parameters
    #     ----------
    #     X
    #         Input batch of examples.
    #     """

    #     self._update_observed_features(X)
    #     X_t = self._df2tensor(X)
    #     self._learn(X_t)

    # def score_many(self, X: pd.DataFrame) -> np.ndarray:
    #     """
    #     Returns an anomaly score for the provided batch of examples in
    #     the form of the autoencoder's reconstruction error.

    #     Parameters
    #     ----------
    #     x
    #         Input batch of examples.

    #     Returns
    #     -------
    #     float
    #         Anomaly scores for the given batch of examples. Larger values
    #         indicate more anomalous examples.
    #     """
    #     self._update_observed_features(X)
    #     x_t = self._df2tensor(X)

    #     self.module.eval()
    #     with torch.inference_mode():
    #         x_pred = self.module(x_t)
    #     loss = torch.mean(
    #         self.loss_func(x_pred, x_t, reduction="none"),
    #         dim=list(range(1, x_t.dim())),
    #     )
    #     score = loss.cpu().detach().numpy()
    #     return score

class LSTMModule(nn.Module):
    def __init__(self, 
                 input_size: int,
                 hidden_size: int,
                 num_layers: int = 1,
                 ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
        )
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # print(f"lstm_out shape: {lstm_out.shape}")
        return lstm_out.view(len(x), -1)
    
class LSTMDataAttributionAnomalyDetector(AnomalyDetector):
    def __init__(self,
                 n_features : int,
                 hidden_size : int = 2,
                 num_layers : int = 1,
                 checkpoints_count : int = 5,
                 step_between_checkpoints=0,
                 warmup_period=0,
                 lr : float = 0.001,
                 ):
        self.__ad = DataAttributionAnomalyDetector(
            module=LSTMModule(
                input_size=n_features,
                hidden_size=hidden_size,
                num_layers=num_layers,
            ),
            out_features=1,
            checkpoints_count=checkpoints_count,
            step_between_checkpoints=step_between_checkpoints,
            warmup_period=warmup_period,
            optimizer_fn="adam",
            lr=lr,
        )
        
    @property
    def _supervised(self):
        return False
    
    def learn_one(self, 
                  x : dict,
                  y = None, 
                  **kwargs):
        self.__ad.learn_one(x)

    def score_one(self, x : dict) -> float:
        return self.__ad.score_one(x)

    
