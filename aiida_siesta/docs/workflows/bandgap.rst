SIESTA BandGap workflow
++++++++++++++++++++++

Description
-----------

The **SiestaBandGapWorkchain** is a simple workflow built on top of the
**SiestaBandsWorkchain**, to determine whether a material is a metal or
an insulator, and to compute the band gap if appropriate.


Supported Siesta versions
-------------------------

At least 4.0.1 of the 4.0 series, and 4.1-b3 of the 4.1 series, which
can be found in the development platform
(https://gitlab.com/siesta-project/siesta).

Inputs
------

The inputs are the same as those of the **SiestaBandsWorkchain**,
using the mechanism of port exposure new in AiiDA 1.0.


Outputs
-------

The outputs include those of the **SiestaBandsWorkchain**,
using the mechanism of port exposure new in AiiDA 1.0. In addition,
there is an extra output node:

* **bandgap_info** :py:class:`Dict <aiida.orm.Dict>` 

A dictionary containing the keys::

       'band_gap':       A float, or None in case of a metal. It is zero when the homo is
                         equal to the lumo (e.g. in semi-metals).
       'band_gap_units': A string indicating the units ('eV')
       'is_insulator':   A boolean

The operation of the workflow depends on a good sampling of the
high-symmetry lines of the Brillouin Zone (BZ). Currently the built-in
sampling (in the **SiestaBandsWorkchain**) corresponds to around 20
points per section (e.g., Gamma to X) of the k-path in the BZ. A
future version will offer a more configurable sampling level.
