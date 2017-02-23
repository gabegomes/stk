from types import SimpleNamespace
from os.path import join
import json
from ..molecular import (MacroMolecule, Molecule, FourPlusSix,
                         StructUnit,
                         StructUnit2, StructUnit3, MacroMolKey)
from ..ga import Population

Population.load(join('data', 'macromolecule', 'mm.json'))

def test_same():
    """
    Tests the `same_cage` method.

    Cages initialized from the same arguments should return ``True``
    through this method, even if the ``Cage`` class stops being cached.

    """

    a = MacroMolecule.testing_init('a', 'b', SimpleNamespace(a=1))
    b = MacroMolecule.testing_init('a', 'a', SimpleNamespace(a=2))
    c = MacroMolecule.testing_init('a', 'a', SimpleNamespace(a=2))
    d = MacroMolecule.testing_init('a', 'b', SimpleNamespace(b=1))

    assert not a.same(b)
    assert b.same(c)
    assert c.same(b)
    assert not d.same(c)

def test_comparison():
    """
    Checks ``==``, ``>``, ``>=``, etc. operators.

    """

    # Generate cages with various fitnesses.
    a = MacroMolecule.testing_init('a','a',SimpleNamespace(a=1))
    a.fitness = 1

    b = MacroMolecule.testing_init('b', 'b', SimpleNamespace(b=1))
    b.fitness = 1

    c = MacroMolecule.testing_init('c', 'c', SimpleNamespace(c=1))
    c.fitness = 2

    # Comparison operators should compare their fitness.
    assert not a < b
    assert a <= b
    assert a == b
    assert c > b
    assert c >= a

def test_caching():

    # Make a MacroMolecule the regular way.
    bb1 = StructUnit2(join('data', 'struct_unit2', 'amine.mol2'))
    bb2 = StructUnit3(join('data', 'struct_unit3', 'amine.mol2'))
    mol1 = MacroMolecule({bb1, bb2}, FourPlusSix())

    # Make a MacroMolecule using JSON.
    with open(join('data', 'macromolecule', 'mm.json'), 'r') as f:
        mol2 = Molecule.load(json.load(f)[0])

    assert mol1 is not mol2

    # Remake the MacroMolecules.
    mol3 = Molecule.load(mol1.json())
    mol4 = MacroMolecule(mol2.building_blocks,
                         mol2.topology.__class__())

    # Confirm they are cached.
    assert mol1 is mol3
    assert mol1 is not mol4
    assert mol2 is mol4
    assert mol2 is not mol3

def test_json_init():
    og_c = dict(MacroMolecule.cache)
    try:
        # Make a MacroMolecule using JSON.
        MacroMolecule.cache = {}
        with open(join('data', 'macromolecule', 'mm.json'), 'r') as f:
            mol = Molecule.load(json.load(f)[0])

        assert mol.fitness == None
        assert all(isinstance(x, StructUnit) for x in
                                        mol.building_blocks)
        assert isinstance(mol.key, MacroMolKey)
        assert mol.optimized == True
        assert mol.unscaled_fitness == {}
        assert mol.bonder_ids == [6, 15, 24, 59, 68, 77, 112, 121, 130,
                              165, 174, 183, 219, 222, 252, 255, 285,
                              288, 318, 321, 351, 354, 384, 387]
        assert mol.failed == False
        assert mol.energy.__class__.__name__ == 'Energy'
        assert mol.topology.__class__.__name__ == 'FourPlusSix'
        assert len(mol.mol.GetAtoms()) == 410
        assert mol.bonds_made == 12
        assert set(mol.bb_counter.values()) == {4, 6}
        assert mol.progress_params == None
    finally:
        MacroMolecule.cache = og_c
