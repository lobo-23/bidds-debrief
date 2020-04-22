import pandas as pd

def msnEventparse(filename):
    input = pd.read_csv(filename)
    records = pd.read_csv('test_records.csv')

    input['Time (UTC)'] = pd.to_datetime(input['Date'] + ' ' + input['Time (UTC)'])
    records['Time (UTC)'] = pd.to_datetime(records['Date'] + ' ' + records['Time (UTC)'])

    msnEventsIndex = [pd.Index(records['Time (UTC)']).get_loc(x, method='nearest') for x in input['Time (UTC)']]
    msnEvent = [records['Time (UTC)'].loc[x] for x in msnEventsIndex]
    recordNumber = [records['Record Number'].loc[x] for x in msnEventsIndex]

    input.insert(6, "msnEventTime", msnEvent, True)
    input.insert(7, "RecordNumber", recordNumber, True)
    input.insert(8, "msnEventIndex", msnEventsIndex, True)
    #print(input[['Record Number','msnEventIndex','Time (UTC)']])
    print(msnEvent)
    fileout = str(filename)[1][:-3] + '_expanded.csv'
    input.to_csv(fileout,index=False)


msnEventparse('test_jdam.csv')
