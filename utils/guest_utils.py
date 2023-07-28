"""
Module for utility functions related to VMs.
"""
import time
from utils import guest_agent


def get_last_network_interface(vm_name):
    """
    Gets the last network interface of a VM.
    """
    data = guest_agent.network_get_interfaces(vm_name)
    return data["return"][-1]["name"]


def check_tx_bytes(vm_name, interface):
    """
    Checks the number of bytes transmitted by a VM's network interface.
    """
    data = guest_agent.network_get_interfaces(vm_name)
    for iface in data["return"]:
        if iface["name"] == interface:
            tx_bytes = int(iface["statistics"]["tx-bytes"])
            return tx_bytes
    return 0


def check_tx_gbits(vm_name, interface):
    """
    Checks the amount of data transmitted by a VM's network interface in Gbits.
    """
    tx_bytes = check_tx_bytes(vm_name, interface)
    tx_gbits = tx_bytes / (2**30) * 8
    return tx_gbits


def print_gbits(vm_name, interface, condition, next_condition):
    # Get the current transmitted gbits
    prev_tx_gbits = check_tx_gbits(vm_name, interface)

    while True:
        with condition:
            condition.wait()  # Wait for our turn to print

            curr_tx_gbits = check_tx_gbits(vm_name, interface)
            diff_tx_gbits = curr_tx_gbits - prev_tx_gbits
            prev_tx_gbits = curr_tx_gbits

            # Print with 6 decimal places
            print(
                f"Data transmitted by {vm_name}: {diff_tx_gbits:.6f} gbits/s")

            time.sleep(1)  # Wait for 1 second

        with next_condition:
            next_condition.notify()  # Notify the next thread that it's their turn to print


def run_python_file(vm_name, python_file_path):
    guest_agent.exec(vm_name, f"python3 {python_file_path}")
