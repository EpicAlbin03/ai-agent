import os

def get_files_info(working_directory, directory="."):
  dir_path = os.path.join(working_directory, directory)

  if not os.path.isdir(dir_path):
    return f'Error: "{directory}" is not a directory'

  abs_path = os.path.abspath(dir_path)
  abs_working_path = os.path.abspath(working_directory)

  if not abs_path.startswith(abs_working_path):
    return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

  files_and_dirs = os.listdir(dir_path)

  try:
    res = []
    for filename in files_and_dirs:
      filepath = os.path.join(dir_path, filename)
      file_size = os.path.getsize(filepath)
      is_dir = os.path.isdir(filepath)
      res.append(f'- {filename}: file_size={file_size} bytes, is_dir={is_dir}')

    return '\n'.join(res)
  except Exception as e:
    return f'Error: {e}'
