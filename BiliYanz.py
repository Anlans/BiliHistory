from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import base64
from PIL import Image
import json

# bilibili用户名、密码
# 全局变量

USERNAME = '18755066052'
PASSWARD = '179656481'
BORDER = 6
INIT_LEFT = 60


class loginBili():

    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'  # B站登录界面
        self.browser = webdriver.Chrome()
        # 定义显示等待
        self.wait = WebDriverWait(self.browser, 20)
        self.username = USERNAME
        self.password = PASSWARD

    # def __del__(self):
    #     # 关闭浏览器
    #     self.browser.close()

    def login_successfully(self):
        """
        判断是否登陆成功
        :return:
        """
        try:
            '''
           <a data-v-4d9bc88b="" href="//message.bilibili.com" target="_blank" title="消息" class="t"><div data-v-4d9bc88b="" class="num">3</div> <!---->
    消息
  </a>
            '''
            # 登录成功后 界面上会有一个消息按钮
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, '//a[@title="消息"]')))
            )
        except TimeoutException:
            return False

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider:滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            # 只有水平方向有运动 按轨迹移动
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()  # 松开鼠标

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        '''
        <div class="geetest_slider_button" style="opacity: 1; transform: translate(0px, 0px);"></div>
        '''
        slider = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.geetest_slider_button')))

        return slider

    def get_track(self, gap):
        """
        根据偏移量 获取移动轨迹
        :param gap: 偏移量
        :return: 移动轨迹
        """

        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = gap * 4 / 5  # 前4/5段加速 后1/5段减速
        # 计算间隔
        t = 0.2
        # 初速度
        v = 10

        while current < gap:
            if current < mid:
                a = 3  # 加速度为+3
            else:
                a = -3  # 加速度为-3

            # 初速度v0
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))

        return track

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两张图片 各个位置的像素是否相同
        :param image1:不带缺口的图片
        :param image2: 带缺口的图片
        :param x: 位置x
        :param y: 位置y
        :return: (x,y)位置的像素是否相同
        """
        # 获取两张图片指定位置的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        # 设置一个阈值 允许有误差
        threshold = 60
        # 彩色图 每个位置的像素点有三个通道
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1:不带缺口的图片
        :param image2: 带缺口的图片
        :return:
        """
        left = INIT_LEFT  # 定义一个左边的起点 缺口一般离图片左侧有一定的距离 有一个滑块
        for i in range(INIT_LEFT, image1.size[0]):  # 从左到右 x方向
            for j in range(image1.size[1]):  # 从上到下 y方向
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i  # 找到缺口的左侧边界 在x方向上的位置
                    return left-5

        return left

    def get_geetest_image(self):
        """
        获取验证码图片
        :return: 图片对象
        """
        '''
        <canvas class="geetest_canvas_bg geetest_absolute" height="160" width="260"></canvas>
        '''
        # 带阴影的图片
        im = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.geetest_canvas_bg')))
        time.sleep(2)
        im.screenshot('captcha.png')

        # 执行 JS 代码并拿到图片 base64 数据
        JS = 'return document.getElementsByClassName("geetest_canvas_fullbg")[0].toDataURL("image/png");'  # 不带阴影的完整图片
        im_info = self.browser.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
        print(im_info)
        # 拿到base64编码的图片信息
        im_base64 = im_info.split(',')[1]
        # 转为bytes类型
        captcha1 = base64.b64decode(im_base64)
        # 将图片保存在本地
        with open('captcha1.png', 'wb') as f:
            f.write(captcha1)

            # 执行 JS 代码并拿到图片 base64 数据
            JS = 'return document.getElementsByClassName("geetest_canvas_bg")[0].toDataURL("image/png");'  # 带阴影的图片
            im_info = self.browser.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
            print(im_info)
            # 拿到base64编码的图片信息
            im_base64 = im_info.split(',')[1]
            # 转为bytes类型
            captcha2 = base64.b64decode(im_base64)
            # 将图片保存在本地
            with open('captcha2.png', 'wb') as f:
                f.write(captcha2)

        captcha1 = Image.open('captcha1.png')
        captcha2 = Image.open('captcha2.png')
        return captcha1, captcha2

    def get_login_btn(self):
        """
        登陆
        :return: None
        """
        '''
        <a class="btn btn-login">登录</a>
        值有空格的 查找时写一半就好 要么前半段要么后半段
        '''
        # button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.btn-login')))
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn')))
        return button

    def open(self):

        """
        打开登陆界面，输入用户名和密码
        :return: None
        """
        self.browser.get(self.url)  # 打开网址
        # 找到用户名输入框
        # 在浏览器中定位它的HTML代码后 根据id属性来找
        '''
        <input type="text" value="" placeholder="你的手机号/邮箱" id="login-username" maxlength="50" autocomplete="off" class="">
        '''
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        # 找到密码输入框
        '''
        <input type="password" placeholder="密码" id="login-passwd" class="">
        '''
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))

        # 输入用户名和密码
        username.send_keys(self.username)
        password.send_keys(self.password)

    def login(self):
        # 输入用户名和密码
        self.open()
        # 点击登录按钮
        button = self.get_login_btn()  # 找到登录按钮
        button.click()  # 点击

        # 获取验证码图片
        image1, image2 = self.get_geetest_image()

        # 找到缺口的左侧边界 在x方向上的位置
        gap = self.get_gap(image1, image2)
        print('缺口位置：', gap)
        # 减去滑块左侧距离图片左侧在x方向上的距离 即为滑块实际要移动的距离
        gap -= BORDER

        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹：', track)

        # 点按滑块
        slider = self.get_slider()

        # 按轨迹拖动滑块
        self.move_to_gap(slider, track)

        if self.login_successfully():
            print("登录成功")
        else:  # 可能不成功 再试一次
            time.sleep(5)
            self.login()

    def get_history(self):
        self.browser.get('http://api.bilibili.com/x/v2/history')
        content = self.browser.find_element_by_xpath('/html/body/pre').text
        jsonContent = json.loads(content)
        cnt = 0
        for i in jsonContent['data']:
            cnt = cnt + 1
            print('av号: %s--->%s' % (i['aid'], i['title']))
        print('总计=' + str(cnt))

if __name__ == '__main__':
    login = loginBili()
    login.login()
    login.get_history()