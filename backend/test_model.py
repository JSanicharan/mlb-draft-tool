import asyncio
from sklearn.metrics import mean_absolute_error, r2_score
from app.services.training_data import (
    fetch_all_seasons, group_by_player, build_training_pairs, 
    fetch_all_fielders, build_fielding_lookup, add_labels,
    build_dataset, TRAINING_SEASONS
)
from app.services.model_training import split_data, train_model, evaluate_model,train_random_forest, train_xgboost
from app.services import league_references
import joblib

async def run():
    await league_references.refresh_reference_data()
    training_reference_distributions = await league_references.build_training_reference_distributions(TRAINING_SEASONS)

    hitting_data = await fetch_all_seasons(TRAINING_SEASONS)
    grouped = group_by_player(hitting_data)
    pairs = build_training_pairs(grouped)

    fielding_lookup = {}
    for season in TRAINING_SEASONS:
        raw_fielding = await fetch_all_fielders(season)
        season_lookup = build_fielding_lookup(raw_fielding)
        fielding_lookup.update(season_lookup)

    labeled_pairs = add_labels(pairs, fielding_lookup, training_reference_distributions)
    X, y, player_ids = build_dataset(labeled_pairs, fielding_lookup, training_reference_distributions)
    print("Total training pairs:", len(X))

    X_train, X_test, y_train, y_test = split_data(X, y, player_ids)
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)

    persistence_pred = [row[5] for row in X_test]
    persistence_mae = mean_absolute_error(y_test, persistence_pred)
    print("Persistence baseline MAE:", persistence_mae)

    mae = evaluate_model(model, X_test, y_test)
    print("Mean Absolute Error:", mae)
    r2 = r2_score(y_test, predictions)
    print("R² score:", r2)

    rf_model = train_random_forest(X_train, y_train)
    rf_predictions = rf_model.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_predictions)
    rf_r2 = r2_score(y_test, rf_predictions)
    print("Random Forest MAE:", rf_mae)
    print("Random Forest R² score:", rf_r2)
    joblib.dump(rf_model, "rf_model.pkl")
    

asyncio.run(run())