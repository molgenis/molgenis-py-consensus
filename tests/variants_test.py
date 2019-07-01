from parameterized import parameterized
from nose.tools import assert_equal

from consensus.Variants import Variants


@parameterized(
    [
        ('G', 'C', 'G', 'C'),
        ('GGGC', 'GGAA', 'GC', 'AA'),
        ('GGGC', 'GAA', 'GGC', 'AA'),
        ('G', 'GAG', '.', 'AG'),
        ('GAG', 'G', 'AG', '.'),
        ('GGAGG', 'GGCGG', 'A', 'C')
    ]
)
def test_simplify_ref_alt(raw_ref, raw_alt, expected_ref, expected_alt):
    ref, alt = Variants._simplify_ref_alt(raw_ref, raw_alt)
    assert_equal(expected_ref, ref)
    assert_equal(expected_alt, alt)


@parameterized(
    [
        ('G', 'C', 'snp'),
        ('GGGC', 'GGAA', 'delins'),
        ('G', 'GAG', 'ins'),
        ('GAG', 'G', 'del'),
        ('GGAGG', 'GGCGG', 'snp'),
        ('GC', 'AA', 'delins'),
        ('.', 'AG', 'ins'),
        ('AG', '.', 'del')
    ]
)
def test_get_variant_type(ref, alt, expected_type):
    type = Variants.get_variant_type(ref, alt)
    assert_equal(expected_type, type)