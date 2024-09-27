import json
from hour_min_manager import HourMinManager
from device import Device

class CellIdManager:
    def __init__(self, cell_ids, max_devices_per_hour_global, max_devices_per_hour_per_cell, interval_between_devices):
        self.max_devices_per_hour_global = max_devices_per_hour_global
        self.max_devices_per_hour_per_cell = max_devices_per_hour_per_cell
        self.interval_between_devices = interval_between_devices
        self.matrix = self._generate_empty_cell_matrix(cell_ids, interval_between_devices)

    def _generate_empty_cell_matrix(self, cell_ids, interval_between_devices):
        matrix = {cell_id: HourMinManager(interval_between_devices) for cell_id in cell_ids}
        return matrix

    def _get_total_devices_in_hour(self, hour):
        total = sum(self.matrix[cell_id].get_total_devices_in_hour(hour) for cell_id in self.matrix)
        return total

    def add_device(self, cell_id, hour, minute, device):
        if cell_id in self.matrix:
            total_devices_in_hour = self._get_total_devices_in_hour(hour)
            devices_in_cell_hour = self.matrix[cell_id].get_total_devices_in_hour(hour)

            if total_devices_in_hour >= self.max_devices_per_hour_global:
                print(f"No se puede añadir el dispositivo. Se ha alcanzado el máximo de {self.max_devices_per_hour_global} dispositivos globales por hora.")
                return False

            if devices_in_cell_hour >= self.max_devices_per_hour_per_cell:
                print(f"No se puede añadir el dispositivo. Se ha alcanzado el máximo de {self.max_devices_per_hour_per_cell} dispositivos por hora en la celda {cell_id}.")
                return False

            added = self.matrix[cell_id].add_device(hour, minute, device)
            if added:
                print(f"Dispositivo añadido en celda {cell_id} a la hora {hour}:{minute}.")
                return True
        else:
            print(f"La celda {cell_id} no existe en la matriz.")
            return False

    def add_device_in_less_busy_previous_min_global(self, cell_id, device):
        if cell_id not in self.matrix:
            print(f"La celda {cell_id} no existe en la matriz.")
            return False

        total_devices_in_hour = self._get_total_devices_in_hour(0)
        devices_in_cell_hour = self.matrix[cell_id].get_total_devices_in_hour(0)

        if total_devices_in_hour < self.max_devices_per_hour_global and devices_in_cell_hour < self.max_devices_per_hour_per_cell:
            for minute in range(device.get_report_min()):
                if self.matrix[cell_id].add_device(0, minute, device):
                    print(f"Dispositivo añadido en celda {cell_id} en el minuto menos saturado global.")
                    return True
        return False

    def add_device_in_less_busy_previous_hour_global(self, cell_id, start_hour, device):
        if cell_id not in self.matrix:
            print(f"La celda {cell_id} no existe en la matriz.")
            return False

        devices_per_hour_global = {hour: self._get_total_devices_in_hour(hour) for hour in range(start_hour, -1, -1)}
        sorted_hours = sorted(devices_per_hour_global, key=devices_per_hour_global.get)

        for hour in sorted_hours:
            total_devices_in_hour = self._get_total_devices_in_hour(hour)
            devices_in_cell_hour = self.matrix[cell_id].get_total_devices_in_hour(hour)

            if total_devices_in_hour < self.max_devices_per_hour_global and devices_in_cell_hour < self.max_devices_per_hour_per_cell:
                for minute in range(60):
                    if self.matrix[cell_id].add_device(hour, minute, device):
                        print(f"Dispositivo añadido en celda {cell_id} en la hora menos saturada global {hour}:{minute}.")
                        return True
        print(f"No se encontró un hueco disponible para añadir el dispositivo en la celda {cell_id}.")
        return False

    def add_device_in_less_busy_hour_considering_times(self, cell_id, device, all_report_times):
        if cell_id not in self.matrix:
            print(f"La celda {cell_id} no existe en la matriz.")
            return False

        devices_per_hour_global = {hour: self._get_total_devices_in_hour(hour) for hour in range(24)}
        sorted_hours = sorted(devices_per_hour_global, key=devices_per_hour_global.get)

        for hour in sorted_hours:
            devices_in_cell_hour = self.matrix[cell_id].get_total_devices_in_hour(hour)

            if devices_in_cell_hour < self.max_devices_per_hour_per_cell:
                for minute in range(60):
                    proposed_time = f"{hour}:{minute:02d}"
                    if self._is_time_valid(proposed_time, all_report_times):
                        if self.matrix[cell_id].add_device(hour, minute, device):
                            print(f"Dispositivo añadido en celda {cell_id} en la hora {hour}:{minute}.")
                            return True
        return False

    def get_device(self, cell_id, hour, minute):
        if cell_id in self.matrix:
            return self.matrix[cell_id].get_device(hour, minute)
        else:
            print(f"La celda {cell_id} no existe en la matriz.")
            return None

    def remove_device(self, cell_id, hour, minute):
        if cell_id in self.matrix:
            self.matrix[cell_id].remove_device(hour, minute)
        else:
            print(f"La celda {cell_id} no existe en la matriz.")

    def get_devices_by_hour(self, hour):
        devices = []
        for cell_id in self.matrix:
            for minute in range(60):
                device = self.matrix[cell_id].get_device(hour, minute)
                if device:
                    devices.append(device)
        return devices

    def get_devices_by_cell(self, cell_id):
        devices = []
        if cell_id in self.matrix:
            for hour in range(24):
                for minute in range(60):
                    device = self.matrix[cell_id].get_device(hour, minute)
                    if device:
                        devices.append(device)
        else:
            print(f"La celda {cell_id} no existe en la matriz.")
        return devices

    def export_matrix_to_txt(self, file_path):
        content = ''
        devices_per_hour = {hour: 0 for hour in range(24)}
        devices_per_cell = {}
        total_devices = 0

        for cell_id in self.matrix:
            content += f"Celda: {cell_id}\n"
            cell_count = 0

            for hour in range(24):
                for minute in range(60):
                    device = self.matrix[cell_id].get_device(hour, minute)
                    if device:
                        content += f"  Hora {hour}:{minute}: {device.sn}\n"
                        cell_count += 1
                        devices_per_hour[hour] += 1
                        total_devices += 1

            devices_per_cell[cell_id] = cell_count
            content += f"Total dispositivos en Celda {cell_id}: {cell_count}\n\n"

        content += f"Total de dispositivos en todas las celdas: {total_devices}\n\n"
        content += "Resumen de dispositivos por hora:\n"
        for hour in range(24):
            content += f"  Hora {hour}: {devices_per_hour[hour]} dispositivos\n"

        content += "\nResumen de dispositivos por celda:\n"
        for cell_id, count in devices_per_cell.items():
            content += f"  Celda {cell_id}: {count} dispositivos\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Matriz exportada a {file_path}")

    def _is_time_valid(self, proposed_time, all_report_times):
        proposed_hour, proposed_minute = map(int, proposed_time.split(':'))
        proposed_total_minutes = proposed_hour * 60 + proposed_minute

        for report_time in all_report_times:
            report_hour, report_minute = map(int, report_time.split(':'))
            report_total_minutes = report_hour * 60 + report_minute

            if abs(proposed_total_minutes - report_total_minutes) < self.interval_between_devices:
                return False

        return True
