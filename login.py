def login(username, password):
    from selenium import webdriver

    driver = webdriver.Chrome()
    url = "http://index.baidu.com/#/"
    driver.get(url)
    await self.sleep(2)
    driver.find_element_by_class_name("username-text").click()
    await self.sleep(4)
    driver.find_element_by_id("TANGRAM__PSP_4__userName").clear()
    driver.find_element_by_id("TANGRAM__PSP_4__password").clear()
    driver.find_element_by_id("TANGRAM__PSP_4__userName").send_keys(username)
    driver.find_element_by_id("TANGRAM__PSP_4__password").send_keys(password)
    logger.info("input password done")
    input("是否出现验证码? 若出现请在浏览器输入验证码并回车")
    driver.find_element_by_id("TANGRAM__PSP_4__submit").click()
    input("是否出现手机验证码？若出现请在浏览器输入验证码")
    cookies = driver.get_cookies()
    dump_dic(cookies, "{}.cookie".format(username)

login(username, password)