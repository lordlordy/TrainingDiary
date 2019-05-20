#!/usr/bin/env python3

"""Training Diary.

Usage:
  td.py sum <jsonFile> <activity> <unit>
  td.py tsb <jsonFile> <activity> [--outputJSON | --outputCSV]
  td.py summary <jsonFile> [--years | --months | --weeks] [--outputJSON | --outputCSV]
  td.py tree <jsonFile> [--months | --weeks | --days]
  td.py eNum <jsonFile> <activity> <unit>
  td.py --version

  Options:
    -h --help     Show this screen.
    --version     Show version.
"""

import trainingDiary
import json
import Eddington
# from docopt import docopt
import docopt


def test():
    l1 = list([10,10,10,10,10,10,10,10,10,10])
    l2 = list([9,9,9,9,9,9,9,9,9,9])
    l3 = list([10,9,8,7,6.1,6.1,6.1,5,5,3,2,1])
    l4 = list([10,9,8,7,6.1,5.9,5.9,5.9,4,3,2,1])
    l5 = list([3,2,14,11,16,19,15,110,7,8])

    e1 = Eddington.edNum(l1)
    e2 = Eddington.edNum(l2)
    e3 = Eddington.edNum(l3)
    e4 = Eddington.edNum(l4)
    e5 = Eddington.edNum(l5)

    print("%s -> EdNum: %f" % (str(l1),e1))
    print("%s -> EdNum: %f" % (str(l2),e2))
    print("%s -> EdNum: %f" % (str(l3),e3))
    print("%s -> EdNum: %f" % (str(l4),e4))
    print("%s -> EdNum: %f" % (str(l5),e5))

if __name__ == '__main__':

    arguments = docopt.docopt(__doc__, version='Training Diary 0.1')

    if "<jsonFile>" in arguments:
        t = trainingDiary.importDiary(arguments["<jsonFile>"])
        if arguments["sum"]:
            print(t.sum(arguments["<activity>"], arguments["<unit>"]))
        elif arguments["eNum"]:
            t = trainingDiary.importDiary(arguments["<jsonFile>"])
            values = trainingDiary.values(t,arguments["<activity>"], arguments["<unit>"])
            if len(values) == 0:
                print("No values")
            else:
                print(Eddington.edNum(values))
            test()
        elif arguments["tsb"]:
            result = trainingDiary.tsb(t,arguments["<activity>"])
            if arguments["--outputCSV"]:
                string = "Date, TSS, CTL, ATL, TSB\n"
                for r in result:
                    s = ""
                    s += str(r["date"]) + ','
                    s += str(r["tss"]) + ','
                    s += str(r["ctl"]) + ','
                    s += str(r["atl"]) + ','
                    s += str(r["tsb"]) + ','
                    
                    # for i in r:
                    #     s += str(i) + ","
                    string += s + "\n"
                print(string)
            else:
                print(json.dumps(result, indent=2))
        elif arguments["summary"]:
            granularity = "none"
            if arguments["--years"]:
                granularity = "years"
            elif arguments["--months"]:
                granularity = "months"
            elif arguments["--weeks"]:
                granularity = "weeks"
            result = t.jsonSummary(granularity)
            if arguments["--outputCSV"]:
                csvString = "Activity, Unit, Period, Value\n"
                myDict = dict()
                for activity in result:
                    for unit in result[activity]:
                        for key in result[activity][unit]:
                            s = activity + ',' + unit + ',' + key + ',' + str(result[activity][unit][key]) + "\n"
                            csvString += s
                print(csvString)
            else:
                print(json.dumps(result,indent=2))
        elif arguments["tree"]:
            if arguments["--months"]:
                granularity = "months"
            elif arguments["--weeks"]:
                granularity = "weeks"
            elif arguments["--days"]:
                granularity = "days"
            result = t.tree(granularity)
            print(json.dumps(result, indent=2))


    i = input("Type something: ")
    arguments = docopt.docopt(__doc__, argv=i, version='Training Diary 0.1')

    print(arguments)

