pygrade
=======

a set of python files to assist in managing grade information for import/export from/to a Scholar ecosystem

## The Problem
The Scholar course-management system has its own special way of managing assignment feedback and grades.  
One of the more useful features is that it provides the ability to import/export a `zip` archive of an assignment providing a file structure containing 
all relevant information.
Because it is often much more convenient to enter comments and grades in a text file locally, I created several scripts that assist 
in the conversian between individual comment files and the Scholar directory format.

In addition, there are tools to facilitate translating group feedback into individual feedback for posting to Scholar

still a work in progress :-)

Current Workflow
----------------
Of course this could all be packaged up into a convenient bash script
Note: During this process submitted code is run using Python's subprocess module.  This should be run as an safe user, 

1. Generate list of URLs submitted via Scholar
    
        find "$SCHOLAR_UNZIPED_ARCHIVE" '*submissionText.html' | extract_pid.py | extract_url.py > pid_urls.out

2. Clone/fetch from github

        gitpull.py $LOCAL_REPOS_DIR <pid_urls.out
        
3. Run tests

        subprocess_test.py --ref $REFDIR/$FILE.test <(find $REPODIR -name $FILE) 
        compare_files.py --ref $REFDIR/$FILE.test <(find $REPODIR -name $FILE)
        
4. Review source and diffs

        review_diffs.py <(find $REPODIR -name $FILE.test)
		
Find Ungraded Workflow
______________________

    find_ungraded.sh repos/ $SRC_NAME | subprocess_test.py --ref solutions/$SRC_NAME.test | \
        compare_files.py --ref solutions/mult.py.test solutions/mult2.py.test > ungraded
    review_diffs.py -t <ungraded

ToDo
----
Better file name matching?  This can be a losing battle.  If the script get's "smarter" with what it accepts there is inevitably more variability in what 
people submit.  A simple rule would be something like, if the assignment asks for `mult.py`, then look for `mult*.py` But then how do differentiate from 
`mult2.py` which was asked for in part 2?  The answer might be a combination of making a smarter file finder, and being smarter about
naming the requested files in the assignment writeup.  I like the simplicity of just being strict with what the filenames are called.

find_ungraded should optionaly read source files from standard input so can run one command to find all ungraded files
