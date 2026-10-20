"""
models/tabnet_model.py — Scikit-learn compatible TabNet Regressor wrapper
for Tabular Deep Learning on Inland India Logistics.
"""

import numpy as np


class TabNetEstimator:
    """
    Scikit-learn compatible wrapper around PyTorch TabNetRegressor.
    Supports standard fit(X, y) and predict(X) APIs for seamless
    integration with scikit-learn metrics, pipelines, and joblib serialization.
    """

    def __init__(
        self,
        n_d=16,
        n_a=16,
        n_steps=4,
        gamma=1.3,
        lambda_sparse=1e-3,
        max_epochs=25,
        batch_size=512,
        seed=42,
        device_name="auto",
    ):
        self.n_d = n_d
        self.n_a = n_a
        self.n_steps = n_steps
        self.gamma = gamma
        self.lambda_sparse = lambda_sparse
        self.max_epochs = max_epochs
        self.batch_size = batch_size
        self.seed = seed
        self.device_name = device_name
        self.model = None

    def fit(self, X, y):
        from pytorch_tabnet.tab_model import TabNetRegressor

        self.model = TabNetRegressor(
            n_d=self.n_d,
            n_a=self.n_a,
            n_steps=self.n_steps,
            gamma=self.gamma,
            lambda_sparse=self.lambda_sparse,
            seed=self.seed,
            device_name=self.device_name,
            verbose=0,
        )
        y_2d = y.reshape(-1, 1).astype(np.float32)
        X_f = X.astype(np.float32)
        self.model.fit(
            X_f,
            y_2d,
            max_epochs=self.max_epochs,
            batch_size=self.batch_size,
            patience=5,
        )
        return self

    def predict(self, X):
        if self.model is None:
            raise RuntimeError("TabNet model is not fitted yet.")
        X_f = X.astype(np.float32)
        preds = self.model.predict(X_f)
        return preds.flatten()
