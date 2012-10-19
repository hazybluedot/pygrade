from sys import stderr,exit
from os import path
from ast import literal_eval
from operator import itemgetter
from maybe import maybe

def load_problem_set(pset,basedir):
    tests = []
    for problem in pset['problems']:
        with open(path.join(basedir, problem['src']+".test")) as f:
            stderr.write("Opened {}\n".format(f.name))
            tests.append(load_test(f))
    return tests

def load_test(ref,**kwargs):
    (basedir,name) = path.split(ref.name)
    if 'basedir' in kwargs:
        basedir = kwargs['basedir']
        name = ref.name
    verbose = maybe(kwargs,'verbose', False)

    ref_test = literal_eval(ref.read())
    ref_test['basedir'] = basedir
    if 'problems' in ref_test:
        if verbose:
            stderr.write("Reading problemset file {}\n".format(ref.name))
        ref_test = load_problem_set(ref_test,basedir)
    return (name,ref_test)

def load_tests(refs, **kwargs):
    ref_test = {}
    basedir = maybe(kwargs, 'basedir', None)
    verbose = maybe(kwargs, 'verbose', False)

    #if not hasattr(refs,'next'):
    #    refs = [refs]
    try:
        for ref in refs:
            ref_test = load_test(ref,**kwargs)
            if not hasattr(ref_test,'items'):
                print ref_test
                ref_test = dict(ref_test)
    except SyntaxError as e:
        stderr.write("Could not parse reference file {}\n".format(ref.name))
        exit(1)

    return ref_test


