from os.path import basename, dirname, splitext
from paramiko import AutoAddPolicy
from paramiko.client import SSHClient

class MisterSSHClient:
    def __init__(self, address, user = 'root', password = '1'):
        self.address = address
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.client.connect(self.address, username=self.user, password=self.password)
        except Exception as e:
            print(f'Error connecting as user {self.user}: {e}')
    
    def disconnect(self):
        try:
            self.client.close()
        except Exception as e:
            print(f'Error disconnecting as user {self.user}: {e}')
    
    def get_client(self):
        transport = self.client.get_transport()
        if self.client is None or not transport.is_alive():
            self.connect()
        return self.client

    def execute_command(self, command):
        client = self.get_client()
        stdin_, stdout_, stderr_ = client.exec_command(command)
        stdout_.channel.recv_exit_status()
        return stdout_.readlines()
    
    def get_base_filename(self, filename):
        return splitext(basename(filename))[0].strip()
    
    def get_name_from_mra(self, file_path):
        name = self.execute_command(f'xmllint --xpath "misterromdescription/name/text()" "{file_path}"')
        return name[0].strip()
    
    def get_platform_from_mra(self, file_path):
        platform = self.execute_command(f'xmllint --xpath "misterromdescription/platform/text()" "{file_path}"')
        return platform[0].strip() if platform else 'Arcade'
    
    def get_core_processes(self):
        processes = self.execute_command('ps aux | grep [r]bf')
        if not processes:
            return None
        return processes

    def get_core_name(self, processes):
        core_name = ''
        for process in processes:
            if not 'rbf' in process:
                continue
            if 'mra' in process:
                file_path = self.execute_command('ps -Ao args | grep [r]bf | sed "s/^.*rbf //"')[0].strip()
                core_name = self.get_platform_from_mra(file_path)
            else:
                core_name = self.get_base_filename(process)
                core_name = core_name.split('_')[0]
        return core_name

    def clear_recents_file(self):
        processes = self.get_core_processes()
        core_name = self.get_core_name(processes)
        filenames = self.execute_command(f'ls -1srt /media/fat/config/*recent* | grep {core_name}')

        if filenames:
            current_filename = filenames.pop()
            current_filename = current_filename.split()[-1]
            self.execute_command(f'> {current_filename}')

    
    def get_latest_recents_file(self, processes):
        filename = ''
        core_name = self.get_core_name(processes)
        filenames = self.execute_command(f'ls -1srt /media/fat/config/*recent* | grep {core_name}')
        while len(filenames) > 0 and not filename:
            current_filename = filenames.pop()
            current_filename = current_filename.split()[-1]
            recent_filename = self.get_base_filename(current_filename)
            recent_idx = recent_filename.split('_')[-1]
            # HACK: The '15' here seems to be an index used by MiSTer for the
            # submenu used to load recent video processing presets
            if not recent_filename == 'cores_recent' and not recent_idx == '15':
                filename = current_filename
        return filename
    
    def get_latest_rom_name(self, processes):
        core_name = self.get_core_name(processes)
        rom_name = core_name
        process = processes[0] if processes else ''
        if core_name == 'MiSTer menu':
            return 'Browsing menus...'
        if '_Arcade' in process and 'mra' in process:
            file_path = self.execute_command('ps -Ao args | grep [r]bf | sed "s/^.*rbf //"')[0].strip()
            return self.get_name_from_mra(file_path)
        if '_Computer' in process or '_Console' in process:
            latest_file = self.get_latest_recents_file(processes)
            if latest_file:
                rom_names = self.execute_command(f'strings {latest_file}')
                return self.get_base_filename(rom_names[2]) if rom_names else None
        return rom_name