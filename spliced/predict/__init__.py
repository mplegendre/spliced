from .base import Prediction, Actual
from .symbolator import SymbolatorPrediction


def get_predictors(names=None):
    """
    Get a lookup of predictors for an experiment to run.
    """
    names = names or []
    predictors = {"actual": Actual(), "symbolator": SymbolatorPrediction()}
    if names:
        keepers = {}
        for name, predictor in predictors.items():
            if name in names:
                keepers[name] = predictor
        predictors = keepers
    return predictors
