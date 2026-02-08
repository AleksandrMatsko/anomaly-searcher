# anomaly-searcher
App to detect anomalies in your metrics and generate alerts

## Launch locally

1. Clone the repository 

2. Create file `./local/alertmanager/tg_bot_token` and paste token of your telegram bot into it

3. Change `chat_id` of telegram receiver in 
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`).
You can obtain `chat_id` it by accessing `https://api.telegram.org/bot{your_bot_token}/getUpdates`

4. Run
    ```shell
    docker compose up -d
    ```

5. In your telegram chat write and send:
    > @your_bot_id /start

6. (Optionally) Test that alertmanager well configured, by adding alert with amtool.
    ```shell
    amtool --alertmanager.url=http://localhost:9093 alert add test-alert node=bar --end={some end time in the future in RFC3339 format}
    ```

7. Run
    ```shell
    python3 main.py -c local/config.yaml
    ```
