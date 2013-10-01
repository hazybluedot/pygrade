#!/usr/bin/env python3

import json
from os import isatty

def pass_string(passed):
    if passed:
        return "PASSED"
    else:
        return "FAILED"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class CucumberReport:
    class Step:
        def __init__(self,step_obj):
            self.json_obj = step_obj
            self.name = self.json_obj["name"]
            self.keyword = self.json_obj["keyword"]
            self.desc = self.keyword + " " + self.name

        def passed(self):
            return self.json_obj["result"]["status"] == "passed"

        def get_message(self):
            return self.desc + " (" + pass_string(self.passed()) + ")"
            
        def get_error_message(self):
            try:
                return self.json_obj["result"]["error_message"]
            except KeyError as e:
                return ""
            
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

def print_scenario(s, colors):
    lines = []
    color = "" if s.passed() else colors.WARNING
    lines.append(color + s.get_message() + colors.ENDC)
    color = "" if s.passed() else colors.FAIL
    if not s.get_error_message() == "":
        lines.append(color + s.get_error_message() + colors.ENDC)
    return lines

if __name__ == '__main__':
    from sys import stdin,stderr,stdout
    from os import isatty

    ttycolors = bcolors
    if not isatty(1):
        bcolors.disable()

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
                    stdout.writelines([ "\t\t" + line.strip() + "\n" for s in scenario.steps() for line in print_scenario(s, ttycolors)  ])                    
            print("\t{0}/{1} scenarios ({2}%)\n".format(passed_scenarios, num_scenarios, passed_scenarios*100/num_scenarios))

    
