# Price List Pricing Rules Engine




Apply pricing rules to plans via price lists, supporting things like

- Multi-currency support
- Percentage discounts / increased
- Fixed amount increase / decrease
- Discount code(s)
- etc


## How to run

```
python3 pricing.py
```

Living design document: (an outdated version is pasted below)
https://quilljs.karmacomputing.co.uk/

Subscribie Multi-currency


Situation: As a shop owner, during sign-up, my shop is set to the default currency of my country
https://github.com/Subscribie/subscribie/issues/903



Chronologically, it's easier to code the onboarding process first, so that we may guess the default currency that a shop owner may was to sell in,

based on the country their IP address comes from.



e.g. A shop ower who signs up from the US, will likley want to sell in USD, compared to a shop owner in the UK, who will likley want to sell in GBP



It's important to test from begining to end because because it's the begining when we detect the country of the shop, which decides it's default currency automatically during sign up.



The order of events is:



User visits Subscibie.co.uk (when running locally, this is Subscribie with the builder module activated and builder theme)
Subscribie stores the country code of the public ip address the request comes from (using geo location ip lookup)
Note: When developing locally, the geo-location-ip is set to "GB" by default because geo location ip lookup is only for public IP addresses
When the user submits the "build my shop form", module builder sends the detected country and new shop details to Subscribie-deployer
Note: Subscribie-deployer only recieves (if successful) the detected country code, not the currency, there is a simple mapping which translates the detected country to it's default currency
Note: If geo location IP fails, the fallback is to se the default country to "GB" there is an open issue
Subscribie-deployer sets the shops default currency, based on the users IP address country or to "GB" as default
The plan is created with no price_list attached (meaning that the base_price of both `interval_amount` and `sell_price` are both unaffected)
Finally, assuming the subscribie-deployer created a new shop successfully, the new shop owner is directed to their new shop


To run the onboarding process locally you need to run locally:

Subscribie with the builder module activated and builder theme) activated
Subscribie deployer
Build a new shop by visitng 127.0.0.1:5000
Stop Subscibie which is running the builder theme and builder module, because it is using port 5000
Start the new shop from the subscribie-deploy
You'll see deployer creates a .env and a data.db for the new shop, see . env.exmple for subscribie-deployer 
The built Subscribie shop starts in GBP because locally geo location ip only works on public ip addresses (you could use a breakpoint() to override it


Once a setup it takes only few seconds to test /generate new shops locally 



Questions

Does the shop owner want to show publically the plan prices in al currencies, or only show the price for the detected currency
If hiding other currency options, does the shop owner want to give the subscriber option to 'change currency' during sign-up?
How does this conflict with abuse, e.g. geographically sensitive pricing, but changing ip to force a lower price (effort vs reward)
Does the shop owner want to decide, per-plan which plan is and is not available in which currency?
Or: As a shop owner, when I 'activate' USD pricing, then I expect all my existing plans to also be available in USD (there are a lot of assumptions being made here by the shop owner- e.g currency conversion (yes or no?), (all pestel).


## peudo code pricing query:



# Get (active) price list(s?) for a given plan and currency

Enforcing:
- One pricelist per plan? 
- Or one pricelist per currency, for each plan?
- Consider: A pricelist being 'active/inactive/applicable' (e.g seasonal: Christmas)
- Note: Price list *rules* help pricelists be more flexible. e.g. rule:
  - Rule one: For USD currency, increase prices by 20%
  - Rule two: During December in the UK (Christmas) 


SELECT pricelist_id
FROM plans
JOIN ?plan_to_currency? ON
plan.id == plan_to_currency.plan_id
WHERE plan_to_currency = "USD"
AND plan.id = 1

If no pricelist_id is found, what to do? 
Possiblity: Use a/enforce a default 'price_list', which operates on a base price?
Possibility: Accept there is no pricelist , and therefore use the shop's default currency
Possiblity: Infer that this plan is *not* available in USD, and delegate to application to inform the user


Map plans to their price list:

Note: There is flexibility to put start_date/end_date on the price_list , and/or individual price_list_rule(s). 
e.g. A a black friday price_list_rule which is added to an existing price_list->rules where the price_list_rule
expires after a day, but the price_list does not, so that a shop owner can quickly respond to events which to 
alter price, without having to define an entire new pricelist.

Purpose: Stores a price list for each currency (note this is per currency, not per plan)
e.g. As a shop owner, I can create a USD price list which increases all prices by 10% of the base price
```
--------------------------------------------
| Table name: PriceList   | e.g. Value
| name        | VARCHAR   | Christmas
| start_date  | timestamp |
| expire_date | timestamp |
| currency    | VARCHAR   | USD
---------------------------------------------
 ```

Purpose: Map plans to their prices for a given currency
e.g. A plan by default is only available in the shops default currency (we don't assume a shop owner wants to sell in all currencies automatically)
e.g. As a shop owner, I can sell some of by plans in GBP and USD, and some of my plans in GBP only. 
```
--------------------------------------------
|Table name: Plan_To_Currency_To_Price_List | e.g value
|plan_id      | INT           |  7
|currency     | VARCHAR       |  USD
|pricelist_id | INT           |  2
-------------------------------------
| Compound unique:
| Unique: (plan_id, currency, pricelist_id)

```
Enforced constraints for "Plan_To_Currency":

- Each plan can have an active price list per currency, but (never?) more than one active price list
  colours colors
```
|Table name: Price_List_Rule
| name                    | varchar
| active                  | BOOL
| position                | int
| affects_sell_price      | BOOL
| affects_interval_amount | BOOL
| start_date              | timestamp
| expire_date             | timestamp
| min_quantity            | int
| percent_discount        | int
| percent_increase        | int
| amount_discount         | int
| amount_increase         | int
| min_sell_price          | int
| min_interval_amount     | int

```

Situation: After sign up*, as a shop owner logged into my dashboard
*Note chronologically, it's easier to code the onboarding process first, so that we may guess the default currency that a shop owner may was to sell in, based on the country their IP address comes from. e.g. A shop ower who signs up from the US, will likley want to sell in USD, compared to a shop owner in the UK, who will likley want to sell in GBP.



Epic: As a shop owner I can set prices in multiple currencies for my plans



For example: As a shop owner I can:



Manually sell my coaching service 
In the UK for 20GBP monthly with an up-front cost of 5GBP
In the US for 25USD monthly with an up-front cost of 5USD

Note that:

I care about being about charging more for USD (a coaching service may cost more time/effort to deliver in a different country)
I may want to charge less, e.g. In India the currency is very weak to the dollar, and may want to charge significantly less in that region
Without having to duplicate plan details/description




Research notes to organise


e.g. Hiding multi currency by default may makes sense if most shop owners don't use multi currency (because then the UI is less confusing)



How hiding too much can go wrong: Here is a user example not able to find the currency option



https://www.odoo.com/forum/help-1/cannot-set-currency-in-pricelist-configuration-32106



More UX to avoid:



https://www.odoo.com/forum/help-1/best-practise-with-multi-currency-price-lists-40226



https://www.odoo.com/documentation/15.0/applications/sales/sales/products_prices/prices/currencies.html


