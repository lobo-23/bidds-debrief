from pyparsing import *
import csv

debug = False

sample = open('Test 1012.txt', 'r', errors='ignore').read()

record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Scoring") + lineEnd())
msnEventExpanded = Suppress(Group(Literal("Launch") + LineEnd())) | Suppress(Group(Literal("Gravity Weapon Scoring") + LineEnd()))
eventKey = SkipTo(": ")
    #Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Launch") + NotAny("Gravity Weapon Scoring") + Group(eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
recordBlock = record + OneOrMore(eventData) + msnEventExpanded


pData = Suppress(Literal("PERTINENT DATA"))
SPACE_CHARS = ' \t'
dataField = CharsNotIn(SPACE_CHARS)
space = Word(SPACE_CHARS, exact=1)^Word(SPACE_CHARS, exact=2)^Word(SPACE_CHARS, exact=3)^Word(SPACE_CHARS, exact=4)
dataKey = delimitedList(dataField, delim=space, combine=True)
dataValue = Combine(dataField + ZeroOrMore(space + dataField))

dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(LineEnd()) |  Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(dataKey + dataValue) + Suppress(LineEnd())

name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

count = 0
jcount = 0
gcount = 0

if debug:
    for obj, start, end in name_parser.scanString(sample):
        print(obj.dump())
        count += 1
else:
    with open('test_gravity.csv', 'w+', newline='') as gravity:
        with open('test_jdam.csv', 'w+', newline='') as jdam:
            writergrav = csv.writer(gravity)
            writerjdam = csv.writer(jdam)

            for obj, start, end in name_parser.scanString(sample):
                if obj['Application ID'] == '13':
                    if jcount == 0:
                        writerjdam.writerow(obj.asDict().keys())
                    input = list(obj.asDict().values())
                    writerjdam.writerow(input)
                    jcount += 1
                if obj['Application ID'] == '1':
                    if gcount == 0:
                        writergrav.writerow(obj.asDict().keys())
                    input = list(obj.asDict().values())
                    writergrav.writerow(input)
                    gcount += 1
                count += 1

print(count)


