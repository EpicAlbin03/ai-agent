from functions.get_files_info import write_file

def main():
  print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"), '\n')
  print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"), '\n')
  print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"), '\n')

if __name__ == "__main__":
    main()