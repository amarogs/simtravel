import unittest
import src.models.cities as cities
import random

class TestCityBuilder(unittest.TestCase):
    

    def test_north_of(self):
        x, y = 10, 3
        cb = cities.CityBuilder()
        self.assertEqual(cb.north_of(x, y), (9,3) , "North of cell not working")
    def test_south_of(self):
        x, y = 10,3
        cb = cities.CityBuilder()
        self.assertEqual(cb.south_of(x, y), (11,3) , "South of cell not working")
    def test_east_of(self):
        x, y = 10, 3
        cb = cities.CityBuilder()
        self.assertEqual(cb.east_of(x, y), (10,4) , "East of cell not working")
    def test_west_of(self):
        x, y = 10,3
        cb = cities.CityBuilder()
        self.assertEqual(cb.west_of(x, y), (10,2) , "West of cell not working")
    def test_next_cell_of(self):
        x, y = 10,3
        cb = cities.CityBuilder()
        self.assertEqual(cb.next_cell_of(x, y, 0, 2, 1, 3), (10,3) , "Direction of cell not working")
    def test_exit_of_N(self):
        x, y = 10,3
        cb = cities.CityBuilder()
        res = [(9,4), (11,4), (11,2), (9,2)]
        for i in range(4):
            self.assertEqual(cb.exit_of(x, y, i), res[i] , "Direction of cell not working: direction {}".format(i))
    def test_entrance_of(self):
        res = 10,3
        cb = cities.CityBuilder()
        pos = [(9,4), (11,4), (11,2), (9,2)]
        for i in range(4):
            self.assertEqual(cb.entrance_of(*pos[i], i), res , "Direction of entrance not working: direction {}".format(i))

class TestStreet(unittest.TestCase):

    def test_street_length(self):
        st = cities.Street(0,0, 1, 10)
        self.assertEqual(len(st.cells), 10, "Street length is not right")

    def test_street_direction(self):
        st = cities.Street(0,0, 1, 10)
        first = st.cells[0]
        last = st.cells[-1]
        dx = last.pos[0] - first.pos[0]
        dy = last.pos[1] - first.pos[1]
        self.assertEqual((dx, dy),(0,9), "Street direction is not right")

class TestIntersection(unittest.TestCase):

    def test_give_way(self):
        intersec = cities.RoadIntersection(10,10, [1,0,1,0])

        give_way = [(10,9)]
        no_give_way = [(11, 10), (10,11),(9,10)]
        
        no_give_way_cells = [x for x in intersec.cells if x.pos in no_give_way]
        give_way_cells = [x for x in intersec.cells if x.pos in give_way]

        self.assertTrue(all([len(c.prio_successors) == 0 for c in give_way_cells ])   )
        self.assertTrue(all([len(c.prio_successors) != 0 for c in no_give_way_cells ])   )
    def test_placement(self):
        intersec = cities.RoadIntersection(10,10, [1,0,1,0])
        positions = [(10,9), (11, 10), (10,11), (9,10), (10,10)]     
        self.assertEqual([c.pos for c in intersec.cells], positions, "Road intersection isn't placed correctly")   

    
class TestSquareCity(unittest.TestCase):

    def test_size(self):
        sq = cities.SquareCity(6, 7*4, 2)
        matrix = sq.city_matrix
        base = 6 + 2 + 7*4
        self.assertEqual(matrix.shape, (2*base, 2*base), "Square city shape is not squared")

    def test_rechability(self):
        sq = cities.SquareCity(6, 5*4, 2)
        city_map = sq.city_map
        all_cells = set(city_map.values())
        start = random.choice(list(all_cells))
        visited = set()
        open_set = [start]
        while open_set:
            current = open_set.pop()
            visited.add(current)
            for cell in current.successors:
                if cell not in visited:
                    open_set.append(cell)
        self.assertEqual(all_cells, visited, "There are cells that are not reachable")
    
    def test_different_types(self):
        sq = cities.SquareCity(6, 7*4, 2)
        av, rb, st = sq.avenues, sq.roundabouts, sq.streets
        self.assertEqual(av.intersection(rb, st), set(), "There are collisions between the cell types")
    
    def test_different_enum_types(self):
        c = set([v.value for v in cities.CellType])
        self.assertEqual(len(c),  4, "At least one CellType value is repeated") 
    
    def test_total_d_stations(self):
        sq = cities.SquareCity(6, 7*4, 2)
        min_d_stations = 10
        self.assertEqual(sq.set_max_chargers_stations(2, 10)[1],16, "Number of small distributed stations is not the expected.")
        self.assertEqual(sq.set_max_chargers_stations(2, 16)[1],16, "Number of small distributed stations is not the expected.")
        self.assertEqual(sq.set_max_chargers_stations(2, 17)[1],36, "Number of small distributed stations is not the expected.")

    def test_stations_placement(self):
        sq = cities.SquareCity(6, 7*4, 2)
        stations, clusters = sq.place_stations_new("central", 16)
        self.assertTrue(len(stations) == len(clusters), "Number of stations cluster doesn't match the service areas.")

        stations, clusters = sq.place_stations_new("distributed", 16)
        self.assertTrue(len(stations) == len(clusters), "Number of stations cluster doesn't match the service areas.")

        stations, clusters = sq.place_stations_new("four", 16)
        self.assertTrue(len(stations) == len(clusters), "Number of stations cluster doesn't match the service areas.")
    
    def test_stations_coverage(self):
        sq = cities.SquareCity(6, 7*4, 2)
        cells = set(sq.city_map.keys())

        stations, clusters = sq.place_stations_new("central", 16)

        self.assertEqual(cells,{c for c in cells for cells in clusters}, "There are cells that are not covered by any station.")

   