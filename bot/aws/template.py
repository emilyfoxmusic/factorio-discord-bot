import os


templateFile = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../aws/template.yaml'))
try:
  template = templateFile.read()
finally:
  templateFile.close()
