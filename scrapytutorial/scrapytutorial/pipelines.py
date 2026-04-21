# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class ScrapytutorialPipeline:
#     def process_item(self, item, spider):
#         return item


import pandas as pd
import os

class CsvProcessingPipeline:

    def process_item(self, item, spider):
        file_path = item.get("file_path")

        if not file_path or not os.path.exists(file_path):
            spider.logger.error("CSV file not found")
            return item

        spider.logger.info("Processing CSV with pandas...")

        df = pd.read_csv(file_path)
        spider.logger.info(f"Head: {df.head()}")
        # print(df.head())

        # -------------------------
        # Example operations
        # -------------------------
        spider.logger.info(f"Total rows: {len(df)}")

        df = df.drop_duplicates()

        # Example filter (adjust based on your columns)
        # df = df[df["status"] == "approved"]

        # Save processed file
        processed_path = "./data/processed_applicants.csv"
        df.to_csv(processed_path, index=False)

        spider.logger.info(f"Processed CSV saved: {processed_path}")




        # -------------------------Final Step : Add more information to item and then return final item-------------------------
        # attach result back to item
        item["processed_file"] = processed_path
        item["total_rows"] = len(df)

        spider.logger.info(f"--------------------------------Finished processing--------------------------------")

        return item