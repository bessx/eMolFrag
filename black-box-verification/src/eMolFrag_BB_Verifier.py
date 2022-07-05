#!/usr/bin/python

# The goal of this script is to validate successful executions of
# eMolFrag using the cases defined in directory black-box validation

# Each sub-directory in black-box verification contains 

# Update Log:
#   @author Chris Alvin
# Initial Version      07/03/2022

import sys
import os         # listdir
import os.path    # isfile
import subprocess # subprocess

def emitError(str):
    print("Error:", str)

def emitWarning(str):
    print("Warning:", str)

def compareDirectory(path):
    print("Black box verification test directory:", bb_test_abs_path)

def getDirectories(path):
    return [f for f in os.listdir(path) if not os.path.isfile(path + f)]

def getFiles(path):
    return [f for f in os.listdir(path) if os.path.isfile(path + f)]
    
INPUT_DIR_NAME = "input"
EXPECTED_OUTPUT_DIR_NAME = "expected-output"
GENERATED_OUTPUT_DIR_NAME = "generated-output"

E_MOL_FRAG = "eMolFrag.py"
E_MOL_FRAG_OPTIONS = ["-c", "0"] # Instructions to create separate fragment files

#
# Build a list of arguments for emolfrag that will be executed 
#
#   A typical set of instructions:
#      python eMolFrag/src/eMolFrag.py -i /content/eMolFrag/black-box-verification/9070-non-c2-c2-double-bond/input/ -o double-bond-output/ -c 0
#
def buildEmolFragEXEArgs(inpath, outdir):

    # Exceutable
    instrs = ["python"]
    instrs.append("./eMolFrag.py")

    # Input
    instrs.append("-i")
    instrs.append("".join(inpath))

    # Output
    instrs.append("-o")
    instrs.append(outdir)

    # Options
    instrs += E_MOL_FRAG_OPTIONS

    return instrs 
 
#
# A well-constructed Black Box directory
# will contain at least 2 directories:
#     input
#     expected-output
#     generated-output
#
def checkBBdirectoryContents(path):

    #
    # Check the contents of the directory for required contents
    #
    files = getFiles(path)
    if len(files) > 0:
        emitWarning("Directory " + path + " contains extraneous files that will be ignored:" + ' '.join(files))

    #
    # Directory checks
    #
    dirs = getDirectories(path)
    
    if INPUT_DIR_NAME not in dirs:
        emitError("Directory " + path + " does not contain expected input directory \'" + INPUT_DIR_NAME + "\'")
        return False

    if EXPECTED_OUTPUT_DIR_NAME not in dirs:
        emitError("Directory " + path + " does not contain expected output directory \'" + \
                  EXPECTED_OUTPUT_DIR_NAME + "\'")
        return False

    if GENERATED_OUTPUT_DIR_NAME in dirs:
        emitWarning("Contents of generated output directory " + \
                    path + GENERATED_OUTPUT_DIR_NAME + " will be deleted (and regenerated).")
                    
    return True

def executeEmolFrag(path):
    #    
    # Run a test:
    #    (1) Run emolfrag
    #    (2) Compare generated output to expected output
    #
    inpath = path + '/' + INPUT_DIR_NAME
    outpath = path + '/' + GENERATED_OUTPUT_DIR_NAME
    
    exeInstructions = buildEmolFragEXEArgs(inpath, outpath)

    print("Executing", " ".join(exeInstructions))

    # TO BE UNCOMMENTED result = subprocess.run(exeInstructions)
    
def compareOutput(path)

    

    return False

#
# Run a single black box test
#
def runBBtest(path):

    if not checkBBdirectoryContents(path):
        return False
    
    executeEmolFrag(path)

    return compareOutput(path)

#
# Run all black box tests within the specified directory
#
def runAllBB(path):
    
    print("Executing black box tests specified in", path)
    
    # Get all black box tests by acquiring a list of sub-directories
    subdirs = getDirectories(path)

    success = []
    failure = []    
    for subdir in subdirs:

        abspath = path + "/" + subdir
        result = runBBtest(abspath)

        if result:
           success.append(abspath)
        else:
            failure.append(abspath)
    
    return success, failure

def usage():
  return "Input is a single argument specifiying the directory containing validation tests."

#
# Input for verification consists of specifying a root directory
# containing a sequence of input / output validation pairs
#    For example, input of a molecule with result in output of a set of fragments (both linkers and rigids)
#
def main():
    # Usage is a single argument (directory or usage)
    # Recall the first argument is the script being executed
    if len(sys.argv) != 2 or sys.argv[1] == "-usage":
        emitError(usage())
        return

    bb_test_abs_path = os.path.abspath(sys.argv[1])
    
    if not os.path.isdir(bb_test_abs_path):
        emitError("Absolute input path " + str(bb_test_abs_path) + " is not a directory.")
        return

    # Perform BB aanlysis on all aub-directories     
    successes, failures = runAllBB(bb_test_abs_path)
    
    #
    # Output the results of BB tests
    #
    print("Executed", len(failures) + len(successes), "black box tests.")
    
    if len(failures) > 0:
        print("Failed", len(failures), "black box tests, including:")
        print("\n\t".join([""] + failures))
    
    if len(successes) > 0:
        print("Succeeded running ", len(successes), "black box tests, including:")
        print("\n\t".join([""] + successes))
   

if __name__ == "__main__":
  main()