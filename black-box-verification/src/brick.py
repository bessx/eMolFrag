#!/usr/bin/python

#
# A class-based representation of a brick fragment
#

# Update Log:
#   @author Chris Alvin
# Initial Version      07/04/2022

import fragment

class Brick(fragment.Fragment):

    def __init__(self, abspath):
        super().__init__(abspath)
        
        #
        # A list of atomtypes
        # Atomtypes parallel the atom list (in _atoms)
        self._atomtypes = []
        self.extractAtomTypes()
            
        #
        # Eligible connection types
        self._connections = []
        self.extractConnections()

    def extractAtomTypes(self):
        # Seek the unique line indicating beginning of contact information
        aTypes_index, _ = fragment.extract_unique_line("ATOMTYPES", self._fragmentTextList)

        # Read all atomtypes, one for each atom
        for atomIndex in range(len(self._atomElements)):
            aTypes_line = self._fragmentTextList[aTypes_index + 1 + atomIndex].split()
            self._atomtypes.append(str(aTypes_line[0]))

    def extractConnections(self):
        # Seek the unique line indicating beginning of contact information
        conn_index, _ = fragment.extract_unique_line("@atom-number", self._fragmentTextList)

        # Read all connectionsl there are a variable number of connections (possibly 0)
        conn_index = conn_index + 1
        connLine = self._fragmentTextList[conn_index].split()
        while len(connLine) == 2:

            self._connections.append((int(connLine[0]), str(connLine[1])))
        
            conn_index = conn_index + 1
            connLine = self._fragmentTextList[conn_index].split()
        
    def equals(self, that):
        if not isinstance(that, Brick):
            return False

        if not super().equals(that):
            return False

        if self._atomtypes != that._atomtypes:
            return False

        if brick._atomtypes != that._atomtypes:
            return False

        #
        # Check equality of connections; order is arbitrary
        #
        if len(self._connections) == len(that._connections):
            return False
        
        foundConns = 0
        for conn in self._connections:
            if conn in that._connections:
                foundConns = foundConns + 1
        
        return foundConns == len(self._connections)

#
#
# Unit tests for Bricks
#
#
def UnitTest_CheckBrick(abspath, \
                        expec_numAtoms, \
                        expec_numBonds, \
                        expec_elements, \
                        expec_bonds, \
                        expec_bondtypes, \
                        expec_atomtypes, \
                        expec_connections):

    print("Testing", abspath.split("/")[-1])
    
    brick = Brick(abspath)

    #
    # Atoms
    #
    assert brick._numAtoms == expec_numAtoms, "Num Atoms"
    assert brick._numBonds == expec_numBonds, "Num Bonds"
    
    for index in range(len(expec_elements)):
        assert brick._atomElements[index] == expec_elements[index], "Atom discrepancy " + str(index + 1)

    #
    # Bonds and Bondtypes
    #
    for index in range(len(expec_bonds)):
        assert brick._bonds[index] == expec_bonds[index], "Bond discrepancy " + str(index + 1)
    
    assert brick._bondTypes == expec_bondtypes, "Bondtypes"

    assert brick._atomtypes == expec_atomtypes, "Brick AtomTypes"

    #
    # The order of the connections may be arbitrary
    #
    assert len(brick._connections) == len(expec_connections), "Number of connections"

    foundConns = 0
    for expec_conn in expec_connections:
        if expec_conn in brick._connections:
            foundConns = foundConns + 1

    assert foundConns == len(expec_connections), "Found only " + str(foundConns) + ", expected " + str(len(expec_connections))
        
import os.path

if __name__ == "__main__":
    
    #
    # Bricks
    #
    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/b-CHEMBL1098067.mol2-000.sdf")
    
    UnitTest_CheckBrick(abspath, 11, 12, \
                  ["C", "C", "C", "C", "N", "C", "N", "N", "C", "C", "C"], \
                  [(1, 2),(1,3),(2,6),(3,8),(4,6),(4,8),(5,9),(5,10),(6,7),(7,10),(7,11),(9,11)], \
                  [1, 1, 1, 1, 1, 1, 4, 4, 1, 4, 4, 4], \
                  ["C.3", "C.3", "C.3", "C.3", "N.ar", "C.3", "N.ar", "N.3", "C.ar", "C.ar", "C.ar"], \
                  [(10, "C.3"), (11, "C.ar"), (8, "C.3"), (9, "C.3")])

    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/b-CHEMBL1098067.mol2-001.sdf")
    
    UnitTest_CheckBrick(abspath, 6, 6, \
                  ["C", "C", "C", "C", "C", "C"], \
                  [(1, 2),(1,3),(2,4),(3,5),(4,6),(5,6)], \
                  [4, 4, 4, 4, 4, 4], \
                  ["C.ar", "C.ar", "C.ar", "C.ar", "C.ar", "C.ar"], \
                  [(6, "C.3")])

    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/b-CHEMBL1098067.mol2-002.sdf")

    UnitTest_CheckBrick(abspath, 12, 12, \
                  ["C", "O", "O", "N", "C", "C", "C", "C", "C", "C", "C", "C"], \
                  [(2, 4),(3,11),(4,11),(5,7),(5,9),(6,8),(6,11),(7,12),(8,12),(9,1),(10,12),(10,1)], \
                  [1, 2, 1, 4, 4, 2, 1, 4, 1, 4, 4, 4], \
                  ["C.ar", "O.3", "O.2", "N.am", "C.ar", "C.2", "C.ar", "C.2", "C.ar", "C.ar", "C.2", "C.ar"], \
                  [(1, "C.ar")])
    
    print("Success.")