import json
import trainingdiarydatamodel
import math
from trainingdiarydatamodel import Workout, Day, TrainingDiary


def importDiary(diaryJSONFile):
    f = open(diaryJSONFile, encoding="utf-8")
    data = json.load(f)
    trainingDiary = TrainingDiary(data["name"], data["athleteName"], data["Included"])
    for d in data["days"]:
        newDay = Day(d["iso8061DateString"], d["type"], d["sleep"], d["sleepQuality"], d["fatigue"], d["motivation"],d["comments"])
        trainingDiary.days.append(newDay)
        if "workouts" in d:
            for w in d["workouts"]:
                new = Workout(w["activityString"], w["activityTypeString"], w["equipmentName"], w["seconds"], w["rpe"], w["tss"], w["tssMethod"], w["km"], w["kj"], w["ascentMetres"], w["reps"], w["keywords"], w["isRace"], w["cadence"], w["watts"], w["wattsEstimated"], w["hr"], w["brick"], w["comments"])
                newDay.workouts.append(new)
    return trainingDiary

def tsb(trainingDiary, activity):
    ctlDecay = math.exp(-1/42)
    ctlImpact = 1 - math.exp(-1/42)
    atlDecay = math.exp(-1/7)
    atlImpact = 1 - math.exp(-1/7)

    ctl = 0
    atl = 0

    results = []
    trainingDiary.days.sort(key=lambda x: x.date)
    for d in trainingDiary.days:
        tss = 0
        for w in d.workouts:
            if w.activityString == activity:
                tss += getattr(w,"tss",0)
        ctl = ctl * ctlDecay + tss * ctlImpact
        atl = atl * atlDecay + tss * atlImpact
        # results.append((d.date.strftime("%Y-%b-%d"), tss,ctl,atl, (ctl-atl)))
        # results.append({'date':d.date.strftime("%Y-%b-%d"), 'tss': tss,'ctl':ctl, 'atl':atl, 'tsb': (ctl-atl)})
        results.append({'date':d.date, 'tss': tss,'ctl':ctl, 'atl':atl, 'tsb': (ctl-atl)})

    return results

def values(trainingDiary, activity, unit):
    print(activity + " " + unit)
    results = []
    for d in trainingDiary.days:
        value = 0
        for w in d.workouts:
            if w.activityString == activity:
                value += getattr(w,unit,0)
        if value > 0:
            results.append(value)
    return results
