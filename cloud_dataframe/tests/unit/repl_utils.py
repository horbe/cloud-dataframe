"""
Utilities for interacting with the Pure Relation REPL.
"""
import subprocess
import json
import time
import os
import tempfile


def send_to_repl(command, timeout=10):
    """
    Send a command to the Pure Relation REPL and return the response.
    
    Args:
        command: The Pure Relation command to execute
        timeout: Maximum time to wait for a response in seconds
        
    Returns:
        dict: The parsed JSON response from the REPL
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(command)
        temp_file_path = temp_file.name
    
    try:
        repl_process = subprocess.Popen(
            ["cat", temp_file_path, "|", "nc", "localhost", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        
        start_time = time.time()
        output = ""
        
        while time.time() - start_time < timeout:
            if repl_process.poll() is not None:
                break
                
            if repl_process.stdout.readable():
                chunk = repl_process.stdout.read(1024)
                if chunk:
                    output += chunk
                    
                    try:
                        json.loads(output)
                        break
                    except json.JSONDecodeError:
                        pass
            
            time.sleep(0.1)
        
        if repl_process.poll() is None:
            repl_process.terminate()
            return {"error": "Timeout waiting for REPL response"}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"error": "Failed to parse REPL response", "raw_output": output}
    
    finally:
        os.unlink(temp_file_path)


def load_csv_to_repl(csv_path, connection_name, table_name):
    """
    Load a CSV file into the REPL.
    
    Args:
        csv_path: Path to the CSV file
        connection_name: Name of the connection to use
        table_name: Name of the table to create
        
    Returns:
        dict: The parsed JSON response from the REPL
    """
    load_cmd = f"load {csv_path} {connection_name} {table_name}"
    return send_to_repl(load_cmd)


def execute_pure_query(pure_query):
    """
    Execute a Pure Relation query in the REPL.
    
    Args:
        pure_query: The Pure Relation query to execute
        
    Returns:
        dict: The parsed JSON response from the REPL
    """
    return send_to_repl(pure_query)


def is_repl_running():
    """
    Check if the Pure Relation REPL is running.
    
    Returns:
        bool: True if the REPL is running, False otherwise
    """
    repl_process = subprocess.Popen(
        ["ps", "-ef"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output, _ = repl_process.communicate()
    return "org.finos.legend.engine.repl.relational.client.RClient" in output
