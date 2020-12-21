from Classes.classUser import user
def main():
    userObj = user("10.0.0.12", 4000)
    userObj.start()

    while True:
        pass


if __name__ == '__main__':
    main()
