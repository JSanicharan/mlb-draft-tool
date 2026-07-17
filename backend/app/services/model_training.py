from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def split_data(X: list, y: list, groups: list) -> tuple:
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=16)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))

    X_train = [X[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_train = [y[i] for i in train_idx]
    y_test = [y[i] for i in test_idx]

    return X_train, X_test, y_train, y_test

def train_model(X_train: list, y_train: list):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def train_random_forest(X_train: list, y_train: list):
    model = RandomForestRegressor(n_estimators=200, random_state=16)
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train: list, y_train: list):
    model = XGBRegressor(n_estimators=200, random_state=16)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test: list, y_test: list) -> float:
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    return mae