import asyncio
import concurrent.futures
import logging
import typing
import datetime

import app.config as config
import app.rules as rules
import app.metrics as metrics
import app.storage as storage
import app.alert as alert

from .per_process import *

class App:
    __cfg : config.AppConfig
    __rules_provider : rules.RulesProvider
    __metric_sources : typing.Dict[metrics.MetricSourceType, metrics.MetricSource]
    __alert_state_storage : storage.AlertInfoStorage
    __alerter : alert.Alerter
    __logger : logging.Logger

    def __init__(self, cfg : config.AppConfig) -> None:
        self.__cfg = cfg
        self.__logger = logging.getLogger(__name__)

        self.__rules_provider = rules.ConfigRulesProvider(cfg_rules=self.__cfg.rules)
        self.__metric_sources = metrics.init_metric_sources_from_configs(cfg.metric_sources)

        self.__alert_state_storage = storage.storage_from_cfg(cfg=cfg.storage)

        self.__alerter = alert.alerter_from_config(cfg=cfg.alerter)

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

        return res
    
    async def __process_single_metric(self, 
                                      metric : metrics.Metric, 
                                      executor : concurrent.futures.Executor,
                                      rule: rules.Rule,
                                      ) -> dict:
        loop = asyncio.get_running_loop()

        task = loop.run_in_executor(
            executor, 
            process_single_metric_task, 
            metric, 
            rule)
        await task

        return task.result()

    async def __process_rule_metrics(self, rule : rules.Rule, executor : concurrent.futures.Executor):
        get_metrics_task = asyncio.create_task(self.__get_metrics(rule.metric_source_type, rule.query))
        await get_metrics_task

        tasks = []

        metrics_list: typing.List[metrics.Metric] = get_metrics_task.result()
        for metric in metrics_list:
            tasks.append(
                asyncio.create_task(
                    self.__process_single_metric(
                        metric, 
                        executor, 
                        rule)
                )
            )

        results : typing.Sequence[typing.Dict[str, typing.Any]] = await asyncio.gather(*tasks, return_exceptions=False)

        for res in results:
            is_anomaly = res.get("is_anomaly", False)
            metric: metrics.Metric | None = res.get("metric", None)
            prev_info = alert.AlertInfo(started_at=(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat(),
                                        state=alert.AlertState.NORMAL)
            
            if metric is None:
                continue

            key = rule.id + ":" + metric.custom_name(rule.alias_by_label_values)
            new_prev_info = self.__alert_state_storage.get_alert_info(key)
            if new_prev_info is not None:
                prev_info = new_prev_info
            else:
                self.__alert_state_storage.save_alert_info(key, prev_info)

            if is_anomaly:
                starts_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                if prev_info.state == alert.AlertState.ANOMALY:
                    starts_at = prev_info.started_at
                else:
                    self.__alert_state_storage.save_alert_info(
                        key=key,
                        info=alert.AlertInfo(started_at=starts_at,
                                             state=alert.AlertState.ANOMALY))
                self.__logger.info(f"rule: {rule.id} metric: {metric} has anomaly")
                self.__alerter.send_alert(rule=rule, metric=metric)
            elif not is_anomaly:
                now = datetime.datetime.now(datetime.timezone.utc)
                ends_at = now
                if prev_info.state == alert.AlertState.ANOMALY:
                    # alert is now recovered
                    self.__logger.info(f"rule: {rule.id} metric: {metric} recovered to normal")
                    self.__alert_state_storage.save_alert_info(
                        key=key,
                        info=alert.AlertInfo(started_at=ends_at.isoformat(),
                                            state=alert.AlertState.NORMAL))
                else:
                    ends_at = datetime.datetime.fromisoformat(prev_info.started_at)

                if now - ends_at <= datetime.timedelta(minutes=5):
                    alert_start = self.__alert_state_storage.get_last_anomaly_start(key)
                    self.__alerter.send_alert(
                        rule=rule, 
                        metric=metric, 
                        startsAt=alert_start if alert_start else "", 
                        endsAt=ends_at.isoformat())

    def shutdown(self):
        pass

    async def start(self):
        self.__logger.info("starting app...")

        with concurrent.futures.ProcessPoolExecutor(
            initializer=init_model_storage_for_worker,
            initargs=(self.__cfg.storage,),
        ) as executor:
            try:
                while True:
                    task = asyncio.create_task(self.__get_rules())
                    await task

                    rules_to_check = task.result()
                    self.__logger.info("got %s rules to check", str(len(rules_to_check)))

                    background_tasks = set()
                    for rule in rules_to_check:
                        task = asyncio.create_task(self.__process_rule_metrics(rule, executor))

                        background_tasks.add(task)

                        task.add_done_callback(background_tasks.discard)

                    # TODO: move sleep delay to config.
                    await asyncio.sleep(60)
            except asyncio.CancelledError:
                self.__logger.info("cancelled")
            finally:
                self.__logger.info("shutting down...")
                self.shutdown() 

                

