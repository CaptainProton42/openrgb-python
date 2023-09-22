from __future__ import annotations
from openrgb import utils
from openrgb.plugins import ORGBPlugin
from dataclasses import dataclass
from typing import Iterator, Union
from enum import IntEnum

class EffectPacketType(IntEnum):
    REQUEST_EFFECT_LIST = 0
    START_EFFECT = 20
    STOP_EFFECT = 21
    REQUEST_PROFILE_LIST = 22
    LOAD_PROFILE = 23


@dataclass
class Effect:
    name: str
    description: str
    enabled: bool

    @classmethod
    def unpack(cls, data: Iterator[int], version: int, *args) -> Effect:
        name = utils.parse_string(data)
        description = utils.parse_string(data)
        enabled = utils.parse_var('?', data)

        return cls(
            name,
            description,
            enabled
        )

@dataclass
class Profile:
    name: str

    @classmethod
    def unpack(cls, data: Iterator[int], version: int, *args) -> Profile:
        name = utils.parse_string(data)

        return cls(
            name
        )

class EffectsPlugin(ORGBPlugin):
    version = 1
    pkt_type_enum = EffectPacketType

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effects = []

    def update(self):
        self.send_packet(EffectPacketType.REQUEST_EFFECT_LIST, request=True)
        self.comms.read()
        self.send_packet(EffectPacketType.REQUEST_PROFILE_LIST, request=True)
        self.comms.read()

    def recv(self, pkt_id: EffectPacketType, data: Iterator[int]):  # type: ignore
        if pkt_id == EffectPacketType.REQUEST_EFFECT_LIST:
            self.effects = utils.parse_list(Effect, data, self.version)
        elif pkt_id == EffectPacketType.REQUEST_PROFILE_LIST:
            self.profiles = utils.parse_list(Profile, data, self.version)
            pass

    def start_effect(self, effect: Union[int, str, Effect]):
        if type(effect) == int:
            effect = self.effects[effect]  # type: ignore
        elif type(effect) == str:
            try:
                effect = next(m for m in self.effects if m.name.lower() == effect.lower())  # type: ignore
            except StopIteration as e:
                raise ValueError(f"Effect `{effect}` not found") from e
        data = utils.pack_string(effect.name)  # type: ignore

        self.send_packet(EffectPacketType.START_EFFECT, data)

    def stop_effect(self, effect: Union[int, str, Effect]):
        if type(effect) == int:
            effect = self.effects[effect]  # type: ignore
        elif type(effect) == str:
            try:
                effect = next(m for m in self.effects if m.name.lower() == effect.lower())  # type: ignore
            except StopIteration as e:
                raise ValueError(f"Effect `{effect}` not found") from e
        data = utils.pack_string(effect.name)  # type: ignore

        self.send_packet(EffectPacketType.STOP_EFFECT, data)

    def load_profile(self, profile: Union[int, str, Effect]):
        if type(profile) == int:
            effect = self.effects[effect]  # type: ignore
        elif type(profile) == str:
            try:
                profile = next(m for m in self.profiles if m.name.lower() == profile.lower())  # type: ignore
            except StopIteration as e:
                raise ValueError(f"Profile `{profile}` not found") from e
        data = utils.pack_string(profile.name)  # type: ignore

        self.send_packet(EffectPacketType.LOAD_PROFILE, data)
