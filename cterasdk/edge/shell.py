from . import taskmgr as TaskManager

import logging

def run_shell_command(ctera_host, shell_command):
    
    logging.getLogger().info("Executing shell command. {0}".format({'shell_command' : shell_command}))
        
    task = ctera_host.execute("/config/device", "bgshell", shell_command)
    
    try:
    
        task = TaskManager.wait(ctera_host, task)
        
        logging.getLogger().info("Shell command executed. {0}".format({'shell_command' : shell_command}))
        
        return task.result.result
        
    except TaskManager.TaskError as error:
    
        raise CTERAException('An error occurred while executing task', error)