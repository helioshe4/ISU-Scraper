import re
class Row:
    def __init__(self, loc_year_type, distance, round, name, country, time, splits):
        self.loc_year_type = loc_year_type
        self.distance = distance
        self.round = round
        self.name = name
        self.country = country
        self.time = time
        self.splits = splits

    def get_loc_year_type(self):
        return self.loc_year_type

    def get_distance(self):
        return self.distance

    def get_round(self):
        return self.round

    def get_name(self):
        return self.name

    def get_country(self):
        return self.country

    def get_time(self):
        return self.time

    def get_splits(self):
        return self.splits

    def my_print(self):
        print(f'{self.get_loc_year_type()} {self.get_distance()} {self.get_round()} {self.get_name()} '
              f'{self.get_country()} {self.get_time()} {self.get_splits()}')

