class test():
    def __init__(self):
        print('In constructor')
    
    def __del__(self):
        print('In destructor')

if __name__ == "__main__":
    testt = test()