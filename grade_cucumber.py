#!/usr/bin/env python3

import json

def pass_string(passed):
    if passed:
        return "PASSED"
    else:
        return "FAILED"

class CucumberReport:
    class Step:
        def __init__(self,step_obj):
            self.json_obj = step_obj
            self.name = self.json_obj["name"]
            self.keyword = self.json_obj["keyword"]
            self.desc = self.keyword + " " + self.name

        def passed(self):
            return self.json_obj["result"]["status"] == "passed"

        def to_str(self):
            return self.desc + " (" + pass_string(self.passed()) + ")"

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

    def scenarios(self):
        scenarios = 0
        for f in self.features():
            scenarios += len([s for s in f.scenarios()])
        #return [ (s for s in f.scenarios() if s.passed() ) for f in self.features() ]
        return scenarios

    def passed_scenarios(self):
        passed = 0
        for f in self.features():
            passed += len([s for s in f.scenarios() if s.passed()])
        return passed
        #return [ [ s for s in f.scenarios() if s.passed() ] for f in self.features()]

if __name__ == '__main__':
    from sys import stdin,stderr,stdout

    json_src = stdin   
    
    creport = CucumberReport(json.load(json_src))
    
    passed_scenarios = creport.passed_scenarios()
    total_scenarios = creport.scenarios()
    print("{0}/{1} ({2}%)".format(passed_scenarios, total_scenarios, passed_scenarios*100/total_scenarios))
    if passed_scenarios < total_scenarios:
        for feature in creport.features():
            print("Feature: {0}\n".format(feature.name))
            num_scenarios = len([s for s in feature.scenarios()])
            passed_scenarios = len([ scenario for scenario in feature.scenarios() if scenario.passed() ])
            for scenario in feature.scenarios():
                print("\t{0} ({1})".format(scenario.name, pass_string(scenario.passed())))
                if not scenario.passed():
                    stdout.writelines([ "\t\t" + s.to_str() + "\n" for s in scenario.steps() ])
            print("\t{0}/{1} scenarios ({2}%)\n".format(passed_scenarios, num_scenarios, passed_scenarios*100/num_scenarios))

    
