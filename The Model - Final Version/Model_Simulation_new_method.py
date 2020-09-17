# We import the DREAM agent
import numpy
import matplotlib.pyplot as plt
from Data import *
from Settings import *
from dream_agent import *
from math import *
from decimal import Decimal as dec

# We allocate an agent object

Model = Agent()

class Loan(Agent):
    def __init__(self, parent = None, principal = None, interest = None, annuity = None, owner = None):
        super().__init__(parent)
        self._principal = principal
        self._interest = interest
        self._annuity = annuity
        self._annuity_after_tax = self._annuity - (self._principal * self._interest/Settings.periods_in_year) * Settings.interest_tax
        self._duration = Settings.loan_length * Settings.periods_in_year
        self._time_left = Settings.loan_length * Settings.periods_in_year
        self._periods = Settings.periods_in_year
        self._owner = owner
        self._start_principal = self._principal


    def __repr__(self):
        return "Loan(ID: {a}, principal: {b}, interest: {c}, annuity: {d} duration: {e}, time left: {f}, owner: {g})".format(
            a = self.get_id(), b = round(self._principal), c = round(self._interest, 4), d = round(self._annuity), e = self._duration, f = self._time_left, g = self._owner.get_id())

    @property
    def principal(self):
        return self._principal

    @property
    def interest(self):
        return self._interest

    @property
    def annuity(self):
        return self._annuity

    @property
    def annuity_after_tax(self):
        return self._annuity_after_tax

    @property
    def duration(self):
        return self._duration

    @property
    def time_left(self):
        return self._time_left

    @property
    def owner(self):
        return self._owner

    def interest_payment(self):
        int_payment = self._interest/Settings.periods_in_year * self._principal
        return int_payment

    def annuity_tax(self):
        after_tax = self._annuity - (self._principal * self._interest/Settings.periods_in_year) * Settings.interest_tax
        return after_tax

    def pay_annuity(self):
        self._principal += -self._annuity + self.interest_payment()
        self._time_left += -1
        if self._time_left == 0:
            self.remove_this_agent()

    def annuity_after_n_years(self, n):
        annuity_after = self._annuity - self._annuity * dict_annuity[n] * Settings.interest_tax

        return annuity_after

    def event_proc(self, id_event):
        if id_event == Event.period_start:
            self._annuity_after_tax = self.annuity_tax()

        if id_event == Event.update:
            self.pay_annuity()


        if id_event == Event.stop:
            if random.uniform(0, 1) < Settings.ratio_print:
                print(repr(self))


class Rent_unit(Agent):
    def __init__(self, parent = None, quality = Settings.rent_quality, annuity = Settings.rent_annuity):
        super().__init__(parent)
        self._parent = parent
        self._quality = quality
        self._annuity = annuity

    @property
    def quality(self):
        return self._quality

    @property
    def annuity(self):
        return self._annuity

class Houses(Agent):
    def __init__(self, parent = None, quality = 0, owner = None, price = 0, for_sale = True, seller = None):
        super().__init__(parent)
        self._parent = parent
        self._quality = quality
        self._owner = owner
        self._price = price
        self._for_sale = for_sale
        self._seller = seller
        self._exp_price = 0
        self._periods_for_sale = 0

    def __repr__(self):
        return "House(ID: {a}, quality: {b}, price: {c}, owner: {d}, for sale: {e}, seller:{f}, periods for sale: {g})".format(
            a = self.get_id(), b = round(self._quality, 4), c = round(self._price), d = self.owner.get_id() if self.owner != None else None,
            e = self._for_sale, f = self.seller.get_id() if self.seller != None else None, g = self._periods_for_sale)

    @property
    def quality(self):
        return self._quality

    @property
    def for_sale(self):
        return self._for_sale

    @property
    def owner(self):
        return self._owner

    @property
    def price(self):
        return self._price

    @property
    def exp_price(self):
        return self._exp_price

    @property
    def seller(self):
        return self._seller

    @property
    def periods_for_sale(self):
        return self._periods_for_sale

    def setting_owner(self, owner):
        self._owner = owner

    def setting_seller(self, seller):
        self._seller = seller

    def setting_for_sale(self, seller):
        if self._for_sale == False:
            self._for_sale = True
            self._seller = seller
            self._periods_for_sale = 0
            if len(Statistics.sorted_house_q) > 1:
                self._price = Settings.price_premium * local_mean_get_value(self.quality, Statistics.sorted_house_q, Statistics.sorted_house_p)
            Simulation.houses_for_sale.append(self)
        else:
            pass

    def price_change(self, change_pct):
        self._price = self._price * (1 + change_pct)
        if self._price <0:
            self._price = 0

    def increase_periods_for_sale(self):
        self._periods_for_sale += 1

    def unlisting_house(self):
        self._periods_for_sale = 0
        self._for_sale = False
        Simulation.houses_for_sale.remove(self)

    def set_price(self, price):
        self._price = price
        #print("House {} price set to {}". format(self.get_id(), self._price))


    def event_proc(self, id_event):
        if id_event == Event.start:
            self._quality = float(numpy.random.beta(2, 3))
            self._price = 10000
            self._exp_price =self._price

        if id_event == Event.period_start:

            if self._for_sale == True:
                self.increase_periods_for_sale()

            if self._for_sale == True and self._owner == None and self._seller == None and self._periods_for_sale % Settings.price_adjustment_frequency == 0:
                self.price_change(-0.05)

        if id_event == Event.update:
            pass

        if id_event == Event.period_end:
                #update expected house price
                if Simulation.time % Settings.periods_between_price_assessment == 0:
                    if len(Statistics.sorted_house_q) > 1:
                        self._exp_price = local_mean_get_value(self.quality, Statistics.sorted_house_q, Statistics.sorted_house_p)
                    else:
                        self._exp_price = self._price

        if id_event == Event.stop:
            if random.uniform(0, 1) < Settings.ratio_print:
                print(repr(self))

class Bank(Agent):
    def __init__(self, parent = None, interest = Settings.interest):
        super().__init__(parent)
        self._interest = interest

        # Children of bank:
        Bank.Loans = Agent(self)

    @property
    def interest(self):
        return self._interest
    # Method that tells a household the price cap for house purchase given income and equity
    def max_budget_household(self, lender):
        piti = lender.income * Settings.piti_multiplier
        interest = Settings.interest
        max_loan_piti = (piti*(1-(1 + interest/Settings.periods_in_year)**(-(Settings.loan_length*Settings.periods_in_year))))/(interest/Settings.periods_in_year)
        max_loan_income = Settings.periods_in_year * Settings.income_loan_multiplier * lender.income
        max_loan = min(max_loan_piti, max_loan_income)
        if lender.equity !=None:
            max_budget = max_loan + lender.equity*0.8
        else:
            max_budget = max_loan
        return max_budget

    def get_annuity(self, principal):
        interest = Settings.interest
        annuity = ( principal * (interest/Settings.periods_in_year) ) / ((1 - (1 + (interest / Settings.periods_in_year)) ** ( - (Settings.loan_length*Settings.periods_in_year) )))
        return annuity

    def get_loan(self, house_price, owner):
        if owner.equity != None:
            principal = house_price - owner.equity
        else:
            principal = house_price

        annuity = self.get_annuity(principal)
        owner.set_loan(Loan(parent=Bank.Loans, principal=principal, interest=Settings.interest, annuity=annuity, owner=owner))

    def event_proc(self, id_event):
        super().event_proc(id_event)
        if id_event == Event.period_start:
            pass

class Household(Agent):

    def __init__(self, parent=None, wealth = 0, pdeath = 0, age = Settings.starting_age, house_owned = None, dead = False, moving = False, max_budget = 0):
        super().__init__(parent)
        # we declare variables
        self._wealth = wealth
        self._income = Settings.starting_income * (1 + numpy.random.normal(0, 0.1))
        self._age = age
        self._pdeath = pdeath
        self._dead = dead
        self._moving = moving
        self._house_owned = house_owned
        self._renting = True
        self._house_selling = None
        self._max_budget = max_budget
        self._houses_bought = 0
        self._loan = None
        self._equity = None
        self._utility = None
        self._low_income_count = 0
        self._utility_alpha = Settings.utility_alpha
        self._annuity = 0
        self._turns_moving = 0
        self._seen_houses = []
        if self._loan != None:
            self._disposable = pay_income_taxes(self._income) - self._loan.annuity_after_tax
        else:
            self._disposable = pay_income_taxes(self._income)

    def __repr__(self):
        return "Household(ID: {a}, Wealth: {b}, Income: {c}, after_tax: {aa}, disposable income: {cc}, Age: {d}, House ID: {e}, renting:{qq}, House quality: {f}, Annuity: {kk}, house selling: {ff}, utility: {dd}, p-death: {g}, max budget: {h}, loan id:{bb} moving: {i}, houses bought: {j}, alpha: {k} )".format(
            a = self._id, b=round(self._wealth),
            c = round(self._income), d=self._age,
            e = self._house_owned.get_id() if self.house_owned != None else None,
            f = round(self.house_owned.quality, 4) if self._house_owned != None else None,
            g = round(self._pdeath, 4), h=round(self._max_budget), i=self._moving, j=self._houses_bought,
            aa = round(pay_income_taxes(self._income)),
            k = round(self._utility_alpha, 3),
            bb = self._loan.get_id() if self._loan != None else None,
            cc = round(self._disposable),
            dd = round(self.household_utility(self.house_owned),1),
            kk = self._loan.annuity_after_tax if self._loan != None else 0,
            ff = self._house_selling.get_id() if self._house_selling != None else None,
            qq = self._renting)

    def get_houses_bought(self):
        return self._houses_bought

    # Report wealth
    @property
    def wealth(self):
        return self._wealth

    @property
    def annuity(self):
        return self._annuity

    @property
    def turns_moving(self):
        return self._turns_moving

    @property
    def low_income_count(self):
        return self._low_income_count

    # Report id of owned house
    @property
    def house_owned(self):
        return self._house_owned

    @property
    def house_selling(self):
        return self._house_selling

    @property
    def renting(self):
        return self._renting

    # Report Income
    @property
    def income(self):
        return self._income

    @property
    def equity(self):
        return self._equity

    # Report Age
    @property
    def age(self):
        return self._age

    #report if dead
    @property
    def dead(self):
        return self._dead

    @property
    def loan(self):
        return self._loan

    @property
    def utility_alpha(self):
        return self._utility_alpha

    def search_interval(self, funds, range):
        test_value = 0.5
        inc = 0.05
        income = pay_income_taxes(self.income)
        # making benchmark utility levels
        house_price_1 = local_mean_get_value(test_value, Statistics.sorted_house_q, Statistics.sorted_house_p)
        house_price_2 = local_mean_get_value(test_value + inc, Statistics.sorted_house_q, Statistics.sorted_house_p)
        house_price_3 = local_mean_get_value(test_value - inc, Statistics.sorted_house_q, Statistics.sorted_house_p)
        utility_1 = math.log10(income - Simulation.bank.get_annuity(house_price_1 - self.equity if self.equity != None else house_price_1)) * a + math.log10(test_value) * (1 - a)
        utility_2 = math.log10(income - Simulation.bank.get_annuity(house_price_2 - self.equity if self.equity != None else house_price_2)) * a + math.log10(test_value + inc) * (1 - a)
        utility_3 = math.log10(income - Simulation.bank.get_annuity(house_price_3 - self.equity if self.equity != None else house_price_3)) * a + math.log10(test_value - inc) * (1 - a)
        if utility_1 >= utility_2 and utility_1 >= utility_3:
            test_value = 0.5
            q_max = test_value + range / 2
            q_min = test_value - range / 2
        if utility_2 >= utility_1 and utility_2 >= utility_3:
            test_value = 0.5 + inc
        if utility_3 >= utility_1 and utility_3 >= utility_2:
            test_value = 0.5 - inc

        p_max = local_mean_get_value(q_max, Statistics.sorted_house_q, Statistics.sorted_house_p)
        p_min = local_mean_get_value(q_min, Statistics.sorted_house_q, Statistics.sorted_house_p)
        return q_max, q_min


    def household_dies(self):
        Simulation.dead_this_period += 1
        self._dead = True
        # remove loan
        if self.loan != None:
            self.loan.remove_this_agent()
        # set house for sale
        if self.house_owned != None:
            self.house_owned.setting_for_sale(self)

    # We define hte household utility used for evaluating houses and for evaluating current house utility
    def household_utility(self, house):
        if house == Simulation.rent_unit:
            annuity = float(house.annuity)

        if house != self.house_owned and house !=Simulation.rent_unit:
            annuity = Simulation.bank.get_annuity(house.price - self.equity if self.equity != None else house.price)

        if house == self.house_owned:
            if self.loan != None:
                annuity = self.loan.annuity_after_tax
            else:
                annuity = 0

        spending = pay_income_taxes(self.income) - annuity
        if spending < 0:
            spending = 0.01

        if house != None:
            quality = house.quality
        else:
            quality = Settings.rent_quality
        a = self.utility_alpha
        #remember to change utility in "search interval" if this is changed
        cd_utility = math.log10(spending) * a + math.log10(quality) * (1 - a)
        return cd_utility

    def bankrupt(self):
        if self._house_owned != None:
            self._house_selling = self.house_owned
            self.house_owned.setting_for_sale(self)
        else:
            pass
        self._house_owned = None
        self._loan = None
        self._moving = False
        self._renting = True

    def set_loan(self, loan):
        self._loan = loan

    def communication(self, communicate, house):
        if communicate == Communication.buy_house:

            #buy house from owner (if owner exists)
            self._houses_bought += 1
            if house.seller != None:
                house.seller.communication(Communication.sell_house, house)
            else:
                pass
            #Set you as owner of house
            self._house_owned = house
            house.setting_owner(self)
            #unlist house and add periods for sale to statistics
            Statistics.days_in_market.append(house._periods_for_sale)
            house.unlisting_house()
            #Add house sales price and quality to statistics database

            Statistics.house_quality.append(house.quality)
            Statistics.house_price.append(house.price)
            Statistics.house_q.append(house.quality)
            Statistics.house_p.append(house.price)
            Statistics.sales_this_period += 1


        if communicate == Communication.sell_house:
            #remove yourself as seller
            house.setting_seller(None)
            self._house_selling = None
            #remove self as owner, if still owner
            if self.house_owned == house:
                self._house_owned = None
            else:
                pass

    def event_proc(self, id_event):
        #checking if household is dead
        #initiating behaviour of living household
        if id_event == Event.start:
            pass

        if id_event == Event.period_start:
            #Remove agent if agent is dead and its estate is settled
            if self._dead == True and self.house_owned == None:
                self.remove_this_agent()

            #Move agent into rent unit, if agent has no house
            if self._house_owned == None:
                self._renting = True
            else:
                self._renting = False

            #set equity and disposable income:
            if self._house_owned != None:
                self._utility = self.household_utility(self._house_owned)
                if self.loan != None:
                    self._equity = self.house_owned.exp_price - self.loan.principal
                    self._disposable = pay_income_taxes(self._income) - self._loan.annuity_after_tax
                else:
                    self._equity = self.house_owned.exp_price
                    self._disposable = pay_income_taxes(self._income)

            if self._renting ==True:
                self._disposable = pay_income_taxes(self._income) - Simulation.rent_unit.annuity

            # count how many months in a row disposable income has been under minimum:
            if self._disposable < max(Settings.minimum_disposable, self.income*Settings.minimum_disposable_ratio):
                self._low_income_count += 1
            else:
                self._low_income_count = 0

            #If household has had too low income for too many periods in a row, evict household (Take away house, clear all loans, lose all equity)
            if self._low_income_count > Settings.max_low_income_count:
                self.bankrupt()
                print("household bankrupt: {}, disposable: {}, time: {}, income: {} count: {}".format(self.get_id(), self._disposable, Simulation.time, pay_income_taxes(self._income), self._low_income_count))
                self._low_income_count = 0

        if id_event == Event.update:  # 2
            if self._dead == False:
                #adjust house price, if selling a house
                if self.house_selling != None:
                    if self.house_selling.periods_for_sale % Settings.price_adjustment_frequency == 0:
                        self.house_selling.price_change(Settings.price_adjustment)

            #check if household wants to move, if so, initiate moving procedure. Households wont move if they have not sold old house yet
                if random.uniform(0,1) < dict_move_prop[self.age] and self._moving == False and self._house_selling == None or self._low_income_count > 2 and self._moving == False and self._house_selling == None :
                    self._moving = True
                    self._turns_moving = 0
                    self._seen_houses = []

                    #if already house owner, set own house for sale
                    if self._house_owned != None:
                        self._house_selling = self.house_owned
                        self.house_owned.setting_for_sale(self)
                    else:
                        pass

                if self._moving == True:
                    self._turns_moving += 1
                    best_house = None
                    first = True
                    # Asking the bank how much the largest possible loan the household can get is (Budget constraint)
                    self._max_budget = Simulation.bank.max_budget_household(self)

                    # Agents find up to 4 houses they can afford
                    houses_checked = 0
                    houses_in_survey = []
                    move_rent_unit = False
                    while len(houses_in_survey) < Settings.houses_surveyed and houses_checked < Settings.max_houses_checked:
                        if houses_checked == 40:
                            print("many houses checked. period: {}".format(Simulation.time))
                        if Simulation.houses_for_sale:
                            house_check = random.choice(Simulation.houses_for_sale)
                            houses_checked += 1
                            if house_check.price <= self._max_budget and houses_in_survey.count(house_check) < 1:
                                self._seen_houses.append(self.household_utility(house_check))
                                houses_in_survey.append(house_check)
                        if not Simulation.houses_for_sale:
                            break

                    #Agents find the best house out of the chosen ones
                    houses_in_survey_utility = []
                    for n in houses_in_survey:
                        if n != self.house_owned and self != n.seller:
                            if first == True:
                                best_house = n
                                first = False
                            if self.household_utility(n) > self.household_utility(best_house):
                                best_house = n
                            else:
                                pass
                    if best_house == None:
                        pass

                    #test if found house is better than rent unit
                    if best_house != None:
                        if self.household_utility(Simulation.rent_unit) > self.household_utility(best_house):
                            best_house = Simulation.rent_unit

                    #test if the found best house is good enough to move into:
                    if best_house != None:
                        if test_if_buy(self._seen_houses, test_percentile(self._seen_houses, self.household_utility(best_house))) == True:
                            print(len(self._seen_houses))
                            if best_house == Simulation.rent_unit:
                                #Move to rent unit if it gave the most utility
                                best_house = None
                                move_rent_unit = True
                                self._renting = True
                                self._moving = False
                                print("moved to rent unit after {} periods on the market".format(self._turns_moving))
                            else:
                                print("moved to house after {} periods on the market".format(self._turns_moving))
                                # buy the best house found:
                                # remove former loan
                                if self.loan != None:
                                    self.loan.remove_this_agent()
                                # get loan for house
                                Simulation.bank.get_loan(best_house.price, self)
                                # buy the best house found
                                self.communication(Communication.buy_house, best_house)
                                self._moving = False

                #check if agent dies
                if random.uniform(0, 1) < self._pdeath:
                    self.household_dies()

        if id_event == Event.update_year:
            if self._dead == False:
                # every year, increase age by 1 and update income
                self._age += 1
                self._pdeath = prop_death(self._age)

                if self._age < Settings.retire_age:
                    self._income += dict_income_raise[get_index(self._age)]
                    self._income = self._income * (math.exp(numpy.random.normal(0, 0.113) + numpy.random.normal(0, 0.155)))

                if self._age == Settings.retire_age:
                    self._income = self._income*Settings.pension_share

                # if income is too low and household is young, set income to SU-level
                if self._age > Settings.starting_age and self._income < Settings.su_income:
                    self._income = Settings.su_income

                if self._age >= 30 and self._income < Settings.kh_income:
                    self._income = Settings.kh_income

                #if agent over max age, kill agent
                if self._age > Settings.max_age:
                    self.household_dies()


        elif id_event == Event.stop:
            if random.uniform(0, 1) < Settings.ratio_print:
                if self._dead == False:
                    print(repr(self))

class Statistics(Agent):

    def event_proc(self, id_event):
        if id_event == Event.start:
            # Creating lists for later use
            Statistics.sales_this_period = 0
            Statistics.sales_total = []
            Statistics.income = []
            Statistics.days_in_market = []
            Statistics.agg_days_in_market = []
            Statistics.avg_days_in_market = []
            Statistics.house_quality = []
            Statistics.house_price = []
            Statistics.sorted_house_quality = []
            Statistics.sorted_house_price = []
            Statistics.house_q = []
            Statistics.house_p = []
            Statistics.agg_house_quality = []
            Statistics.agg_house_price = []
            Statistics.agg_sorted_house_quality = []
            Statistics.agg_sorted_house_price = []
            Statistics.period = []

        if id_event == Event.period_start:
            # Every period, make poor-mans local regression of sales the last 6 months house sales
            # we add sales this period to list of all sales:
            Statistics.sales_total.append(Statistics.sales_this_period)
            print(Statistics.sales_total)
            sales_last_interval = sum(Statistics.sales_total[-Settings.periods_regression:-1])+Statistics.sales_total[-1]
            print(sales_last_interval)
            Statistics.sales_this_period = 0
            print(Statistics.house_q[-sales_last_interval-1:-1])

            if sales_last_interval > 1:
                Statistics.sorted_house_q, Statistics.sorted_house_p = local_mean(Statistics.house_q[-sales_last_interval:-1],
                                                                                            Statistics.house_p[-sales_last_interval:-1],
                                                                                            Settings.number_of_batches)
                print(Statistics.sorted_house_q)

            if len(Statistics.days_in_market) > 0:
                avg_days = float(sum(Statistics.days_in_market) / len(Statistics.days_in_market))
            else:
                avg_days = 0
            Statistics.avg_days_in_market.append(avg_days)

            if Simulation.time % Settings.periods_between_price_assessment == 0:


                if len(Statistics.house_quality) > 1:
                    Statistics.sorted_house_quality, Statistics.sorted_house_price = local_mean(Statistics.house_quality, Statistics.house_price, Settings.number_of_batches)

                #Adding sales data to aggregated database
                for i in Statistics.house_quality:
                    Statistics.agg_house_quality.append(i)

                for i in Statistics.house_price:
                    Statistics.agg_house_price.append(i)

                for i in Statistics.sorted_house_quality:
                    Statistics.agg_sorted_house_quality.append(i)

                for i in Statistics.sorted_house_price:
                    Statistics.agg_sorted_house_price.append(i)

                for i in Statistics.days_in_market:
                    Statistics.agg_days_in_market.append(i)

                Statistics.period.append(Simulation.time)



                #reset yearly database
                Statistics.house_quality = []
                Statistics.house_price = []
                Statistics.days_in_market = []

        if id_event == Event.period_end:
            pass


        if id_event == Event.stop:
            household_inc = []
            household_q = []
            for n in Simulation.households:
                household_inc.append(n.income)
                if n.house_owned != None:
                    household_q.append(n.house_owned.quality)
                else:
                    household_q.append(Simulation.rent_unit.quality)

            print(len(household_inc))
            print(len(household_q))



            plt.subplot(131)
            plt.scatter(Statistics.period[-51: -1], Statistics.avg_days_in_market[-51: -1])
            #plt.hist(Statistics.agg_house_quality, bins=40)
            #making scatterplot of house quality/price
            plt_listx = Statistics.agg_house_quality[-101 :-1]
            plt_listy = Statistics.agg_house_price[-101 :-1]
            plt.subplot(132)
            plt.scatter(plt_listx, plt_listy)
            plt.title("House price and quality")
            plt.xlabel("quality")
            plt.ylabel("price")
            print(sum(Statistics.agg_days_in_market[-3001 :-1])/len(Statistics.agg_days_in_market[-3001 :-1]))
            plt.subplot(133)
            plt.xlim(0.06, 1)
            plt.ylim(5000, 50000)
            plt.scatter(household_q, household_inc)

            renters = []
            for n in Simulation.households:
                if n.renting == True:
                    renters.append(n)
            print(len(renters))


class Simulation(Agent):
    # Static fields
    Households = Agent()
    time = 1
    bank = None
    rent_unit = None

    def __init__(self):
        super().__init__()
        # Initial allocation of all agents
        # Children of simulation:
        Simulation.rent_unit = Rent_unit(self)
        Simulation.houses = Agent(self)
        self._statistics = Statistics(self)
        Simulation.bank = Bank(self)
        Simulation.households = Agent(self)


        for _ in range(Settings.number_of_agents):
            Household(Simulation.households)

        for _ in range(Settings.number_of_houses):
            Houses(Simulation.houses)

        # Start the simulation
        self.event_proc(Event.start)

    def event_proc(self, id_event):
        if id_event == Event.start:
            Simulation.houses_for_sale = []
            Simulation.outstanding_loans = []
            super().event_proc(id_event)
            # set houses for sale
            for n in Simulation.houses:
                Simulation.houses_for_sale.append(n)

            # The Event Pump
            while Simulation.time < Settings.number_of_periods:
                self.event_proc(Event.period_start)
                self.event_proc(Event.update)
                if Simulation.time % Settings.periods_in_year == 0:
                    self.event_proc(Event.update_year)
                self.event_proc(Event.period_end)
                Simulation.time += 1


            # Stop the simulation
            self.event_proc(Event.stop)

        if id_event == Event.period_start:
            #make counter for number of deaths this period
            Simulation.dead_this_period = 0
            super().event_proc(id_event)

        if id_event == Event.update:
            super().event_proc(id_event)

        if id_event == Event.update_year:
            super().event_proc(id_event)

        if id_event == Event.period_end:
            # Adding new born persons to the population
            for _ in range(Simulation.dead_this_period):
                    Household(Simulation.households)
            super().event_proc(id_event)

        if id_event == Event.stop:
            super().event_proc(id_event)

#We run the simulation
if Settings.random_seed != 0:
    numpy.random.seed(Settings.random_seed)


Simulation()

plt.show()
plt.show()



