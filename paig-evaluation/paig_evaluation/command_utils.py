import os
import subprocess
import sys
import logging

logger = logging.getLogger("paig_eval")


def run_command_in_foreground(command: str, verbose: bool = False):
    """
    Run a command in the foreground and return the output.

    Args:
        command (str): Command to run in the foreground.
        verbose (bool): If True, log the output in real-time.

    Returns:
        tuple: (stdout, stderr) of the command.

    """
    try:
        splited_command = command.split(" ")
        env = os.environ.copy()

        process = subprocess.Popen(
            splited_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
        )

        stdout_lines = []
        stderr_lines = []

        # Read output line by line
        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()

            if output:
                stdout_lines.append(output.strip())
                if verbose:
                    logger.info(output.strip())

            if error:
                stderr_lines.append(error.strip())
                if verbose:
                    logger.error(error.strip())

            if process.poll() is not None and not output and not error:
                break

        # Collect remaining output after the process ends
        remaining_stdout, remaining_stderr = process.communicate()
        stdout_lines.extend(remaining_stdout.splitlines())
        stderr_lines.extend(remaining_stderr.splitlines())
    except Exception as e:
        logger.error(f"Error running command: {e}")
        raise RuntimeError(f"Error running command: {e}")

    return "\n".join(stdout_lines), "\n".join(stderr_lines)


def run_command_in_background(command: str):
    """
    Run a command in the background and return the process object.

    Args:
        command (str): Command to run in the background.

    Returns:
        subprocess.Popen: Process object.

    """
    splited_command = command.split(" ")
    env = os.environ.copy()
    return subprocess.Popen(splited_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def check_process_status(process: subprocess.Popen):
    """
    Check the status of the process.

    Args:
        process (subprocess.Popen): Process object.

    Returns:
        int: 1 if the process is running, 0 if the process is completed.
    """
    try:
        status = process.poll()
        if status is None:
            return 1  # Process is running
        return 0 if status == 0 else -1  # Process is completed
    except Exception as e:
        logger.error(f"Error checking process status: {e}")
        raise RuntimeError(f"Error checking process status: {e}")


def wait_for_process_complete(process: subprocess.Popen, verbose: bool = False):
    """
    Wait for the process to complete and return the output.

    Args:
        process (subprocess.Popen): Process object.
        verbose (bool): Verbose mode.

    Returns:
        str: Output of the process.

    """
    # Check the process status
    while True:
        status = check_process_status(process)
        if status == 0:
            break
        elif status == -1:
            error_message = process.stderr.read()
            if error_message:
                logger.error(error_message)
            break
        else:
            if verbose:
                stdout_line = process.stdout.readline()
                if stdout_line:
                    logger.info(stdout_line.strip())
