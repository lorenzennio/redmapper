import fitsio
import esutil as eu
import numpy as np
import itertools
from solver_nfw.solver_nfw_lib import Solver
from catalog import Catalog, Entry
from utilities import chisq_pdf


class Cluster(Entry):
    """Docstring."""

    def find_members(self, radius=None, galcat=None):
        if galcat is None:
            raise ValueError("A GalaxyCatalog object must be specified.")
        if radius is None or radius < 0 or radius > 180:
            raise ValueError("A radius in degrees must be specified.")
        indices, dists = galcat.match(self, radius) # techincally need to pass in a Galaxy
        self.members = galcat[indices]
        new_fields = np.array(zip(dists, np.zeros(len(indices))),
                                    dtype=[('DIST', 'f8'), ('PMEM', 'f8')])
        self.members.add_fields(new_fields)

    def calc_richness(self, zredstr, bkg, r0, beta, mpc_scale):
        r = self.members.dist * mpc_scale
        chisq = zredstr.calculate_chisq(self.members, self.z)
        rho = chisq_pdf(chisq, zredstr.ncol) # chisq dist with ncol DOF
        sigma = 0 # two dimensional cluster galaxy density profile (NFW)
        phi = 0 # cluster luminosity function
        ucounts = (2*np.pi*sigma) * phi * rho
        bcounts = 0
        
        w = 0

        richness_obj = Solver(r0, beta, ucounts, bcounts, r, w)
        return richness_obj.solve_nfw()


class ClusterCatalog(Catalog): 
    """Dosctring."""
    entry_class = Cluster

