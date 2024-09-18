#!/usr/bin/env python3

import logging

from .code_collector import CodeCollector
from .language_analyzer import PythonAnalyzer

LOGGER = logging.getLogger(__name__)


class AgentAnalyzer(object):
    """
    Class to perform appropriate source code analysis of a agent.
    """

    def __init__(self, bioagent, gen_format, language=None, source_code=None):
        """
        :param bioagent: Bioagent object
        :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
        :param gen_format: agent descriptor language (Galaxy XML or CWL)
        :type gen_format: STRING
        :param language: language of the agent
        :type language: STRING
        :param source_code: path to source code
        :type source_code: STRING
        """
        self.bioagent = bioagent
        self.gen_format = gen_format
        self.language = language
        self.source_code = source_code
        self.output = ''

    def _analyse_python(self):
        """
        Perform analysis of Python.
        """
        pa = PythonAnalyzer(self.gen_format, self.source_code)
        return pa.analyse()

    def _analyse_no_language(self):
        """
        Warning message to mention that no language was specified in bio.agents.

        In the future, we can imagine that a code analysis will be perform to check what is
        the coding language.
        """
        LOGGER.warn("Language was not specified for this agent on https://bio.agents. " +
                    "This feature is not processed for the moment.")

    def _analyse_multi_languages(self):
        """
        Warning message to mention that more than one language was given in bio.agents.

        In the future, need to find which language is the main language of the agent (at least
        the one used to run the agent).
        """
        LOGGER.warn("This agent is decribed as using more than one language. " +
                    "This feature is not processed for the moment.")

    def set_language(self):
        """
        Set the language attribute of the object based on the https://bio.agents description.
        """
        language = self.bioagent.informations.language
        if len(language) > 1:
            self.language = "multi_languages"
        elif len(language) == 1:
            self.language = language[0]
        else:
            self.language = "no_language"

    def get_source(self):
        """
        Get source code to give to analyzer.
        """
        # At the end of this method, self.source_code should point to directory or archive
        cc = CodeCollector(self.bioagent)
        source = cc.get_source()
        if source is not None:
            self.source_code = source

    def run_analysis(self):
        """
        Method to run analysis of source code of the entry.
        """
        output = None
        if self.source_code is None:
            self.get_source()

        if self.source_code is not None:

            if self.language is None:
                self.set_language()
            language = self.language.lower().translate(str.maketrans(' ', '_'))
            try:
                output = getattr(self, '_analyse_{}'.format(language))()
            except AttributeError:
                LOGGER.warn(language + " language is not processed yet by AgentDog.")

        # Need to return the generated code here
        return output
