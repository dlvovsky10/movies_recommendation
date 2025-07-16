from user_movies_table import User_movie_table





def main():
    users = []
    # Creating Interactive CLI
    signed_up = False
    is_on = True
    while is_on:
        command = input("Enter 1 to login or 2 to signup")
        while command not in ('1', '2'):
            command = input("Enter 1 to login or 2 to signup")


if __name__ == "__main__":
    main()
