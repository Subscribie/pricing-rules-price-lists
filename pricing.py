from dataclasses import dataclass

USD = "USD"
GBP = "GBP"


def get_discount_code():
    """Get discount code from the current session
    :return: The discount code, or None
    :rtype: str
    """
    return "xmas"


@dataclass
class Plan:
    name: str
    sell_price: int
    interval_price: int
    price_lists: list

    def getPrice(self, currency="GBP"):
        """Mock tables to work out which price list a plan is using for
        a given currency"""

        # Find price_lists for plan
        print(f"Get correct price_list for currency {currency}")
        # if no price_list assigned, fallback to base prices
        if len(self.price_lists) == 0:
            print(
                f"Returning base prices sell: {self.sell_price}. interval: {self.interval_price}"  # noqa: E501
            )
            return self.sell_price, self.interval_price
        for price_list in self.price_lists:
            print(f"only use price list if currency {currency}")

            if price_list.currency == currency:
                print(f"Correct priceList is: {price_list}")
                foundRules = []
                for rule in price_list.rules:
                    print(f"{rule}")
                    foundRules.append(rule)

                # Pass callable get_discount_code to support external context (e.g. session data) # noqa: E501
                context = {"get_discount_code": get_discount_code}
                sell_price, interval_price = applyRules(
                    self, rules=foundRules, context=context
                )

        print(f"getPrice: sell price: {sell_price}")
        print(f"getPrice: interval p: {interval_price}")
        return sell_price, interval_price


@dataclass
class Rule:
    name: str
    affects_sell_price: bool = False
    affects_interval_price: bool = False
    percent_increase: int = 0
    percent_discount: int = 0
    requires_discount_code: bool = False
    discount_code: str = None
    amount_decrease: int = 0


@dataclass
class PriceList:
    name: str
    currency: str
    rules: list = None


price_list1 = PriceList(**{"name": "USD default pricelist", "currency": USD})
price_list2 = PriceList(**{"name": "GBP default pricelist", "currency": GBP})


rule1 = Rule(
    **{
        "name": "10% increase price",
        "affects_sell_price": True,
        "affects_interval_price": True,
        "percent_increase": 10,
    }
)


rule2 = Rule(
    **{
        "name": "10% discount",
        "affects_sell_price": True,
        "affects_interval_price": True,
        "percent_discount": 10,
    }
)


rule3 = Rule(
    **{
        "name": "100% discount",
        "requires_discount_code": True,
        "affects_sell_price": True,
        "affects_interval_price": True,
        "percent_discount": 100,
        "discount_code": "xmas",
    }
)

rule4 = Rule(
    **{
        "name": "Two pence off",
        "requires_discount_code": False,
        "affects_sell_price": True,
        "affects_interval_price": True,
        "amount_decrease": 2,
    }
)


# Price lists have an array of rules attached
price_list1.rules = [rule1, rule4]
price_list2.rules = [rule3]


plan1 = Plan(
    **{
        "name": "Hair Gel",
        "sell_price": 500,
        "interval_price": 10,
        "price_lists": None,
    }
)


plan2 = Plan(
    **{
        "name": "Soap",
        "sell_price": 1500,
        "interval_price": 10,
        "price_lists": [],
    }
)


plan3 = Plan(
    **{
        "name": "Tea",
        "sell_price": 0,
        "interval_price": 2000,
        "price_lists": [],
    }
)


plan1.price_lists = [price_list1, price_list2]
plan2.price_lists = [price_list1, price_list2]


def applyRules(plan, rules=[], context={}):
    """Apply pricelist rules to a given plan

    :param plan: The Plan object
    :param rules: List of rules to apply to the plan price
    :param context: Dictionary storing session context, for example get_discount_code callable for validating discount codes # noqa: E501
    """
    print(f"the plan is: {plan}")

    sell_price = plan.sell_price
    interval_price = plan.interval_price

    print(f"before apply_rules sell price is: {plan.sell_price}")
    print(f"before apply_rules inverval_price is: {plan.interval_price}")

    def apply_percent_increase(base: int, percent_increase: int) -> int:
        add = int((base / 100) * percent_increase)
        base += add
        return base

    def apply_percent_discount(base: int, percent_discount: int) -> int:
        minus = int((base / 100) * percent_discount)
        base -= minus
        return base

    def apply_amount_decrease(base: int, amount_decrease: int) -> int:
        base -= amount_decrease
        return base

    def check_discount_code_valid(expected_discount_code=None, f=None) -> bool:
        """
        Check discount code is valid

        :param expected_discount_code: str, the expected discount code from a given rule # noqa: E501
        :param f: Callable, which must return a string of the discount code
        :return: bool success (True) or fail (False) check against rule's discount code # noqa: E501
        """
        if f is None:
            return False
        else:
            # Call the get_discount_code callable
            return expected_discount_code == f()

    def calculatePrice(
        sell_price: int, interval_price: int, rules, context={}
    ):  # noqa: E501
        """Apply all Return tuple of sell_price, interval_price

        :param sell_price: The base sell_price of the plan
        :type sell_price: int
        :param interval_price: The base interval_price
        :type interval_price: int
        :param rules: List of rules to apply to the plan
        :type rules: list
        :param context: Context for passing callables which may access session data, like get_discount_code # noqa: E501
        :type context: dict, optional
        :return Tuple of sell_price, interval_price after price rules have been applied, if any
        :rtype tuple
        """
        for rule in rules:
            print(f"applying rule {rule}")

            if rule.requires_discount_code:
                expected_discount_code = rule.discount_code
                f = context["get_discount_code"]
                if (
                    check_discount_code_valid(
                        expected_discount_code=expected_discount_code, f=f
                    )
                    is False
                ):
                    # Skip this rule if discount_code validation fails
                    continue

            if rule.affects_sell_price:

                sell_price = apply_percent_increase(
                    sell_price, rule.percent_increase
                )  # noqa: E501
                sell_price = apply_percent_discount(
                    sell_price, rule.percent_discount
                )  # noqa: E501

                sell_price = apply_amount_decrease(
                    sell_price, rule.amount_decrease
                )  # noqa: E501

            if rule.affects_interval_price:

                if rule.percent_increase:
                    interval_price = apply_percent_increase(
                        plan.interval_price, rule.percent_increase
                    )  # noqa: E501

                if rule.percent_discount:
                    interval_price = apply_percent_discount(
                        interval_price, rule.percent_discount
                    )  # noqa: E501

                interval_price = apply_amount_decrease(
                    interval_price, rule.amount_decrease
                )  # noqa: E501

            print(f"after apply_rules sell price is: {sell_price}")
            print(f"after apply_rules interval_price is: {interval_price}")

        return sell_price, interval_price

    sell_price, interval_price = calculatePrice(
        sell_price, interval_price, rules, context=context
    )  # noqa: E501

    return sell_price, interval_price


# First validate that GBP pricelist, 100% discount
sell_price, interval_price = plan1.getPrice("GBP")

assert sell_price == 0
assert interval_price == 0

# USD 10% increase, with amount_decrease 2 cents
sell_price, interval_price = plan1.getPrice("USD")

assert sell_price == 548
assert interval_price == 9

sell_price, interval_price = plan3.getPrice("GBP")
