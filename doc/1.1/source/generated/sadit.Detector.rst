Detector Package
================
.. toctree::
    
    sadit.Detector.rst

.. automodule:: sadit.Detector.API
    :members:

:mod:`Data` Module
------------------
.. automodule:: sadit.Detector.Data

.. autoclass:: sadit.Detector.Data.Data
    :members:
    :show-inheritance:

`HardDisk File`
+++++++++++++++++++++++

.. autoclass:: sadit.Detector.Data.MEM_DiskFile
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.Data.MEM_FS
    :members:
    :show-inheritance:
    :undoc-members:


.. autoclass:: sadit.Detector.Data.MEM_Pcap2netflow
    :show-inheritance:
    :members:
    :undoc-members:

.. autoclass:: sadit.Detector.Data.MEM_FlowExporter
    :members:
    :show-inheritance:
    :undoc-members:

.. autoclass:: sadit.Detector.Data.HDF_Xflow
    :members:
    :show-inheritance:
    :undoc-members:

 
`Database`
+++++++++++++++++++++++
.. autoclass:: sadit.Detector.Data.MySQLDatabase
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.Data.SperottoIPOM
    :members:
    :show-inheritance:


:mod:`DataHandler` Module
-------------------------

.. automodule:: sadit.Detector.DataHandler

.. autosummary::

    QuantizeDataHandler
    ModelFreeQuantizeDataHandler
    ModelBasedQuantizeDataHandler
    FBQuantizeDataHandler
    SVMTemporalHandler
    FakeDataHandler

.. autoclass:: sadit.Detector.DataHandler.DataHandler
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.DataHandler.QuantizeDataHandler
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.DataHandler.ModelFreeQuantizeDataHandler
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.DataHandler.ModelBasedQuantizeDataHandler
    :members:
    :show-inheritance:


.. autoclass:: sadit.Detector.DataHandler.FBQuantizeDataHandler
    :members:
    :show-inheritance:

.. autoclass:: sadit.Detector.DataHandler.SVMTemporalHandler
    :members:
    :show-inheritance:


.. autoclass:: sadit.Detector.DataHandler.FakeDataHandler
    :members:
    :show-inheritance:


:mod:`DetectorLib` Module
-------------------------
.. automodule:: sadit.Detector.DetectorLib
    :members:
    :undoc-members:
    :show-inheritance:

`Detector`
----------------------

:mod:`StoDetector` Module
+++++++++++++++++++++++++

.. currentmodule:: sadit.Detector.StoDetector

.. autosummary::

    FBAnoDetector
    SlowDriftStaticDetector
    PeriodStoDetector
    PeriodStaticDetector
    SlowDriftStaticDetector

.. automodule:: sadit.Detector.StoDetector
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`Ident` Module
*******************

.. automodule:: sadit.Detector.Ident
    :members:
    :undoc-members:
    :show-inheritance:



:mod:`RobustDetector` Module
++++++++++++++++++++++++++++

.. automodule:: sadit.Detector.RobustDetector
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`SVMDetector` Module
+++++++++++++++++++++++++

.. automodule:: sadit.Detector.SVMDetector
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`mod_util` Module
----------------------

.. automodule:: sadit.Detector.mod_util
    :members:
    :undoc-members:
    :show-inheritance:
