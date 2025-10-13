import asyncio
import concurrent.futures
import logging
import typing
import datetime

import app.config as config
import app.rules as rules
import app.metrics as metrics

class App:
    __cfg : config.AppConfig
    __rules_provider : rules.RulesProvider
    __metric_sources : typing.Dict[metrics.MetricSourceType, metrics.MetricSource]
    __logger : logging.Logger

    def __init__(self, cfg : config.AppConfig) -> None:
        self.__cfg = cfg
        self.__rules_provider = rules.ConfigRulesProvider(cfg_rules=self.__cfg.rules)
        self.__logger = logging.getLogger(__name__)
        self.__metric_sources = metrics.init_metric_sources_from_configs(cfg.metric_sources)

    async def __get_rules(self):
        return await self.__rules_provider.get_rules()
    
    async def __get_metrics(self, src_type : metrics.MetricSourceType,  query : str) -> list:
        src = self.__metric_sources.get(src_type)
        if src is None:
            raise metrics.UnknownMetricSourceError(src_type)

        res = await src.query(
            query=query,
            interval_start=datetime.datetime.now() - datetime.timedelta(hours=1),
            interval_end=datetime.datetime.now(),
            step="1m",
        )

        print(res)

        return []
    
    async def __process_single_metric(self, metric, executor : concurrent.futures.Executor) -> dict:
        # TODO:
        # 1. Get model from db
        # 2. Get anomaly prediction based for time series
        # 3. Learn on datapoints
        # 4. Save updated model
        # 5.

        loop = asyncio.get_running_loop()

        # loop.run_in_executor(executor, func, args...)

        return {}

    async def __process_metrics(self, rule : rules.Rule, executor : concurrent.futures.Executor):
        get_metrics_task = asyncio.create_task(self.__get_metrics(rule.metric_source_type, rule.query))
        await get_metrics_task

        tasks = []

        metrics_list = get_metrics_task.result()
        for metric in metrics_list:
            tasks.append(asyncio.create_task(self.__process_single_metric(metric, executor)))

        results = await asyncio.gather(*tasks, return_exceptions=False)

    def shutdown(self):
        pass

    async def start(self):
        self.__logger.info("starting app...")

        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                while True:
                    task = asyncio.create_task(self.__get_rules())
                    await task

                    rules_to_check = task.result()
                    self.__logger.info("got %s rules to check", str(len(rules_to_check)))

                    background_tasks = set()
                    for rule in rules_to_check:
                        task = asyncio.create_task(self.__process_metrics(rule, executor))

                        background_tasks.add(task)

                        task.add_done_callback(background_tasks.discard)

                    # TODO: move sleep delay to config.
                    await asyncio.sleep(60)
            except asyncio.CancelledError:
                self.__logger.info("cancelled")
            finally:
                self.__logger.info("shutting down...")
                self.shutdown()

                

