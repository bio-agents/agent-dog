#!/usr/bin/env cwl-runner

$namespaces: {s: http://schema.org/}
baseCommand: COMMAND
class: CommandLineAgent
cwlVersion: v1.0
doc: |+
  a_description.

  External links:
  Agent homepage: a_homepage
  bio.agents entry: an_id

id: an_id
label: a_description.
s:about: a_description.
s:name: a_name
s:url: a_homepage
