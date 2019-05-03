class Figure(object):

    def get_area(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__


class Circle(Figure):
    def __init__(self, radius):
        self.radius = radius

    def _area(self):
        return 3.14 * self.radius ** 2

    def get_area(self):
        return self._area()

    def __repr__(self):
        return '{0}: radius {1}'.format(
            self.__class__.__name__,
            self.radius,
        )


class Rectangle(Figure):
    def __init__(self, weight, height):
        self.weight = weight
        self.height = height

    def _area(self):
        return self.weight * self.height

    def get_area(self):
        return self._area()

    def __repr__(self):
        return '{0}: weight - {1}, height - {2}'.format(
            self.__class__.__name__,
            self.weight,
            self.height,
        )


if __name__ == "__main__":
    c = Circle(2)
    print(c, 'Area: {}'.format(c.get_area()), sep='\n')
    r = Rectangle(3, 4)
    print(r, 'Area: {}'.format(r.get_area()), sep='\n')
