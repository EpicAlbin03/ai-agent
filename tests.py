from functions.get_files_info import run_python_file


def main():
    print(run_python_file("calculator", "main.py"), "\n")
    print(run_python_file("calculator", "main.py", ["3 + 5"]), "\n")
    print(run_python_file("calculator", "tests.py"), "\n")
    print(run_python_file("calculator", "../main.py"), "\n")
    print(run_python_file("calculator", "nonexistent.py"), "\n")


if __name__ == "__main__":
    main()
