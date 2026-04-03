# anomaly-searcher

App to detect anomalies in your metrics and generate alerts

## Launch locally

### With alerts via email

1. Clone the repository 

2. Create file `./local/alertmanager/email_password` and paste password of email account into it

3. Change `to` of email receiver in 
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`)
to email, on which you want to receive alerts.

4. Change `from` of email receiver in
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`)
to email, from which you want to send alerts.

5. Change `smarthost` of email receiver in
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`)
to SMTP server you are using.

6. Change `auth_username` of email receiver in
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`)
to username for authorization (typically the same as `from`).

7. Run
    ```shell
    docker compose up -d
    ```

8. (Optionally) Test that alertmanager well configured, by adding alert with amtool.
    ```shell
    amtool --alertmanager.url=http://localhost:9093 alert add test-alert node=bar --end={some end time in the future in RFC3339 format}
    ```

9. Run
    ```shell
    python3 main.py -c local/config.yaml
    ```

### With alerts via telegram

1. Clone the repository 

2. Create file `./local/alertmanager/tg_bot_token` and paste token of your telegram bot into it

3. Change `chat_id` of telegram receiver in 
[`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`).
You can obtain `chat_id` it by accessing `https://api.telegram.org/bot{your_bot_token}/getUpdates`

4. Uncomment route with telegram receiver in [`./local/alertmanager/alertmanager.yaml`](`./local/alertmanager/alertmanager.yaml`).

5. Run
    ```shell
    docker compose up -d
    ```

6. In your telegram chat write and send:
    > @your_bot_id /start

7. (Optionally) Test that alertmanager well configured, by adding alert with amtool.
    ```shell
    amtool --alertmanager.url=http://localhost:9093 alert add test-alert node=bar --end={some end time in the future in RFC3339 format}
    ```

8. Run
    ```shell
    python3 main.py -c local/config.yaml
    ```
