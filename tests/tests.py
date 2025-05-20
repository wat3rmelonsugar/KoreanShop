from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import get_user_model
from products.models import Category, Brand, Product
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

User = get_user_model()

class ProductSystemTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='System Category', slug='system-category')
        self.brand = Brand.objects.create(name='System Brand', slug='system-brand')
        self.product = Product.objects.create(
            name='System Product',
            slug='system-product',
            category=self.category,
            brand=self.brand,
            price=100,
            available=True
        )

    def test_user_can_login_and_submit_review(self):
        wait = WebDriverWait(self.driver, 15)

        try:

            print("Opening login page...")
            self.driver.get(f'{self.live_server_url}/login/')
            self.driver.save_screenshot('01_login_page.png')


            print("Filling login form...")
            username = wait.until(
                EC.presence_of_element_located((By.NAME, 'username')))  # Django использует 'username' по умолчанию
            username.send_keys('testuser')

            password = self.driver.find_element(By.NAME, 'password')  # Django использует 'password' по умолчанию
            password.send_keys('testpass')

            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()


            print("Checking login success...")
            try:

                wait.until(EC.text_to_be_present_in_element(
                    (By.TAG_NAME, 'body'), 'Добро пожаловать'))
                print("Login success message found!")

                wait.until(lambda driver: driver.current_url != f'{self.live_server_url}/login/')
                print(f"Redirected to: {self.driver.current_url}")

                self.driver.save_screenshot('02_after_login.png')

            except Exception as e:
                self.driver.save_screenshot('03_login_failed.png')
                print("Current page source:", self.driver.page_source[:2000])
                raise Exception(f"Login verification failed: {str(e)}")

                print("Opening product page...")
                product_url = f'{self.live_server_url}/products/{self.product.id}/{self.product.slug}/'
                self.driver.get(product_url)
                self.driver.save_screenshot('04_product_page.png')

                print("Switching to reviews tab...")
                reviews_tab = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//li[contains(@class, "tab-link") and contains(text(), "Отзывы")]')))
                reviews_tab.click()

                print("Waiting for review form...")
                wait.until(EC.visibility_of_element_located((By.ID, 'tab-2')))

                print("Filling review form...")
                rating_field = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="rating"]')))
                rating_field.send_keys('5')

                comment_field = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="comment"]')
                comment_field.send_keys('Системный отзыв')

                print("Submitting review...")
                submit_button = self.driver.find_element(
                    By.XPATH, '//form[@method="post"]//button[@type="submit"]')
                submit_button.click()

                print("Verifying review...")
                wait.until(
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, '#tab-2'), 'Системный отзыв'))

                print("Test completed successfully!")
                self.driver.save_screenshot('05_test_success.png')

        except Exception as e:
            self.driver.save_screenshot('error.png')
            print(f"Test failed on URL: {self.driver.current_url}")
            print(f"Page source snippet: {self.driver.page_source[:2000]}")
            raise e