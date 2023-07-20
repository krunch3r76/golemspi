# update view with changes on the model
from utils.mylogger import console_logger, file_logger

def _interpret_active_flag(controller, active_flag):
    if active_flag == "subnet":
        controller.view.update_resources(subnet=controller.model.subnet)
    elif active_flag == "hardware_resource_cap_info":
        controller.view.update_resources(threads=controller.model.hardware_resource_cap_info["cpu_threads"], memory=controller.model.hardware_resource_cap_info["mem_gib"], storage=controller.model.hardware_resource_cap_info["storage_gib"])
    elif active_flag == "pid":
        task_start_time, task_package, pid = controller.model.retrievals.get_current_exeunit_info()
        resource = task_package
        if resource is not None:
            if '/' in task_package:
                resource = task_package.rsplit('/', 1)[-1]
        
        controller.view.update_running_exeunit(task_start_time, resource, pid)
    elif active_flag == "exeunit terminated":
        controller.view.update_running_exeunit(None, None, None)
        # kludge
        controller.view._status_scr.set_lines_to_display([None, controller.view.exeunit_line.print()])
        controller.view._status_scr.redraw()
def perform_view_updates(controller, active_flags):
    for active_flag in active_flags:
        _interpret_active_flag(controller, active_flag)

        
