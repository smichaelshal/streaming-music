from Classes.classServer import server
def main():
    serverObj = server("10.0.0.12", 4000)
    serverObj.start()
    data = input("Enter to exit: ")
    serverObj.exit()


if __name__ == '__main__':
    main()
