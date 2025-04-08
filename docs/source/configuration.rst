.. _configuration_head:

Configuration
#############

The configuration is kept in the Python dictionary,
where keys are case-sensitive strings and values depend on parameters.
They can be strings, float values, integer values, boolean values, sub-dictionaries, or lists.

The configuration file (example name: ``config.json``) is a file in JavaScript Object Notation (JSON)
Here is the example file::

    {
      "source_model": "Haskell",
      "green_function": "homogeneous",
      "dt": 0.001,
      "density": 2700,
      "radial_radiation": 1.0,
      "vp": 5000.0,
      "vs": 2900.0,
      "stop_simulation": "rupture_time",
      "source_parameters": [
        {"moment_scalar": 1e14, "rupture_time": 0.05},
        {"moment_scalar": 1e15, "rupture_time": 0.1},
        {"moment_scalar": 1e16, "rupture_time": 0.3}
      ],
      "inversion_type": "general",
      "distances": [500, 1000, 2000, 5000, 10000, 20000],
      "inventory": {
        "file_name": "VN_Stations.xml",
        "file_format": "STATIONXML"
      },
      "stream": {
        "source": "arclink",
        "host": "tytan.igf.edu.pl",
        "port": "18001",
        "user": "anonymous@igf.edu.pl",
        "timeout": 300,
        "net": "VN",
        "cache" : "cache_Mw"
      }
    }


Configuration parameters
========================

Below is the description of parameters.

:source_model: (str) The source model name.
    Two values are allowed "Haskell", or "Brune"
:green_function:  (str) The Green function type  name.
    So far only "homogeneous" is allowed.
:dt: (float) The time sampling step for calculations
:density: (float) The density at the source [kg/m^3]
:radial_radiation: (float) The radial radiation absolute value in the far field. 
:transversal_radiation: (float) The transversal radiation absolute value in the far field.
    This parameter is not used so far in the assessment.
    Together with the radial_radiation, using both parameters required correct calculations
    according  :cite:`AkiRichards2002` page 79 or  :cite:`GibowiczKijko1994` page 192.
:vp: (float) The P wave velocity [m/s].
:vs: (float) The S wave velocity [m/s].
:stop_simulation: (str or float) The information when stop simulation and signal visualization.
    There are three possibilities: "rupture_time" stops simulation at phase S time arrival
    + the rupture time + 0.5 s, "phase_time" stops simulation at phase S time arrival,
    where the digit value stops simulation after the defined number of seconds.
:source_parameters: (list) The list of source parameters, that figures are plotted
    See :ref:`Source parameters description`.
:inversion_type: The name of tensor inversion type.
    It must belong to the QuakeML MTInversionType category:
    ``'general'``, ``'zero trace'``, ``'double couple'``, or None.
:inversion_type: The focal mechanism inversion type name for choosing the focal mechanism.
:distances: (list) The list of distances at which displacements plotted are plotted in each figure.
:inventory: (dict) The dictionary of parameters defining how to get the inventory of all stations
    (see :ref:`Inventory parameters`)
:stream: (dict) :ref:`Stream parameters` describing how to get streams and inventories
    from the seismic data server (required only if the inventory file must be created,
    see. :ref:`Stream parameters`)

Source parameters description
=============================
The source parameters are dictionary of two items required to calculate the source.

:moment_scalar: (float) The moment scalar of the DC seismic moment - :math:`M_0`.
:rupture_time: (float) The rupture time in the case of Haskell model.
    In other models it is the time parameters of the model.

Inventory parameters
====================

The `Inventory parameters` describe how to read station inventories.

:file_name: The file name of the inventory file (optional, default value is "inventory.xml").
    When the file doesn't exist, the program tries to download the inventory to the file
    from the server defined in :ref:`Stream parameters`,
:file_format: The inventory format (optional, default value is "STATIONXML").
    It is not required when the inventory file exists

Stream parameters
=================

:source: (str) The web server source type (required, available options "arclink", "fdsnws")
:host: (str) Host name (required)
:port: (int) Server port number, (optional)
:user: (int) User name, (required for arclink)
:timeout: The waiting time for the server response (optional)
:net: (str) The network code (required if `stations` parameter is missing)
:loc: (str) The location filter (optional)
:chan: (str) Channels filter (optional)
:stations: (list(str)) list of station names. When stations names are in the form "NN.SSSS"
    where "NN" is the network code and "SSSS" is the station code.
    The "net" parameter can be omitted.
    If stations names are in the form "SSSS", the "net" parameter must be defined.
    It is possible to define in the list individual channels in the form "NN.SSSS.LL.CCC"
    where "LL" is a location code (can be empty) and "CCC" is the channel code.
:cache: (str) the cache directory (optional, if missing data are not cached)
