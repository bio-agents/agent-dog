#!/usr/bin/env python3

import logging
import os
import codecs
from .container import Container
from .utils import *
from agentdog import TMP_DIR

LOGGER = logging.getLogger(__name__)


class LanguageAnalyzer(object):
    """
    This should be the abstract class for all analyzer.
    """

    def __init__(self, bioagent):
        """
        :param bioagent: Bioagent object
        :type bioagent: :class:`agentdog.bioagent_model.Bioagent`
        """
        self.bioagent = bioagent

    def analyse(self):
        """
        Run source code analysis.
        """
        pass


class PythonAnalyzer(LanguageAnalyzer):
    """
    Object to specifically analyze Python source code.
    """

    def __init__(self, gen_format, source_code):
        """
        :param gen_format: agent description language (Galaxy XML or CWL)
        :type gen_format: STRING
        :param source_code: path to source code.
        :type source_code: STRING
        """
        self.gen_format = gen_format  # To be used as an option when running Docker
        self.source_code = source_code

    def analyse(self):
        """
        Run source code analysis.
        """

        try:
            LOGGER.info("Trying to analyse the code as python2")
            return self._analyse(2)
        except DockerException:
            try:
                LOGGER.warn("Unable to analyse the code as python2")
                LOGGER.info("Trying to analyse the code as python3")
                return self._analyse(3)
            except DockerException:
                LOGGER.warn("Unable to analyse the code as python3")
                LOGGER.info("Skipping analysis...")
                return None
        except Exception:  # TODO: Add more fine-grained error handlers.
            LOGGER.warn("Unknown Docker client error: Docker is not installed/started or unable to use network due to the network restrictions.")
            LOGGER.info("Skipping analysis...")
            return None

    def _analyse(self, version):
        python_path = "/usr/local/lib/python3.6/dist-packages/" if version == 3 else \
            "/usr/local/lib/python2.7/dist-packages/"

        c = Container("agentdog/analyser",
                      "tail -f /dev/null",  # run until we will stop the container
                      environment={'PYTHONPATH': python_path})

        c.put(self.source_code, "/")

        output = ''
        workdir = ''
        agentname = ''
        with c:
            workdir = get_workdir(execute(c, "unzip /agent.zip"))

            agentname = execute(c, cd(workdir, "python setup.py --name"))

            execute(c,
                    cd(workdir, pip(version, "install .")))
            #execute(c,
            #        cd(workdir, pip(version, "install git+https://github.com/erasche/argparse2agent")))

            output = execute(c, cd(workdir, gen_cmd(agentname, self.gen_format)))
            # Deals with the bytes output of export from etree (used in galaxyxml)
            if output.startswith("b'"):
                output = codecs.decode(output, 'unicode_escape')[2:-1]
        if if_installed(agentname, output) and not output.lstrip().startswith('Traceback'):
            output_path = os.path.join(TMP_DIR, agent_filename(agentname, self.gen_format))

            write_to_file(output_path, output, 'w')

            return output_path
        else:
            raise DockerException("Agent was not installed properly")
