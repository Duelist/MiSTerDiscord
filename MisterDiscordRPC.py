import time
from datetime import timezone
from pypresence import Presence

from MisterSSHClient import MisterSSHClient
from MisterRichPresence import MisterRichPresence

class MisterDiscordRPCClient:
    def __init__(self, address):
        self.discord_client = Presence('952480301404282900')
        self.address = address
        self.ssh_client = MisterSSHClient(self.address)
        self.last_core = None
        self.last_rom = None
        self.discord_client.connect()
    
    def run(self):
        try:
            while True:
                presence = self.get_mister_data()
                if presence is None or not presence.core:
                    self.discord_client.clear()
                else:
                    self.update_discord_presence(presence)
                time.sleep(3)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.discord_client.clear()
            self.discord_client.close()
            self.ssh_client.disconnect()
    
    def get_mister_data(self):
        processes = self.ssh_client.get_core_processes()
        if not processes:
            return None
        core = self.ssh_client.get_core_name(processes)
        rom = ''
        if core != 'menu':
            rom = self.ssh_client.get_latest_rom_name(processes)
        return MisterRichPresence(core, rom)
    
    def update_discord_presence(self, presence):
        try:
            if self.last_core != presence.core:
                print(f'Updating presence: Browsing the menu on {presence.core}')
                self.discord_client.update(
                    details=presence.core,
                    large_image=presence.large_image,
                    state='Browsing the menu',
                    start=int(round(presence.start.replace(tzinfo=timezone.utc).timestamp()))
                )
                self.last_core = presence.core
                self.last_rom = None

                # Clear recent file for core
                self.ssh_client.clear_recents_file()
            elif self.last_rom != presence.rom:
                print(f'Updating presence: Playing {presence.rom} on {presence.core}')
                self.discord_client.update(
                    details=presence.core,
                    large_image=presence.large_image,
                    state=presence.rom,
                    start=int(round(presence.start.replace(tzinfo=timezone.utc).timestamp()))
                )
                self.last_core = presence.core
                self.last_rom = presence.rom
        except Exception as e:
            print(f'Failed to update presence: {e}')