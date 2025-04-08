# SSSPY

## Methodology

The goal of this programme was the assessment of the near and intermediate field influence on the seismic signal parameters,
like maximum displacement amplitude of specific phases.
The assessment is based on a very simple seismic signal simulation.
The assumption point source, homogeneous and isotropic medium, simple Haskell :cite:`Haskell1964` source time function,
and a double couple mechanism was taken.
Additionally, the Brune model :cite:`Brune1970`, :cite:`Brune1971`
and Knopoff and Gillbert :cite:`KnopoffGillbert1959` 
are analysed to check the source time function impact on the estimates.
Knopoff and Gillbert source time function is tested only in the frequency domain.
The the radial component of displacement is analyzed, which partially equals the signal of the P wave
and was used for moment tensor estimation in many anthropogenic seismicity cases for the moment tensor estimation.

## Source time functions

For simplicity the Haskell source time function is tested
and, additionally, for comparison, the Brune source time function is applied and the Knopoff and Gillbert
model only in the frequency domain.

## Executable modules

Executable modules can be run. Hovewer, they can contain functions
used in other modules.

* ssspy
* ssscat

## License

GNU Lesser General Public License v3 (LGPLv3)
