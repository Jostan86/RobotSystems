class Jedi():
    def __init__(self, name):
        self.name = name
        print("The Jedi is named " + self.name)

        def say_hello():
            print("the jedi says hello")




jedi = Jedi('bob')
jedi.say_hello()
