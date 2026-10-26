# Model definitions and small hyperparameter grids, all with fixed seeds

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

MODEL_NAMES = ("logistic_regression", "decision_tree", "random_forest", "xgboost")


class ModelUnavailableError(RuntimeError):
    pass


def xgboost_available():
    try:
        import xgboost  # noqa: F401
    except ImportError:
        return False
    return True


def make_model(name, seed=42, scale_pos_weight=1.0):
    # Returns (estimator, parameter grid) for GridSearchCV
    if name == "logistic_regression":
        est = Pipeline([("scale", StandardScaler()),
                        ("clf", LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed))])
        return est, {"clf__C": [0.01, 0.1, 1.0, 10.0]}
    if name == "decision_tree":
        est = DecisionTreeClassifier(class_weight="balanced", random_state=seed)
        return est, {"max_depth": [2, 3, 4, 6], "min_samples_leaf": [1, 5, 20]}
    if name == "random_forest":
        est = RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample", random_state=seed, n_jobs=1)
        return est, {"max_depth": [3, 6, None], "min_samples_leaf": [1, 5]}
    if name == "xgboost":
        if not xgboost_available():
            raise ModelUnavailableError("xgboost is not installed; pip install -r requirements-research.txt")
        from xgboost import XGBClassifier
        est = XGBClassifier(n_estimators=200, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
                            scale_pos_weight=scale_pos_weight, random_state=seed, n_jobs=1, tree_method="hist")
        return est, {"max_depth": [2, 3, 4], "learning_rate": [0.05, 0.1], "n_estimators": [100, 300]}
    raise ValueError(f"unknown model '{name}', expected one of {', '.join(MODEL_NAMES)}")
