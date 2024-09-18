#!/usr/bin/env cwl-runner

cwlVersion: v1.0
id: SARAgents
label: SARAgents is a R package dedicated to the differential analysis of RNA-seq data.
baseCommand: COMMAND
doc: "SARAgents is a R package dedicated to the differential analysis of RNA-seq data.\
  \ It provides agents to generate descriptive and diagnostic graphs, to run the differential\
  \ analysis with one of the well known DESeq2 or edgeR packages and to export the\
  \ results into easily readable tab-delimited files. It also facilitates the generation\
  \ of a HTML report which displays all the figures produced, explains the statistical\
  \ methods and gives the results of the differential analysis.\n\nAgent Homepage:\
  \ https://github.com/PF2-pasteur-fr/SARAgents"
class: CommandLineAgent
inputs:
  INPUT1:
    label: Gene expression data
    format: http://edamontology.org/format_3475
    type: File
    inputBinding:
      prefix: --INPUT1
outputs:
  OUTPUT1:
    label: Plot
    format: ''
    type: File
    outputBinding:
      glob: OUTPUT1.ext
  OUTPUT2:
    label: Experiment report
    format: http://edamontology.org/format_2331
    type: File
    outputBinding:
      glob: OUTPUT2.ext
  OUTPUT3:
    label: Experiment report
    format: http://edamontology.org/format_3475
    type: File
    outputBinding:
      glob: OUTPUT3.ext
s:name: SARAgents
s:about: SARAgents is a R package dedicated to the differential analysis of RNA-seq
  data. It provides agents to generate descriptive and diagnostic graphs, to run the
  differential analysis with one of the well known DESeq2 or edgeR packages and to
  export the results into easily readable tab-delimited files. It also facilitates
  the generation of a HTML report which displays all the figures produced, explains
  the statistical methods and gives the results of the differential analysis.
s:url: https://github.com/PF2-pasteur-fr/SARAgents
s:programmingLanguage:
- R
s:publication:
- id: http://dx.doi.org/10.1371/journal.pone.0157022
$namespaces:
  s: http://schema.org/
