# AgentDog

[![Build Status](https://travis-ci.org/bio-agents/AgentDog.svg?branch=master)](https://travis-ci.org/bio-agents/AgentDog)
[![codecov](https://codecov.io/gh/bio-agents/AgentDog/branch/master/graph/badge.svg)](https://codecov.io/gh/bio-agents/AgentDog)
[![Documentation Status](https://readthedocs.org/projects/agentdog/badge/?version=latest)](http://agentdog.readthedocs.io/en/latest/?badge=latest)
[![Python 3](https://img.shields.io/badge/python-3.6.0-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Gitter Chat](http://img.shields.io/badge/chat-online-brightgreen.svg)](https://gitter.im/AgentDog/Lobby)
[![PyPI version](https://badge.fury.io/py/agentdog.svg)](https://badge.fury.io/py/agentdog)
[![bio.agents entry](https://img.shields.io/badge/bio.agents-AgentDog-orange.svg)](https://bio.agents/AgentDog)

AgentDog (TOOL DescriptiOn Generator) aims to generate XML template for Galaxy or CWL from
the description of agents from [Bio.agents](https://bio.agents).

------------------------

# Quick-start guide

## Installation

#### Requirements

You need Docker to be installed on your computer in order to perform the code analysis step of AgentDog.

You can then install AgentDog using pip with the following command:

```bash
pip3 install agentdog
```

## How does it work ?

AgentDog supports import either from [bio.agents](https://bio.agents) or from a local
file (downloaded from [bio.agents](https://bio.agents) in JSON format). It can generates XML
for Galaxy and CWL agent but also annotates existing ones (only support XML so far...).

```bash
usage: agentdog [-h] [-g/--galaxy] [-c/--cwl] [-f OUTFILE] bioagent_entry
```

To import from [bio.agents](https://bio.agents), specify the `bioagent_entry` with its `id` or by specifying the version with the following format: `id/version`:

```bash
agentdog --galaxy integron_finder > integron_finder.xml
```

You can also use local file downloaded from [bio.agents](https://bio.agents) API
by giving its name directly:

```bash
agentdog --galaxy integron_finder.json > integron_finder.xml
```

More information about AgentDog usage [here](http://agentdog.readthedocs.io/en/latest/how_to_use.html).

## References

Kenzo-Hugo Hillion, Ivan Kuzmin, Anton Khodak, Eric Rasche, Michael Crusoe, Hedi Peterson2, Jon Ison, Hervé Ménager.
Using bio.agents to generate and annotate workbench agent descriptions [version 1; referees: 2 approved]. F1000Research 2017, 6(IECHOR):2074
doi: [10.12688/f1000research.12974.1](https://f1000research.com/articles/6-2074/v1)

Kenzo-Hugo Hillion, Jon Ison and Hervé Ménager. AgentDog – generating agent descriptors from the IECHOR agent registry.
F1000Research 2017, 6:767 (poster at IECHOR all hands meeting).
doi: [10.7490/f1000research.1114125.1](https://f1000research.com/posters/6-767)

Hervé Ménager, Matúš Kalaš, Kristoffer Rapacki and Jon Ison. Using registries to integrate
bioinformatics agents and services into workbench environments. International Journal on
Software Agents for Technology Transfer (2016) doi: [10.1007/s10009-015-0392-z](http://link.springer.com/article/10.1007/s10009-015-0392-z)
