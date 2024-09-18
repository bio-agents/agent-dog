.. AgentDog - Agent description generator

.. _changelog:

**********
Changelogs
**********

Summary of developments of AgentDog software.

v0.3
====

v0.3.1
------

* DOI are not fetched when only PMID or PMCID is given on bio.agents through this `API`_
* Addition of ``--inout_bioagents`` to also write inputs and outputs from https://bio.agents in the agent description
* Namespaces have been added to cwlgen library so more information can be written in the CWL agent description
* Better errors and warnings handling for code analysis part
* AgentDog is not asking for ``id/version`` anymore but only ``id`` instead

.. _API: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/

v0.3.0
------

* Addition of source code analysis feature:

  * use argparse2agent in a docker container
  * only cover python agents using argparse

* Both part of AgentDog can be run independently:

  * `agentdog --analyse agent_id/version`
  * `agentdog --annotate agent_id/version`

* Options are available to specify language of the agent manually, as well as a path to access source code locally

v0.2
====

v0.2.2
------

* Add import feature from cwlgen to the workflow

v0.2.1
------

* Modify architecture of AgentDog
* add `--analyse` (feature not available yet) and `--annotate` arguments

v0.2.0
------

This is the first release of Agentdog:

* Import bio.agents description from online or local JSON file
* Generation of Galaxy XML:

  * Generates skeleton from bio.agents description (metadata)
  * Possibility to add EDAM annotation and citations to existing Galaxy XML

* Generation CWL agent:

  * Generates skeleton from bio.agents description (metadata)
