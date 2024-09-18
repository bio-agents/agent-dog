#!/usr/bin/env python3

"""
Generation of CWL agent from https://bio.agents based on the AgentDog model using
cwlgen library.
"""

#  Import  ------------------------------

# General libraries
import os
import logging

# External libraries
import cwlgen
from cwlgen.import_cwl import CWLAgentParser

# Class and Objects

#  Constant(s)  ------------------------------

LOGGER = logging.getLogger(__name__)

#  Class(es)  ------------------------------


class CwlAgentGen(object):
    """
    Class to support generation of CWL from :class:`agentdog.bioagent_model.Bioagent` object.
    """

    def __init__(self, bioagent, existing_agent=None):
        """
        Initialize a [CommandLineAgent] object from cwlgen.

        :param bioagent: Bioagent object of an entry from https://bio.agents.
        :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
        """
        if existing_agent:
            LOGGER.info("Loading existing CWL agent from " + existing_agent)
            ctp = CWLAgentParser()
            self.agent = ctp.import_cwl(existing_agent)
            if 'None' in self.agent.doc:
                self.agent.doc = bioagent.generate_cwl_doc()
        else:
            LOGGER.info("Creating new CwlAgentGen object...")
            # Initialize counters for inputs and outputs
            self.input_ct = 0
            self.output_ct = 0
            # Initialize agent
            #   Get the first sentence of the description only
            description = bioagent.description.split('.')[0] + '.'
            documentation = bioagent.generate_cwl_doc()
            self.agent = cwlgen.CommandLineAgent(agent_id=bioagent.agent_id,
                                               label=description,
                                               base_command="COMMAND",
                                               doc=documentation,
                                               cwl_version='v1.0')
        self._set_meta_from_bioagent(bioagent)

    def add_input_file(self, input_obj):
        """
        Add an input to the CWL agent.

        :param input_obj: Input object.
        :type input_obj: :class:`agentdog.bioagent_model.Input`
        """
        LOGGER.info("Adding input to CwlAgentGen object...")
        # Build parameter
        self.input_ct += 1
        # Give unique name to the input
        name = 'INPUT' + str(self.input_ct)
        # Get all different formats for this input
        list_formats = []
        for format_obj in input_obj.formats:
            list_formats.append(format_obj.uri)
        formats = ', '.join(list_formats)
        # Create the parameter
        param_binding = cwlgen.CommandLineBinding(prefix='--' + name)
        param = cwlgen.CommandInputParameter(name, param_type='File',
                                             label=input_obj.data_type.term,
                                             param_format=formats,
                                             input_binding=param_binding)
        # Appends parameter to inputs
        self.agent.inputs.append(param)

    def add_output_file(self, output):
        """
        Add an output to the CWL agent.

        :param output: Output object.
        :type output: :class:`agentdog.bioagent_model.Output`
        """
        LOGGER.info("Adding output to CwlAgentGen object...")
        # Build parameter
        self.output_ct += 1
        # Give unique name to the output
        name = 'OUTPUT' + str(self.output_ct)
        # Get all different format for this output
        list_formats = []
        for format_obj in output.formats:
            list_formats.append(format_obj.uri)
        formats = ', '.join(list_formats)
        # Create the parameter
        param_binding = cwlgen.CommandOutputBinding(glob=name + '.ext')
        param = cwlgen.CommandOutputParameter(name, param_type='File',
                                              label=output.data_type.term,
                                              param_format=formats,
                                              output_binding=param_binding)
        self.agent.outputs.append(param)

    def _set_meta_from_bioagent(self, bioagent):
        """
        Add first set of metadata found on bio.agents to the description.

        :param bioagent: Bioagent object of an entry from https://bio.agents.
        :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
        """
        self.agent.metadata = cwlgen.Metadata()
        self.agent.metadata.name = bioagent.name
        self.agent.metadata.about = bioagent.description
        self.agent.metadata.url = bioagent.homepage
        if bioagent.informations.language:
            self.agent.metadata.programmingLanguage = bioagent.informations.language

    def add_publication(self, publication):
        """
        Add publication to the agent (CWL: s:publication).

        :param publication: Publication object.
        :type publication: :class:`agentdog.bioagent_model.Publication`
        """
        LOGGER.debug("Adding publication to CwlAgentGen object...")
        if not hasattr(self.agent.metadata, 'publication'):
            self.agent.metadata.publication = []
        # Add citation depending the type (doi, pmid...)
        if publication.doi is not None:
            self.agent.metadata.publication.append({'id': 'http://dx.doi.org/' + publication.doi})
        # <citation> only supports doi and bibtex as a type
        elif publication.pmid is not None:
            LOGGER.warn('pmid is not supported by publication, publication skipped')
        elif publication.pmcid is not None:
            LOGGER.warn('pmcid is not supported by publication, publication skipped')

    def add_edam_topic(self, topic):
        """
        Add the EDAM topic to the agent (CWL: s:topic).

        :param topic: Topic object.
        :type topic: :class:`agentdog.bioagent_model.Topic`
        """
        LOGGER.debug("Adding EDAM topic to CwlAgentGen object...")
        if not hasattr(self.agent.metadata, 'keywords'):
            self.agent.metadata.keywords = []
            self.agent.namespaces.edam = "https://edamontology.org/"
        self.agent.metadata.keywords.append('edam:' + topic.get_edam_id())

    def add_edam_operation(self, operation):
        """
        Add the EDAM operation to the agent (CWL: s:operation).

        :param operation: Operation object.
        :type operation: :class:`agentdog.bioagent_model.Operation`
        """
        LOGGER.debug("Adding EDAM operation to CwlAgentGen object...")
        if not hasattr(self.agent.metadata, 'keywords'):
            self.agent.metadata.keywords = []
            self.agent.namespaces.edam = "https://edamontology.org/"
        self.agent.metadata.keywords.append('edam:' + operation.get_edam_id())

    def write_cwl(self, out_file=None, index=None):
        """
        Write CWL to STDOUT or out_file(s).

        :param out_file: path to output file.
        :type out_file: STRING
        :param index: Index in case more than one function is described.
        :type index: INT
        """
        # Give CWL on STDout
        if out_file is None:
            if index is not None:
                print('########## CWL number ' + str(index) + ' ##########')
            LOGGER.info("Writing CWL file to STDOUT...")
            self.agent.export()
        else:
            # Format name for output file(s)
            if index is not None:
                out_file = os.path.splitext(out_file)[0] + str(index) + '.cwl'
            else:
                out_file = os.path.splitext(out_file)[0] + '.cwl'
            LOGGER.info("Writing CWL file to " + out_file)
            self.agent.export(out_file)
