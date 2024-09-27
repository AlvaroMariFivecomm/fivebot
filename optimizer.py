import time
from optimizer.device import Device
from optimizer.fetch_devices_from_db import fetch_devices_from_db
from optimizer.cell_id_manager import CellIdManager

async def optimize_devices():
    start_time = time.time()

    interval_between_device_reports = 20
    max_global_devices_per_hour = 500
    max_devices_per_cell_per_hour = 8

    devices = await fetch_devices_from_db()
    cell_ids = Device.get_all_cell_ids(devices)

    cell_id_manager = CellIdManager(
        cell_ids,
        max_global_devices_per_hour,
        max_devices_per_cell_per_hour,
        interval_between_device_reports
    )

    sorted_devices_by_cell_id = Device.group_and_sort_devices_by_cell_id(devices, True)
    conflicting_devices = []

    for cell_id, devices_in_cell_id in sorted_devices_by_cell_id.items():
        for device in devices_in_cell_id:
            if not cell_id_manager.add_device(cell_id, device.get_report_hour(), device.get_report_min(), device):
                conflicting_devices.append(device)

    unassigned_devices = []
    sorted_conflicting_devices = Device.sort_by_report_time(conflicting_devices)

    while sorted_conflicting_devices:
        device = sorted_conflicting_devices.pop(0)
        cell_id = device.cell_id

        device_added = (
            cell_id_manager.add_device_in_less_busy_previous_min_global(cell_id, device)
            if device.get_report_hour() == 0
            else cell_id_manager.add_device_in_less_busy_previous_hour_global(cell_id, device.get_report_hour(), device)
        )

        if not device_added:
            unassigned_devices.append(device)

    reallocated_devices = []
    unallocatable_devices = []

    sorted_unassigned_devices = Device.sort_by_report_time(unassigned_devices)

    for device in sorted_unassigned_devices:
        cell_id = device.cell_id
        all_devices_in_cell = Device.get_all_devices_by_cell_id(devices, cell_id)
        assigned_devices_in_cell = cell_id_manager.get_devices_by_cell(cell_id)
        all_sorted_devices_in_cell = Device.sort_by_report_time(all_devices_in_cell + assigned_devices_in_cell)
        all_report_times_in_cell = Device.get_all_report_times(all_sorted_devices_in_cell)

        if not cell_id_manager.add_device_in_less_busy_hour_considering_times(cell_id, device, all_report_times_in_cell):
            reallocated_devices.append(device)

            if not cell_id_manager.add_device_in_less_busy_hour_global(cell_id, device):
                unallocatable_devices.append(device)

    assigned_percentage = (len(devices) - len(unassigned_devices)) / len(devices) * 100
    reassigned_count = len(unassigned_devices) - len(reallocated_devices)
    reallocated_count = len(reallocated_devices)
    unallocatable_count = len(unallocatable_devices)

    print(f"{assigned_percentage}% --- {len(devices) - len(unassigned_devices)} dispositivos asignados correctamente.")
    print(f"{reassigned_count} dispositivos reasignados con reportTime posterior.")
    print(f"{reallocated_count} dispositivos reasignados sin tener en cuenta los reportTimes antes de la optimización.")
    print(f"{unallocatable_count} dispositivos no se pudieron reasignar.")

    for device in unallocatable_devices:
        print(f"\n{device.sn} -- {device.report_time} -- {device.cell_id}")

    cell_id_manager.export_matrix_to_txt('output.txt')

    elapsed_time = time.time() - start_time
    print(f"OptimizeDevicesExecutionTime: {elapsed_time:.2f} seconds")

