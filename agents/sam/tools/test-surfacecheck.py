"""check the face overlap test without blender."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'assets/blender/scripts'))
from surfacecheck import overlaps


def face(name='a', z=0, x=0, reverse=False, material=None):
    points = [(x, 0, z), (x + 1, 0, z), (x, 1, z)]
    return {'object': name, 'face': 0, 'material': material or name, 'points': points[::-1] if reverse else points}


class SurfaceCheck(unittest.TestCase):
    def testCoincident(self):
        self.assertEqual(overlaps([face(), face('b')]), [('a', 'b')])

    def testSameMaterial(self):
        self.assertFalse(overlaps([face(), face('b', material='a')]))

    def testNear(self):
        self.assertFalse(overlaps([face(), face('b', .099)]))

    def testClear(self):
        self.assertFalse(overlaps([face(), face('b', .25)]))

    def testEdgeContact(self):
        self.assertFalse(overlaps([face(), face('b', x=1)]))

    def testPartialOverlap(self):
        self.assertTrue(overlaps([face(), face('b', x=.9)]))

    def testOppositeNormal(self):
        self.assertFalse(overlaps([face(), face('b', reverse=True)]))

    def testCellBoundary(self):
        self.assertTrue(overlaps([face(x=7.95), face('b', x=8.01)]))

    def testSameMeshDifferentFaces(self):
        b = face()
        b['face'] = 1
        b['material'] = 'other'
        self.assertTrue(overlaps([face(), b]))

    def testSameFace(self):
        self.assertFalse(overlaps([face(), face()]))

    def testShipUnits(self):
        self.assertTrue(overlaps([face(), face('b', .000001)], 1e-5 / 7.2))
        self.assertFalse(overlaps([face(), face('b', .00001)], 1e-5 / 7.2))

    def testRotatedPlane(self):
        a, b = face(), face('b')
        for item in (a, b):
            item['points'] = [(z, x, y) for x, y, z in item['points']]
        self.assertTrue(overlaps([a, b]))


if __name__ == '__main__':
    unittest.main()
