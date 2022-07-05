#!/usr/bin/python

#
# A class-based representation of fragment
#

# Update Log:
#   @author Chris Alvin
# Initial Version      07/04/2022

#
# Utility function to extract a particular line from a file
#
# @input: a string to seek
# @input: a list of strings to search over
#
def extract_unique_line(keyString, listOfStrings):

    # Seek the unique line containing V2000 since it has atom / bond information
    matchingLines = list(filter(lambda line: keyString in line, listOfStrings))
        
    if len(matchingLines) != 1:
        print("Unexpected number of lines in SDF when seeking", keyString)
        print("Number of matching lines", len(matchingLines))
        print("Fatal parsing error.")
        raise ValueError
        
    # Use the unique line
    uniqueLine = matchingLines[0]

    index = listOfStrings.index(uniqueLine)
        
    return index, uniqueLine

class Fragment:

    def __init__(self, sdf_abspath):

        #
        # Instance variables
        #

        # A representation of this fragment as a list of lines of text;
        # each index contains one line
        self._fragmentTextList = []

        self._numAtoms = -1
        self._numBonds = -1
    
        # Atoms in the sequence given by the input file
        self._atomElements = []

        # Bonds in the sequence given by the input file
        self._bonds = []
        self._bondTypes = []

        #
        # Read in the fragment text
        #
        with open(sdf_abspath, 'r') as infile:
            self._fragmentTextList = infile.readlines()

        # Parse the atom file
        self.extractAtoms()
        self.extractBonds()
        
    def equals(self, that):
        if self._numAtoms != that._numAtoms:
            return False
            
        if self._numBonds != that._numBonds:
            return False
                
        if self._atomLines != that._atomLines:
            return False
         
    def extractAtoms(self):

        cl_index, countLine = extract_unique_line('V2000', self._fragmentTextList)

        if cl_index != 3:
            print("SDF Count line is not line 3 as expected; it is line", clIndex)
        
        # SDF format has exactly 3 spaces for number of atoms and number of bonds
        # -------
        self._numAtoms = int(countLine[0:3])

        # Determine the lines where atoms are
        atomsStartIndex = cl_index + 1

        # Extract the exact atoms lines
        atomLines = self._fragmentTextList[atomsStartIndex : atomsStartIndex + self._numAtoms]
        
        if self._numAtoms != len(atomLines):
            print("Unexpected unequal number of atoms", self._numAtoms, " compared to", len(atomLines))
            
        # Acquire the elements of each atom
        self._atomElements = [atomLine.split()[3] for atomLine in atomLines]       
            
    def extractBonds(self):

        cl_index, countLine = extract_unique_line('V2000', self._fragmentTextList)

        # SDF format has exactly 3 spaces for number of atoms followed by number of bonds
        # -------
        self._numBonds = int(countLine[3:6])

        # Determine the lines where atoms and bonds are    
        bondsStartIndex = self._fragmentTextList.index(countLine) + 1 + self._numAtoms

        # Extract the exact lines: bonds
        bondLines = self._fragmentTextList[bondsStartIndex : bondsStartIndex + self._numBonds]
        
        # Extract exact bonds into a list of pairs
        # along with the bond types (integers)
        for bondLine in bondLines:
            bondLineSplit = bondLine.split()
            self._bonds.append((int(bondLineSplit[0]), int(bondLineSplit[1])))
            self._bondTypes.append(int(bondLineSplit[2]))
            
    def toString(self):
        result = ""

        # Stripped down count line
        result += str(self._numAtoms) + " " + str(self._numBonds) + "\n"
         
        # Stripped down atoms
        result += "\n".join(self._atomElements)

        result += "\n"

        # Stripped down bonds and bond types
        for b_index in range(len(self._bonds)):
            result += str(self._bonds[b_index][0]) + " " + str(self._bonds[b_index][1]) + " "
            result += str(self._bondTypes[b_index]) + "\n"
 
        return result

#
#
# Unit tests for a Brick and Linker
#
#
def UnitTest_CheckFragment(abspath, \
                           expec_numAtoms, \
                           expec_numBonds, \
                           expec_elements, \
                           expec_bonds, \
                           expec_bondtypes):

    print("Testing", abspath.split("/")[-1])
    
    fragment = Fragment(abspath)

    #
    # Atoms
    #
    assert fragment._numAtoms == expec_numAtoms, "Num Atoms"
    assert fragment._numBonds == expec_numBonds, "Num Bonds"
    
    for index in range(len(expec_elements)):
        assert fragment._atomElements[index] == expec_elements[index], "Atom discrepancy " + str(index + 1)

    #
    # Bonds and Bondtypes
    #
    for index in range(len(expec_bonds)):
        assert fragment._bonds[index] == expec_bonds[index], "Bond discrepancy " + str(index + 1)
    
    assert fragment._bondTypes == expec_bondtypes, "Bondtypes"

import os.path

if __name__ == "__main__":

    #
    # Brick
    #
    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/b-CHEMBL1098067.mol2-002.sdf")

    UnitTest_CheckFragment(abspath, 12, 12, \
                  ["C", "O", "O", "N", "C", "C", "C", "C", "C", "C", "C", "C"], \
                  [(2, 4),(3,11),(4,11),(5,7),(5,9),(6,8),(6,11),(7,12),(8,12),(9,1),(10,12),(10,1)], \
                  [1, 2, 1, 4, 4, 2, 1, 4, 1, 4, 4, 4])
    
    #
    # Linker
    #
    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/l-CHEMBL1098067.mol2-000.sdf")
    
    UnitTest_CheckFragment(abspath, 3, 2, \
                  ["C", "C", "N"], \
                  [(1, 2),(2,3)], \
                  [1, 1])
    
    print("Success.")