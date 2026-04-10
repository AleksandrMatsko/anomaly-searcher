import pytest

import app.metrics as metrics
from app.model import HolesFinderAnomalyDetector

testdata = [
    (metrics.Metric(
        name="metric_with_no_values",
        values=[],
        ), 0, True),
    (metrics.Metric(
        name="metric_when_first_value_received",
        values=[metrics.MetricValue(1775294135, 10)],
        queried_at=1775294135
        ), 0, False),
    (metrics.Metric(
        name="metric_when_first_n_values_received",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294135
        ), 0, False),
    (metrics.Metric(
        name="metric_when_values_received_at_exact_ts",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294375,
        ), 1775294315, False),
    (metrics.Metric(
        name="metric_when_values_received_at_non_exact_ts",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294320,
        ), 1775294315, False),
    (metrics.Metric(
        name="metric_on_the_hole_start_with_exact_tx",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294915
        ), 1775294855, False),
    (metrics.Metric(
        name="metric_on_the_hole_start_with_non_exact_tx",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294930
        ), 1775294860, True),
    (metrics.Metric(
        name="metric_in_the_middle_of_hole",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
        ],
        queried_at=1775294975
        ), 1775294855, True),
    (metrics.Metric(
        name="metric_at_the_end_of_hole",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
            metrics.MetricValue(1775295215, 50.55),
        ],
        queried_at=1775295215
        ), 1775294855, False),
    (metrics.Metric(
        name="metric_usual_values",
        values=[
            metrics.MetricValue(1775294135, 50.96),
            metrics.MetricValue(1775294195, 49.99),
            metrics.MetricValue(1775294255, 49.20),
            metrics.MetricValue(1775294315, 49.16),
            metrics.MetricValue(1775294375, 50.37),
            metrics.MetricValue(1775294435, 50.37),
            metrics.MetricValue(1775294495, 50.37),
            metrics.MetricValue(1775294555, 50.37),
            metrics.MetricValue(1775294615, 50.37),
            metrics.MetricValue(1775294675, 49.62),
            metrics.MetricValue(1775294735, 50.16),
            metrics.MetricValue(1775294795, 49.65),
            metrics.MetricValue(1775294855, 49.32),
            metrics.MetricValue(1775295215, 50.55),
            metrics.MetricValue(1775295275, 50.11),
        ],
        queried_at=1775295276
        ), 1775295215, False),
]

@pytest.mark.parametrize("metric,last_observed_ts,anomaly_expected", testdata)
def test_predict_one(
    metric: metrics.Metric,
    last_observed_ts: int,
    anomaly_expected: bool,
    ):
    model = HolesFinderAnomalyDetector(
        last_observed_ts=last_observed_ts
        )

    anomaly_got = model.predict_one(metric)

    assert anomaly_expected == anomaly_got, f"prediction about anomaly does not match expected for metric {metric.name}"