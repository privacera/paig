import json
import os


class FileUtils:
    @staticmethod
    def get_file_paths_in_directory(directory):
        """
        Retrieves file paths in the specified directory.

        Args:
            directory (str): The directory path.

        Returns:
            list: A list of file paths in the directory.
        """
        return [os.path.join(directory, filename) for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]

    @staticmethod
    def load_json_from_file(file_path):
        """
        Loads JSON data from the specified file.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            obj: The JSON data loaded from the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(file_path, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            return []

    @staticmethod
    def read_json_file(file_path):
        """
        Loads list of JSON data from the specified file.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            obj: The list of JSON data loaded from the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def append_json_to_file(file_path, data):
        """
        Appends JSON data to the specified file.

        Args:
            file_path (str): The path to the JSON file.
            data (obj): The JSON data to append to the file.
        """
        with open(file_path, 'a') as f:
            json.dump(data, f)
            f.write('\n')

    @staticmethod
    def remove_line_from_file(file_path, line_to_remove):
        """
        Removes a specific line from a file.

        Args:
            file_path (str): The path to the file.
            line_to_remove (obj): The line to remove from the file.
        """
        temp_file_path = file_path + '.temp'
        with open(file_path, 'r') as read_file, open(temp_file_path, 'w') as write_file:
            for line in read_file:
                if json.loads(line) != line_to_remove:
                    write_file.write(line)
        os.replace(temp_file_path, file_path)

    @staticmethod
    def remove_empty_files(spool_directory, exclude_files=[]):
        """
        Removes empty files from the spool directory, excluding specified files.

        Args:
            spool_directory (str): The directory containing spool files.
            exclude_files (list): List of file names to exclude from deletion.
        """
        for file_name in os.listdir(spool_directory):
            file_path = os.path.join(spool_directory, file_name)
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0 and file_name not in exclude_files:
                os.remove(file_path)