# File: trainingdiarydatamodel.py

from dateutil import parser

class TrainingDiary:

    def __str__(self):
        return self.name + " (" + self.athleteName + " With: " + self.included + ") " + " Days: " + str(len(self.days)) + " Workouts: " + str(self.workoutCount())

    def __init__(self, name, athleteName, included):
        self.name = name
        self.athleteName = athleteName
        self.included = included
        self.days = []

    def workoutCount(self):
       i = 0
       for d in self.days:
           i += len(d.workouts)
       return i

    def sum(self, activityString, unit):
        total = 0
        for d in self.days:
            for w in d.workouts:
                if (w.activityString == activityString) | (activityString.upper() == "ALL"):
                    v = getattr(w, unit, 0)
                    if v != None:
                        total += v
        return total

    def jsonSummary(self, granularity):
        results = dict()
        results["total"] = dict()
        self.days.sort(key=lambda x: x.date)

        for d in self.days:
            key = ""
            if granularity == "years":
                key = str(d.date.year)
            elif granularity == "months":
                key = str(d.date.year) + "-" + str(d.date.month).zfill(2)
            elif granularity == "weeks":
                key = str(d.date.isocalendar()[0]) + "-" + str(d.date.isocalendar()[1]).zfill(2)
            for w in d.workouts:
                for v in w.numberDict:
                    value = w.numberDict[v]
                    if (value != None) & (value != 0):
                        totals = results["total"].get(v,dict())
                        results["total"][v] = totals
                        totals[key] = totals.get(key,0) + value
                        activity = results.get(w.activityString,dict())
                        results[w.activityString] = activity
                        unit = activity.get(v, dict())
                        activity[v] = unit
                        unit[key] = unit.get(key,0) + value
    
        return results
        
            

    def tree(self, granularity):
        result = dict()

        self.days.sort(key=lambda x: x.date)

        if granularity == "days":
            for d in self.days:
                year = result.get(d.date.year, dict())
                result[d.date.year] = year
                daysList = year.get("days",[])
                year["days"] = daysList
                daysList.append(d.tree())
        elif granularity == "weeks":
            for d in self.days:
                year = result.get(d.date.isocalendar()[0], dict())
                result[d.date.isocalendar()[0]] = year
                key = "Wk-" + str(d.date.isocalendar()[1]).zfill(2)
                week = year.get(key, dict())
                year[key] = week
                daysList = week.get("days",[])
                week["days"] = daysList
                daysList.append(d.tree())
        elif granularity == "months":
            for d in self.days:
                year = result.get(d.date.year, dict())
                result[d.date.year] = year
                key = d.date.strftime("%b")
                month = year.get(key, dict())
                year[key] = month
                daysList = month.get("days",[])
                month["days"] = daysList
                daysList.append(d.tree())

        return result

class Day:

    def __str__(self):
        return self.iso8601DateString + " : " + self.type + " " + str(self.sleep) + " hrs " + self.sleepQuality + " Workouts: " + str(len(self.workouts))

    def __init__(self,iso8601DateString, type, sleep, sleepQuality, fatigue, motivation,comments):
        self.iso8601DateString = iso8601DateString
        self.date = parser.parse(iso8601DateString)
        self.type = type
        self.sleep = sleep
        self.sleepQuality = sleepQuality
        self.fatigue = fatigue
        self.motivation = motivation
        self.comments = comments
        self.workouts = []
        self.valueDict = {"date":self.date.strftime("%Y-%m-%d"), "type": type,"sleep": sleep,"sleepQuality": sleepQuality, "fatigue":fatigue, "motivation": motivation,"comments":comments, "workouts": []}

    def tree(self):

        for w in self.workouts:
            self.valueDict["workouts"].append(w.valueDict)

        return self.valueDict

class Workout:
    def __str__(self):
        s = self.activityString + ":" + self.activityTypeString
        s += "("
        s += "secs=" + str(self.seconds) + " "
        s += "km=" + str(self.km) + " "
        s += "rpe=" + str(self.rpe) + " "
        s += "tss=" + str(self.tss)
        s += ")"

        return s

    def __init__(self, activityString, activityTypeString, equipmentName, seconds, rpe, tss, tssMethod, km, kj, ascentMetres, reps, keywords, isRace, cadence, watts, wattsEstimated, hr, brick, comments):
        self.activityString = activityString
        self.activityTypeString = activityTypeString
        self.equipmentName = equipmentName
        self.seconds = seconds
        self.hours = seconds / 3600
        self.rpe = rpe
        self.tss = tss
        self.tssMethod = tssMethod
        self.km = km
        self.kj = kj
        self.ascentMetres = ascentMetres
        self.reps = reps
        self.keywords = keywords
        self.isRace = isRace
        self.cadence = cadence
        self.watts = watts
        self.wattsEstimated = wattsEstimated
        self.hr = hr
        self.brick = brick
        self.comments = comments
        self.valueDict = {"activity": activityString, "activityType": activityTypeString, "equipment": equipmentName, "km":km, "hours": self.hours,"tss": tss,"kj": kj, "ascentMetres": ascentMetres, "reps": reps}
        self.numberDict = {"km":km, "hours": self.hours,"tss": tss,"kj": kj, "ascentMetres": ascentMetres, "reps": reps}
