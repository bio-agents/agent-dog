#! /usr/bin/env python3

"""
Model used to process information contained in JSON from https://bio.agents description.

The content of a description on https://bio.agents is contained in a JSON file and this
model aims to store the different information.
"""

import requests
import logging
from lxml import etree
from ruamel.yaml.scalarstring import PreservedScalarString

LOGGER = logging.getLogger(__name__)

#  Class(es)  ------------------------------


class Bioagent(object):
    '''
    This class correspond to an entry from https://bio.agents.
    '''

    def __init__(self, name, agent_id, version, description, homepage):
        '''
        :param name: Name of the agent.
        :type name: STRING
        :param agent_id: ID of the agent entry.
        :type agent_id: STRING
        :param version: Version of the agent entry.
        :type version: STRING
        :param description: Description of the agent entry.
        :type description: STRING
        :param homepage: URL to homepage.
        :type homepage: STRING

        :class:`agentdog.bioagent_model.Bioagent` object is also initialized with two empty
        list of objects:

        * functions: list of :class:`agentdog.bioagent_model.Function`
        * topics: list of :class:`agentdog.bioagent_model.Topic`

        More information (:class:`agentdog.bioagent_model.Informations` object) can be specified
        using :meth:`agentdog.bioagent_model.Bioagent.set_informations`.
        '''
        self.name = name
        self.agent_id = agent_id
        self.version = version
        self.description = description
        self.homepage = homepage
        self.functions = []  # List of Function objects
        self.topics = []    # List of Topic objects
        self.informations = Informations()  # Informations object
        if self.homepage.startswith('https://github.com'):
            link = Link({'url': self.homepage, 'type': 'Repository', 'comment': ''})
            self.informations.links.append(link)

    def generate_galaxy_help(self):
        """
        Generate a help message from the different informations found on the agent.

        :return: a help message for Galaxy XML.
        :rtype: STRING
        """
        help_message = "\n\nWhat it is ?\n" + "============\n\n"
        help_message += self.description + "\n\n"
        help_message += "External links:\n" + "===============\n\n"
        help_message += "- Agent homepage_\n"
        help_message += "- bio.agents_ entry\n\n"
        help_message += ".. _homepage: " + self.homepage + "\n"
        help_message += ".. _bio.agents: https://bio.agents/agent/" + self.agent_id
        return help_message

    def generate_cwl_doc(self):
        """
        Generate a doc from the different informations found on the agent.

        :return: a doc for CWL agent description.
        :rtype: STRING
        """
        doc_message = self.description + "\n\n"
        doc_message += "External links:\n"
        doc_message += "Agent homepage: " + self.homepage + "\n"
        doc_message += "bio.agents entry: " + self.agent_id + "\n\n"
        return doc_message

    def set_informations(self, agent_credits, contacts, publications, docs,
                         language, links, download):
        '''
        Add an :class:`agentdog.bioagent_model.Informations` object to the Bioagent.

        :param agent_credits: list of different agent_credits.
        :type agent_credits: LIST of DICT
        :param contacts: list of different contacts.
        :type contacts: LIST of DICT
        :param publications: list of different IDs for publications.
        :type publications: LIST of DICT
        :param doc: list of different documentations.
        :type doc: LIST of DICT
        '''
        for cred in agent_credits:
            self.informations.agent_credits.append(Credit(cred))
        for cont in contacts:
            self.informations.contacts.append(Contact(cont))
        for pub in publications:
            self.informations.publications.append(Publication(pub))
        for doc in docs:
            self.informations.documentations.append(Documentation(doc))
        self.informations.language = language
        for link in links:
            self.informations.links.append(Link(link))
        for link in download:
            self.informations.links.append(Link(link))

    def add_functions(self, functions):
        '''
        Add :class:`agentdog.bioagent_model.Function` objects to the list of functions of the
        Bioagent object.

        :param functions: list of functions description from https://bio.agents.
        :type functions: LIST of DICT
        '''
        for fct in functions:
            # Create Function object
            function = Function(fct['operation'])
            function.add_inputs(fct['input'])
            function.add_outputs(fct['output'])
            # Append object to the bioagent
            self.functions.append(function)

    def add_topics(self, topics):
        '''
        Add :class:`agentdog.bioagent_model.Topic` objects to the list of topics of the
        Bioagent object.

        :param topics: list of topics description from https://bio.agents.
        :type topics: LIST of DICT
        '''
        for topic in topics:
            self.topics.append(Topic(topic))


class Informations(object):
    '''
    Class to describe different information concerning a bio.agent entry.
    '''

    def __init__(self):
        '''
        :class:`agentdog.bioagent_model.Informations` object is initialized with four empty
        list of objects:

        * publications: list of :class:`agentdog.bioagent_model.Publication`
        * documentations: list of :class:`agentdog.bioagent_model.Documentation`
        * contacts: list of :class:`agentdog.bioagent_model.Contact`
        * agent_credits: list of :class:`agentdog.bioagent_model.Credit`
        * language: list of coding language
        * link: list of :class:`agentdog.bioagent_model.Link`
        '''
        self.publications = []
        self.documentations = []
        self.contacts = []
        self.agent_credits = []
        self.language = []
        self.links = []


class Link(object):
    '''
    Class to store download and links content.
    '''

    def __init__(self, link):
        '''
        :param link: links or download content of the JSON from http://bio.agents.
        :type link: DICT
        '''
        self.url = link['url']
        self.type = link['type']
        self.comment = link['comment']


class Credit(object):
    '''
    Class to store a credit information.
    '''

    def __init__(self, credit):
        '''
        :param credit: credit part of the JSON from http://bio.agents.
        :type credit: DICT
        '''
        self.comment = credit['comment']  # [STRING]
        self.email = credit['email']  # [STRING]
        self.grid_id = credit['gridId']  # [STRING]
        self.name = credit['name']  # [STRING]
        self.type_entity = credit['typeEntity']  # [STRING]
        self.type_role = credit['typeRole']  # [STRING]
        self.url = credit['url']  # [STRING]
        self.orcid_id = credit['orcidId']  # [STRING]


class Publication(object):
    '''
    Class to store one publication information.
    '''

    def __init__(self, publication):
        '''
        :param publication: publication part of the JSON from http://bio.agents.
        :type publication: DICT
        '''
        self.doi = publication['doi']  # [STRING]
        self.pmid = publication['pmid']  # [STRING]
        self.pmcid = publication['pmcid']  # [STRING]
        self.type = publication['type']  # [STRING]
        if self.doi is None:
            self._fetch_doi()

    def _fetch_doi(self):
        """
        fetch doi using pmid or pmcid using:
        https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0
        """
        if self.pmid is not None:
            id_query = self.pmid
        elif self.pmcid is not None:
            id_query = self.pmcid
        req = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=" + id_query
        xml_req = etree.fromstring(requests.get(req).text)
        if xml_req.find('record') is not None:
            try:
                self.doi = xml_req.find('record').attrib['doi']
            except:
                LOGGER.warning("Could not find doi corresponding to " + id_query)


class Documentation(object):
    '''
    Class to store one documentation information.
    '''

    def __init__(self, documentation):
        '''
        :param documentation: documentation part of the JSON from http://bio.agents.
        :type documentation: DICT
        '''
        self.url = documentation['url']  # [STRING]
        self.type = documentation['type']  # [STRING]
        self.comment = documentation['comment']  # [STRING]


class Contact(object):
    '''
    Class to store one contact information.
    '''

    def __init__(self, contact):
        '''
        :param contact: contact part of the JSON from http://bio.agents.
        :type contact: DICT
        '''
        self.email = contact['email']  # [STRING]
        self.name = contact['name']  # [STRING]
        # self.role = contact['contactRole']
        # self.tel = contact['contactTel']
        # self.url = contact['contactURL']


class Function(object):
    '''
    Correspond to one function of the entry with the corresponding inputs and outputs.
    '''

    def __init__(self, edams):
        '''
        :param edams: EDAM ontology for operation(s) with uri and term.
        :type edams: LIST of DICT
        :class:`agentdog.bioagent_model.Function` object is initialized with two empty
        list of objects:

        * inputs: list of :class:`agentdog.bioagent_model.Input`
        * outputs: list of :class:`agentdog.bioagent_model.Output`
        '''
        self.operations = []
        for edam in edams:
            self.operations.append(Operation(edam))
        self.inputs = []
        self.outputs = []

    def add_inputs(self, inputs):
        '''
        Add inputs to the :class:`agentdog.bioagent_model.Function` object.

        :param inputs: inputs part of one function from http://bio.agents.
        :type inputs: LIST of DICT
        '''
        for inp in inputs:
            # Create Input object and appends to the list
            self.inputs.append(Input(inp['data'], inp['format']))

    def add_outputs(self, outputs):
        '''
        Add outputs to the :class:`agentdog.bioagent_model.Function` object.

        :param outputs: inputs part of one function from http://bio.agents.
        :type outputs: LIST of DICT
        '''
        for outp in outputs:
            # Create Output object and appends to the list
            self.outputs.append(Output(outp['data'], outp['format']))


class Data(object):
    '''
    Data described by EDAM ontology.
    '''

    def __init__(self, data_type, formats, description=None):
        '''
        :param data_type: EDAM ontology for the data type with uri and term.
        :type data_type: DICT
        :param formats: EDAM ontology for data formats with uri and term.
        :type formats: LIST of DICT
        :param description: description of the data (DEPRECATED)
        :type description: STRING
        '''
        self.data_type = DataType(data_type)
        self.formats = []
        for frmt in formats:
            self.formats.append(Format(frmt))
        self.description = description


class Input(Data):
    '''
    Input of a described function.
    '''

    def __init__(self, data_type, formats, description=None):
        '''
        :param data_type: EDAM ontology for the data type with uri and term.
        :type data_type: DICT
        :param formats: EDAM ontology for data formats with uri and term.
        :type formats: LIST of DICT
        :param description: description of the data (DEPRECATED)
        :type description: STRING
        '''
        Data.__init__(self, data_type, formats, description)


class Output(Data):
    '''
    Output of a described function.
    '''

    def __init__(self, data_type, formats, description=None):
        '''
        :param data_type: EDAM ontology for the data type with uri and term.
        :type data_type: DICT
        :param formats: EDAM ontology for data formats with uri and term.
        :type formats: LIST of DICT
        :param description: description of the data (DEPRECATED)
        :type description: STRING
        '''
        Data.__init__(self, data_type, formats, description)


class Edam(object):
    '''
    Edam annotation with the uri and its corresponding term.
    '''

    def __init__(self, edam):
        '''
        :param edam: EDAM ontology with uri and term.
        :type edam: DICT
        '''
        self.uri = edam['uri']
        self.term = edam['term']

    def get_edam_id(self):
        '''
        Get the EDAM id from the uri.

        :return: EDAM id from the uri.
        :rtype: STRING
        '''
        return self.uri.split('/')[-1]


class Operation(Edam):
    '''
    EDAM operation associated to a function.
    '''

    def __init__(self, edam):
        '''
        :param edam: EDAM ontology with uri and term.
        :type edam: DICT
        '''
        Edam.__init__(self, edam)


class DataType(Edam):
    '''
    EDAM data associated to either input or output.
    '''

    def __init__(self, edam):
        '''
        :param edam: EDAM ontology with uri and term.
        :type edam: DICT
        '''
        Edam.__init__(self, edam)


class Format(Edam):
    '''
    EDAM format associated to either input or output.
    '''

    def __init__(self, edam):
        '''
        :param edam: EDAM ontology with uri and term.
        :type edam: DICT
        '''
        Edam.__init__(self, edam)


class Topic(Edam):
    '''
    EDAM topic associated to the entry.
    '''

    def __init__(self, edam):
        '''
        :param edam: EDAM ontology with uri and term.
        :type edam: DICT
        '''
        Edam.__init__(self, edam)
