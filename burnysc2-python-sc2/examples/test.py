import random
from copy import deepcopy

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer


class MyTestBot(BotAI):

    def print_basic_info(self):
        'print basic resource information'
        basic_resource_information = (
            "ITERATION:{ITERATION}, Minerals:{MINERALS}, VESPENE:{VESPENE}, WORKERS:{WORKERS}, IDLE_WORKERS:{IDLE_WORKERS}, SUPPLY:{SUPPLY}  {nexus} {probes}").format(
            ITERATION=self.iteration,
            MINERALS=self.minerals,
            VESPENE=self.vespene,
            WORKERS=self.workers.amount,
            IDLE_WORKERS=self.idle_worker_count,
            SUPPLY=str(self.supply_used) + "/" + str(self.supply_cap),
            nexus=self.units(UnitTypeId.NEXUS).amount,
            probes=self.units(UnitTypeId.PROBE).amount,
        )
        print(basic_resource_information)

    def train_army(self):
        if self.units(UnitTypeId.VOIDRAY).amount < 20:
            for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                if self.can_afford(UnitTypeId.VOIDRAY):
                    sg.train(UnitTypeId.VOIDRAY)

    async def build_infrastructure(self):

        if self.townhalls:
            nexus = self.townhalls.random

            # train probes, more four probes
            if self.workers.amount <= 82:
                if (self.workers.amount < (self.structures(UnitTypeId.NEXUS).amount * 22)) and nexus.is_idle:
                    if self.can_afford(UnitTypeId.PROBE):
                        nexus.train(UnitTypeId.PROBE)

            # build the first pylons and expand direction: build more pylons
            # if self.supply_cap < 196:
            # first pylons
            if not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                pos = nexus.position.towards(self.enemy_start_locations[0], random.randint(8, 15))
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=pos)
            if 12 < self.supply_used and self.supply_used < 100 and (self.supply_cap - self.supply_used < 10):
                pos = nexus.position.towards(self.enemy_start_locations[0], random.randint(8, 15))
                if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                    await self.build(UnitTypeId.PYLON, near=pos)
            if 100 < self.supply_used and self.supply_used < 196 and (self.supply_cap - self.supply_used < 15):
                pos = nexus.position.towards(self.enemy_start_locations[0], random.randint(8, 15))
                if self.can_afford(UnitTypeId.PYLON, num=2) and self.already_pending(UnitTypeId.PYLON) == 0:
                    await self.build(UnitTypeId.PYLON, near=pos)
                    await self.build(UnitTypeId.PYLON, near=pos)

            # assimilator
            if not self.structures(UnitTypeId.ASSIMILATOR) or (
                    self.structures(UnitTypeId.ASSIMILATOR).amount < self.structures(UnitTypeId.NEXUS).amount * 2):
                for v in self.vespene_geyser.closer_than(15, nexus):
                    if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                        await self.build(UnitTypeId.ASSIMILATOR, v)

            # build aggresive structures and units
            # Gateway
            elif not self.structures(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randint(2, 6))
                    await self.build(UnitTypeId.GATEWAY, near=pos)

            # Cybernetic core
            elif not self.structures(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randint(2, 6))
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=pos)
            # Stargate
            elif not self.structures(UnitTypeId.STARGATE):
                if self.can_afford(UnitTypeId.STARGATE):
                    result = await self.build(UnitTypeId.STARGATE, near=nexus)

            # nexus expand
            elif self.workers.amount >= self.townhalls.amount * 22:
                if self.can_afford(UnitTypeId.NEXUS):
                    to_nexus_list = deepcopy(self.expansion_locations_list)
                    for existed_nexus in self.townhalls:
                        to_nexus_list.remove(existed_nexus.position)
                    target_nexus = nexus.position.closest(to_nexus_list)
                    await self.build(UnitTypeId.NEXUS, near=target_nexus)

            # forge
            elif not self.structures(UnitTypeId.FORGE):
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near=nexus)
            # PHOTONCANNON
            elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount:
                if self.can_afford(UnitTypeId.PHOTONCANNON):
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randint(2, 6))
                    # self.build(UnitTypeId.PHOTONCANNON, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                    await self.build(UnitTypeId.PHOTONCANNON, near=pos)


    async def on_step(self, iteration):
        '''Basic order: Army units first, then consider the structures.
Hence 1. [army unit] 2. [infrastructure]
        '''

        # print basic resource information
        self.iteration = iteration
        self.print_basic_info()

        await self.distribute_workers()

        # [army unit]
        self.train_army()

        # [infrastructure]
        await self.build_infrastructure()

        # [attack]
        if self.units(UnitTypeId.VOIDRAY).amount > 2:
            for vg in self.units(UnitTypeId.VOIDRAY).idle:
                if self.enemy_units:
                    vg.attack(random.choice(self.enemy_units))
                elif self.enemy_structures:
                    vg.attack(random.choice(self.enemy_structures))
                else:
                    vg.attack(self.enemy_start_locations[0])


def main():
    run_game(
        maps.get("AcropolisLE"),
        [
            Bot(Race.Protoss, MyTestBot(), name="LittleAntiVirus"),
            Computer(Race.Zerg, Difficulty.Easy)
        ],
        realtime=False,
        # realtime=True,
    )


if __name__ == "__main__":
    main()
