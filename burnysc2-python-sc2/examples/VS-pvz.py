import random
from copy import deepcopy

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race, Alert
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

    async def on_before_start(self, ):
        await self.chat_send("AntiVirus's Bot, Good Luck!")

    async def on_step(self, iteration):
        '''Basic order: Army units first, then consider the structures.
Hence 1. [army unit] 2. [infrastructure]
        '''

        # print basic resource information
        self.iteration = iteration
        self.print_basic_info()

        await self.distribute_workers()



        # esl = self.enemy_start_locations
        # print(esl)
        # await self.expand_now()



def main():
    run_game(
        maps.get("AcropolisLE"),
        [
            Bot(Race.Terran, MyTestBot(), name="AntiVirusBot"),
            Computer(Race.Zerg, Difficulty.Easy)
        ],
        # realtime=False,
        realtime=True,
    )


if __name__ == "__main__":
    main()
