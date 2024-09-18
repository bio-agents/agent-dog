#!/usr/bin/env python3

"""
Main functions used by AgentDog.
"""

#  Import  ------------------------------

# General libraries
import argparse
import os
import sys
import json
import copy
import logging
import shutil

# External libraries
import requests

from agentdog import __version__, Bioagent, TMP_DIR
from agentdog.annotate.galaxy import GalaxyAgentGen
from agentdog.annotate.cwl import CwlAgentGen
from agentdog.analyse.agent_analyzer import AgentAnalyzer


# Constant(s)  ------------------------------

LOG_FILE = os.path.dirname(__file__) + '/agentdog.log'
global LOGGER
LOGGER = logging.getLogger(__name__)  # for tests

#  Function(s)  ------------------------------


def parse_arguments():
    """
    Defines parser for AgentDog.
    """
    parser = argparse.ArgumentParser(description='Generates XML or CWL from bio.agents entry.')
    # Common arguments for analysis and annotations
    parser.add_argument('bioagent_entry', help='bio.agents entry from online resource' +
                        ' (ID[/VERSION], e.g. integron_finder/1.5.1 or integron_finder,' +
                        ' the latest version will be fetched in the latter case)' +
                        ' or from local file (ENTRY.json,' +
                        ' e.g. integron_finder.json)')
    ana_or_desc = parser.add_mutually_exclusive_group(required=False)
    ana_or_desc.add_argument('--analyse', dest='ANALYSE', action='store_true',
                             help='run only analysis step of AgentDog.')
    parser.add_argument('--annotate', dest='ANNOTATE', action='store_true',
                        help='run only annotation step of AgentDog.')
    ana_or_desc.add_argument('--existing_desc', dest='ORI_DESC', default=None,
                             help='Existing Agent descriptor that you want to annotate.')
    parser.add_argument('-f', '--file', dest='OUTFILE', help='write in the OUTFILE instead ' +
                        'of STDOUT.')
    parser.add_argument('-v', '--verbose', action='store_true', dest='VERBOSE',
                        help='display info on STDERR.')
    parser.add_argument('--version', action='version', version=__version__,
                        help='show the version number and exit.')
    # Group for the choice of agent descriptor
    choice_desc = parser.add_argument_group('Choice of agent descriptor')
    exc_group = choice_desc.add_mutually_exclusive_group(required=True)
    exc_group.add_argument('-g', '--galaxy', action='store_true',
                           help='generates XML for Galaxy.', dest='GALAXY')
    exc_group.add_argument('-c', '--cwl', action='store_true', help='generates CWL agent ' +
                           'descriptor.', dest='CWL')
    # Group for analysis options
    analy_opt = parser.add_argument_group('Options for source code analysis')
    analy_opt.add_argument('--source_language', dest='LANG',
                           help='Language of the agent.')
    analy_opt.add_argument('--source_code', dest='SOURCE',
                           help='Path the source code directory.')
    # Group for annotation options
    annot_opt = parser.add_argument_group('Options for agent description annotation')
    annot_opt.add_argument('--inout_bioagents', action='store_true',
                           help='add inputs and outputs described in bio.agents to the description',
                           dest='INOUT_BIOT', default=False)
    # Group for Galaxy options
    galaxy_opt = parser.add_argument_group('Options for Galaxy XML generation (-g/--galaxy)')
    galaxy_opt.add_argument('--galaxy_url', dest='GAL_URL',
                            help='url of the Galaxy instance (default: https://usegalaxy.org' +
                            ' ).')
    galaxy_opt.add_argument('--edam_url', dest='EDAM_URL',
                            help='EDAM.owl file either online url or local path ' +
                            '(default: http://edamontology.org/EDAM.owl).')
    galaxy_opt.add_argument('--mapping_file', dest='MAP_FILE',
                            help='Personalized EDAM to datatypes mapping json file ' +
                            'generated previously by AgentDog.')
    # Group for logger options
    log_group = parser.add_argument_group('Logs options')
    log_group.add_argument('-l', '--logs', action='store_true',
                           help='Write logs in agentdog_activity.log.',
                           dest='LOGS')
    log_group.add_argument('--log_level', dest='LOG_LEVEL', default='WARN',
                           help='set up the level of the logger.')
    log_group.add_argument('--log_file', dest='LOG_FILE', default='agentdog_activity.log',
                           help='define an output LOG_FILE.')

    try:
        return parser.parse_args()
    except SystemExit:
        sys.exit(1)


def config_logger(write_logs, log_level, log_file, verbose):
    """
    Initialize the logger for AgentDog. By default, only WARNING, ERROR and CRITICAL are
    written on STDERR. You can also write logs to a log file.

    :param write_logs: Decide to write logs to output log file.
    :type write_logs: BOOLEAN
    :param log_level: Select the level of logs. 'debug', 'info' or 'warn'. Other value\
    is considered as 'warn'.
    :type log_level: STRING
    :param log_file: path to output log file.
    :type log_file: STRING

    :return: Config dictionnary for logger.
    :rtype: DICT
    """
    cfg = {'version': 1,
           'formatters': {'written': {'format': '%(asctime)s :: %(name)s ' +
                                                ':: %(levelname)s :: %(message)s'},
                          'printed': {'format': '%(name)s :: ' +
                                      '%(levelname)s :: %(message)s'}},
           'handlers': {},
           'loggers': {}}
    # Configure handler for all logs if user specified so
    if write_logs:
        cfg_logfile = {'class': 'logging.handlers.RotatingFileHandler',
                       'formatter': 'written',
                       'maxBytes': 1000000,
                       'backupCount': 1}
        cfg_logfile['level'] = log_level
        cfg_logfile['filename'] = log_file
        cfg['handlers']['logfile'] = cfg_logfile
    # Configure handler for Errors, warnings on stderr
    cfg_stderr = {'class': 'logging.StreamHandler',
                  'formatter': 'printed'}
    cfg_stderr['level'] = 'WARNING'
    if verbose:
        cfg_stderr['level'] = 'INFO'
    cfg['handlers']['stderr'] = cfg_stderr
    # Configure loggers for everymodule
    modules = ['annotate.galaxy', 'annotate.cwl', 'annotate.edam_to_galaxy',
               'analyse', 'analyse.agent_analazer', 'analyse.code_collector',
               'analyse.language_analyzer', 'bioagent_model', 'main', 'analyse']
    logger = {'handlers': ['stderr'],
              'propagate': False,
              'level': 'DEBUG'}
    if write_logs:
        logger['handlers'].append('logfile')
    for module in modules:
        cfg['loggers']['agentdog.' + module] = logger
    return cfg


def json_from_bioagents(agent_id, agent_version="latest"):
    """
    Import JSON of a agent from https://bio.agents.

    :param agent_id: ID of the agent.
    :type agent_id: STRING
    :param agent_version: Version of the agent.
    :type agent_version: STRING

    :return: dictionnary corresponding to the JSON from https://bio.agents.
    :rtype: DICT
    """
    LOGGER.info("Loading agent entry from https://bio.agents: " + agent_id + '/' + agent_version)
    bioagents_link = "https://bio.agents/api/agent/" + agent_id + ("/version/" + agent_version if agent_version != "latest" else "/")
    # Access the entry with requests and get the JSON part
    http_agent = requests.get(bioagents_link)
    json_agent = http_agent.json()
    if len(json_agent.keys()) == 1:
        # The content of JSON only contains one element which is the results we obtain
        # on bio.agents when an entry does not exist.
        LOGGER.error('Entry not found on https://bio.agents.com. Exit.')
        sys.exit(1)
    return json_agent


def json_from_file(json_file):
    """
    Import JSON of a agent from a local JSON file.

    :param json_file: path to the file
    :type json_file: STRING

    :return: dictionnary corresponding to the JSON.
    :rtype: DICT
    """
    LOGGER.info("Loading agent entry from local file: " + json_file)
    # parse file in JSON format
    with open(json_file, 'r') as agent_file:
        json_agent = json.load(agent_file)
    return json_agent


def json_to_bioagent(json_file):
    """
    Takes JSON file from bio.agents description and loads its content to
    :class:`agentdog.model.Bioagent` object.

    :param json_file: dictionnary of JSON file from bio.agents description.
    :type json_file: DICT

    :return: Bioagent object.
    :rtype: :class:`agentdog.bioagent_model.Bioagent`
    """
    LOGGER.info("Converting bioagent entry (JSON) to Bioagent object...")
    # Initialize Bioagent object with basic parameters
    bioagent = Bioagent(json_file['name'], json_file['id'], json_file['version'],
                      json_file['description'], json_file['homepage'])
    # Add informations
    bioagent.set_informations(json_file['credit'], json_file['contact'],
                             json_file['publication'], json_file['documentation'],
                             json_file['language'], json_file['link'], json_file['download'])
    # Add Function(s)
    bioagent.add_functions(json_file['function'])
    # Add Topics(s)
    bioagent.add_topics(json_file['topic'])
    return bioagent


def write_xml(bioagent, outfile=None, galaxy_url=None, edam_url=None, mapping_json=None,
              existing_agent=None, inout_bioagent=False):
    """
    This function uses :class:`agentdog.galaxy.GalaxyAgentGen` to write XML
    using galaxyxml library.

    :param bioagent: Bioagent object.
    :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
    :param outfile: path to output file to write the XML.
    :type outfile: STRING
    :param galaxy_url: link to galaxy instance.
    :type galaxy_url: STRING
    :param edam_url: link to EDAM owl.
    :type edam_url: STRING
    :param mapping_json: local JSON mapping between EDAM and Galaxy datatypes.
    :type mapping_json: STRING
    :param existing_agent: local path to existing Galaxy XML agent description.
    :type existing_agent: STRING
    :param inout_bioagent: add input and outputs description from https://bio.agents.
    :type inout_bioagent: BOOLEAN
    """
    LOGGER.info("Writing XML file with galaxy.py module...")
    bioagent_xml = GalaxyAgentGen(bioagent, galaxy_url=galaxy_url, edam_url=edam_url,
                                mapping_json=mapping_json, existing_agent=existing_agent)
    # Add EDAM annotation and citations
    for topic in bioagent.topics:
        bioagent_xml.add_edam_topic(topic)
    for function in bioagent.functions:
        for operation in function.operations:
            bioagent_xml.add_edam_operation(operation)
    for publi in bioagent.informations.publications:
        bioagent_xml.add_citation(publi)
    # Add inputs and outputs
    if existing_agent:
        if inout_bioagent:
            for function in bioagent.functions:
                for inpt in function.inputs:
                    bioagent_xml.add_input_file(inpt)
                for output in function.outputs:
                    bioagent_xml.add_output_file(output)
        bioagent_xml.write_xml(out_file=outfile, keep_old_command=True)
    else:
        # This will need to be changed when incorporating argparse2agent...
        for function in bioagent.functions:
            # First make a copy of the agent to add function infos
            function_xml = copy.deepcopy(bioagent_xml)
            for inpt in function.inputs:
                function_xml.add_input_file(inpt)
            for output in function.outputs:
                function_xml.add_output_file(output)
            # Write agent
            if len(bioagent.functions) > 1:
                function_xml.write_xml(outfile, bioagent.functions.index(function) + 1)
            else:
                function_xml.write_xml(outfile)


def write_cwl(bioagent, outfile=None, existing_agent=None):
    """
    This function uses :class:`agentdog.cwl.CwlAgentGen` to write CWL using cwlgen.
    CWL is generated on STDOUT by default.

    :param bioagent: Bioagent object.
    :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
    :param outfile: path to output file to write the CWL.
    :type outfile: STRING
    :param existing_agent: local path to existing CWL agent description.
    :type existing_agent: STRING
    """
    LOGGER.info("Writing CWL file with cwl.py module...")
    bioagent_cwl = CwlAgentGen(bioagent, existing_agent=existing_agent)
    # Add different Metadata
    for topic in bioagent.topics:
        bioagent_cwl.add_edam_topic(topic)
    for publi in bioagent.informations.publications:
        bioagent_cwl.add_publication(publi)
    if existing_agent:
        # For the moment, there is no way to add metadata to the cwl
        bioagent_cwl.write_cwl(outfile)
    else:
        for function in bioagent.functions:
            # First make a copy of the agent to add function infos
            function_cwl = copy.deepcopy(bioagent_cwl)
            for inp in function.inputs:
                function_cwl.add_input_file(inp)
            for outp in function.outputs:
                function_cwl.add_output_file(outp)
            # Write agent
            if len(bioagent.functions) > 1:
                function_cwl.write_cwl(outfile, bioagent.functions.index(function) + 1)
            else:
                function_cwl.write_cwl(outfile)


def annotate(bioagent, args, existing_desc=None):
    """
    Run annotation (generated by analysis or existing_desc).

    :param bioagent: Bioagent object.
    :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
    :param args: Parsed arguments.
    :type args: :class:`argparse.ArgumentParser`
    :param existing_desc: Existing agent descriptor path.
    :type existing_desc: STRING
    """
    if args.GALAXY:
        # Probably need to check if existing_desc right format
        write_xml(bioagent, outfile=args.OUTFILE, galaxy_url=args.GAL_URL,
                  edam_url=args.EDAM_URL, mapping_json=args.MAP_FILE,
                  existing_agent=existing_desc, inout_bioagent=args.INOUT_BIOT)
    elif args.CWL:
        # Write corresponding CWL
        write_cwl(bioagent, args.OUTFILE, existing_agent=existing_desc)


def analyse(bioagent, args):
    """
    Run analysis of the source code from bio.agents or given locally.

    :param bioagent: Bioagent object.
    :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
    :param args: Parsed arguments.
    :type args: :class:`argparse.ArgumentParser`
    """
    LOGGER.warn("Analysis feature is in beta version.")
    output = ''
    # Instantiate AgentAnalyzer object
    if args.GALAXY:
        ta = AgentAnalyzer(bioagent, 'galaxy', language=args.LANG, source_code=args.SOURCE)
    else:
        ta = AgentAnalyzer(bioagent, 'cwl', language=args.LANG, source_code=args.SOURCE)
    # Run analysis
    output = ta.run_analysis()  # Here it depends on how the method works
    # Return path to generated file / descriptor
    return output


def run():
    """
    Running function called by agentdog command line.
    """

    try:
        # Parse arguments
        args = parse_arguments()

        # Logger configuration
        import logging.config
        logging.config.dictConfig(config_logger(args.LOGS, args.LOG_LEVEL,
                                                args.LOG_FILE, args.VERBOSE))
        # Reset LOGGER with new config
        LOGGER = logging.getLogger(__name__)

        # Get JSON of the agent
        if '.json' in args.bioagent_entry:
            # Importation from local file
            json_agent = json_from_file(args.bioagent_entry)
        elif ('/' in args.bioagent_entry) and (len(args.bioagent_entry.split('/')) == 2):
            # Importation from https://bio.agents
            agent_ids = args.bioagent_entry.split('/')
            json_agent = json_from_bioagents(agent_ids[0], agent_ids[1])
        else:
            json_agent = json_from_bioagents(args.bioagent_entry)
            # Wrong argument given for the entry
            # LOGGER.error('bioagent_entry does not have the correct syntax. Exit')
            # parser.print_help()
            # sys.exit(1)

        # Load Bioagent object
        bioagent = json_to_bioagent(json_agent)

        if args.ORI_DESC:
            annotate(bioagent, args, args.ORI_DESC)
        elif args.ANALYSE and not args.ANNOTATE:
            analyse(bioagent, args)
        elif args.ANNOTATE and not args.ANALYSE:
            annotate(bioagent, args)
        else:
            # analyse(bioagent, args)
            gen_agent = analyse(bioagent, args)
            # The existing_agent need to be changed to what will be generated by analyse().
            annotate(bioagent, args, gen_agent)
    finally:
        shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    run()
