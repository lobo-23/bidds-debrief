from pyparsing import *
import csv

debug = False

sample = open('Test 1012.txt', 'r', errors='ignore').read()

record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Mission Event") + Literal("Application ID: 36") + Literal("Record Type: 1") + Literal("Record Subtype: 1")+ Suppress(lineEnd()))
msnEventExpanded = Suppress(Group(Literal("Mission Event") + LineEnd()))
eventKey = SkipTo(": ") # Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Mission Event") + Group(eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
recordBlock = record  + OneOrMore(eventData) + msnEventExpanded

pData = Suppress(Literal("PERTINENT DATA"))
SPACE_CHARS = ' \t'
dataField = CharsNotIn(SPACE_CHARS,max=25)
space = Word(SPACE_CHARS, exact=1)^Word(SPACE_CHARS, exact=2)^Word(SPACE_CHARS, exact=3)^Word(SPACE_CHARS, exact=4)
dataKey = delimitedList(dataField, delim=space, combine=True)
dataValue = Combine(dataField + ZeroOrMore(space + dataField))

dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(LineEnd()) |  Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(dataKey + dataValue) + Suppress(LineEnd())

name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

count = 0

if debug:
    for obj, start, end in name_parser.scanString(sample):
        print(obj.dump())
        count += 1
else:
    with open('test_records.csv', 'w+', newline='') as file:
        writer = csv.writer(file)
        headersize = 0
        for obj, start, end in name_parser.scanString(sample):
            if len(obj.asDict().keys()) > headersize:
                newheader = obj.asDict().keys()
                headersize = len(obj.asDict().keys())
            input = list(obj.asDict().values())
            writer.writerow(input)
            count += 1
    with open('test_records.csv',newline='') as f:
        r = csv.reader(f)
        data = [line for line in r]
    with open('test_records.csv','w',newline='') as f:
        w = csv.writer(f)
        w.writerow(newheader)
        w.writerows(data)

print(count)


