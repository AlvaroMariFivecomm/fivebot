class Device:
    def __init__(self, sn: str, imei: str, report_time: str, cell_id: str):
        self.sn = sn
        self.imei = imei
        self.report_time = report_time
        self.cell_id = cell_id

    @staticmethod
    def sort_by_report_time(devices: list['Device']) -> list['Device']:
        return sorted(devices, key=lambda device: (Device._parse_report_time(device.report_time)['hour'], Device._parse_report_time(device.report_time)['min']))

    @staticmethod
    def group_devices_by_cell_id(devices: list['Device']) -> dict[str, list['Device']]:
        grouped_devices = {}
        for device in devices:
            if device.cell_id not in grouped_devices:
                grouped_devices[device.cell_id] = []
            grouped_devices[device.cell_id].append(device)
        return grouped_devices

    @staticmethod
    def group_and_sort_devices_by_cell_id(devices: list['Device'], sort_by_report_time: bool = False) -> list[tuple[str, list['Device']]]:
        grouped_devices = Device.group_devices_by_cell_id(devices)
        sorted_entries = sorted(grouped_devices.items(), key=lambda item: len(item[1]), reverse=True)

        if not sort_by_report_time:
            return sorted_entries

        return [(cell_id, Device.sort_by_report_time(devices_in_cell)) for cell_id, devices_in_cell in sorted_entries]

    @staticmethod
    def get_all_report_times(devices: list['Device']) -> list[str]:
        return [device.report_time for device in devices]

    @staticmethod
    def get_all_devices_by_cell_id(devices: list['Device'], cell_id: str) -> list['Device']:
        return [device for device in devices if device.cell_id == cell_id]

    @staticmethod
    def get_all_cell_ids(devices: list['Device']) -> list[str]:
        return list(set(device.cell_id for device in devices))

    @staticmethod
    def _parse_report_time(report_time: str) -> dict[str, int]:
        hour, min = map(int, report_time.split(':'))
        return {'hour': hour, 'min': min}

    def set_report_time(self, report_time: str) -> None:
        self.report_time = report_time

    def get_report_hour(self) -> int:
        return Device._parse_report_time(self.report_time)['hour']

    def get_report_min(self) -> int:
        return Device._parse_report_time(self.report_time)['min']

    def get_cell_id(self) -> str:
        return self.cell_id
