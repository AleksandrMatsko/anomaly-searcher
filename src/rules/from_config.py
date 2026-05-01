from .rules import Rule, RulesProvider
import logging

class ConfigRulesProvider(RulesProvider):
    """Returns rules passed in constructor"""

    def __init__(self, cfg_rules : list[Rule]) -> None:
        super().__init__()

        self.__rules = cfg_rules
        logging.getLogger(__name__).info("ConfigRulesProvider initialized with %s rules", str(len(cfg_rules)))

    async def get_rules(self) -> list[Rule]:
        return self.__rules