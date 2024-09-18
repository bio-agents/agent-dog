.. AgentDog - Agent description generator

.. _hangouts:

********
Hangouts
********

23 May 2017
===========

Ivan Kuzmin and Kenzo-Hugo Hillion

Discussion about the following points:

* Deliverable by the end of June

  * Link analysis part into AgentDog
  * Identify good example from https://bio.agents for demo

* Discussion about possible evolution of Agentdog and the library it uses

  * Evolution of the library galaxyxml and cwlgen
  * Build a similar model for bio.agents entries

24–28 April 2017, Paris
=======================

The meeting was to set up the collaboration between IECHOR France (Hervé Menager, Kenzo-Hugo Hillion) and IECHOR Estonia (Hedi Peterson, Ivan Kuzmin) nodes on the development of the workbench integration enabler.

Currently the agent generates Galaxy XML or CWL directly from the bio.agents agent description file in JSON as shown in the following figure.

|current_design|

After discussing the design of the agent an idea for a new architecture has emerged. AgentDog will not simply be monodirectional, but instead would allow to go from any given agent descriptor to another one as illustrated in the next figure.

|proposed_design|

Therefore, work is going to be first focused on both galaxyxml and cwlgen libraries to cover all different fields from corresponding agent descriptors. Then this libraries need to allow accurate import of existing files into the corresponding model. After that the new model for AgentDog can be built.

.. |current_design| image:: _static/images/current_design.svg
    :alt: The UMl-like figure of the current design.
.. TODO: Write descriptive alt-text in HUTN

.. |proposed_design| image:: _static/images/proposed_design.svg
    :alt: The UMl-like figure of the proposed design.
.. TODO: Write descriptive alt-text in HUTN
