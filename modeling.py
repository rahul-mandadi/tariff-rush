"""Shared pieces for the forecasting scripts: models, tuning, the review rule, resampling.

Every forecasting script used to carry its own copy of these. They live here once so each script
reads as its own steps. Behaviour is unchanged: the scripts that use this reproduce their earlier
outputs exactly (checked when this module was introduced, 2026-11-15).
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

LOGISTIC_GRID = [0.03, 0.1, 0.3, 1.0]   # inverse regularization strengths tried
BOOSTING_GRID = [50, 100, 200, 400]     # numbers of trees tried


def logistic(features, label="y"):
    """A maker for L2 logistic regression: make(C, train) returns a function that predicts the
    chance of label = 1 for new rows. Each row is weighted by its column w."""
    def make(C, tr):
        m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
        m.fit(tr[features], tr[label], logisticregression__sample_weight=tr.w)
        return lambda te: m.predict_proba(te[features])[:, 1]
    return make


def boosting_model(n_trees):
    """The project's gradient boosting settings: shallow trees, slow learning, strong regularization."""
    return HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n_trees,
                                          l2_regularization=1.0, min_samples_leaf=40, random_state=0)


def boosting(features, label="y"):
    """A maker for gradient boosting, used like logistic()."""
    def make(n_trees, tr):
        m = boosting_model(n_trees).fit(tr[features], tr[label], sample_weight=tr.w)
        return lambda te: m.predict_proba(te[features])[:, 1]
    return make


def tune(tr, grid, make, label="y", group="cluster"):
    """Pick the setting from grid with the lowest Brier score in 5-fold cross-validation inside the
    training rows, keeping each investigation group in one fold."""
    folds = GroupKFold(n_splits=min(5, tr[group].nunique()))
    best, best_setting = None, None
    for setting in grid:
        scores = []
        for a, b in folds.split(tr, groups=tr[group]):
            predicted = make(setting, tr.iloc[a])(tr.iloc[b])
            scores.append(brier_score_loss(tr[label].iloc[b], predicted, sample_weight=tr.w.iloc[b]))
        if best is None or np.mean(scores) < best:
            best, best_setting = np.mean(scores), setting
    return best_setting


def review_shares(score, cap, weights=None):
    """Which items of one review queue get reviewed, highest score first, when there is time for a
    share cap of the queue. Returns each item's reviewed share in [0, 1]: where the limit falls
    inside a block of tied scores, the block shares what is left equally."""
    score = np.asarray(score, float)
    w = np.ones(len(score)) if weights is None else np.asarray(weights, float)
    left, r = cap * w.sum(), np.zeros(len(score))
    for v in np.unique(score)[::-1]:
        idx = np.where(score == v)[0]
        if left <= 0:
            break
        need = w[idx].sum()
        take = min(1.0, left / need)
        r[idx] = take
        left -= take * need
    return r


def log_odds(p):
    """Log-odds of a probability, as a column, clipped away from 0 and 1."""
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p)).reshape(-1, 1)


def platt(p, y, w):
    """Logistic recalibration (Platt scaling) of predictions p against outcomes y, weights w."""
    return LogisticRegression(C=1e6, max_iter=1000).fit(log_odds(p), y, sample_weight=w)
