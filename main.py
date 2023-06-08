from pydotenvs import load_env
import os
import hashlib
import sys
import re
load_env()


def ignore_dir(file_path: str) -> bool:
    for _dir in IGNORE_DIRS:
        if _dir in file_path:
            return True
    return False


def get_file_path() -> None:
    for root, dirs, files in os.walk(git_path, topdown=True):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.basename(full_path) in IGNORE_FILES:
                continue
            if ignore_dir(full_path):
                continue
            FILES.append(full_path)


def write_csv(csv_data: str, file_name: str, md5_hash: str) -> None:
    full_path = os.path.join(save_directory, file_name + f'_{md5_hash}.csv')
    with open(full_path, mode='w') as data:
        data.write(csv_data)
    print(f'CSV written to: {full_path}')


def main() -> None:
    # Get files from git repo
    get_file_path()
    # Verify if files were found
    if len(FILES) == 0:
        print(f"No files found in in git directory: {os.environ.get('GIT_PROJECT_DIRECTORY')}")
        sys.exit(1)
    print(f'File count: {len(FILES)}')
    # Build CSV
    print('Creating CSV...')
    for index, file in enumerate(FILES):
        csv = "line_number,text,file_path,project_name"
        print(f'File #{index+1}: {file}')
        with open(file, mode='r', encoding='utf-8') as git_file:
            md5_hash = hashlib.md5(git_file.read().encode('utf-8')).hexdigest()
            file_name = os.path.basename(file)
            git_file.seek(0)
            git_file_lines = git_file.readlines()
            if len(git_file_lines) == 0:
                print('FILE IS EMPTY. IGNORING.')
            else:
                for file_index, file_line in enumerate(git_file_lines):
                    # Replace newline characters with a single space
                    file_line = re.sub(r'\n', ' ', file_line)
                    # Replace multiple spaces at start of string with a single space
                    file_line = re.sub(r'^\s+', '', file_line)
                    # If line is empty, skip it
                    if os.environ.get('SKIP_EMPTY_LINES').upper() == 'TRUE' and file_line.isspace():
                        continue
                    # Create CSV row
                    csv += f'\n{file_index+1},{file_line},{file[file.find(PROJECT_NAME):]},{PROJECT_NAME}'
                write_csv(csv_data=csv, file_name=file_name, md5_hash=md5_hash)



if __name__ == '__main__':
    FILES = []
    IGNORE_FILES = os.environ.get('IGNORE_FILES').split(',')
    IGNORE_DIRS = os.environ.get('IGNORE_DIRS').split(',')
    PROJECT_NAME = os.path.basename(os.environ.get("GIT_PROJECT_DIRECTORY"))
    
    git_path = os.environ.get('GIT_PROJECT_DIRECTORY')
    if not os.path.isdir(git_path):
        raise FileNotFoundError('GIT_PROJECT_DIRECTORY not found or not a directory.')
    save_directory = os.environ.get('SAVE_DIRECTORY')
    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)
    # create a CSV for each page, instead of combining all results into one CSV
    main()
    print(f'Training data can be found in {save_directory}/ directory.')
