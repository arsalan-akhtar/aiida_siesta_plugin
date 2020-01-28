"""
Workchain to calculate the band gap with Siesta.
It is built on top of the SiestaBandsWorkChain
"""

from __future__ import absolute_import
from aiida import orm
from aiida.engine import WorkChain, calcfunction, ToContext
from aiida.engine.launch import submit
from aiida.plugins import WorkflowFactory
from aiida.common import AttributeDict

SiestaBandsWorkChain = WorkflowFactory('siesta.bands')


@calcfunction
def get_bandgap(e_fermi, band):
    """
    Takes a band object, and a Fermi energy, 
    and extracts the band gap value and 'is_insulator' boolean

    :param band: (orm.BandsData): band-structure object
    :param e_energy: (orm.Float): value of the fermi energy.

    :return: An orm.Dict containing the keys:
             'band_gap':  A float, or None in case of a metal. It is zero when the homo is
                          equal to the lumo (e.g. in semi-metals).
             'band_gap_units': A string, here 'eV'
             'is_insulator': A boolean
    """
    from aiida.orm.nodes.data.array.bands import find_bandgap

    is_insulator, bandgap = find_bandgap(fermi_energy=e_fermi.value,
                                         bandsdata=band)
    output = {}
    output['band_gap'] = bandgap
    output['band_gap_units'] = 'eV'
    output['is_insulator'] = is_insulator
    return orm.Dict(dict=output)


class SiestaBandGapWorkChain(WorkChain):
    """
    Extension to the SiestaBandsWorkChain to compute a band gap for a given structure
    using Siesta
    """
    @classmethod
    def define(cls, spec):
        super(SiestaBandGapWorkChain, cls).define(spec)
        #inputs
        spec.expose_inputs(SiestaBandsWorkChain)
        #outline
        spec.outline(cls.run_band_structure, cls.get_bandgap)
        #outputs
        spec.expose_outputs(SiestaBandsWorkChain)
        spec.output('bandgap_info', valid_type=orm.Dict)

    def run_band_structure(self):
        """
        Run the SiestaBandsWorkChain to compute the band structure
        """

        # Further enhancements:

        # We might want to increase the density of the k-point sampling
        # for bands.

        # Optionally, use seekpath to normalize the structure before
        # calling the Bands workflow.

        # Decide whether to use spin-polarization in some cases.

        # Set the band_gap to 'None' for an odd number of electrons in
        # the unit cell if the calculation is not spin-polarized

        inputs = AttributeDict(self.exposed_inputs(SiestaBandsWorkChain))

        running = self.submit(SiestaBandsWorkChain, **inputs)
        self.report('launching SiestaBandsWorkChain<{}>'.format(running.pk))
        return ToContext(workchain_bands=running)

    def get_bandgap(self):
        """
        From the band object obtained by the band structure
        calculation, run a simple script to obtain the band gap
        """

        from aiida.orm import Float

        bands_object = self.ctx.workchain_bands.outputs.bands
        e_fermi = self.ctx.workchain_bands.outputs.output_parameters.get_dict(
        )['E_Fermi']
        bandgap_info = get_bandgap(Float(e_fermi), bands_object)

        self.out_many(
            self.exposed_outputs(self.ctx.workchain_bands,
                                 SiestaBandsWorkChain))

        self.out('bandgap_info', bandgap_info)

        self.report('BandGap workchain completed')

        return
