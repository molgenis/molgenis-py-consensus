from parameterized import parameterized
from nose.tools import assert_equal, assert_true, assert_false

from consensus.Classifications import Classifications


@parameterized([
    ('vus', 'VUS'),
    ('lp', '(Likely) pathogenic'),
    ('p', '(Likely) pathogenic'),
    ('lb', '(Likely) benign'),
    ('b', '(Likely) benign')
])
def test_transform_classification(classification, expected):
    assert_equal(expected, Classifications.transform_classification(classification))


@parameterized([
    (1, 1, 1, 0, 0),
    (1, 1, 1, 1, 0)
])
def test_is_no_consensus_true(v, b, lb, p, lp):
    classifications = {'vus': v, 'b': b, 'lb': lb, 'p': p, 'lp': lp}
    assert_true(Classifications.is_no_consensus(classifications))


@parameterized([
    (2, 0, 0, 0, 0),
    (0, 0, 0, 1, 1),
    (0, 1, 1, 0, 0)
])
def test_is_no_consensus_false(v, b, lb, p, lp):
    classifications = {'vus': v, 'b': b, 'lb': lb, 'p': p, 'lp': lp}
    assert_false(Classifications.is_no_consensus(classifications))


def test_is_conflicting_classification_true():
    classifications = {'vus': 1, 'b': 1, 'lb': 1, 'p': 1, 'lp': 0}
    assert_true(Classifications.is_conflicting_classification(classifications))


@parameterized([
    (1, 1, 1, 0, 0),
    (2, 0, 0, 0, 0),
    (0, 0, 0, 1, 1),
    (0, 1, 1, 0, 0)
])
def test_is_conflicting_classification_false(v, b, lb, p, lp):
    classifications = {'vus': v, 'b': b, 'lb': lb, 'p': p, 'lp': lp}
    assert_false(Classifications.is_conflicting_classification(classifications))


@parameterized([
    ('b', 'Benign'),
    ('lb', 'Likely benign'),
    ('vus', 'VUS'),
    ('lp', 'Likely pathogenic'),
    ('p', 'Pathogenic')
])
def test_get_full_classification_from_abbreviation(abbr, expected):
    observed = Classifications.get_full_classification_from_abbreviation(abbr)
    assert_equal(expected, observed)


@parameterized([
    ('Likely benign', 'LB'),
    ('Benign', 'LB'),
    ('(Likely) benign', 'LB'),
    ('Pathogenic', 'LP'),
    ('Likely pathogenic', 'LP'),
    ('(Likely) pathogenic', 'LP'),
    ('VUS', 'VUS')
])
def test_get_abbreviation_from_classification(classification, expected):
    observed = Classifications.get_abbreviation_from_classification(classification)
    assert_equal(expected, observed)
