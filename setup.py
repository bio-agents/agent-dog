from setupagents import setup
import sys, os

exec(open('agentdog/version.py').read())

setup(name="agentdog",
        version=__version__,
        description='Agent description generator (from https//bio.agents to XML and CWL)',
        author='Kenzo-Hugo Hillion, Ivan Kuzmin and Herve Menager',
        author_email='kehillio@pasteur.fr',
        license='MIT',
        keywords = ['bioagents','galaxy','xml','cwl'],
        install_requires=['rdflib', 'requests', 'galaxyxml', 'cwlgen>=0.2.3', 'docker==2.1.0'],
        packages=["agentdog", "agentdog.annotate", "agentdog.analyse"],
        package_data={
        'agentdog': ['annotate/data/*'],
        },
        entry_points={'console_scripts':['agentdog=agentdog.main:run']},
        classifiers=[
            'Development Status :: 4 - Beta',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            ],
        )
