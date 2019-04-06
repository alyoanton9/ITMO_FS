import random as rnd
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer
from copy import copy


class Add_del(object):
    """
        Creates add-del feature wrapper

        Parameters
        ----------
        estimator: object
            A supervised learning estimator with a fit method
        score : callable
            A callable function which will be used to estimate score
        score : boolean
            maximize = True if bigger values are better for score function
        seed: int
            Seed for python random

        See Also
        --------

        Examples
        --------
        >>> from sklearn.metrics import accuracy_score
        >>> data = datasets.make_classification(n_samples=1000, n_features=20)
        >>> X = np.array(data[0])
        >>> y = np.array(data[1])
        >>> lg = linear_model.LogisticRegression(solver='lbfgs')
        >>> add_del = Add_del(lg, accuracy)
        >>> features, score = add_del.run(X, y)
        >>> features
        [5, 6, 8, 11, 16]

        >>> from sklearn.metrics import mean_absolute_error
        >>> boston = datasets.load_boston()
        >>> X = pd.DataFrame(boston['data'], columns=boston['feature_names'])
        >>> y = pd.DataFrame(boston['target'])
        >>> lasso = linear_model.Lasso()
        >>> add_del = Add_del(lasso, mean_absolute_error, maximize=False)
        >>> features, score = add_del.run(X, y)
        >>> features
        ['ZN', 'INDUS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B']

    """

    def __init__(self, estimator, score, maximize=True, seed=42):

        self.estimator = estimator
        self.score = score
        self.maximize = maximize
        rnd.seed(seed)

    def _add(self, X, y, cv=3, silent=True):

        prev_score = 0
        current_score = 0
        scores = []

        to_append = [i for i in range(X.shape[1])]  # list of features not used in final configuration
        appended = []  # list of features in final configuration

        for feature in to_append:

            appended.append(feature)

            current_score = abs(np.mean(cross_val_score(self.estimator, X[:, appended], y,
                                                        scoring=make_scorer(self.score,
                                                                            greater_is_better=self.maximize),
                                                        cv=cv)))
            scores.append(current_score)

            if silent == False:
                print('feature {} (score: {})'.format(feature, current_score))

            if self.maximize == True and current_score <= prev_score:
                appended.pop()

            elif self.maximize == False and current_score > prev_score:
                appended.pop()

            prev_score = current_score

        if silent == False:
            if self.maximize == True:
                print('max score: {}'.format(np.max(scores)))
            elif self.maximize == False:
                print('min score: {}'.format(np.min(scores)))

        return appended

    def _del(self, X, y, features, cv=3, silent=True):

        prev_score = abs(np.mean(cross_val_score(self.estimator, X[:, features], y,
                                                 scoring=make_scorer(self.score, greater_is_better=self.maximize),
                                                 cv=cv)))
        current_score = 0
        scores = [prev_score]

        if silent == False:
            print('score: {}'.format(prev_score))

        iter_features = copy(features)

        for feature in iter_features:

            features.remove(feature)

            current_score = abs(np.mean(cross_val_score(self.estimator, X[:, features], y,
                                                        scoring=make_scorer(self.score,
                                                                            greater_is_better=self.maximize),
                                                        cv=cv)))
            scores.append(current_score)

            if silent == False:
                print('remove feature {} (score: {})'.format(feature, current_score))

            if self.maximize == True and prev_score > current_score:
                features.append(feature)

            if self.maximize == False and prev_score <= current_score:
                features.append(feature)

            if self.maximize == True and current_score > prev_score:
                prev_score = current_score

            if self.maximize == False and current_score <= prev_score:
                prev_score = current_score

        if self.maximize == True:
            res_score = np.max(scores)
        elif self.maximize == False:
            res_score = np.min(scores)

        if silent == 'False':
            print('score: {}'.format(res_score))

        return (features, res_score)

    def run(self, X, y, cv=3, silent=True):
        """
           Fits wrapper.

           Parameters
           ----------
           X : numpy array or pandas DataFrame, shape (n_samples, n_features)
               The training input samples.
           y : numpy array of pandas Series, shape (n_samples, )
               The target values.
           cv=3 : int
               Number of splits in cross-validation
           silent=True : boolean
               If silent=False then prints all the scores during add-del procedure

           Returns:
           ----------
           features : list
               List of feature after add-del procedure

           score : float
               The best score after add-del procedure of `score` metric.

           See Also
           --------

           Examples
           --------

       """

    return_feature_names = False

    if isinstance(X, pd.DataFrame):
        return_feature_names = True
        columns = np.array(X.columns)

    X = np.array(X)
    y = np.array(y).ravel()

    if silent == False:
        print('add trial')
    features = self._add(X, y, cv, silent)

    if silent == False:
        print('del trial')
    features, score = self._del(X, y, features, cv, silent)

    if return_feature_names:
        return (list(columns[features]), score)

    return (features, score)

