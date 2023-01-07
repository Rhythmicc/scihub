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
            ": ", "--"
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
    try:
        if driver.find_element(By.ID, "smile").text == ":(":
            QproDefaultConsole.print(
                QproWarnString,
                "未找到相关论文" if user_lang == "zh" else "No related papers found",
            )
            QproDefaultConsole.print(QproInfoString, "URL:", url)
            requirePackage("pyperclip", "copy")(url)
            QproDefaultConsole.print(QproInfoString, "URL已复制到剪贴板")
            return None
    except:
        pass

    try:
        # get url from button
        url = driver.find_element(By.TAG_NAME, "button").get_attribute("onclick")
        url = url.split("'")[1]
        return url
    except:
        QproDefaultConsole.print(
            QproWarnString,
            "未找到相关论文" if user_lang == "zh" else "No related papers found",
        )
        return None


def searchPaper(keywords, driver, status):
    """
    通过 Google Scholar 搜索论文
    """
    from selenium.webdriver.common.by import By

    status.update("正在搜索..." if user_lang == "zh" else "Searching...")
    driver.get("https://scholar.google.com/")
    driver.find_element(By.ID, "gs_hdr_tsi").send_keys(keywords)
    driver.find_element(By.ID, "gs_hdr_tsb").click()

    status.update("正在解析..." if user_lang == "zh" else "Parsing...")
    # 如果有人工验证
    try:
        driver.find_element(By.ID, "gs_captcha_ccl")
        QproDefaultConsole.print(
            QproWarnString,
            "Google Scholar 需要人工验证"
            if user_lang == "zh"
            else "Google Scholar needs human verification",
        )
        status.stop()
        ask(
            {
                "type": "confirm",
                "name": "continue",
                "message": "是否继续？" if user_lang == "zh" else "Continue?",
                "default": True,
            }
        )
        status.start()
    except:
        pass
    # 筛选前五个结果以供选择，标题、作者、摘要、链接、[PDF链接]
    top, mid = driver.find_element(By.ID, "gs_res_ccl_top"), driver.find_element(
        By.ID, "gs_res_ccl_mid"
    )
    results = top.find_elements(By.CLASS_NAME, "gs_r") + mid.find_elements(
        By.CLASS_NAME, "gs_r"
    )
    _results = results[:5]
    results = []
    for result in _results:
        # 判断有引用标签的跳过
        try:
            result.find_element(By.CLASS_NAME, "gs_rt").find_element(
                By.CLASS_NAME, "gs_ctu"
            )
            continue
        except:
            pass

        title = result.find_element(By.CLASS_NAME, "gs_rt").text
        author = result.find_element(By.CLASS_NAME, "gs_a").text
        abstract = result.find_element(By.CLASS_NAME, "gs_rs").text
        url = (
            result.find_element(By.CLASS_NAME, "gs_rt")
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
        )
        # 尝试提取pdf链接
        try:
            pdf_url = (
                result.find_element(By.CLASS_NAME, "gs_or_ggsm")
                .find_element(By.TAG_NAME, "a")
                .get_attribute("href")
            )
        except:
            pdf_url = None
        results.append(
            {
                "name": title,
                "author": author,
                "abstract": abstract,
                "url": url,
                "pdf_url": pdf_url,
            }
        )

    # 选择结果
    if len(results) == 0:
        QproDefaultConsole.print(
            QproWarnString,
            "未找到相关论文" if user_lang == "zh" else "No related papers found",
        )
        return None, None
    elif len(results) == 1:
        return results[0]

    from QuickStart_Rhy.TuiTools.Table import qs_default_table

    table = qs_default_table(
        [
            "序号",
            "标题",
            "作者",
            {
                "header": "摘要",
                "justify": "left",
            },
        ],
        title="搜索结果\n",
    )
    for i, result in enumerate(results):
        table.add_row(
            f"[bold cyan]{i + 1}[/]",
            f'[bold {"magenta" if result["name"] == keywords else "gray"}]{result["name"]}[/]',
            result["author"],
            result["abstract"],
        )
    QproDefaultConsole.print(table, justify="center")

    status.stop()

    index = ask(
        {
            "type": "input",
            "message": "请输入序号" if user_lang == "zh" else "Enter the number",
            "default": "1",
            "validate": lambda val: val.isdigit() and 1 <= int(val) <= 5,
        }
    )
    status.start()
    return results[int(index) - 1]


@app.command()
def dl(folder: str = "", search: bool = False, _clip: bool = True):
    """
    下载ACM/IEEE论文

    :param folder: 保存路径
    :param search: 是否搜索论文关键词获取链接
    """
    keywords, url = "", ""
    if search:
        keywords = (
            ask(
                {
                    "type": "input",
                    "message": "请输入关键词",
                    "default": _tmp
                    if _clip and (_tmp := requirePackage("pyperclip").paste())
                    else "",
                }
            )
            .replace("--", ": ")
            .strip()
        )
    else:
        url = ask(
            {
                "type": "input",
                "message": "请输入论文链接",
                "default": url
                if _clip and (url := requirePackage("pyperclip").paste())
                else "",
            }
        ).strip()

    if not _clip and not url and not keywords:
        closeDriver()
        return False

    status = QproDefaultConsole.status(
        "正在打开浏览器..." if user_lang == "zh" else "Opening browser..."
    )

    status.start()
    driver = getDriver()

    if search:
        # 通过 Google Scholar 搜索论文
        scholar = searchPaper(keywords, driver, status)
        url = scholar["url"]

    meeting, year, title = pageCheck(url, driver, status)
    url = (
        scholar["pdf_url"]
        if search and scholar["pdf_url"]
        else getUrl(url, driver, status)
    )

    if _clip:
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
            title.replace(": ", "--").replace("/", "-").strip(".") + ".pdf",
        )
    else:
        status.update("正在下载..." if user_lang == "zh" else "Downloading...")
        path = os.path.join(
            folder, title.replace(": ", "--").replace("/", "-").strip(".") + ".pdf"
        )

    retry = 3

    while retry:
        try:
            requirePackage(
                "QuickStart_Rhy.NetTools.NormalDL", "normal_dl", "QuickStart_Rhy"
            )(
                url
                if url.startswith("http://") or url.startswith("https://")
                else "https:" + url
                if url.startswith("//")
                else "https://sci-hub.se" + url,
                path,
                disableStatus=True,
            )
            break
        except Exception as e:
            QproDefaultConsole.print(QproErrorString, repr(e))
            retry -= 1
            status.update(
                f"下载失败, 正在重试...({3 - retry}/3)"
                if user_lang == "zh"
                else f"Download failed, retrying...({3 - retry}/3)"
            )

    status.stop()
    if retry > 0:
        QproDefaultConsole.print(
            QproInfoString,
            f'下载完成: "{path}"' if user_lang == "zh" else f'Download complete: "{path}"',
        )

        from QuickStart_Rhy import open_file

        open_file(os.path.dirname(path))
    else:
        QproDefaultConsole.print(
            QproErrorString,
            "下载失败，已拷贝下载指令"
            if user_lang == "zh"
            else "Download failed, download command copied",
        )
        requirePackage("pyperclip", "copy")(
            f'qs dl "{url if url.startswith("http://") or url.startswith("https://") else "https:" + url if url.startswith("//") else "https://sci-hub.se" + url}" --name "{path}"'
        )
    return True


@app.command()
def serv(search: bool = False):
    """
    启动服务
    """
    while True:
        _st = app.real_call("dl", search=search, _clip=False)
        if not _st:
            break
    closeDriver()


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == "__main__":
    main()
