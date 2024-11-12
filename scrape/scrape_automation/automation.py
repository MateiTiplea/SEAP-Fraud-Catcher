import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Optional

from discord_webhook import DiscordEmbed, DiscordWebhook
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from db_connection.MongoDBConnection import MongoDBConnection
from scrape.acquisition_fetcher import AcquisitionFetcher
from services.acquisition_service import AcquisitionService
from services.item_service import ItemService

# MAX_DAYS_DEPTH = 10 * 365  # 10 years
MAX_DAYS_DEPTH = 1  # 1 day
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(ENV_PATH)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def create_discord_embed(
    title: str, description: str, color: int, fields: List[dict], footer: dict
):
    embed = DiscordEmbed(title=title, description=description, color=color)
    for field in fields:
        embed.add_embed_field(
            name=field["name"], value=field["value"], inline=field.get("inline", True)
        )
    embed.set_footer(text=footer["text"], icon_url=footer["icon_url"])
    return embed


def send_webhook_message(webhook_url: str, embed: DiscordEmbed):
    webhook = DiscordWebhook(url=webhook_url)
    webhook.add_embed(embed)
    response = webhook.execute()
    return response


def check_last_update_date():
    last_time = None
    last_update_file_path = os.path.join(os.path.dirname(__file__), "last_update.txt")
    if os.path.exists(last_update_file_path):
        with open(last_update_file_path, "r") as f:
            last_time = f.read()

        # convert string to datetime, only the year, month and day are needed
        last_time = datetime.strptime(last_time, "%Y-%m-%d")
    return last_time


def create_days_array():
    today = datetime.now()
    last_time = check_last_update_date()

    starting_day = None
    if not last_time:
        starting_day = today - timedelta(days=MAX_DAYS_DEPTH)
    else:
        starting_day = last_time

    days = []
    while starting_day <= today:
        days.append(starting_day)
        starting_day += timedelta(days=1)

    return days


def get_cpvs_data():
    with open("final_cpv_mapping.json", "r", encoding="utf-8") as f:
        cpvs = json.load(f)

    return cpvs


def get_acquisitions_for_day_and_cpv(
    acquisition_fetcher: AcquisitionFetcher, day: datetime, cpv_id: int
):
    fetched_acquisitions = acquisition_fetcher.get_all_acquisitions_data(
        day, day, cpv_code_id=cpv_id
    )
    return fetched_acquisitions


def get_acquisitions(
    days: List[datetime],
    cpvs: dict,
    db_conn: MongoDBConnection,
    current_acquisitions_ids: List[str],
):
    acquisition_fetcher = AcquisitionFetcher()
    total_acquisitions = []

    for day in tqdm(days[::-1], desc="Processing days", position=2, leave=True):
        acquisitions = list()
        category_progress = tqdm(
            cpvs,
            desc=f"Processing CPV categories on day {day.strftime('%Y-%m-%d')}",
            leave=False,
            position=1,
        )
        for cpv_category in category_progress:
            inner_progress = tqdm(
                cpvs[cpv_category],
                desc=f"Processing CPVs for category {cpv_category} on day {day.strftime('%Y-%m-%d')}",
                leave=False,
                position=0,
            )
            for cpv_data in inner_progress:
                cpv_id = cpv_data["seap_cpv_id"]
                fetched_acquisitions = get_acquisitions_for_day_and_cpv(
                    acquisition_fetcher, day, cpv_id
                )

                acquisitions.extend(fetched_acquisitions)
            inner_progress.close()

        # filter out the acquisitions that are already in the database
        acquisitions = [
            acquisition
            for acquisition in acquisitions
            if acquisition["directAcquisitionID"] not in current_acquisitions_ids
        ]

        tqdm.write(
            f"\n\nFound {len(acquisitions)} new acquisitions to insert on {day.strftime('%Y-%m-%d')}\n\n"
        )

        discord_embed = create_discord_embed(
            title="New acquisitions found",
            description=f"Found {len(acquisitions)} new acquisitions to insert on {day.strftime('%Y-%m-%d')}",
            color=0x00FF00,
            fields=[
                {
                    "name": "Acquisitions",
                    "value": f"{len(acquisitions)} new acquisitions",
                }
            ],
            footer={"text": "SEAP Scraper", "icon_url": ""},
        )

        send_webhook_message(webhook_url=DISCORD_WEBHOOK_URL, embed=discord_embed)

        db_conn.connect()

        for to_insert_acquisition in acquisitions:
            AcquisitionService.create_acquisition_with_items(
                acquisition_data=to_insert_acquisition,
                items_data=to_insert_acquisition["directAcquisitionItems"],
            )

        db_conn.disconnect()

        total_acquisitions.extend(acquisitions)

        category_progress.close()

    return total_acquisitions


def main():
    today = datetime.now()
    days = create_days_array()

    with open("last_update.txt", "w") as f:
        f.write(today.strftime("%Y-%m-%d"))

    cpvs = get_cpvs_data()

    db_connection = MongoDBConnection(env_file=ENV_PATH)
    db_connection.connect()

    current_acquisitions = AcquisitionService.get_all_acquisitions()
    current_acquisitions_ids = [
        acquisition["acquisition_id"] for acquisition in current_acquisitions
    ]

    print(f"Found {len(current_acquisitions_ids)} acquisitions in the database.")

    db_connection.disconnect()

    acquisitions = get_acquisitions(days, cpvs, db_connection, current_acquisitions_ids)

    print(f"Found a total {len(acquisitions)} acquisitions from this run.")


if __name__ == "__main__":
    main()
