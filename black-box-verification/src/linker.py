#!/usr/bin/python

#
# A class-based representation of linker fragment
#

# Update Log:
#   @author Chris Alvin
# Initial Version      07/04/2022

import fragment

class Linker(fragment.Fragment):
    
    def __init__(self, abspath):
        super().__init__(abspath)

        #
        # A list of pairs, one for each atom in the linker
        # Contains number of connections that can be made to the parallel atom (in _atoms)
        #
        self._contacts = []
    
        # Extract the contacts from the text-based fragment representation
        self.extractContacts()

    def extractContacts(self):
        # Seek the unique line indicating beginning of contact information
        contactsIndex, contactsLine = fragment.extract_unique_line("MAX-NUMBER-Of-CONTACTS ATOMTYPES", self._fragmentTextList)

        # Read all contacts, one for each atom
        for atomIndex in range(len(self._atomElements)):
            contactLine = self._fragmentTextList[contactsIndex + 1 + atomIndex].split()
            self._contacts.append((int(contactLine[0]), str(contactLine[1])))
        
    def equals(self, that):
        if not isinstance(that, Linker):
            return False

        if not super().equals(that):
            return False

        # Check equality of contacts 
        return self._contacts == that._contacts
        
#
#
# Unit tests for Linkers
#
#
def UnitTest_CheckLinker(abspath, \
                         expec_numAtoms, \
                         expec_numBonds, \
                         expec_elements, \
                         expec_bonds, \
                         expec_bondtypes,
                         expec_contacts):

    print("Testing", abspath.split("/")[-1])
    
    linker = Linker(abspath)

    #
    # Atoms
    #
    assert linker._numAtoms == expec_numAtoms, "Num Atoms"
    assert linker._numBonds == expec_numBonds, "Num Bonds"
    
    for index in range(len(expec_elements)):
        assert linker._atomElements[index] == expec_elements[index], "Atom discrepancy " + str(index + 1)

    #
    # Bonds and Bondtypes
    #
    for index in range(len(expec_bonds)):
        assert linker._bonds[index] == expec_bonds[index], "Bond discrepancy " + str(index + 1)
    
    assert linker._bondTypes == expec_bondtypes, "Bondtypes"

    assert linker._contacts == expec_contacts, "Linker Contacts"

import os.path

if __name__ == "__main__":
    
    #
    # Linkers
    #
    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/l-CHEMBL1098067.mol2-000.sdf")
    
    UnitTest_CheckLinker(abspath, 3, 2, \
                  ["C", "C", "N"], \
                  [(1, 2),(2,3)], \
                  [1, 1],
                  [(0, "C.3"), (0, "C.3"), (2, "N.3")])

    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/l-CHEMBL1098067.mol2-001.sdf")
    
    UnitTest_CheckLinker(abspath, 2, 1, \
                  ["C", "C"], \
                  [(1, 2)], \
                  [1],
                  [(0, "C.3"), (2, "C.ar")])

    abspath = os.path.abspath("../tests/1098067-c2-c2-double-bond/expected-output/l-CHEMBL1098067.mol2-002.sdf")

    UnitTest_CheckLinker(abspath, 3, 2, \
                  ["C", "C", "C"], \
                  [(1, 2), (1, 3)], \
                  [1, 1],
                  [(0, "C.3"), (2, "C.ar"), (2, "C.ar")])
    
    print("Success.")