from QuickProject.Commander import Commander
from . import _ask as ask
from . import *

app = Commander(name)


def pageCheck(url, driver, status):
    """
    解析论文信息
    """
    from selenium.webdriver.common.by import By

    status.update("正在解析论文信息")
    driver.get(url)

    status.update("判断页面类型")

    try:
        is_acm_paper = (
            driver.find_element(By.TAG_NAME, "a").get_attribute("title")
            == "ACM Digital Library home"
        )
    except:
        is_acm_paper = False

    if is_acm_paper:
        status.update("正在解析ACM论文信息")
        title = driver.find_element(By.CLASS_NAME, "citation__title").text.replace(
            ": ", "："
        )
        meeting = driver.find_element(
            By.CLASS_NAME, "epub-section__title"
        ).text.split()[0]
        year = (
            driver.find_element(By.CLASS_NAME, "CitationCoverDate")
            .text.strip()
            .split()[-1]
        )
    else:
        status.update("正在解析IEEE论文信息")
        title = driver.find_element(
            By.XPATH,
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/h1/span',
        ).text
        _info = (
            driver.find_element(By.CLASS_NAME, "stats-document-abstract-publishedIn")
            .find_element(By.TAG_NAME, "a")
            .text.strip()
        )
        meeting = _info.split()[-1][1:-1]
        year = _info.split()[0]

    return meeting, year, title


def getUrl(url, driver, status):
    """
    获取论文链接
    """
    from selenium.webdriver.common.by import By

    status.update("正在打开Sci-Hub..." if user_lang == "zh" else "Opening Sci-Hub...")

    driver.get("https://sci-hub.se/")

    status.update("正在搜索..." if user_lang == "zh" else "Searching...")

    driver.find_element(By.ID, "request").send_keys(url)
    driver.find_element(By.TAG_NAME, "button").click()

    status.update("正在解析..." if user_lang == "zh" else "Parsing...")
    # is exist?
    try:
        if driver.find_element(By.ID, "smile").text == ":(":
            QproDefaultConsole.print(
                QproWarnString,
                "未找到相关论文" if user_lang == "zh" else "No related papers found",
            )
            return None
    except:
        pass

    try:
        # get url from button
        url = driver.find_element(By.TAG_NAME, "button").get_attribute("onclick")
        url = url.split("'")[1][:-1]
        return url
    except:
        QproDefaultConsole.print(
            QproWarnString,
            "未找到相关论文" if user_lang == "zh" else "No related papers found",
        )
        return None


@app.command()
def dl(url: str = "", folder: str = ""):
    """
    下载ACM/IEEE论文

    :param url: 论文链接
    :param folder: 保存路径
    """
    import re

    url = ask(
        {
            "type": "input",
            "message": "请输入论文链接",
            "default": url if (url := requirePackage("pyperclip").paste()) else "",
        }
    )

    status = QproDefaultConsole.status(
        "正在打开浏览器..." if user_lang == "zh" else "Opening browser..."
    )

    status.start()
    driver = getDriver()

    meeting, year, title = pageCheck(url, driver, status)
    url = getUrl(url, driver, status)

    status.update("正在关闭浏览器..." if user_lang == "zh" else "Closing browser...")
    closeDriver()
    if not url:
        status.stop()
        return
    status.update("正在解析..." if user_lang == "zh" else "Parsing...")

    if not folder:
        # move file to meeting dir
        work_path = config.select("work_path")
        if not os.path.exists(os.path.join(work_path, meeting)):
            os.mkdir(os.path.join(work_path, meeting))
        if not os.path.exists(os.path.join(work_path, meeting, year)):
            os.mkdir(os.path.join(work_path, meeting, year))

        status.update("正在下载..." if user_lang == "zh" else "Downloading...")

        # download
        path = os.path.join(
            config.select("work_path"),
            meeting,
            year,
            title.replace(": ", "：").replace("/", "-").strip(".") + ".pdf",
        )
    else:
        status.update("正在下载..." if user_lang == "zh" else "Downloading...")
        path = os.path.join(
            folder, title.replace(": ", "：").replace("/", "-").strip(".") + ".pdf"
        )

    if os.path.exists(path):
        QproDefaultConsole.print(
            QproInfoString,
            f'文件已存在: "{path}"'
            if user_lang == "zh"
            else f'File already exists: "{path}"',
        )
        status.stop()
        return

    requirePackage("QuickStart_Rhy.NetTools.NormalDL", "normal_dl", "QuickStart_Rhy")(
        "https://sci-hub.se" + url,
        path,
        disableStatus=True,
    )
    status.stop()
    QproDefaultConsole.print(
        QproInfoString,
        f'下载完成: "{path}"' if user_lang == "zh" else f'Download complete: "{path}"',
    )


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == "__main__":
    main()
