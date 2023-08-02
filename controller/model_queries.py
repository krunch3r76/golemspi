# update view with changes on the model
import subprocess
import time
from utils.mylogger import console_logger, file_logger


def _interpret_active_flag(controller, active_flag):
    if active_flag == "subnet":
        controller.view.update_resources(subnet=controller.model.subnet)
    if active_flag == "hardware_resource_cap_info":
        controller.view.update_resources(
            threads=controller.model.hardware_resource_cap_info["cpu_threads"],
            memory=controller.model.hardware_resource_cap_info["mem_gib"],
            storage=controller.model.hardware_resource_cap_info["storage_gib"],
        )
    if active_flag == "pid":
        (
            task_start_time,
            task_package,
            pid,
        ) = controller.model.retrievals.get_current_exeunit_info()
        resource = task_package
        if resource is not None:
            if "/" in task_package:
                resource = task_package.rsplit("/", 1)[-1]

        controller.view.update_running_exeunit(task_start_time, resource, pid)
    if active_flag == "exeunit terminated":
        controller.view.update_running_exeunit(None, None, None)
        # kludge
        # controller.view._status_scr.set_lines_to_display(
        #     [None, controller.view.exeunit_line.print()]
        # )
        controller.view._status_scr.redraw()
    if active_flag == "payment network":
        payment_network = controller.model.retrievals.get_payment_network()
        payment_networks = controller.model.payment_networks
        (
            address,
            token,
        ) = controller.model.retrievals.get_payment_account_address_info_on_network(
            payment_networks
        )

        if payment_network is not None and address is not None:  # shouldn't be
            controller.view.update_payment_network(payment_network, address, token)


def perform_view_updates(controller, active_flags):
    # process active flags
    for active_flag in active_flags:
        _interpret_active_flag(controller, active_flag)

    # if refresh timer elapsed, update any running exeunit's resource utilizations
    if controller.subprocess_start_time is None:
        controller.subprocess_start_time = time.perf_counter()
    if time.perf_counter() - controller.subprocess_start_time > 0.9:
        # check with model if there is a running exeunit
        time_start, _, pid = controller.model.retrievals.get_current_exeunit_info()

        if pid:  # implies running exeunit
            # run a subprocess to collect cpu and memory usage

            def get_vmrt_child_pid(parent_pid):
                # Get all child PIDs of the parent process
                result = subprocess.run(
                    ["pgrep", "-P", str(parent_pid)], stdout=subprocess.PIPE, text=True
                )
                child_pids = result.stdout.splitlines()

                # Check each child PID to see if it's running vmrt
                for pid in child_pids:
                    result = subprocess.run(
                        ["ps", "-p", str(pid), "-o", "comm="],
                        stdout=subprocess.PIPE,
                        text=True,
                    )
                    if "vmrt" in result.stdout:
                        return int(pid)  # Found the vmrt process

                return None  # No vmrt process found

            def get_vmrt_pid():
                # Get PID of the process running vmrt
                result = subprocess.run(
                    ["pgrep", "vmrt"], stdout=subprocess.PIPE, text=True
                )
                pid = result.stdout.strip()
                return int(pid) if pid else None

            def get_cpu_memory(pid):
                result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "pcpu,rss"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                lines = result.stdout.splitlines()
                if len(lines) >= 2:
                    cpu, mem = lines[1].strip().split()
                    return float(cpu), int(mem)
                else:
                    return None, None

            vmrt_pid = get_vmrt_child_pid(pid)
            if vmrt_pid is None:  # If the child process was not found
                vmrt_pid = get_vmrt_pid()  # Try to find the process running vmrt

            if vmrt_pid is not None:
                cpu, mem = get_cpu_memory(vmrt_pid)
                # time.sleep(0.001)
                controller.view.update_running_exeunit_utilization(
                    time.time() - time_start, cpu, mem
                )
        controller.subprocess_start_time = None
