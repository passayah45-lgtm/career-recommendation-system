# Ranks careers by a trained model's probability while keeping the engine's explanations and skill gaps

import numpy as np

from src.ml.features import build_pair_dataset, profile_matrix
from src.ml.models import make_model
from src.services.recommendations import recommend


class NotTrainedError(RuntimeError):
    pass


def rank_by_probability(career_ids, probabilities):
    # Highest probability first, ties broken by career id so the order is deterministic
    order = sorted(range(len(career_ids)), key=lambda i: (-round(float(probabilities[i]), 9), career_ids[i]))
    return [career_ids[i] for i in order]


class TrainedRanker:
    def __init__(self, model_name, params=None, seed=42):
        self.model_name = model_name
        self.params = dict(params or {})
        self.seed = seed
        self.estimator = None

    def fit(self, profiles, catalog):
        X, y, _, _ = build_pair_dataset(profiles, catalog)
        y = np.asarray(y)
        if y.sum() == 0 or y.sum() == len(y):
            raise ValueError("training data needs both relevant and non-relevant pairs")
        spw = float((y == 0).sum()) / float((y == 1).sum())
        est, _ = make_model(self.model_name, seed=self.seed, scale_pos_weight=spw)
        est.set_params(**self.params)
        est.fit(np.asarray(X, dtype=float), y)
        self.estimator = est
        return self

    def predict_proba(self, profile_data, catalog):
        if self.estimator is None:
            raise NotTrainedError("call fit() before predicting")
        ids, rows = profile_matrix(profile_data, catalog)
        return ids, self.estimator.predict_proba(np.asarray(rows, dtype=float))[:, 1]

    def rank(self, profile_data, catalog):
        ids, proba = self.predict_proba(profile_data, catalog)
        return rank_by_probability(ids, proba)

    def recommend(self, profile_data, catalog, top_k=5):
        # Same output schema as recommend(), reordered by model probability, with engine explanations kept
        ids, proba = self.predict_proba(profile_data, catalog)
        base = recommend(profile_data, catalog, top_k=None)
        by_id = {r["career_id"]: r for r in base["recommendations"]}
        p_of = dict(zip(ids, proba))
        ordered = []
        for rank, cid in enumerate(rank_by_probability(ids, proba), start=1):
            rec = dict(by_id[cid])
            rec["rank"] = rank
            rec["model_probability"] = round(float(p_of[cid]), 4)
            ordered.append(rec)
        out = dict(base)
        out["recommendations"] = ordered[:top_k] if top_k else ordered
        out["ranking_model"] = self.model_name
        return out
