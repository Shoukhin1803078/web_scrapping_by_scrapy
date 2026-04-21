import scrapy
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


class AirRegiFormRequestSpider(scrapy.Spider):
    name = "airregi"

    LOGIN_URL = (
        "https://connect.airregi.jp/login?client_id=AWR&redirect_uri=https%3A%2F%2Fconnect.airregi.jp%2Foauth%2Fauthorize%3Fclient_id%3DAWR%26hruid%3D4a3dd0b3-c95b-4721-bf93-1e11b5d55559%26hrvos%3Dno_referrer%26nonce%3Dt9uu4FH-XiUO-xUbgCLJbF3dT9Zdo1iPQnEJCm96MxY%26redirect_uri%3Dhttps%253A%252F%252Fats.rct.airwork.net%252Fairplf%252Flogin%252Fcb%26response_type%3Dcode%26scope%3Dopenid%2Bprofile%2Bemail%26state%3D2bY88UNZz6wclQJUit3GJAmcPbH8D6SCzEv57n_8Hqs"
    )

    def start_requests(self):
        # Use Playwright so browser launch settings (headless=False) take effect.
        yield scrapy.Request(
            url=self.LOGIN_URL,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context": "regi_auth",
            },
            callback=self.parse,
            errback=self.errback_debug,
            dont_filter=True,
        )

    async def parse(self, response):
        self.logger.info("Login page loaded")
        page = response.meta.get("playwright_page")
        if page:
            # Keep window visible briefly so you can confirm non-headless mode.
            await page.wait_for_timeout(2000)

        # -----------------------------
        # STEP 1: Extract CSRF token
        # -----------------------------
        csrf = response.css("input[name='_csrf']::attr(value)").get()

        self.logger.info(f" CSRF TOKEN: {csrf}")

        if not csrf:
            self.logger.error(" CSRF not found!")
            return

        # -----------------------------
        # STEP 2: Build FORM DATA
        # -----------------------------
        formdata = {
            "_csrf": csrf,
            "username": USERNAME,
            "password": PASSWORD,
        }

        self.logger.info(f" Sending FormRequest: {formdata}")

        # -----------------------------
        # STEP 3: SUBMIT LOGIN
        # -----------------------------
        try:
            yield scrapy.FormRequest.from_response(
                response,
                formxpath="//form[@id='command']",
                formdata=formdata,
                callback=self.after_login,
                meta={
                    "playwright": True,
                    "playwright_context": "regi_auth",
                },
                dont_filter=True,
            )
        finally:
            if page:
                await page.close()

    def after_login(self, response):
        self.logger.info(" AFTER LOGIN RESPONSE RECEIVED")
        self.logger.info(f"URL: {response.url}")

        self.logger.info(" RESPONSE SNIPPET:")


        # CHECK LOGIN STATUS
        if "login" in response.url or "timeout" in response.text:
            self.logger.error(" LOGIN FAILED (FormRequest)")
            return

        self.logger.info(" ==========LOGIN SUCCESS======== ")

        # Try follow redirect manually
        yield scrapy.Request(
            url="https://ats.rct.airwork.net/dashboards",
            meta={
                "playwright": True,
                "playwright_context": "regi_auth",
                "playwright_include_page": True,
            },
            callback=self.after_dashboard,
            dont_filter=True,
        )



    async def after_dashboard(self, response):
        self.logger.info("DASHBOARD PAGE")
        self.logger.info(f"URL======>: {response.url}")

        page = response.meta.get("playwright_page")
        if not page:
            self.logger.error("PAGE NOT FOUND")
            return

        # Check for "ホーム"
        home = response.css("a[href='/dashboards']::text").get()

        if home and "ホーム" in home:
            self.logger.info("DASHBOARD CONFIRMED")
        else:
            self.logger.error("DASHBOARD NOT CONFIRMED")


        # STEP 1: Go to Entries Page

        await page.wait_for_selector("a[href='/entries']")
        await page.click("a[href='/entries']")

        #  Wait for Entries page via heading
        await page.wait_for_selector("h1.styles_heading__3b3pw")

        heading = await page.text_content("h1.styles_heading__3b3pw")

        if "応募者" in heading:
            self.logger.info("Entries page confirmed")
        else:
            self.logger.error("Entries page NOT CONFIRMED")
            return


        #  STEP 2: Build Date Range

        date1 = "2000/1/11"
        today = datetime.today()
        date2 = f"{today.year}/{today.month}/{today.day}"
        date_range = f"{date1} - {date2}"

        self.logger.info(f"DATE RANGE: {date_range}")


        # STEP 3: Set Date (React input)

        await page.wait_for_selector("input[data-la='entries_search_calendar_input']")

        await page.evaluate(
            """(value) => {
                const input = document.querySelector("input[data-la='entries_search_calendar_input']");
                input.removeAttribute('readonly');
                input.value = value;

                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            date_range,
        )

        self.logger.info("Date range applied")

        # Wait for data refresh (important)
        await page.wait_for_timeout(3000)

        # Optional (if needed to trigger filter)
        # await page.keyboard.press("Enter")
        # await page.click("body")


        # STEP 4: Download CSV
        async with page.expect_download() as download_info:
            await page.click("button[data-la='entries_download_btn_click']")

        download = await download_info.value

        file_path = f"./data/all_applicants.csv"
        await download.save_as(file_path)

        self.logger.info(f"CSV downloaded: {file_path}")



        # await page.close()
        # Optional debug
        # self.logger.info(response.text[:500])

        self.logger.info(f"CSV processed: started.....")
        yield {
            "status": "success",
            "message": "Dashboard confirmed",
            "home": home,
            "file_path": file_path,
            "date_range": date_range,
        }





    def errback_debug(self, failure):
        self.logger.error(" REQUEST FAILED")
        self.logger.error(repr(failure))