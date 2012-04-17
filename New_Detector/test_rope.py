import test3
class A(self):
    def __init__(self):
        pass

    def f1(self):
        self.extracted_f1()
        print 'f1'

    def extracted_f1(self):
        x = 2

    def f2(self):
        print 'f2'

def B():
    print 'B'


if __name__ == "__main__":
    test2.main()
