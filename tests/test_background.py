import unittest
import numpy.testing as testing
import numpy as np
import fitsio

from redmapper.background import Background

class BackgroundTestCase(unittest.TestCase):

    def runTest(self):
        file_name, file_path = 'test_bkg.fit', 'data'
        # test that we fail if we try a non-existent file
        self.assertRaises(IOError, Background, 'nonexistent.fit')
        # test that we fail if we read a non-fits file
        self.assertRaises(IOError, Background,
                          '%s/testconfig.yaml' % (file_path))
        # test that we fail if we try a file without the right header info
        self.assertRaises(AttributeError, Background, 
                          '%s/test_dr8_pars.fit' % (file_path))
        bkg = Background('%s/%s' % (file_path, file_name))


        inputs = [(172,15,64), (323,3,103), (9,19,21), (242,4,87),
                  (70,12,58), (193,6,39), (87,14,88), (337,5,25), (333,8,9)]
        py_outputs = np.array([bkg.sigma_g[idx] for idx in inputs])
        idl_outputs = np.array([0.32197464, 6.4165196, 0.0032830855, 
                                1.4605126, 0.0098356586, 0.79848081, 
                                0.011284498, 9.3293247, 8.7064905])
        testing.assert_almost_equal(py_outputs, idl_outputs, decimal=1)


if __name__=='__main__':
        unittest.main()