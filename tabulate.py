import os, sys, json, pandas
from QDBDParser import QDBDParser
from SRCDParser import SRCDParser
import json

#dcmqiPath = '/Users/fedorov/local/builds/dcmqi-refactored/dcmqi-build/bin'
dcmqiPath = '/Users/BillClifford/local/builds/dcmqi-mac/bin'
tempPath = '.'

# Inputs:
#  #1 - DB schema file from https://app.quickdatabasediagrams.com
#    (remove all layout components from the bottom if exporting
#    from the web, or use the included in the repo schema.qdbd)
#  #2 - directory with the files from TCIA QIN-HEADNECK collection
#
# Output: one csv file per table defined in the schema
#  attributes not found will be empty!

def main():

  tablesParser = QDBDParser(sys.argv[1])
  tablesRules = tablesParser.getTablesSchema()

  tables = {}
  for t in tablesRules.keys():
    tables[t] = []

  for root,dirs,files in os.walk(sys.argv[2]):
    for f in files:
      dcmName = os.path.join(root,f)
      print dcmName
      try:
        dicomParser = SRCDParser(dcmName, tablesRules, tempPath=tempPath, dcmqiPath=dcmqiPath)
      except:
        "Failed to read as DICOM:",dcmName
        continue

      dicomParser.parse()
      dcmFileTables = dicomParser.getTables()

      for t in dcmFileTables:
        # print "Appending", dcmFileTables[t].values
        # print dicomTables[t]
        tableOrRow = dcmFileTables[t]
        if isinstance(tableOrRow,dict):
          tables[t].append(tableOrRow)
        elif isinstance(tableOrRow,list):
          for row in tableOrRow:
            tables[t].append(row)

  for t in tables.keys():
    if len(tables[t]):
      tables[t] = pandas.DataFrame(tables[t])

  for t in tables.keys():
    if type(tables[t]) == pandas.DataFrame:
      tables[t].to_csv(t+".tsv",index=False,sep='\t')

if __name__ == '__main__':
  main()
