"""
Test for ordering products
"""
import random
import re
import unittest

from selenium import webdriver, common
from selenium.common.exceptions import TimeoutException

from pages import HomePage, DetailsPage, ShoppingCartPage


class TestOrderProduct(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.get("PATH_TO_APP")
        cls.home_page = HomePage(cls.driver)
        cls.details_page = DetailsPage(cls.driver)
        cls.shopping_page = ShoppingCartPage(cls.driver)

    def setUp(self):
        try:
            self._check_if_cart_is_empty()
        except TimeoutException:
            self.home_page._click_cart_button()
            self.home_page._clean_cart()

    def test_add_product_from_home_page(self):
        """
        1. Add product to cart from home page.
        2. Check if quantity == 1.
        3. Check if value is the same as in description.
        4. Clean cart.
        5. Do for each product.
        """
        amount_of_added_products = '1'
        for prod_id, _ in self.home_page.PRODUCT_IDS_XPATHS.items():
            self.home_page._add_single_product_to_cart(prod_id)
            self.assertEqual(amount_of_added_products, self.home_page._get_cart_items_quantity())
            prod_price = self.home_page._get_product_value(prod_id)
            self.assertEqual(prod_price, self.home_page._get_cart_items_value())
            self.home_page._clean_cart()

    def test_add_product_from_product_details_page(self):
        """
        1. Add product to cart from details page.
        2. Check if quantity is equal to default.
        3. Check if value is the same as in description.
        4. Clean cart.
        5. Do for each product.
        """
        for prod_id, _ in self.home_page.PRODUCT_IDS_XPATHS.items():
            prod_price = self.home_page._convert_price_to_float(self.home_page._get_product_value(prod_id))
            self.home_page._click_enabled_element(self.home_page.PRODUCT_DETAILS_XPATHS[prod_id])
            default_value = self.details_page._get_default_quantity()
            self.details_page._click_enabled_element(self.details_page.ADD_TO_CART_XPATH)
            prod_price_sum = int(default_value) * prod_price
            self.assertEqual(default_value, self.details_page._get_cart_items_quantity())
            self.assertEqual(prod_price_sum, self.details_page._convert_price_to_float(self.details_page.
                                                                                       _get_cart_items_value()))
            self.details_page._clean_cart()
            self.details_page._go_to_home_page()

    def test_quantity_and_value_addition_in_cart(self):
        """
        1. Add each product to cart from home page.
        2. Sum all quantities of added products.
        3. Sum all values of added products.
        4. Check if quantity in cart is the same as sum from point 2.
        5. Check if value in cart is the same as sum from point 3.
        6. Clean cart.
        """
        value_sum = 0.0
        amount_of_added_products = str(len(self.home_page.PRODUCT_IDS_XPATHS))
        for prod_id, _ in self.home_page.PRODUCT_IDS_XPATHS.items():
            self.home_page._add_single_product_to_cart(prod_id)
            prod_price = self.home_page._convert_price_to_float(self.home_page._get_product_value(prod_id))
            value_sum += prod_price
        self.assertEqual(amount_of_added_products, self.home_page._get_cart_items_quantity())
        self.assertEqual(value_sum, self.home_page._convert_price_to_float(self.home_page._get_cart_items_value()))

    def test_cart_value_between_pages(self):
        """
        1. Add randomly selected product to cart from home page.
        2. Go to product details page.
        3. Check if value is the same.
        4. Go to shopping cart page.
        5. Check if value is the same on button.
        6. Check if value is the same on total.
        """
        amount_of_added_products = '1'
        id_of_selected_product = self._select_random_item()
        prod_price = self.home_page._get_product_value(id_of_selected_product)

        self.home_page._add_single_product_to_cart(id_of_selected_product)
        self._compare_given_quantity_and_value_with_current_cart(amount_of_added_products, prod_price)

        self.home_page._go_to_product_details_page(id_of_selected_product)
        self._compare_given_quantity_and_value_with_current_cart(amount_of_added_products, prod_price)

        self.details_page._go_to_shopping_cart_page()
        self._compare_given_quantity_and_value_with_current_cart(amount_of_added_products, prod_price)
        self.assertEqual(prod_price, self.shopping_page._get_sub_total_value())

    def test_estimate_shipping_and_taxes(self):
        """
        1. Add random product from details page.
        2. Go to shopping cart page.
        3. Fill "Estimate Shipping & Taxes" formulae.
        4. Get value of selected shipping method.
        5. Check if it is added properly to the total value.
        """
        id_of_selected_product = self._select_random_item()
        self.home_page._click_enabled_element(self.home_page.PRODUCT_DETAILS_XPATHS[id_of_selected_product])
        self.details_page._click_enabled_element(self.details_page.ADD_TO_CART_XPATH)
        self.details_page._go_to_shopping_cart_page()
        self.shopping_page._click_enabled_element(self.shopping_page.ESTIMATE_SHOPPING_AND_TAXES_XPATH)
        from time import sleep
        sleep(1)
        self.shopping_page._select_region_from_taxes_form()
        self.shopping_page._click_enabled_element(self.shopping_page.GET_QUOTES_BUTTON_XPATH)

        self.shopping_page._click_enabled_element(self.shopping_page.FLAT_RATE_XPATH)
        taxes_popup = self.shopping_page._convert_price_to_float(self.shopping_page._get_taxes())
        self.shopping_page._click_enabled_element(self.shopping_page.APPLY_SHOPPING_BUTTON_XPATH)
        taxes_summary = self.shopping_page._get_text_from_enabled_element(self.shopping_page.FLAT_SHIPPING_RATE_VALUE)
        taxes_summary = re.search("(?<=\$)(.*)", taxes_summary).group()
        taxes_summary = self.shopping_page._convert_price_to_float(taxes_summary)
        self.assertEqual(taxes_popup, taxes_summary)

        total_summary = self.shopping_page._get_text_from_enabled_element(self.shopping_page.TOTAL_VALUE)
        total_summary = re.search("(?<=\$)(.*)", total_summary).group()
        total_summary = self.shopping_page._convert_price_to_float(total_summary)
        self.assertEqual(self.shopping_page._calculated_sub_total_price_with_flat_shipping_rate(), total_summary)

        self.assertEqual(self.shopping_page._calculated_sub_total_price_with_flat_shipping_rate(),
                         self.shopping_page._convert_price_to_float(self.shopping_page._get_cart_items_value()))

    def test_buying_process(self):
        """
        1. Add random product from details page.
        2. Go to shopping cart.
        3. Click Checkout.
        4. Fill all forms.
        5. Check if "Your order has been placed!" appeared.
        :return:
        """
        expected_buy_message = 'Your order has been placed!'
        expected_success_message = 'Success'

        self.shopping_page._register_user()
        id_of_selected_product = self._select_random_item()
        self.home_page._click_enabled_element(self.home_page.PRODUCT_DETAILS_XPATHS[id_of_selected_product])
        self.details_page._click_enabled_element(self.details_page.ADD_TO_CART_XPATH)
        self.details_page._go_to_shopping_cart_page()
        self.shopping_page._click_enabled_element(self.shopping_page.CHECKOUT_BUTTON_XPATH)
        self.shopping_page._fill_checkout_form()
        success_subpage = self.shopping_page._get_text_from_enabled_element(self.shopping_page.SUCCESS_CHECKOUT_XPATH)
        self.assertEqual(expected_success_message, success_subpage)
        self.assertEqual(expected_buy_message, self.shopping_page._get_text_from_enabled_element(self.shopping_page.
                                                                                                 BUY_MESSAGE_XPATH))
        self.shopping_page._click_enabled_element(self.shopping_page.FINISH_ORDER_BUTTON_XPATH)

    def test_select_quantity_from_checkout_page(self):
        """
        1. Add random product from details page.
        2. Go to shopping cart page.
        3. Change quantity of selected product.
        4. Sum quantities and values of all products.
        5. Compare it to values in cart button.
        """
        id_of_selected_product = self._select_random_item()
        prod_price = self.home_page._convert_price_to_float(self.home_page._get_product_value(id_of_selected_product))
        self.home_page._click_enabled_element(self.home_page.PRODUCT_DETAILS_XPATHS[id_of_selected_product])
        current_value = int(self.details_page._get_default_quantity())
        self.details_page._click_enabled_element(self.details_page.ADD_TO_CART_XPATH)

        self.details_page._go_to_shopping_cart_page()
        new_value = current_value + 1
        self.shopping_page._fill_qty_field_with_given_amount(new_value)
        self.shopping_page._click_enabled_element(self.shopping_page.UPDATE_BUTTON_XPATH)
        self.assertEqual(prod_price * new_value, self.shopping_page._convert_price_to_float(self.shopping_page
                                                                                            ._get_cart_items_value()))

    def test_validate_quantity_restrictions(self):
        """
        1. Go to product details page.
        2. Check for restrictions.
        3. Get QTY value from string.
        4. Select QTY-1 amount.
        5. Go to checkout page.
        6. Click checkout button.
        7. Check if "Minimum order amount for Test product 1 is 2!" appears.
        8. Change quantity to Qty.
        9. Click checkout .
        10. Fill buying form.
        :return:
        """
        expected_positive_msg = "Success: You have modified your shopping cart!"
        expected_negative_msg = "Minimum order amount for Test product 1 is 2!"

        for prod_id, _ in self.home_page.PRODUCT_IDS_XPATHS.items():
            self.home_page._click_enabled_element(self.home_page.PRODUCT_DETAILS_XPATHS[prod_id])
            try:
                self.driver.find_element_by_css_selector(self.details_page.ALERT_INFO_CSS).is_displayed()
            except common.exceptions.NoSuchElementException:
                pass
            else:
                validation_msg = self.driver.find_element_by_css_selector(self.details_page.ALERT_INFO_CSS).text
                keywords = re.search("(?<=This product has a )(.*) quantity of ([0-9]*)", validation_msg)
                if keywords.group(1) == "minimum":
                    self.details_page._fill_qty_field_with_given_amount(keywords.group(2))
                    self.details_page._click_enabled_element(self.details_page.ADD_TO_CART_XPATH)
                    self.details_page._go_to_shopping_cart_page()
                    self.shopping_page._click_enabled_element(self.shopping_page.UPDATE_BUTTON_XPATH)
                    self.assertEqual(expected_positive_msg, self.shopping_page._get_first_alert_message())
                    self.shopping_page._click_enabled_element(self.shopping_page.CLOSE_MESSAGE_XPATH)
                    too_low_value = int(keywords.group(2)) - 1
                    self.shopping_page._fill_qty_field_with_given_amount(too_low_value)
                    self.shopping_page._click_enabled_element(self.shopping_page.UPDATE_BUTTON_XPATH)
                    self.assertEqual(expected_positive_msg, self.shopping_page._get_first_alert_message())
                    self.assertEqual(expected_negative_msg, self.shopping_page._get_second_alert_message())
            self.shopping_page._go_to_home_page()

    def test_remove_product_with_setting_quantity_to_zero(self):
        """
        1. Add random product from details page.
        2. Go to shopping cart page.
        3. Change quantity of selected product to 0.
        4. Check if "Your shopping cart is empty!" appeared.
        """
        expected_message = 'Your shopping cart is empty!'
        id_of_selected_product = self._select_random_item()
        self.home_page._add_single_product_to_cart(id_of_selected_product)
        self.details_page._go_to_shopping_cart_page()

        self.shopping_page._fill_qty_field_with_given_amount(0)
        self.shopping_page._click_enabled_element(self.shopping_page.UPDATE_BUTTON_XPATH)
        self.assertEqual(expected_message, self.shopping_page._get_text_from_enabled_element(self.shopping_page.
                                                                                             VALIDATION_MESSAGE_XPATH))

    def tearDown(self):
        cur_url = self.driver.current_url
        if cur_url != "https://rekrutacjaqa2.xsolve.software/" and \
           cur_url != "https://rekrutacjaqa2.xsolve.software/index.php?route=common/home":
            self.details_page._go_to_home_page()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def _check_if_cart_is_empty(self):
        self.home_page._click_cart_button()
        message = self.home_page._get_text_from_enabled_element(self.home_page.MESSAGE_CART_XPATH)
        self.assertEqual('Your shopping cart is empty!', message)
        self.assertEqual('0', self.home_page._get_cart_items_quantity())
        self.assertEqual('0.00', self.home_page._get_cart_items_value())
        self.home_page._click_cart_button()

    def _compare_given_quantity_and_value_with_current_cart(self, qty, value):
        """
        :param qty: type: str
        :param value: type: str
        """
        self.assertEqual(qty, self.home_page._get_cart_items_quantity())
        self.assertEqual(value, self.home_page._get_cart_items_value())

    def _select_random_item(self):
        return random.choice(list(self.home_page.PRODUCT_IDS_XPATHS))
