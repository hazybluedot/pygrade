#!/usr/bin/env python3

import json

class CucumberReport:
    class Step:
        def __init__(self,step_obj):
            self.json_obj = step_obj
            self.name = self.json_obj["name"]

        def passed(self):
            return self.json_obj["result"]["status"] == "passed"

    class Scenario:
        def __init__(self,scenario_obj):
            self.json_obj = scenario_obj
            self.name = self.json_obj["name"]

        def steps(self):
            return ( CucumberReport.Step(obj) for obj in self.json_obj["steps"] )

        def passed(self):
            return all( [ step.passed() for step in self.steps() ] )

    class Feature:
        def __init__(self,feature_obj):
            self.json_obj = feature_obj
            self.name = self.json_obj["name"]

        def scenarios(self):
            return ( CucumberReport.Scenario(obj) for obj in self.json_obj["elements"] if obj["keyword"] == "Scenario" )

    def __init__(self, json_obj):
        self.json_obj = json_obj

    def passed(self):
        return all( [ scenario.passed() for scenario in self.scenarios() ] )

    def features(self):
        return ( CucumberReport.Feature(obj) for obj in self.json_obj if obj["keyword"] == "Feature" )

if __name__ == '__main__':
    from sys import stdin

    json_src = stdin   
    
    creport = CucumberReport(json.load(json_src))
    
    for feature in creport.features():
        print("Feature: {0}\n".format(feature.name))
        num_scenarios = len([s for s in feature.scenarios()])
        passed_scenarios = len([ scenario for scenario in feature.scenarios() if scenario.passed() ])
        #for scenario in feature.scenarios():
        #    print("\tScenario: {0} {1}\n".format(scenario.name, scenario.passed()))
        #    steps = [ s for s in scenario.steps() ]
        #    print("\t {0} steps\n".format(len(steps)))
            
        print("{0}/{1} scenarios ({2}%)\n".format(passed_scenarios, num_scenarios, passed_scenarios*100/num_scenarios))

