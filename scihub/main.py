from QuickProject.Commander import Commander
from . import *

app = Commander(name)


@app.command()
def dl(keywords: list):
    """
    下载论文

    :param keywords: 关键词
    """
    keywords = " ".join(keywords)

    from selenium.webdriver.common.by import By

    with QproDefaultConsole.status("正在打开浏览器...") as st:
        driver = getDriver()

        st.update("正在打开Sci-Hub...")

        driver.get("https://sci-hub.se/")

        st.update("正在搜索...")

        driver.find_element(By.ID, "request").send_keys(keywords)
        driver.find_element(By.TAG_NAME, "button").click()

        st.update("正在解析...")
        # get paper title
        content = driver.find_element(By.ID, "citation")
        content = content.find_element(By.TAG_NAME, "i").text
        title = content.split(".")[0].strip()

        # get meeting
        meeting = content.split(".")[1].strip().split()[-1][1:-1]
        year = content.split(".")[1].strip().split()[0].strip()

        # get url from button
        url = driver.find_element(By.TAG_NAME, "button").get_attribute("onclick")
        url = url.split("'")[1][:-1]

        st.update("正在关闭浏览器...")

        closeDriver()

        # move file to meeting dir
        work_path = config.select("work_path")
        if not os.path.exists(os.path.join(work_path, meeting)):
            os.mkdir(os.path.join(work_path, meeting))
        if not os.path.exists(os.path.join(work_path, meeting, year)):
            os.mkdir(os.path.join(work_path, meeting, year))

        st.update("正在下载...")

        # download

        path = os.path.join(
            config.select("work_path"),
            meeting,
            year,
            title.replace(": ", "：").strip(".") + ".pdf",
        )
        if os.path.exists(path):
            QproDefaultConsole.print(
                QproInfoString,
                f'文件已存在: "{path}"',
            )
            return
    requirePackage("QuickStart_Rhy.NetTools.NormalDL", "normal_dl", "QuickStart_Rhy")(
        "https://sci-hub.se" + url,
        path,
    )
    QproDefaultConsole.print(QproInfoString, f'下载完成: "{path}"')


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == "__main__":
    main()
