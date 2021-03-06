import unittest
import numpy.testing as testing
import numpy as np
import fitsio

from esutil.cosmology import Cosmo
from redmapper.catalog import Entry
from redmapper.cluster import Cluster
from redmapper.config import Configuration
from redmapper.galaxy import GalaxyCatalog
from redmapper.background import Background
from redmapper.redsequence import RedSequenceColorPar
from redmapper.mask import HPMask

class BackgroundStub(Background):

    def __init__(self, filename):
        obkg = Entry.from_fits_file(filename)
        self.refmagbins = obkg.refmagbins
        self.chisqbins = obkg.chisqbins
        self.lnchisqbins = obkg.lnchisqbins
        self.zbins = obkg.zbins
        self.sigma_g = obkg.sigma_g
        self.sigma_lng = obkg.sigma_lng

class ClusterFiltersTestCase(unittest.TestCase):
    """
    This file tests multiple features of the cluster object.
    """
    def runTest(self):
        """
        First test the filters:
        nfw, lum, and bkg
        """
        self.cluster = Cluster(np.empty(1))
        self.file_path = 'data_for_tests'
        filename = 'test_cluster_members.fit'
        self.cluster.neighbors = GalaxyCatalog.from_fits_file(self.file_path + '/' + filename)

        hdr=fitsio.read_header(self.file_path+'/'+filename,ext=1)
        self.cluster.z = hdr['Z_LAMBDA']
        self.richness_compare = hdr['LAMBDA']
        self.cluster.z = self.cluster.neighbors.z[0]
        # this should explicitly set our default cosmology
        cosmo = Cosmo()

        #The configuration
        #Used by the mask, background and richness calculation
        conf_filename = 'testconfig.yaml'
        confstr = Configuration(self.file_path + '/' + conf_filename)

        #Set up the mask
        mask = HPMask(confstr) #Create the mask
        #TODO - Need to know the mpcscale
        #mask.set_radmask(self.cluster,mpcscale???)
        print "In development: printing features of the mask"
        print "mask.maskfile",mask.maskfile
        print "mask.fracgood.shape: ",mask.fracgood.shape
        print "mask.fracgood_float: ",mask.fracgood_float
        print "mask.nside: ",mask.nside
        print "mask.offset: ",mask.offset
        print "mask.npix: ",mask.npix
        print "len(mask.maskgals): ",len(mask.maskgals)

        # nfw
        test_indices = np.array([46, 38,  1,  2, 11, 24, 25, 16])
        py_nfw = self.cluster._calc_radial_profile()[test_indices]
        idl_nfw = np.array([0.23875841, 0.033541825, 0.032989189, 0.054912228, 
                            0.11075225, 0.34660992, 0.23695366, 0.25232968])
        testing.assert_almost_equal(py_nfw, idl_nfw)

        # lum
        test_indices = np.array([47, 19,  0, 30, 22, 48, 34, 19])
        zred_filename = 'test_dr8_pars.fit'
        zredstr = RedSequenceColorPar(self.file_path + '/' + zred_filename)
        mstar = zredstr.mstar(self.cluster.z)
        maxmag = mstar - 2.5*np.log10(confstr.lval_reference)
        py_lum = self.cluster._calc_luminosity(zredstr, maxmag)[test_indices]
        idl_lum = np.array([0.31448608824729662, 0.51525195091720710, 
                            0.50794115714566024, 0.57002321121039334, 
                            0.48596850373287931, 0.53985704075616792, 
                            0.61754178397796256, 0.51525195091720710])
        testing.assert_almost_equal(py_lum, idl_lum)

        # bkg
        test_indices = np.array([29, 16, 27, 38, 25])
        bkg_filename = 'test_bkg.fit'
        bkg = BackgroundStub(self.file_path + '/' + bkg_filename)
        py_bkg = self.cluster._calc_bkg_density(bkg, cosmo)[test_indices]
        idl_bkg = np.array([1.3140464045388294, 0.16422314236185420, 
                            0.56610846527410053, 0.79559933744885403, 
                            0.21078853798218194])
        testing.assert_almost_equal(py_bkg, idl_bkg)

        """
        This tests the calc_richness() function from cluster.py.
        The purpose of this function is to calculate the richness,
        also written as lambda_chisq, of the cluster
        for a single iteration during the redmapper algorithm.

        THIS TEST IS STILL IN DEVELOPEMENT!!!
        """
        self.cluster.neighbors.dist = np.degrees(self.cluster.neighbors.r/cosmo.Dl(0,self.cluster.z))
        zredstr = RedSequenceColorPar(self.file_path + '/' + zred_filename,fine=True)
        bkg_full = Background('%s/%s' % (self.file_path, bkg_filename))
        richness = self.cluster.calc_richness(zredstr, bkg_full, cosmo, confstr)
        # this will just test the ~24.  Closer requires adding the mask
        testing.assert_almost_equal(richness/10.,self.richness_compare/10.,decimal=1)

        #End of the tests
        return

class ClusterMembersTestCase(unittest.TestCase):

    #This next test MUST be done before the calc_richness test can be completed.
    def test_member_finding(self): pass #Do this with a radius that is R_lambda of a 
    #lambda=300 cluster, so 8.37 arminutes or 0.1395 degrees
    def test_richness(self): pass

if __name__=='__main__':
    unittest.main()

