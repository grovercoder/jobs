from playwright.sync_api import sync_playwright

class Browser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.get_browser()  # Implement your custom get_browser method
            self.get_browser_page() 

    def close(self):
        """Closes the browser and releases resources."""
        if self.page and not self.page.is_closed():
            self.page.close()
        if self.browser and not self.browser.is_connected():
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
            
    def get_browser(self, p=None):
        if p:
            self.playwright = p

        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions'
            ]
        )

    def get_browser_page(self):
        chrome_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

        # selected_proxy = choose_proxy()
        # print(f'selected_proxy: {selected_proxy["server"]}')
        selected_proxy = None

        if selected_proxy:
            context = self.browser.new_context(
                proxy={'server': selected_proxy['server']},
                user_agent=chrome_user_agent,
                viewport={"width": 1280, "height": 800},
                timezone_id="America/Edmonton",
                geolocation={"longitude": -73.935242, "latitude": 51.318500},
                permissions=["geolocation"],
                ignore_https_errors=True
            )
        else:
            context = self.browser.new_context(
                user_agent=chrome_user_agent,
                viewport={"width": 1280, "height": 800},
                timezone_id="America/Edmonton",
                geolocation={"longitude": -73.935242, "latitude": 51.318500},
                permissions=["geolocation"],
                ignore_https_errors=True
            )


        context.set_extra_http_headers({
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            })
        
        self.page = context.new_page()
        # attempt to bypass anti-bot mechanisms
        self.page.evaluate("navigator.wedriver = false")
