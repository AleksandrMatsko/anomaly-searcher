from typing import Any, Callable, List, Union
from collections import deque

import io

import torch
from river import anomaly
from torch import nn

from deep_river.base import RollingDeepEstimator
from deep_river.utils.tensor_conversion import deque2rolling_tensor

from .data_attribution_anomaly_detector import LinearWrapper
from .simple_deep_autoencoder import LSTMAutoencoderSutskever

class RollingDataAttributionAnomalyDetector(RollingDeepEstimator, anomaly.base.AnomalyDetector):
    """
    Parameters
    ----------
    module : torch.nn.Module
        Autoencoder (or encoder-only) style module operating on a rolling tensor.
    loss_fn : str | Callable, default='mse'
        Loss for reconstruction error measurement.
    optimizer_fn : str | Callable, default='sgd'
        Optimizer specification.
    lr : float, default=1e-3
        Learning rate.
    device : str, default='cpu'
        Torch device.
    seed : int, default=42
        Random seed.
    window_size : int, default=10
        Number of past samples retained.
    append_predict : bool, default=False
        If True, the scored sample (during prediction) is appended to the window.
    **kwargs
        Forwarded to :class:`~deep_river.base.RollingDeepEstimator`.

    Notes
    -----
    The provided module should expect input shape roughly (seq_len, batch=1, n_features)
    which is what :func:`deque2rolling_tensor` produces.
    """

    def __init__(
        self,
        module: torch.nn.Module,
        out_features : int,
        # loss_fn: Union[str, Callable] = "mse",
        optimizer_fn: Union[str, Callable] = "sgd",
        checkpoints_count: int = 5,
        step_between_checkpoints: int = 1,
        warmup_period : int = 0,
        lr: float = 1e-3,
        device: str = "cpu",
        seed: int = 42,
        window_size: int = 10,
        #append_predict: bool = False,
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
            device=device,
            seed=seed,
            window_size=window_size,
            append_predict=False,
            **kwargs,
        )

        self.is_feature_incremental = False

        self.checkpoints_count = checkpoints_count
        self.step_between_checkpoints = step_between_checkpoints
        self.__checkpoints = deque([], maxlen=checkpoints_count)
        self.__cur_step_state = 0
        self.step_between_checkpoints = step_between_checkpoints
        self.warmup_period = warmup_period
        self.__warmup_state = 0
    

    def learn_one(self, x: dict, y: Any = None, **kwargs) -> None:
        """Update model using a single sample appended to the rolling window.

        Parameters
        ----------
        x : dict
            Dictionary containing feature name-value pairs for the sample.
        y : Any, optional
            Target value (not used in autoencoder training).
        **kwargs
            Additional keyword arguments.
        """
        self._update_observed_features(x)
        self._x_window.append(list(x.values()))

        x_t = deque2rolling_tensor(self._x_window, device=self.device)
        #print(f"learn x_t shape {x_t.shape}")
        self._learn(x=x_t)
        if self.__cur_step_state == self.step_between_checkpoints:
            buf = io.BytesIO()
            torch.save(self.module, buf)
            self.__checkpoints.append(buf.getvalue())
            self.__cur_step_state = 0
        else:
            self.__cur_step_state += 1
        self.__warmup_state = self.__warmup_state + 1 if self.__warmup_state < self.warmup_period else self.warmup_period

    # def learn_many(self, X: pd.DataFrame, y=None) -> None:
    #     """Batch update; extends window with rows from X and learns if full.

    #     Parameters
    #     ----------
    #     X : pd.DataFrame
    #         DataFrame containing the input features for each sample.
    #     y : None
    #         Ignored, present for compatibility.
    #     """
    #     self._update_observed_features(X)

    #     self._x_window.append(X.values.tolist())
    #     if len(self._x_window) == self.window_size:
    #         X_t = deque2rolling_tensor(self._x_window, device=self.device)
    #         self._learn(x=X_t)

    def score_one(self, x: dict) -> float:
        """Return reconstruction error for current window + candidate sample.

        Parameters
        ----------
        x : dict
            Dictionary containing feature name-value pairs for the candidate sample.

        Returns
        -------
        float
            Computed anomaly score (reconstruction error).
        """
        if self.__warmup_state < self.warmup_period:
            return 0.0

        res = 0.0
        self._update_observed_features(x)
        if len(self._x_window) == self.window_size:
            x_win = self._x_window.copy()
            x_win.append(list(x.values()))
            x_t = deque2rolling_tensor(x_win, device=self.device)
            #print(f"score x_t shape: {x_t.shape}")
            #print(f"x_t: {x_t}")

            checkpoint_models = [torch.load(io.BytesIO(chp)) for chp in list(self.__checkpoints)]
            if len(checkpoint_models) == 0:
                return 0

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
                    #print(f"x_pred shape {x_pred.shape}")
                    #print(f"x_pred {x_pred}")
                    doubled_diff = 2 * (x_pred - x_t)
                    #print(f"doubled_diff shape {doubled_diff.shape}")
                    squared_diff = doubled_diff ** 2
                    #print(f"squared_diff shape {squared_diff.shape}")
                    #print(f"squared_diff = {squared_diff}")
                    return squared_diff

                # to_sum = list(map(lambda m: (2 * (m(x_t) - x_t))**2, checkpoint_models))
                to_sum = list(map(calc, checkpoint_models))

                influence = self.lr * (x_t**2) * sum(to_sum)

                #print(f"influence shape {influence.shape}")

                influence = influence / len(checkpoint_models)

            res = torch.sum(influence).item()

        if self.append_predict:
            self._x_window.append(list(x.values()))
        return res

    # def score_many(self, X: pd.DataFrame) -> List[Any]:
    #     """Return list of reconstruction errors for each row in X.

    #     If the window is not yet full, zeros are returned for alignment.

    #     Parameters
    #     ----------
    #     X : pd.DataFrame
    #         DataFrame containing the input features for each sample.

    #     Returns
    #     -------
    #     List[float]
    #         List of computed anomaly scores (reconstruction errors) for each sample in X.
    #     """
    #     self._update_observed_features(X)
    #     x_win = self._x_window.copy()
    #     x_win.append(X.values.tolist())
    #     if self.append_predict:
    #         self._x_window.append(X.values.tolist())

    #     if len(self._x_window) == self.window_size:
    #         X_t = deque2rolling_tensor(x_win, device=self.device)
    #         self.module.eval()
    #         with torch.inference_mode():
    #             x_pred = self.module(X_t)
    #         loss = torch.mean(
    #             self.loss_func(x_pred, x_pred, reduction="none"),
    #             dim=list(range(1, x_pred.dim())),
    #         )
    #         losses = loss.detach().numpy()
    #         if len(losses) < len(X):
    #             losses = np.pad(losses, (len(X) - len(losses), 0))
    #         return losses.tolist()
    #     else:
    #         return np.zeros(len(X)).tolist()

class LSTMRollingDataAttributionAnomalyDetector(anomaly.base.AnomalyDetector):
    def __init__(self,
                 hidden_size: int = 5,
                 window_size: int = 10,
                 num_layers: int = 1,
                 checkpoints_count : int = 5,
                 step_between_checkpoints=0,
                 warmup_period=0,
                 lr : float = 0.001,
                 ):
        self.__rad = RollingDataAttributionAnomalyDetector(
            module=LSTMAutoencoderSutskever(
                n_features=1, 
                hidden_size=hidden_size,
                n_layers=num_layers,
            ),
            out_features=1,
            window_size=window_size,
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
        self.__rad.learn_one(x)

    def score_one(self, x : dict) -> float:
        return self.__rad.score_one(x)