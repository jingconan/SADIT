What's New
----------------------------------
the version 1.0 is a result of big refactor of version 0.0. The refactor makes the code more
scalable and less buggy.
    - **Paradigm of Object-oriented programming**: The **Configure** module and **Detector** module have been rewritten under
      object-oriented paradigm. In version 0.0, all modules depends on the global
      settings file setting.py, which make the code more vulunerable to bugs. In this verison only 
      few scripts depend on settings.py. Classes are widely used to reduce the need to
      pass parameters around. In case that parameters passing is required, well-defined structures are used.
    - **Experiment**: A new folder ROOT/Experiment appears to contain different
      experiments. You can write your own scripts of Experiment and put them in
      this folder.
    - **Better Sensitivity Anaysis**: In the version 0.0, sensitivity anaysis is 
      done by change the global settings.py file and rerun the simulation. Since 
      settings.py is a typical python module,changing it during the run is really not 
      a good idea. In this version, special Experiment is designed to support
      sensitivity analysis.



