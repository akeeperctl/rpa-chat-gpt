from selenium_driverless import webdriver

import akp.root
from akp.selenium_driverless_ex import webdriver_ex


async def start_driver():
    browser_path = akp.root.get_external_project_root() / "browser"
    extensions_dir = browser_path / "extensions"
    extensions = [extensions_dir / "adguard"]

    options = webdriver.ChromeOptions()
    [options.add_extension(i) for i in extensions]
    options.user_data_dir = browser_path / "user_data1"
    options.headless = True

    return await webdriver_ex.ChromeEx(options=options)
