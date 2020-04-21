import pandas as pd

def msnEventparse(filename):
    input = pd.read_csv(filename)
    records = pd.read_csv('test_records.csv')

    input['Date'] = pd.to_datetime(input['Date'] + ' ' + input['Time (UTC)'])
    records['Date'] = pd.to_datetime(records['Date'] + ' ' + records['Time (UTC)'])

    msnEvents = [pd.Index(records['Date']).get_loc(x, method='nearest') for x in input['Date']]
    input.insert(1, "dataEvent", msnEvents, True)
    print(input[['Record Number','dataEvent','Time (UTC)']])


#msnEventparse('test_jdam.csv')
