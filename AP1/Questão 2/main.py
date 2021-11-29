import numpy

def main():
    A = numpy.array([[4, 3, 0], 
                       [3, 4, -1], 
                       [0, -1, 4]])
    B = numpy.array([24, 30, -24])
    print(numpy.linalg.solve(A, B))


if __name__ == '__main__':
    main()