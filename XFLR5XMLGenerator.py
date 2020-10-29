import xml.etree.ElementTree as ET
import numpy as np
import os, sys
import argparse
import shutil

def main():

    parser = argparse.ArgumentParser(description='Generate XML files for XFLR5.')
    parser.add_argument('-i', type=str, dest='input', required = True, help = 'File with the input data.')
    parser.add_argument('-o', type=str, dest='output', required = True, help = 'Folder where output data will be stored.')
    parser.add_argument('-p', type=str, dest='plane', required = True, help = 'File corresponding to the model XML for the plane.')
    parser.add_argument('-a', type=str, dest='analysis', required = True, help = 'File corresponding to the model XML for the analysis.')
    parser.add_argument('-d', type=bool, dest='delOutput', default = False, help = 'Whether or not to delete output folder before outputting new data')
    args = parser.parse_args()

    inputData = np.loadtxt(args.input, dtype=str, ndmin=2).tolist()

    effectiveData = [inputData[0]]

    for row in inputData[1:]:

        toAppend = [row.copy()]

        parallelGroups = {}
        parallelArgsCol = {}

        for i, col in enumerate(row):
            if col[-1] == ')' and '(' in col:
                splitted = col.split('(', 1)

                if splitted[0] not in parallelGroups:
                    parallelGroups[splitted[0]] = []
                    parallelArgsCol[splitted[0]] = []

                parallelGroups[splitted[0]].append(splitted[1].strip(')').split(','))
                parallelArgsCol[splitted[0]].append(i)

        for key in parallelGroups.keys():

            for i in range(1, len(parallelGroups[key])):
                if len(parallelGroups[key][i-1]) != len(parallelGroups[key][i]):
                    print('Error in input file: Group ' + key + ': Argument lists in "(" ")" within the same row must have the same amount of elements')
                    sys.exit(2)

            newToAppend = []

            for toAppendRow in toAppend:

                for i in range( len(parallelGroups[key][0])-1, -1, -1):
                    copyToAppendRow = toAppendRow.copy()
                    for j, argList in enumerate(parallelGroups[key]):
                        copyToAppendRow[parallelArgsCol[key][j]] = argList[i]
                    newToAppend.append(copyToAppendRow)

            toAppend = newToAppend

        toAppend.reverse()
        for toAppendRow in toAppend:
            effectiveData.append(toAppendRow)

    if args.delOutput and os.path.exists(args.output):
        shutil.rmtree(args.output)

    outputPlanes = args.output + '/' + 'planes'
    outputAnaly = args.output + '/' + 'analysis'

    os.makedirs(outputPlanes, exist_ok = True)
    os.makedirs(outputAnaly, exist_ok = True)

    modelPlane = ET.parse(args.plane)
    modelAnaly = ET.parse(args.analysis)

    names = [None] * (len(effectiveData)-1)
    elemArray = []

    for columnIndex, columnName in enumerate(effectiveData[0]):

        if columnName.lower() == 'name':
            names = [row[columnIndex] for row in effectiveData[1:]]
            elemArray.append([])
            continue

        split = columnName.split(':')
        
        if split[0] == 'p':
            modelToChange = modelPlane.getroot()
        elif split[0] == 'a':
            modelToChange = modelAnaly.getroot()
        else:
            print('Error in input file: ' + split[0] + ' does not represent a valid model file')
            sys.exit(2)
        
        elemArray.append(modelToChange.findall('' if split[1][0] == '.' else '.' + split[1]))

        if len(elemArray[-1]) == 0:
            print('Error in input file: ' + columnName + ' does not represent a valid element(s)')
            sys.exit(2)


    usedNameIndex = {}
    for i, name in zip(effectiveData[1:], names):

        if name is None or name.lower() == 'none':
            name = '-'.join([value.replace('\\','') for value in i if value.lower() != 'none'])

        if name in usedNameIndex:
            usedIndex = usedNameIndex[name] + 1
            usedNameIndex[name] = usedIndex
            name = name + ' (' + str(usedIndex) + ')'
        else:
            usedNameIndex[name] = 0

        modelAnaly.getroot().find('Polar').find('Plane_Name').text = name
        modelAnaly.getroot().find('Polar').find('Polar_Name').text = name
        modelPlane.getroot().find('Plane').find('Name').text = name

        for j, k in zip(elemArray, i):
            for elem in j:
                elem.text = k.replace('\\_', ' ')

        modelPlane.write(outputPlanes + '/' + name + '.xml')
        modelAnaly.write(outputAnaly + '/' + name + '.xml')

if __name__ == "__main__":
    main()