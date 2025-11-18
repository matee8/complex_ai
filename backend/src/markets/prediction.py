import logging
import os
# import joblib
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from tensorflow.keras import models  # type: ignore

from complex_ai.settings import SUPPORTED_STOCKS

logger = logging.getLogger(__name__)


class StockPredictor:

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        base_path = Path(__file__).resolve().parent.parent.parent
        model_dir = base_path / 'models'
        model_path = model_dir / f'{self.symbol}.keras'

        if os.path.exists(model_path):
            try:
                self.model = models.load_model(model_path)
                logger.info('Model loaded for %s.', self.symbol)
            except (OSError, ValueError) as e:
                logger.error('Failed to load model for %s: %s',
                             self.symbol,
                             e,
                             exc_info=True)
        else:
            logger.warning('Model file not found: %s', model_path)

        # TODO: Load the Scaler here once received from teammate
        # scaler_path = os.path.join(base_dir, 'models',
        #                            f'{self.symbol}_scaler.pkl')
        # self.scaler = joblib.load(scaler_path)

    def predict(self, recent_prices: List[float]) -> Optional[float]:
        if not self.model:
            logger.error('Cannot predict for %s: Model not initialized.',
                         self.symbol)
            return None

        try:
            data = np.array(recent_prices)

            # TODO: Apply Scaling (Critical!)
            # The model expects values between 0 and 1.
            # that expects 0.5. The result will likely be garbage until fixed.
            # data = self.scaler.transform(data.reshape(-1, 1))

            input_tensor = data.reshape((1, -1, 1))

            prediction_scaled = self.model.predict(input_tensor, verbose=0)

            # TODO: Inverse Scale
            # result = self.scaler.inverse_transform(prediction_scaled)
            # return float(result[0][0])

            return float(prediction_scaled[0][0])

        except (ValueError, IndexError, TypeError) as e:
            logger.error('Prediction error for %s: %s',
                         self.symbol,
                         e,
                         exc_info=True)
            return None


PREDICTORS: Dict[str, StockPredictor] = {}


def load_all_models():
    logger.info('Loading Neural Network models...')
    for symbol in SUPPORTED_STOCKS:
        PREDICTORS[symbol] = StockPredictor(symbol)
