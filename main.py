import subprocess

def main():
    # Initialize the database
    subprocess.run(["flask", "--app", "flaskr", "init-db"])

    # Run the application
    subprocess.run(["flask", "--app", "flaskr", "run", "--debug"])

if __name__ == "__main__":
    main()