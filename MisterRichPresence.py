from datetime import datetime

class MisterRichPresence:
    def __init__(self, core=None, rom=None):
        self.core = self.get_formal_core_name(core)
        self.rom = rom
        self.start = datetime.utcnow()
        self.large_image = 'mister'
    
    def get_formal_core_name(self, core):
        match core:
            case 'Atari5200':
                return 'Atari 5200'
            case 'Atari7800':
                return 'Atari 7800'
            case 'AtariLynx':
                return 'Atari Lynx'
            case 'Gameboy2P':
                return 'Gameboy (2-Player)'
            case 'GBA':
                return 'Gameboy Advance'
            case 'GBA2P':
                return 'Gameboy Advance (2-Player)'
            case 'Genesis':
                return 'Sega Genesis'
            case 'MegaCD':
                return 'Sega Mega CD'
            case 'NeoGeo':
                return 'NEO•GEO'
            case 'NES':
                return 'Nintendo Entertainment System'
            case 'PSX':
                return 'Playstation'
            case 'SMS':
                return 'Sega Master System'
            case 'SNES':
                return 'Super Nintendo Entertainment System'
            case 'TurboGrafx16':
                return 'PC Engine'
            case _:
                return core