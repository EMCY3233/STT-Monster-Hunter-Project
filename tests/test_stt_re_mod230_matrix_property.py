from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from check_mod230_matrix_property import check,matrix,TOLERANCE


def flat(rows):return [rows[r][c] for c in range(4) for r in range(4)]


I=flat([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
R=flat([[0,-1,0,2],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
R_INV=flat([[0,1,0,0],[-1,0,0,2],[0,0,1,0],[0,0,0,1]])
L=flat([[1,0,0,3],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
G_INV=flat([[0,1,0,-3],[-1,0,0,2],[0,0,1,0],[0,0,0,1]])


class MatrixPropertyTests(unittest.TestCase):
    def test_parent_before_local_noncommuting(self):
        r=check([255,0],[R,L],[R_INV,G_INV])
        self.assertTrue(r['property_holds_for_all_pairs']);self.assertEqual(r['max_absolute_residual'],0)
        self.assertEqual(r['nonroot_pairs_within_tolerance'],1)

    def test_local_inverse_is_not_child_global_inverse(self):
        local_inv=flat([[1,0,0,-3],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        r=check([255,0],[R,L],[R_INV,local_inv])
        self.assertFalse(r['property_holds_for_all_pairs'])

    def test_column_major_translation(self):
        self.assertEqual(matrix(L)[0][3],3);self.assertEqual(matrix(L)[3][0],0)

    def test_fixed_tolerance_boundary(self):
        small=I.copy();small[0]+=TOLERANCE/2
        big=I.copy();big[0]+=TOLERANCE*2
        self.assertTrue(check([255],[I],[small])['property_holds_for_all_pairs'])
        self.assertFalse(check([255],[I],[big])['property_holds_for_all_pairs'])

    def test_count_mismatch(self):
        with self.assertRaises(ValueError):check([255,0],[I],[I])

    def test_parent_bounds(self):
        with self.assertRaisesRegex(ValueError,'parent bounds'):check([8],[I],[I])

    def test_cycle(self):
        with self.assertRaisesRegex(ValueError,'cycle'):check([1,0],[I,I],[I,I])

    def test_nan(self):
        bad=I.copy();bad[0]=float('nan')
        with self.assertRaisesRegex(ValueError,'nonfinite'):check([255],[bad],[I])


if __name__=='__main__':unittest.main()
