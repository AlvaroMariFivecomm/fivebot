from fetch_devices_from_db import fetch_devices_from_db
from optimizer.cell_id_manager import CellIdManager
from optimizer.device import Device

async def optimize_devices():
    interval_between_devices = 10
    max_devices_per_hour_global = 400
    max_devices_per_hour_per_cell = 10

    devices = fetch_devices_from_db()
    cell_ids = Device.get_all_cell_ids(devices)

    cell_id_manager = CellIdManager(
        cell_ids,
        max_devices_per_hour_global,
        max_devices_per_hour_per_cell,
        interval_between_devices
    )

    devices_by_cell_id_ordered = Device.group_and_sort_devices_by_cell_id_and_report_time(devices)
    device_conflicts = []

    for cell_id, devices_in_cell_id in devices_by_cell_id_ordered.items():
        for device in devices_in_cell_id:
            added = cell_id_manager.add_device(cell_id, device.get_report_hour(), device.get_report_min(), device)
            if not added:
                device_conflicts.append(device)

    device_conflict_sorted = Device.sort_by_report_time(device_conflicts)
    rezagaos = []

    while device_conflict_sorted:
        device = device_conflict_sorted.pop(0)
        cell_id = device.cell_id
        added = cell_id_manager.add_device_in_less_busy_previous_hour_global(cell_id, device.get_report_hour(), device)
        if not added:
            rezagaos.append(device)

    cell_id_manager.export_matrix_to_txt('output2.txt')

    rezagaos_sorted = Device.sort_by_report_time(rezagaos)
    for device in rezagaos_sorted:
        cell_id = device.cell_id
        aux1 = Device.get_all_devices_by_cell_id(devices, cell_id)
        aux2 = cell_id_manager.get_devices_by_cell(cell_id)
        aux3 = aux1 + aux2
        aux4 = Device.get_all_report_times(Device.sort_by_report_time(aux3))

        added = cell_id_manager.add_device_in_less_busy_hour_considering_times(cell_id, device, aux4)

        if not added:
            print(f"No se pudo añadir el dispositivo {device.sn} en la celda {cell_id}.")

    print((len(devices) - len(rezagaos)) / len(devices) * 100)
    print(len(rezagaos))
    print(len(devices))

    cell_id_manager.export_matrix_to_txt('output.txt')
