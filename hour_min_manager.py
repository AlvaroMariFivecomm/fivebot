from optimizer.device import Device
from typing import Optional, Dict

class HourMinManager:
    def __init__(self, interval_between_devices: int):
        self.matrix = self._generate_empty_hour_min_matrix()
        self.interval_between_devices = interval_between_devices

    def add_device(self, hour: int, minute: int, device: Device) -> bool:
        if hour in self.matrix and minute in self.matrix[hour]:
            if self.matrix[hour][minute] is None:
                if self._check_time_interval(hour, minute):
                    device.report_time = f"{hour}:{minute}"
                    self.matrix[hour][minute] = device
                    return True
                else:
                    print(f"No se puede añadir el dispositivo. Debe haber al menos {self.interval_between_devices} minutos de diferencia entre dispositivos en la misma celda.")
                    return False
            else:
                print(f"La casilla en la hora {hour}:{minute} ya tiene un dispositivo asignado.")
                return False
        else:
            print(f"La hora {hour} o el minuto {minute} no existe en la matriz.")
            return False

    def get_device(self, hour: int, minute: int) -> Optional[Device]:
        if hour in self.matrix and minute in self.matrix[hour]:
            return self.matrix[hour][minute]
        else:
            print(f"La hora {hour} o el minuto {minute} no existe en la matriz.")
            return None

    def remove_device(self, hour: int, minute: int) -> None:
        if hour in self.matrix and minute in self.matrix[hour]:
            self.matrix[hour][minute] = None
        else:
            print(f"La hora {hour} o el minuto {minute} no existe en la matriz.")

    def get_matrix(self) -> Dict[int, Dict[int, Optional[Device]]]:
        return self.matrix

    def print_matrix(self) -> None:
        import json
        print(json.dumps(self.matrix, indent=2))

    def get_total_devices_in_hour(self, hour: int) -> int:
        return sum(1 for minute in range(60) if self.matrix[hour][minute] is not None)

    def _generate_empty_hour_min_matrix(self) -> Dict[int, Dict[int, Optional[Device]]]:
        return {hour: {minute: None for minute in range(60)} for hour in range(24)}

    def _check_time_interval(self, hour: int, minute: int) -> bool:
        # Compruebo hacia atrás en la misma hora
        for i in range(max(minute - self.interval_between_devices, 0), minute):
            if self.matrix[hour][i] is not None:
                return False

        # Compruebo hacia adelante en la misma hora
        for i in range(minute + 1, min(minute + self.interval_between_devices, 59) + 1):
            if self.matrix[hour][i] is not None:
                return False

        # Si el minuto es menor a 5, compruebo la hora anterior desde el minuto 59 hacia atrás
        if minute < 5:
            prev_hour = 23 if hour == 0 else hour - 1
            for i in range(59, 59 - (5 - minute), -1):
                if self.matrix[prev_hour][i] is not None:
                    return False

        return True
