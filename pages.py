"""
Module represents products section in pages
"""
import random
import re
import string

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select


class BasicPage:
    PROD1_DETAILS_XPATH = '/html/body/div[2]/div/div/div[2]/div[1]/div/div[2]/h4/a'
    PROD2_DETAILS_XPATH = '/html/body/div[2]/div/div/div[2]/div[2]/div/div[2]/h4/a'
    PROD3_DETAILS_XPATH = '/html/body/div[2]/div/div/div[2]/div[3]/div/div[2]/h4/a'
    PROD4_DETAILS_XPATH = '/html/body/div[2]/div/div/div[2]/div[4]/div/div[2]/h4/a'
    PRODUCT_DETAILS_XPATHS = {'1': PROD1_DETAILS_XPATH,
                              '2': PROD2_DETAILS_XPATH,
                              '3': PROD3_DETAILS_XPATH,
                              '4': PROD4_DETAILS_XPATH}
    HOME_PAGE_XPATH = '/html/body/div[2]/ul/li[1]/a/i'
    SHOPPING_CART_PAGE_XPATH = '/html/body/nav/div/div[2]/ul/li[4]/a/span'

    MY_ACCOUNT_BUTTON_XPATH = '/html/body/nav/div/div[2]/ul/li[2]/a/span[1]'
    REGISTER_BUTTON_CSS = '.dropdown-menu-right > li:nth-child(1) > a:nth-child(1)'
    FIRST_NAME_REGISTRY_XPATH = '//*[@id="input-firstname"]'
    LAST_NAME_REGISTRY_XPATH = '//*[@id="input-lastname"]'
    EMAIL_REGISTRY_XPATH = '//*[@id="input-email"]'
    TEL_REGISTRY_XPATH = '//*[@id="input-telephone"]'
    PASSWORD_REGISTRY_XPATH = '//*[@id="input-password"]'
    PASSWORD_CONFIRM_REGISTRY_XPATH = '//*[@id="input-confirm"]'
    PRIVACY_POLICY_BUTTON_REGISTRY_XPATH = '/html/body/div[2]/div/div/form/div/div/input[1]'
    CONTINUE_BUTTON_REGISTRY_XPATH = '/html/body/div[2]/div/div/form/div/div/input[2]'
    FINISH_ORDER_BUTTON_XPATH = '/html/body/div[2]/div/div/div/div/a'

    VIEW_BUTTON_FROM_CART_XPATH = '/html/body/header/div/div/div[3]/div/ul/li[2]/div/p/a[1]/strong'
    REMOVE_BUTTON_XPATH = '/html/body/header/div/div/div[3]/div/ul/li[1]/table/tbody/tr[1]/td[5]/button'
    CART_XPATH = '//*[@id="cart-total"]'

    def __init__(self, driver):
        self.driver = driver

    def _wait_for_element(self, xpath, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def _wait_for_element_to_be_clickable(self, xpath, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def _click_enabled_element(self, xpath, timeout=10):
        self._wait_for_element_to_be_clickable(xpath, timeout)
        self.driver.find_element_by_xpath(xpath).click()

    def _insert_text_to_enabled_element(self, xpath, text, timeout=10):
        self._wait_for_element(xpath, timeout)
        elem = self.driver.find_element_by_xpath(xpath)
        elem.send_keys(Keys.CONTROL + 'a')
        elem.send_keys(Keys.DELETE)
        elem.send_keys(text)

    def _get_text_from_enabled_element(self, xpath, timeout=10):
        self._wait_for_element(xpath, timeout)
        return self.driver.find_element_by_xpath(xpath).text

    def _get_element_from_enabled_element(self, xpath, timeout=10):
        self._wait_for_element(xpath, timeout)
        return self.driver.find_element_by_xpath(xpath)

    @staticmethod
    def _convert_price_to_float(price):
        """
        Convert string price formats, eg. 10,000,000.00 will be converted to 10000000.0
        :param price: type: str
        """
        return float(price.replace(",", "")) if "," in price else float(price)

    def _get_cart_items_quantity(self):
        self.driver.refresh()
        cart_string = self._get_text_from_enabled_element(self.CART_XPATH)
        return re.match("(.*) item", cart_string).group(1)

    def _get_cart_items_value(self):
        self.driver.refresh()
        cart_string = self._get_text_from_enabled_element(self.CART_XPATH)
        return re.search("(?<=\$)(.*)", cart_string).group()

    def _click_cart_button(self):
        self._click_enabled_element(self.CART_XPATH)

    def _click_view_button(self):
        self._click_enabled_element(self.VIEW_BUTTON_FROM_CART_XPATH)

    def _clean_cart(self):
        while True:
            self.driver.refresh()
            self._click_cart_button()
            try:
                self.driver.find_element_by_xpath(self.REMOVE_BUTTON_XPATH).is_displayed()
                self._click_enabled_element(self.REMOVE_BUTTON_XPATH)
            except NoSuchElementException:
                break
        self._click_cart_button()

    def _go_to_home_page(self):
        self._click_enabled_element(self.HOME_PAGE_XPATH)

    def _go_to_product_details_page(self, product_number):
        self._click_enabled_element(self.PRODUCT_DETAILS_XPATHS[product_number])

    def _go_to_shopping_cart_page(self):
        self._click_enabled_element(self.SHOPPING_CART_PAGE_XPATH)

    def _register_user(self):
        self._click_enabled_element(self.MY_ACCOUNT_BUTTON_XPATH)
        self.driver.find_element_by_css_selector(self.REGISTER_BUTTON_CSS).click()
        first_name = self._get_element_from_enabled_element(self.FIRST_NAME_REGISTRY_XPATH)
        first_name.send_keys('Jan')
        import time
        time.sleep(2)
        last_name = self._get_element_from_enabled_element(self.LAST_NAME_REGISTRY_XPATH)
        last_name.send_keys('Kowalski')
        email = self._get_element_from_enabled_element(self.EMAIL_REGISTRY_XPATH)
        email.send_keys(self._email_generator())
        tel = self._get_element_from_enabled_element(self.TEL_REGISTRY_XPATH)
        tel.send_keys('46652033')
        password = self._get_element_from_enabled_element(self.PASSWORD_REGISTRY_XPATH)
        password.send_keys('1qazZAQ!')
        password_confirm = self._get_element_from_enabled_element(self.PASSWORD_CONFIRM_REGISTRY_XPATH)
        password_confirm.send_keys('1qazZAQ!')
        self._get_element_from_enabled_element(self.PRIVACY_POLICY_BUTTON_REGISTRY_XPATH).click()
        self._get_element_from_enabled_element(self.CONTINUE_BUTTON_REGISTRY_XPATH).click()
        self._click_enabled_element(self.FINISH_ORDER_BUTTON_XPATH)
        self._click_enabled_element(self.HOME_PAGE_XPATH)

    @staticmethod
    def _email_generator():
        letters = string.ascii_letters + string.digits
        return '{}{}@gmail.com'.format(''.join(random.choices(letters, k=10)), random.randint(0, 10000000000))


class HomePage(BasicPage):
    PROD1_ADD_TO_CART_XPATH = '/html/body/div[2]/div/div/div[2]/div[1]/div/div[3]/button[1]'
    PROD2_ADD_TO_CART_XPATH = '/html/body/div[2]/div/div/div[2]/div[2]/div/div[3]/button[1]'
    PROD3_ADD_TO_CART_XPATH = '/html/body/div[2]/div/div/div[2]/div[3]/div/div[3]/button[1]'
    PROD4_ADD_TO_CART_XPATH = '/html/body/div[2]/div/div/div[2]/div[4]/div/div[3]/button[1]'
    PRODUCT_IDS_XPATHS = {'1': PROD1_ADD_TO_CART_XPATH,
                          '2': PROD2_ADD_TO_CART_XPATH,
                          '3': PROD3_ADD_TO_CART_XPATH,
                          '4': PROD4_ADD_TO_CART_XPATH}

    PROD1_PRICE_XPATH = '/html/body/div[2]/div/div/div[2]/div[1]/div/div[2]/p[2]/span'
    PROD2_PRICE_XPATH = '/html/body/div[2]/div/div/div[2]/div[2]/div/div[2]/p[2]/span'
    PROD3_PRICE_XPATH = '/html/body/div[2]/div/div/div[2]/div[3]/div/div[2]/p[2]/span'
    PROD4_PRICE_XPATH = '/html/body/div[2]/div/div/div[2]/div[4]/div/div[2]/p[2]/span'
    PRODUCT_PRICES_XPATHS = {'1': PROD1_PRICE_XPATH,
                             '2': PROD2_PRICE_XPATH,
                             '3': PROD3_PRICE_XPATH,
                             '4': PROD4_PRICE_XPATH}

    REGISTRY_BUTTON_XPATH = '//*[@id="button-register"]'
    MESSAGE_CART_XPATH = '/html/body/header/div/div/div[3]/div/ul/li/p'

    def __init__(self, driver):
        self.driver = driver
        super(HomePage, self).__init__(self.driver)

    def _add_single_product_to_cart(self, product_number):
        """

        :param product_number: type: str [1-4]
        """
        self._click_enabled_element(self.PRODUCT_IDS_XPATHS[product_number])

    def _get_product_value(self, product_number):
        """
        :param product_number: type: str [1-4]
        """
        value_string = self._get_text_from_enabled_element(self.PRODUCT_PRICES_XPATHS[product_number])
        return re.search("(?<=\$)(.*)", value_string).group()


class DetailsPage(BasicPage):
    INPUT_QUANTITY_DETAILS_PAGE_XPATH = '//*[@id="input-quantity"]'
    ADD_TO_CART_XPATH = '//*[@id="button-cart"]'
    ALERT_INFO_CSS = '.alert'
    SET_QTY_XPATH = '//*[@id="input-quantity"]'

    def __init__(self, driver):
        self.driver = driver
        super(DetailsPage, self).__init__(self.driver)

    def _get_default_quantity(self):
        qty = self.driver.find_element_by_xpath(self.INPUT_QUANTITY_DETAILS_PAGE_XPATH)
        return qty.get_attribute('value')

    def _fill_qty_field_with_given_amount(self, value):
        self._insert_text_to_enabled_element(self.SET_QTY_XPATH, value)


class ShoppingCartPage(BasicPage):
    SUB_TOTAL_VALUE_BEFORE_SHIPPING = '/html/body/div[2]/div/div/div[2]/div/table/tbody/tr[1]/td[2]'
    SUB_TOTAL_VALUE = '/html/body/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[2]'
    FLAT_SHIPPING_RATE_VALUE = '/html/body/div[2]/div[2]/div/div[2]/div/table/tbody/tr[2]/td[2]'
    TOTAL_VALUE = '/html/body/div[2]/div[2]/div/div[2]/div/table/tbody/tr[3]/td[2]'
    CHECKOUT_BUTTON_XPATH = '/html/body/div[2]/div/div/div[3]/div[2]/a'

    FIRST_NAME_INPUT_XPATH = '//*[@id="input-payment-firstname"]'
    LAST_NAME_INPUT_XPATH = '//*[@id="input-payment-lastname"]'
    ADDRESS1_INPUT_XPATH = '//*[@id="input-payment-address-1"]'
    CITY_INPUT_XPATH = '//*[@id="input-payment-city"]'
    REGION_INPUT_XPATH = '//*[@id="input-payment-zone"]'

    CONTINUE_BILLING_DETAILS_BUTTON_XPATH = '//*[@id="button-payment-address"]'
    SHOPPING_BUTTON_XPATH = '//*[@id="button-shipping-address"]'
    SHOPPING_METHOD_BUTTON_XPATH = '//*[@id="button-shipping-method"]'
    PAYMENT_BUTTON_XPATH = '//*[@id="button-payment-method"]'
    TERM_AND_CONDITIONS_BUTTON_XPATH = '/html/body/div[2]/div/div/div/div[5]/div[2]/div/div[2]/div/input[1]'
    CONFIRM_ORDER_XPATH = '//*[@id="button-confirm"]'

    ALERT_FROM_CHECKOUT_PAGE_XPATH = '/html/body/div[2]/div[1]'
    SECOND_ALERT_FROM_CHECKOUT_PAGE = '/html/body/div[2]/div[2]'
    CLOSE_MESSAGE_XPATH = '/html/body/div[2]/div[1]/button'

    SUCCESS_CHECKOUT_XPATH = '/html/body/div[2]/ul/li[4]/a'
    BUY_MESSAGE_XPATH = '/html/body/div[2]/div/div/h1'
    VALIDATION_MESSAGE_XPATH = '/html/body/div[2]/div/div/p'
    UPDATE_BUTTON_XPATH = '/html/body/div[2]/div/div/form/div/table/tbody/tr/td[4]/div/span/button[1]'

    ESTIMATE_SHOPPING_AND_TAXES_XPATH = '/html/body/div[2]/div/div/div[1]/div[2]/div[1]/h4/a'
    REGION_FROM_TAXES_FORM_XPATH = '//*[@id="input-zone"]'
    FLAT_RATE_XPATH = '/html/body/div[3]/div/div/div[2]/div/label/input'
    SHIPPING_METHOD_XPATH = '/html/body/div[3]/div/div/div[2]/div/label'
    GET_QUOTES_BUTTON_XPATH = '//*[@id="button-quote"]'
    APPLY_SHOPPING_BUTTON_XPATH = '//*[@id="button-shipping"]'
    SET_QTY_FROM_SHOPPING_PAGE = '/html/body/div[2]/div/div/form/div/table/tbody/tr[1]/td[4]/div/input'

    def __init__(self, driver):
        self.driver = driver
        super(ShoppingCartPage, self).__init__(self.driver)

    def _get_sub_total_value(self):
        try:
            taxes = self._get_text_from_enabled_element(self.SUB_TOTAL_VALUE_BEFORE_SHIPPING)
        except AttributeError:
            taxes = self._get_text_from_enabled_element(self.SUB_TOTAL_VALUE)
        return re.search("(?<=\$)(.*)", taxes).group()

    def _get_first_alert_message(self):
        cart_string = self._get_text_from_enabled_element(self.ALERT_FROM_CHECKOUT_PAGE_XPATH)
        return re.match("(.*)\n", cart_string).group(1)

    def _get_second_alert_message(self):
        cart_string = self._get_text_from_enabled_element(self.SECOND_ALERT_FROM_CHECKOUT_PAGE)
        return re.match("(.*)\n", cart_string).group(1)

    def _get_taxes(self):
        taxes = self._get_text_from_enabled_element(self.SHIPPING_METHOD_XPATH)
        return re.search("(?<=\$)(.*)", taxes).group()

    def _fill_qty_field_with_given_amount(self, value):
        self._insert_text_to_enabled_element(self.SET_QTY_FROM_SHOPPING_PAGE, value)

    def _select_region_from_taxes_form(self):
        region = Select(self._get_element_from_enabled_element(self.REGION_FROM_TAXES_FORM_XPATH))
        region.select_by_value('2632')

    def _calculated_sub_total_price_with_flat_shipping_rate(self):
        from time import sleep
        sleep(5)
        taxes = self._get_text_from_enabled_element(self.SUB_TOTAL_VALUE)
        sub_total = re.search("(?<=\$)(.*)", taxes).group()
        sub_total_price = self._convert_price_to_float(sub_total)

        taxes = self._get_text_from_enabled_element(self.FLAT_SHIPPING_RATE_VALUE)
        rate_price = re.search("(?<=\$)(.*)", taxes).group()
        rate_price = self._convert_price_to_float(rate_price)
        total_price = sub_total_price + rate_price
        return total_price

    def _fill_checkout_form(self):
        first_name = self._get_element_from_enabled_element(self.FIRST_NAME_INPUT_XPATH)
        first_name.send_keys('Jan')
        import time
        time.sleep(5)
        last_name = self._get_element_from_enabled_element(self.LAST_NAME_INPUT_XPATH)
        last_name.send_keys('Kowalski')
        adress1 = self._get_element_from_enabled_element(self.ADDRESS1_INPUT_XPATH)
        adress1.send_keys('Sloneczna 1')
        city = self._get_element_from_enabled_element(self.CITY_INPUT_XPATH)
        city.send_keys('Wroclaw')
        region = Select(self._get_element_from_enabled_element(self.REGION_INPUT_XPATH))
        region.select_by_value('2631')
        self._click_enabled_element(self.CONTINUE_BILLING_DETAILS_BUTTON_XPATH)
        self._click_enabled_element(self.SHOPPING_BUTTON_XPATH)
        self._click_enabled_element(self.SHOPPING_METHOD_BUTTON_XPATH)
        self._click_enabled_element(self.TERM_AND_CONDITIONS_BUTTON_XPATH)
        self._click_enabled_element(self.PAYMENT_BUTTON_XPATH)
        self._click_enabled_element(self.CONFIRM_ORDER_XPATH)