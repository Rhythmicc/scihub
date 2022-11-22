from QuickProject.Commander import Commander
from . import _ask
from . import *

app = Commander(name)


@app.command()
def dl(meeting: str = ""):
    """
    下载论文

    :param meeting: 会议
    """
    import re

    keywords = _ask(
        {
            "type": "input",
            "message": "请输入关键词",
        }
    )

    from selenium.webdriver.common.by import By

    status = QproDefaultConsole.status(
        "正在打开浏览器..." if user_lang == "zh" else "Opening browser..."
    )

    status.start()

    driver = getDriver()

    status.update("正在打开Sci-Hub..." if user_lang == "zh" else "Opening Sci-Hub...")

    driver.get("https://sci-hub.se/")

    status.update("正在搜索..." if user_lang == "zh" else "Searching...")

    driver.find_element(By.ID, "request").send_keys(keywords)
    driver.find_element(By.TAG_NAME, "button").click()

    status.update("正在解析..." if user_lang == "zh" else "Parsing...")
    # is exist?
    try:
        if driver.find_element(By.ID, "smile").text == ":(":
            QproDefaultConsole.print(
                QproWarnString,
                "未找到相关论文" if user_lang == "zh" else "No related papers found",
            )
            status.update("正在关闭浏览器..." if user_lang == "zh" else "Closing browser...")
            closeDriver()
            status.stop()
            return
    except:
        pass

    try:
        content = driver.find_element(By.ID, "citation")
        i = content.find_element(By.TAG_NAME, "i").text
        # get url from button
        url = driver.find_element(By.TAG_NAME, "button").get_attribute("onclick")
        url = url.split("'")[1][:-1]

        # get paper title
        content = content.text
    except:
        QproDefaultConsole.print(
            QproWarnString,
            "未找到相关论文" if user_lang == "zh" else "No related papers found",
        )
        status.update("正在关闭浏览器..." if user_lang == "zh" else "Closing browser...")
        closeDriver()
        status.stop()
        return

    status.update("正在关闭浏览器..." if user_lang == "zh" else "Closing browser...")
    closeDriver()
    status.update("正在解析..." if user_lang == "zh" else "Parsing...")

    title = i.split(".")[0].strip()

    # get meeting
    if meeting == "":
        meeting = content.split(".")[1].strip().split()[-1][1:-1]
        if meeting not in ["HPCA", "ASPLOS", "ISCA", "MICRO", "EMC2"]:
            status.stop()
            QproDefaultConsole.print(
                QproWarnString,
                f"未识别: {meeting}, 请修正!"
                if user_lang == "zh"
                else f"Unrecognized: {meeting}, please fix!",
            )

            from . import _ask

            meeting = _ask(
                {
                    "type": "input",
                    "message": "请输入会议简称"
                    if user_lang == "zh"
                    else "Please enter the conference abbreviation",
                }
            )
            status.start()
    year = re.findall(r"\d{4}", content)[0]

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
