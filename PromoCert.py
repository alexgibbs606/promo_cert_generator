from pathlib import Path
from json import load
from subprocess import run
from sys import argv
from datetime import datetime

PROMO_CERT_FILEPATH = Path('img') / 'promo.svg'

RANK_MAP = {
    'e-1': 'Private',
    'e-2': 'Private First Class',
    'e-3': 'Lance Corporal',
    'e-4': 'Corporal',
    'e-5': 'Sergant',
    'e-6': 'Staff Sergeant',
    'e-7': 'Gunnery Sergeant',
    'e-8': 'First Sergeant',
    'e-9': 'Sergeant Major',
    'e-9a': 'Master Gunnery Sergeant',
    'e-9b': 'Sergeant Major of the Marine Corps',

    'wo-1': 'Warrant Officer 1',
    'wo-2': 'Chief Warrant Officer 2',
    'wo-3': 'Chief Warrant Officer 3',
    'wo-4': 'Chief Warrant Officer 4',
    'wo-5': 'Chief Warrant Officer 5',
    
    'o-1': 'Second Lieutenant',
    'o-2': 'First Lieutenant',
    'o-3': 'Captain',
    'o-4': 'Major',
    'o-5': 'Lieutenant Colonel',
    'o-6': 'Colonel',
    'o-7': 'Brigadier General',
    'o-8': 'Major General',
    'o-9': 'Lieutenant General',
    'o-10': 'General',
}

class PromoCert:
    def __init__(self, config:Path):
        with open(config, 'r', encoding='utf-8') as configFile:
            self.config = load(configFile)
        with open(PROMO_CERT_FILEPATH, 'r', encoding='utf-8') as promoFile:
            self.promoFile = promoFile.read()

        # Placing today's date in the config
        now = datetime.now()
        day = int(now.strftime('%d'))
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        self.config[r'day'] = str(day) + suffix
        self.config[r'month'] = now.strftime('%B')
        self.config[r'year'] = now.strftime('%Y')

        for key, value in self.config.items():
            if isinstance(key, str):
                self.promoFile = self.promoFile.replace(r'{{' + key + r'}}', value)

    def makePromo(self, name:str, rank:str):

        # Checking if bad rank
        if rank.lower() not in RANK_MAP:
            raise ValueError('Invalid rank')
        
        # Replacing name and rank in cert
        promoFile = (self.promoFile + '.')[:-1]
        promoFile = promoFile.replace(r'{{name}}', name).replace(r'{{rank}}', RANK_MAP[rank.lower()])

        # Making rank insignia visible
        promoFile = promoFile.replace(
            f'inkscape:label="{rank.upper()}"\n         style="display:none"',
            f'inkscape:label="{rank.upper()}" ',
        )

        # Finding promo cert location
        promoFilepath = Path('promos', f'{rank}_{name}.svg')
        promoFilepath.parent.mkdir(exist_ok=True)

        # Making a new promo cert file
        with open(promoFilepath, 'w', encoding='utf-8') as promoFileOut:
            promoFileOut.write(promoFile)

        # Generating the png file
        run(f'inkscape --export-area-page --export-type="png" "{promoFilepath.absolute()}"')


if __name__ == '__main__':
    if len(argv) % 2 == 0:
        raise ValueError('Arguments must be in pairs of name, then new rank (in code form)')
    del argv[0]

    certGenerator = PromoCert(Path('config.cfg'))
    for num in range(0, int(len(argv)/2)):
        certGenerator.makePromo(*argv[num:num+2])