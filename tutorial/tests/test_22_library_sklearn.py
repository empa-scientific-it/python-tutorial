import numpy as np
import pytest
from sklearn import datasets, model_selection, preprocessing


def get_scaled_dataset(dataset_type: str):
    if dataset_type == "classification":
        data = datasets.load_breast_cancer()
    else:
        data = datasets.load_diabetes()

    features = data["data"]
    targets = data["target"]
    (
        features_train,
        features_test,
        targets_train,
        targets_test,
    ) = model_selection.train_test_split(
        features, targets, test_size=0.20, random_state=42
    )
    (
        features_train,
        features_test,
        targets_train,
        targets_test,
    ) = model_selection.train_test_split(
        features_train, targets_train, test_size=0.25, random_state=42
    )
    standard_scaler = preprocessing.StandardScaler()
    standard_scaler.fit(features_train)
    features_train_standardised = standard_scaler.transform(features_train)
    features_test_standardised = standard_scaler.transform(features_test)

    return (
        features_train_standardised,
        targets_train,
        features_test_standardised,
        targets_test,
    )


def reference_obtain_five_best_features(dataset):
    from sklearn import feature_selection

    features, targets = dataset
    select_kbest_model = feature_selection.SelectKBest(
        score_func=feature_selection.mutual_info_classif, k=5
    )
    select_kbest_model.fit(features, targets)
    return select_kbest_model.get_support(indices=True)


@pytest.mark.parametrize("dataset", [get_scaled_dataset("classification")])
def test_obtain_five_best_features(dataset, function_to_test):
    features_train, targets_train, _, _ = dataset
    train_set = [features_train, targets_train]
    assert np.array_equal(
        reference_obtain_five_best_features(train_set), function_to_test(train_set)
    )


def reference_obtain_total_explained_variance_ratio(dataset):
    from sklearn import decomposition

    features, _ = dataset
    pca_model = decomposition.PCA(n_components=5, random_state=42)
    pca_model.fit(features)
    explained_variance_ratio_by_component = pca_model.explained_variance_ratio_
    total_explained_variance_ratio = sum(explained_variance_ratio_by_component)
    return total_explained_variance_ratio


@pytest.mark.parametrize(
    "dataset", [get_scaled_dataset("classification"), get_scaled_dataset("regression")]
)
def test_obtain_total_explained_variance_ratio(dataset, function_to_test):
    features_train, targets_train, _, _ = dataset
    train_set = [features_train, targets_train]
    assert reference_obtain_total_explained_variance_ratio(
        train_set
    ) == function_to_test(train_set)


def reference_obtain_clustering_labels(dataset):
    from sklearn import cluster

    features, _ = dataset
    clustering_model = cluster.AgglomerativeClustering()
    clustering_model.fit(features)
    return clustering_model.labels_


@pytest.mark.parametrize("dataset", [get_scaled_dataset("classification")])
def test_obtain_clustering_labels(dataset, function_to_test):
    features_train, targets_train, _, _ = dataset
    train_set = [features_train, targets_train]
    assert np.array_equal(
        reference_obtain_clustering_labels(train_set), function_to_test(train_set)
    )


def reference_train_classifier_and_obtain_accuracy(train_set, test_set):
    from sklearn import metrics, svm

    features_train, targets_train = train_set
    features_test, targets_test = test_set
    svm_model = svm.SVC(C=0.5, kernel="linear", random_state=42)
    svm_model.fit(features_train, targets_train)
    predicted_test = svm_model.predict(features_test)
    accuracy_test = metrics.accuracy_score(targets_test, predicted_test)
    return accuracy_test


@pytest.mark.parametrize("dataset", [get_scaled_dataset("classification")])
def test_train_classifier_and_obtain_accuracy(dataset, function_to_test):
    features_train, targets_train, features_test, targets_test = dataset
    train_set = [features_train, targets_train]
    test_set = [features_test, targets_test]
    assert reference_train_classifier_and_obtain_accuracy(
        train_set, test_set
    ) == function_to_test(train_set, test_set)


def reference_train_regressor_and_obtain_rmse(train_set, test_set):
    from sklearn import ensemble, metrics

    features_train, targets_train = train_set
    features_test, targets_test = test_set
    rfr_model = ensemble.RandomForestRegressor(n_estimators=32, random_state=42)
    rfr_model.fit(features_train, targets_train)
    predicted_test = rfr_model.predict(features_test)
    rmse_test = metrics.mean_squared_error(targets_test, predicted_test, squared=False)
    return rmse_test


@pytest.mark.parametrize("dataset", [get_scaled_dataset("regression")])
def test_train_regressor_and_obtain_rmse(dataset, function_to_test):
    features_train, targets_train, features_test, targets_test = dataset
    train_set = [features_train, targets_train]
    test_set = [features_test, targets_test]
    assert reference_train_regressor_and_obtain_rmse(
        train_set, test_set
    ) == function_to_test(train_set, test_set)


def reference_build_regressor_and_obtain_rmse():
    from sklearn import (
        datasets,
        ensemble,
        feature_selection,
        metrics,
        model_selection,
        pipeline,
        preprocessing,
    )

    data = datasets.fetch_california_housing()
    features = data["data"]
    targets = data["target"]
    data["feature_names"]
    (
        features_train,
        features_test,
        targets_train,
        targets_test,
    ) = model_selection.train_test_split(
        features, targets, test_size=0.3, random_state=42
    )

    model_pipeline = pipeline.Pipeline(
        [
            ("scaler", preprocessing.StandardScaler()),
            (
                "feature_selector",
                feature_selection.SelectKBest(
                    score_func=feature_selection.mutual_info_regression, k=3
                ),
            ),
            (
                "rfr_regressor",
                ensemble.RandomForestRegressor(n_estimators=128, random_state=42),
            ),
        ]
    )

    model_pipeline.fit(features_train, targets_train)

    predicted_test = model_pipeline.predict(features_test)

    rmse_test = metrics.mean_squared_error(targets_test, predicted_test, squared=False)

    return rmse_test


def test_build_regressor_and_obtain_rmse(function_to_test):
    assert reference_build_regressor_and_obtain_rmse() == function_to_test()


def reference_build_classifier_and_obtain_f1score():
    import numpy as np
    from sklearn import (
        datasets,
        ensemble,
        feature_extraction,
        feature_selection,
        metrics,
        model_selection,
        pipeline,
    )

    data = datasets.fetch_20newsgroups()
    texts = data["data"]
    targets = data["target"]
    (
        texts_train,
        texts_test,
        targets_train,
        targets_test,
    ) = model_selection.train_test_split(texts, targets, test_size=0.2, random_state=42)

    (
        texts_train,
        texts_val,
        targets_train,
        targets_val,
    ) = model_selection.train_test_split(
        texts_train, targets_train, test_size=0.25, random_state=42
    )

    features_pipeline = pipeline.Pipeline(
        [
            ("feature_extraction", feature_extraction.text.TfidfVectorizer()),
            (
                "feature_selector",
                feature_selection.SelectKBest(
                    score_func=feature_selection.f_classif, k=100
                ),
            ),
        ]
    )

    features_train = features_pipeline.fit_transform(texts_train, targets_train)
    features_train = features_train.toarray()
    features_val = features_pipeline.transform(texts_val).toarray()
    features_test = features_pipeline.transform(texts_test).toarray()

    range_nr_trees = [16, 32, 64, 128, 256]
    validation_scores = []
    for nr_trees in range_nr_trees:
        rfr_classifier = ensemble.RandomForestClassifier(
            n_estimators=nr_trees, random_state=42
        )
        rfr_classifier.fit(features_train, targets_train)
        predicted_val = rfr_classifier.predict(features_val)
        f1score_val = metrics.f1_score(targets_val, predicted_val, average="weighted")
        validation_scores.append(f1score_val)

    best_model_index = np.argmax(validation_scores)

    features_train = np.vstack((features_train, features_val))
    targets_train = np.hstack((targets_train, targets_val))

    final_rfr_classifier = ensemble.RandomForestClassifier(
        n_estimators=range_nr_trees[best_model_index], random_state=42
    )
    final_rfr_classifier.fit(features_train, targets_train)

    predicted_test = final_rfr_classifier.predict(features_test)

    f1score_test = metrics.f1_score(targets_test, predicted_test, average="weighted")

    return f1score_test


def test_build_classifier_and_obtain_f1score(function_to_test):
    assert reference_build_classifier_and_obtain_f1score() == function_to_test()
