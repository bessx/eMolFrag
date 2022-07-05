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

from linker import Linker
from brick import Brick

def emit(level, s):
    print("  " * level + s)
    
def emitError(level, s):
    print("  " * level + "Error:", s)

def emitWarning(level, s):
    print("  " * level + "Warning:", s)

def getDirectories(path):
    return [f for f in os.listdir(path) if not os.path.isfile(path + "/" + f)]

def getFiles(path):
    return [f for f in os.listdir(path) if os.path.isfile(path + "/" + f)]

DEFAULT_EMOLFRAG_DIRECTORY = "eMolFrag"
DEFAULT_TEST_DIRECTORY = DEFAULT_EMOLFRAG_DIRECTORY + "/black-box-verification/tests"
INPUT_DIR_NAME = "input"
EXPECTED_OUTPUT_DIR_NAME = "expected-output"
GENERATED_OUTPUT_DIR_NAME = "generated-output"

E_MOL_FRAG_OUTPUT_BRICKS_DIR = "output-brick"
E_MOL_FRAG_OUTPUT_LINKERS_DIR = "output-linker"
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
    instrs.append(DEFAULT_EMOLFRAG_DIRECTORY + "/src/eMolFrag.py")

    # Input
    instrs.append("-i")
    instrs.append("".join(inpath))

    # Output
    instrs.append("-o")
    instrs.append(outdir)

    # Options
    instrs += E_MOL_FRAG_OPTIONS

    return instrs 
 
def executeEmolFrag(path):
    #    
    # Run a test:
    #    (1) Run emolfrag
    #    (2) Compare generated output to expected output
    #
    inpath = path + '/' + INPUT_DIR_NAME
    outpath = path + '/' + GENERATED_OUTPUT_DIR_NAME
    
    exeInstructions = buildEmolFragEXEArgs(inpath, outpath)

    emit(1, "Executing " + " ".join(exeInstructions))

    subprocess.run(exeInstructions)

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
        emitWarning(1, "Directory " + path + " contains extraneous files that will be ignored:" + ' '.join(files))

    #
    # Directory checks
    #
    dirs = getDirectories(path)
    
    if INPUT_DIR_NAME not in dirs:
        emitError(1, "Directory " + path + " does not contain expected input directory \'" + INPUT_DIR_NAME + "\'")
        return False

    if EXPECTED_OUTPUT_DIR_NAME not in dirs:
        emitError(1, "Directory " + path + " does not contain expected output directory \'" + \
                  EXPECTED_OUTPUT_DIR_NAME + "\'")
        return False

    if GENERATED_OUTPUT_DIR_NAME in dirs:
        emitWarning(1, "Contents of generated output directory " + \
                    path + "/" + GENERATED_OUTPUT_DIR_NAME + " will be deleted (and regenerated).")
        import shutil # for directory removal
        shutil.rmtree(path + "/" + GENERATED_OUTPUT_DIR_NAME)
                    
    return True
    
#
#
# We are comparing the contents of two directories:
#      expected-output   and   generated-output
#
#

#
# From the given, path read each fragment into their object representation
#
import random
def readFragmentDirectory(path):

    frag_files = getFiles(path)

    # Permute the list to add a greater likelihood of verification correctness
    random.shuffle(frag_files)

    linkers = []
    bricks = []
    for frag_file in frag_files:

        frag_path = path + '/' + frag_file

        if frag_file[0] == 'l':
            linkers.append(Linker(frag_path))

        elif frag_file[0] == 'b' or frag_file[0] == 'r':
            bricks.append(Brick(frag_path))

        else:
            emitWarning(2, "File " + frag_file + " ignored due to prefix not l- or b-")
    
    return linkers, bricks

#
# Compare the fragment set for unique equality
#
def compareFragments(expec, gen_frags, fragType):

    verified = True

    if len(expec) != len(gen_frags):
        emitError(2, "Expected " + str(len(expec)) + " " + fragType + \
                     " fragments; found " + str(len(gen_frags)))
        verified = False

    #
    # Index-based uniqueness checking of fragments via a parallel array marking scheme
    #
    marked = [False] * len(expec)

    # Check each generated fragment
    for g_index in range(len(gen_frags)):

        #emit(3, "Comparing " + gen_frags[g_index].name())

        g_mark = False
        for e_index in range(len(expec)):
            #emit(4, "to " + expec[e_index].name())

            # Unmarked and equal fragments are what we seek
            if not marked[e_index]:
                if expec[e_index].equals(gen_frags[g_index]):
                    marked[e_index] = True
                    g_mark = True
                    break

        # Not found
        if not g_mark:
            emitError(2, "Generated fragment " + gen_frags[g_index].name() + " not an expected fragment.")       

    return verified and False not in marked

def compareOutput(path):

    #
    # Acquire linkers / brick objects from both the expected and generated directors
    #
    expec_linkers, expec_bricks = readFragmentDirectory(path + "/" + EXPECTED_OUTPUT_DIR_NAME)

    # EmolFrag output is in two directories
    gen_linkers, _ = readFragmentDirectory(path + "/" + GENERATED_OUTPUT_DIR_NAME + "/" + E_MOL_FRAG_OUTPUT_LINKERS_DIR) 
    _ , gen_bricks = readFragmentDirectory(path + "/" + GENERATED_OUTPUT_DIR_NAME + "/" + E_MOL_FRAG_OUTPUT_BRICKS_DIR)

    verified = True
    if not compareFragments(expec_linkers, gen_linkers, "linker"):
        emitError(2, "Linker fragments failed to verify.")
        verified = False
    else:
        emit(2, "Linker fragments verified.")

    if not compareFragments(expec_bricks, gen_bricks, "brick"):
        emit(2, "Brick fragments failed to verify.")
        verified = False
    else:
        emit(2, "Brick fragments verified.")

    return verified

#
# Run a single black box test
#
def runBBtest(path):

    emit(1, "Executing test in " + path)

    if not checkBBdirectoryContents(path):
        emit(1, "Directory check failed, tests in " + path + " not executed.")
        return False

    executeEmolFrag(path)

    return compareOutput(path)

#
# Run all black box tests within the specified directory
#
def runAllBB(path):
    
    emit(0, "Executing black box tests defined in " + path)
    
    # Get all black box tests by acquiring a list of sub-directories
    subdirs = getDirectories(path)

    successes = []
    failures = []    
    for subdir in subdirs:

        emit(0, "")

        abspath = path + "/" + subdir

        if runBBtest(abspath):
           successes.append(abspath)
        else:
            failures.append(abspath)
    
    return successes, failures

#
# Input for verification consists of specifying a root directory
# containing a sequence of input / output validation pairs.
#    For example, input of a molecule with result in output of a
#    set of fragments (both linkers and bricks)
#
# If a directory is not specified, a default directory will be used.
#

def usage():
    return "Usage: " + sys.argv[0] + "<emolfrag-directory>"
  
def main():

    rel_path = DEFAULT_TEST_DIRECTORY

    # Recall the first argument is the script being executed    
    if len(sys.argv) == 1: # No command-line args
        pass

    elif len(sys.argv) > 2:
        emitError(0, usage())
        return

    # User asked for usage
    elif len(sys.argv) == 2 and sys.argv[1] == "-usage":
        emit(0, usage())
        return

    # User specified a directory
    else:
        rel_path = sys.argv[1]

    bb_test_abs_path = os.path.abspath(rel_path)
    
    if not os.path.isdir(bb_test_abs_path):
        emitError(0, "Absolute input path " + str(bb_test_abs_path) + " is not a directory.")
        return

    # Perform BB aanlysis on all aub-directories     
    successes, failures = runAllBB(bb_test_abs_path)
    
    #
    # Output the results of BB tests
    #
    print("\nExecuted", len(failures) + len(successes), "black box tests.")
    
    if len(failures) > 0:
        print("Failed", len(failures), "black box tests, including:")
        print("\n\t".join([""] + failures))
    
    if len(successes) > 0:
        print("Succeeded running ", len(successes), "black box tests, including:")
        print("\n\t".join([""] + successes))
   
if __name__ == "__main__":
    main()