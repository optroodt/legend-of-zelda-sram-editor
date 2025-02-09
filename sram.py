import struct
from enum import Enum

MAX_NUMBER_OF_GAMES = 3

LEVEL_MIN = 1
LEVEL_MAX = 9

KEYS_MIN = 0
KEYS_MAX = 255

BOMBS_MIN = 0
BOMBS_MAX = 16

RUPEES_MIN = 0
RUPEES_MAX = 255

HEART_CONTAINERS_MIN = 1
HEART_CONTAINERS_MAX = 16

PLAYCOUNT_MIN = 0
PLAYCOUNT_MAX = 255

TRIFORCE_MIN = 1
TRIFORCE_MAX = 8


class LOZSRAMOffsets:
    ARROWS_OFFSET = 0x2
    BOMBCAPACITY_OFFSET = 0x25
    BOMBS_OFFSET = 0x1
    CANDLE_OFFSET = 0x4
    CHECKSUM_OFFSET = 0x524
    COMPASS_OFFSET = 0x10
    COMPASS9_OFFSET = 0x12
    HEART_CONTAINERS_OFFSET = 0x18
    INVENTORY_DATA = 0x1A
    INVENTORY_DATA_SIZE = 0x28
    KEYS_OFFSET = 0x17
    MAP_DATA = 0x92
    MAP_DATA_SIZE = 0x180
    MAP_OFFSET = 0x11
    MAP9_OFFSET = 0x13
    MISC_DATA = 0x512
    MISC_DATA_SIZE = 0x4
    NAME_DATA = 0x2
    NAME_DATA_SIZE = 0x8
    NOTE_OFFSET = 0xF
    QUEST_OFFSET = 0x9
    PLAYCOUNT_OFFSET = 0x6
    POTION_OFFSET = 0x7
    RING_OFFSET = 0xB
    RUPEES_OFFSET = 0x16
    SRAM_SIZE = 0x2000
    SWORD_OFFSET = 0x0
    TRIFORCE_OFFSET = 0x1A


class SFArrow(Enum):
    ARROW_NONE = 0
    ARROW_WOODEN = 1
    ARROW_SILVER = 2


class SFCandle(Enum):
    CANDLE_NONE = 0
    CANDLE_BLUE = 1
    CANDLE_RED = 2


class SFNote(Enum):
    NOTE_OLDMAN = 0
    NOTE_LINK = 1
    NOTE_OLDWOMAN = 2


class SFPotion(Enum):
    POTION_NONE = 0
    POTION_BLUE = 1
    POTION_RED = 2


class SFQuest(Enum):
    QUEST_FIRST = 0
    QUEST_SECOND = 1


class SFRing(Enum):
    RING_NONE = 0
    RING_BLUE = 1
    RING_RED = 2


class SFSword(Enum):
    SWORD_NONE = 0
    SWORD_WOODEN = 1
    SWORD_WHITE = 2
    SWORD_MASTER = 3


class SFItem(Enum):
    ITEM_BOW = 3
    ITEM_WHISTLE = 5
    ITEM_BAIT = 6
    ITEM_WAND = 8
    ITEM_RAFT = 9
    ITEM_BOOK = 10
    ITEM_LADDER = 12
    ITEM_MAGICKEY = 13
    ITEM_POWERBRACELET = 14
    ITEM_BOOMERANG = 29
    ITEM_MAGICBOOMERANG = 30
    ITEM_MAGICSHIELD = 31


class InvalidSRAMFileException(Exception):
    pass


class SRAMFile:
    def __init__(self, filename: str) -> None:
        self.modified = False
        self.sram = None
        self.valid = [False] * MAX_NUMBER_OF_GAMES
        self.game = 0

        try:
            with open(filename, "rb") as file:
                self.sram = bytearray(file.read())
        except FileNotFoundError:
            raise InvalidSRAMFileException("File not found")

        if len(self.sram) != LOZSRAMOffsets.SRAM_SIZE:
            raise InvalidSRAMFileException("Invalid file size")

        empty_name = "        "
        found_valid = False

        for game in range(MAX_NUMBER_OF_GAMES):

            if self.checksum(game) == self.get_checksum(game):
                self.valid[game] = True
                if self.get_name(game) == empty_name:
                    self.valid[game] = False
                else:
                    found_valid = True

        if not found_valid:
            raise InvalidSRAMFileException("No valid games found")

    def checksum(self, game: int):
        assert 0 <= game < MAX_NUMBER_OF_GAMES

        checksum = 0

        # Name data
        for i in range(LOZSRAMOffsets.NAME_DATA_SIZE):
            checksum += self.sram[
                LOZSRAMOffsets.NAME_DATA + i + (game * LOZSRAMOffsets.NAME_DATA_SIZE)
            ]

        # Inventory data
        for i in range(LOZSRAMOffsets.INVENTORY_DATA_SIZE):
            checksum += self.sram[
                LOZSRAMOffsets.INVENTORY_DATA
                + i
                + (game * LOZSRAMOffsets.INVENTORY_DATA_SIZE)
            ]

        # Map data
        for i in range(LOZSRAMOffsets.MAP_DATA_SIZE):
            checksum += self.sram[
                LOZSRAMOffsets.MAP_DATA + i + (game * LOZSRAMOffsets.MAP_DATA_SIZE)
            ]

        # Misc data
        for i in range(LOZSRAMOffsets.MISC_DATA_SIZE):
            checksum += self.sram[LOZSRAMOffsets.MISC_DATA + (i * 3) + game]

        return checksum

    def get_checksum(self, game: int):
        assert 0 <= game < MAX_NUMBER_OF_GAMES
        offset = LOZSRAMOffsets.CHECKSUM_OFFSET + (game * 2)
        return struct.unpack(">H", self.sram[offset : offset + 2])[0]

    def set_checksum(self, game: int, checksum) -> None:
        assert 0 <= game < MAX_NUMBER_OF_GAMES
        offset = LOZSRAMOffsets.CHECKSUM_OFFSET + (game * 2)
        self.sram[offset : offset + 2] = struct.pack(">H", checksum)
        self.modified = True

    def get_name(self, game: int) -> str:
        assert 0 <= game < MAX_NUMBER_OF_GAMES
        offset = LOZSRAMOffsets.NAME_DATA + (game * LOZSRAMOffsets.NAME_DATA_SIZE)
        raw_name = self.sram[offset : offset + LOZSRAMOffsets.NAME_DATA_SIZE]
        return self.decode_name(raw_name)

    def set_name(self, game: int, name: str) -> None:
        assert 0 <= game < MAX_NUMBER_OF_GAMES
        encoded_name = self.encode_name(name)
        offset = LOZSRAMOffsets.NAME_DATA + (game * LOZSRAMOffsets.NAME_DATA_SIZE)
        self.sram[offset : offset + LOZSRAMOffsets.NAME_DATA_SIZE] = encoded_name
        self.modified = True

    @staticmethod
    def decode_name(raw_name) -> str:
        name = ""
        for ch in raw_name:
            if 0 <= ch <= 9:
                name += chr(48 + ch)
            elif 0xA <= ch <= 0x23:
                name += chr(65 + ch - 0xA)
            elif ch == 0x24:
                name += " "
            elif ch == 0x28:
                name += ","
            elif ch == 0x29:
                name += "!"
            elif ch == 0x2A:
                name += "'"
            elif ch == 0x2B:
                name += "&"
            elif ch == 0x2C:
                name += "."
            elif ch == 0x2D:
                name += '"'
            elif ch == 0x2E:
                name += "?"
            elif ch == 0x2F:
                name += "_"
            else:
                raise ValueError("Invalid character in name data")
        return name

    @staticmethod
    def encode_name(name: str) -> bytearray:
        encoded = bytearray(LOZSRAMOffsets.NAME_DATA_SIZE)
        for i, ch in enumerate(name[: LOZSRAMOffsets.NAME_DATA_SIZE]):
            if "0" <= ch <= "9":
                encoded[i] = ord(ch) - 48
            elif "A" <= ch <= "Z":
                encoded[i] = ord(ch) - 65 + 0xA
            elif ch == " ":
                encoded[i] = 0x24
            elif ch == ",":
                encoded[i] = 0x28
            elif ch == "!":
                encoded[i] = 0x29
            elif ch == "'":
                encoded[i] = 0x2A
            elif ch == "&":
                encoded[i] = 0x2B
            elif ch == ".":
                encoded[i] = 0x2C
            elif ch == '"':
                encoded[i] = 0x2D
            elif ch == "?":
                encoded[i] = 0x2E
            elif ch == "_":
                encoded[i] = 0x2F
            else:
                raise ValueError("Invalid character in name input")
        return encoded

    def get_arrows(self) -> SFArrow:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFArrow(self.sram[index + LOZSRAMOffsets.ARROWS_OFFSET])

    def set_arrows(self, arrows: SFArrow):
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.ARROWS_OFFSET] = arrows.value
        self.modified = True

    def get_bomb_capacity(self) -> int:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return self.sram[index + LOZSRAMOffsets.BOMBCAPACITY_OFFSET]

    def set_bomb_capacity(self, capacity: int) -> None:
        assert BOMBS_MIN <= capacity <= BOMBS_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.BOMBCAPACITY_OFFSET] = capacity
        self.modified = True

    def get_bombs(self) -> int:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return self.sram[index + LOZSRAMOffsets.BOMBS_OFFSET]

    def set_bombs(self, bombs: int) -> None:
        assert BOMBS_MIN <= bombs <= BOMBS_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.BOMBS_OFFSET] = bombs
        self.modified = True

    def get_candle(self) -> SFCandle:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFCandle(self.sram[index + LOZSRAMOffsets.CANDLE_OFFSET])

    def set_candle(self, candle: SFCandle) -> None:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.CANDLE_OFFSET] = candle.value
        self.modified = True

    def get_rupees(self) -> int:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return self.sram[index + LOZSRAMOffsets.RUPEES_OFFSET]

    def set_rupees(self, rupees: int) -> None:
        assert RUPEES_MIN <= rupees <= RUPEES_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.RUPEES_OFFSET] = rupees
        self.modified = True

    def get_heart_containers(self) -> int:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return (self.sram[index + LOZSRAMOffsets.HEART_CONTAINERS_OFFSET] >> 4) + 1

    def set_heart_containers(self, containers: int):
        assert HEART_CONTAINERS_MIN <= containers <= HEART_CONTAINERS_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        self.sram[
            index + LOZSRAMOffsets.HEART_CONTAINERS_OFFSET
        ] &= 0x0F  # Keep last 4 bits
        self.sram[index + LOZSRAMOffsets.HEART_CONTAINERS_OFFSET] |= (
            containers - 1
        ) << 4
        self.modified = True

    def has_compass(self, level: int) -> bool:
        assert LEVEL_MIN <= level <= LEVEL_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        if level == LEVEL_MAX:
            return self.sram[index + LOZSRAMOffsets.COMPASS9_OFFSET] == 1

        return (
            self.sram[index + LOZSRAMOffsets.COMPASS_OFFSET] & (1 << (level - 1))
        ) != 0

    def set_compass(self, level: int, give: bool) -> None:
        assert LEVEL_MIN <= level <= LEVEL_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        if level == LEVEL_MAX:
            self.sram[index + LOZSRAMOffsets.COMPASS9_OFFSET] = 1 if give else 0
        else:
            if give:
                self.sram[index + LOZSRAMOffsets.COMPASS_OFFSET] |= 1 << (level - 1)
            else:
                self.sram[index + LOZSRAMOffsets.COMPASS_OFFSET] &= ~(1 << (level - 1))

        self.modified = True

    def has_item(self, item: int) -> bool:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return self.sram[index + item] == 1

    def set_item(self, item: int, give: bool) -> None:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + item] = 1 if give else 0
        self.modified = True

    def get_keys(self) -> int:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return self.sram[index + LOZSRAMOffsets.KEYS_OFFSET]

    def set_keys(self, keys: int) -> None:
        assert KEYS_MIN <= keys <= KEYS_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.KEYS_OFFSET] = keys
        self.modified = True

    def has_map(self, level: int) -> bool:
        assert LEVEL_MIN <= level <= LEVEL_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        if level == 9:
            return self.sram[index + LOZSRAMOffsets.MAP9_OFFSET] == 1

        return (self.sram[index + LOZSRAMOffsets.MAP_OFFSET] & (1 << (level - 1))) != 0

    def set_map(self, level: int, give: bool):
        assert LEVEL_MIN <= level <= LEVEL_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        if level == 9:
            self.sram[index + LOZSRAMOffsets.MAP9_OFFSET] = 1 if give else 0
        else:
            if give:
                self.sram[index + LOZSRAMOffsets.MAP_OFFSET] |= 1 << (level - 1)
            else:
                self.sram[index + LOZSRAMOffsets.MAP_OFFSET] &= ~(1 << (level - 1))

        self.modified = True

    def get_note(self) -> SFNote:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFNote(self.sram[index + LOZSRAMOffsets.NOTE_OFFSET])

    def set_note(self, note: SFNote):

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.NOTE_OFFSET] = note
        self.modified = True

    def get_play_count(self) -> int:

        index = LOZSRAMOffsets.MISC_DATA + LOZSRAMOffsets.PLAYCOUNT_OFFSET
        return self.sram[index + self.game]

    def set_play_count(self, count: int):
        assert PLAYCOUNT_MIN <= count <= PLAYCOUNT_MAX

        index = LOZSRAMOffsets.MISC_DATA + LOZSRAMOffsets.PLAYCOUNT_OFFSET
        self.sram[index + self.game] = count
        self.modified = True

    def get_potion(self) -> SFPotion:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFPotion(self.sram[index + LOZSRAMOffsets.POTION_OFFSET])

    def set_potion(self, potion: SFPotion) -> None:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.POTION_OFFSET] = potion.value
        self.modified = True

    def get_quest(self) -> SFQuest:

        index = LOZSRAMOffsets.MISC_DATA + LOZSRAMOffsets.QUEST_OFFSET
        return SFQuest(self.sram[index + self.game])

    def set_quest(self, quest: SFQuest) -> None:

        index = LOZSRAMOffsets.MISC_DATA + LOZSRAMOffsets.QUEST_OFFSET
        self.sram[index + self.game] = quest.value
        self.modified = True

    def get_ring(self) -> SFRing:

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFRing(self.sram[index + LOZSRAMOffsets.RING_OFFSET])

    def set_ring(self, ring: SFRing):

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.RING_OFFSET] = ring.value
        self.modified = True

    def get_sword(self) -> SFSword:
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return SFSword(self.sram[index + LOZSRAMOffsets.SWORD_OFFSET])

    def set_sword(self, sword: SFSword):
        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        self.sram[index + LOZSRAMOffsets.SWORD_OFFSET] = sword.value
        self.modified = True

    def has_triforce(self, piece: int) -> bool:
        assert TRIFORCE_MIN <= piece <= TRIFORCE_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )
        return bool(
            self.sram[index + LOZSRAMOffsets.TRIFORCE_OFFSET] & (1 << (piece - 1))
        )

    def set_triforce(self, piece: int, give: bool):
        assert TRIFORCE_MIN <= piece <= TRIFORCE_MAX

        index = LOZSRAMOffsets.INVENTORY_DATA + (
            self.game * LOZSRAMOffsets.INVENTORY_DATA_SIZE
        )

        if give:
            self.sram[index + LOZSRAMOffsets.TRIFORCE_OFFSET] |= 1 << (piece - 1)
        else:
            self.sram[index + LOZSRAMOffsets.TRIFORCE_OFFSET] &= ~(1 << (piece - 1))

        self.modified = True

    def save(self, filename: str) -> bool:
        for game in range(MAX_NUMBER_OF_GAMES):
            if self.valid[game]:
                self.set_checksum(game, self.checksum(game))

        try:
            with open(filename, "wb") as file:
                file.write(self.sram)
            self.modified = False
            return True
        except IOError:
            return False


if __name__ == "__main__":
    # This is how you max out the first save slot
    save_game = "empty.sav"  # There must be a valid save in the first slot
    saves = SRAMFile(save_game)
    saves.set_name(0, "YOURNAME")
    saves.set_rupees(RUPEES_MAX)
    saves.set_heart_containers(HEART_CONTAINERS_MAX)
    saves.set_bomb_capacity(BOMBS_MAX)
    saves.set_bombs(BOMBS_MAX)
    saves.set_arrows(SFArrow.ARROW_SILVER)
    saves.set_candle(SFCandle.CANDLE_RED)
    saves.set_sword(SFSword.SWORD_MASTER)
    saves.set_ring(SFRing.RING_RED)
    saves.set_potion(SFPotion.POTION_RED)
    saves.set_play_count(1)
    for triforce in range(TRIFORCE_MIN, TRIFORCE_MAX + 1):
        saves.set_triforce(triforce, True)

    saves.set_keys(KEYS_MAX)
    for level in range(LEVEL_MIN, LEVEL_MAX + 1):
        saves.set_map(level, True)
        saves.set_compass(level, True)
    for item in SFItem:
        saves.set_item(item.value, True)
    saves.save("Legend of Zelda, The (U) (PRG 1).sav")
