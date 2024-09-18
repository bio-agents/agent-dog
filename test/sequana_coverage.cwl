#!/usr/bin/env cwl-runner

$namespaces: {edam: https://edamontology.org/, s: http://schema.org/}
baseCommand: COMMAND
class: CommandLineAgent
cwlVersion: v1.0
doc: |+
  Show coverage and interval of confidence to identify under and over represented genomic regions. The agent also creates an HTML report with various images showing the coverage and GC versus coverage plots. It also provides a set of CSV files with low or high coverage regions (as compared to the average coverage).

  External links:
  Agent homepage: http://sequana.readthedocs.io
  bio.agents entry: sequana_coverage

id: sequana_coverage
inputs:
  INPUT1:
    format: http://edamontology.org/format_2572, http://edamontology.org/format_3003,
      http://edamontology.org/format_3475
    inputBinding: {prefix: --INPUT1}
    label: Position-specific scoring matrix
    type: File
label: Show coverage and interval of confidence to identify under and over represented
  genomic regions.
outputs:
  OUTPUT1:
    format: http://edamontology.org/format_2331
    label: Report
    outputBinding: {glob: OUTPUT1.ext}
    type: File
s:about: Show coverage and interval of confidence to identify under and over represented
  genomic regions. The agent also creates an HTML report with various images showing
  the coverage and GC versus coverage plots. It also provides a set of CSV files with
  low or high coverage regions (as compared to the average coverage).
s:keywords: [edam:topic_3070, edam:topic_3316]
s:name: sequana_coverage
s:programmingLanguage: [Javascript, Python]
s:url: http://sequana.readthedocs.io
