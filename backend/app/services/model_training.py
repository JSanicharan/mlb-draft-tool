from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def split_data(X: list, y: list) -> tuple:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=16)
    return X_train, X_test, y_train, y_test

def train_model(X_train: list, y_train: list):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test: list, y_test: list) -> float:
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    return mae