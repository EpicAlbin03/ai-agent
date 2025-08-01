import os
from config import MAX_CHARS
import subprocess


def get_files_info(working_directory, directory="."):
    abs_working_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, directory))

    if not os.path.isdir(target_path):
        return f'Error: "{directory}" is not a directory'
    if not target_path.startswith(abs_working_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    files_and_dirs = os.listdir(target_path)

    try:
        res = []
        for filename in files_and_dirs:
            filepath = os.path.join(target_path, filename)
            file_size = os.path.getsize(filepath)
            is_dir = os.path.isdir(filepath)
            res.append(f"- {filename}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(res)
    except Exception as e:
        return f"Error: {e}"


def get_file_content(working_directory, file_path):
    abs_working_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not os.path.isfile(target_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    if not target_path.startswith(abs_working_path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    try:
        with open(target_path, "r") as f:
            content = f.read(MAX_CHARS)
            if len(content) >= MAX_CHARS:
                return (
                    content + f'[...File "{file_path}" truncated at 10000 characters]'
                )
            return content
    except Exception as e:
        return f"Error: {e}"


def write_file(working_directory, file_path, content):
    abs_working_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))

    if os.path.isdir(target_path):
        return f'Error: "{file_path}" is a directory'
    if not target_path.startswith(abs_working_path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    try:
        if not os.path.exists(target_path):
            dir_path = os.path.dirname(target_path)
            os.makedirs(dir_path, exist_ok=True)

        with open(target_path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'


def run_python_file(working_directory, file_path, args=[]):
    abs_working_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not os.path.exists(target_path):
        return f'Error: File "{file_path}" not found.'
    if not target_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    if not target_path.startswith(abs_working_path):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    try:
        completed_process = subprocess.run(
            args=["python3", target_path, *args],
            cwd=abs_working_path,
            timeout=30,
            capture_output=True,
            text=True,
        )
        output = []
        if completed_process.stdout:
            output.append(f"STDOUT:\n{completed_process.stdout}")
        if completed_process.stderr:
            output.append(f"STDERR:\n{completed_process.stderr}")
        if completed_process.returncode != 0:
            output.append(f"Process exited with code {completed_process.returncode}")
        return "\n".join(output) if output else "No output produced."
    except Exception as e:
        return f"Error: executing Python file: {e}"
