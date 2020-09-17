from Model_Simulation import *
all_houses_quality = []
all_incomes = []
all_ages = []
kh_number = 0
total_income = 0

for n in Simulation.Houses:
        all_houses_quality.append(n.quality)


for n in Simulation.Households:
    if n.dead == 0:
        all_incomes.append(n.income)
    else:
        pass

for n in Simulation.Households:
    if n.dead == 0:
        all_ages.append(n.age)
    else:
        pass

for value in all_incomes:
    total_income += value

average_income = total_income / len(all_incomes)
median_income = statistics.median(all_incomes)
# print(Simulation.Household.number_of_agents())
# print(total_income)
# print(average_income)
# print(deaths_period)
# print(all_incomes)
print(median_income)
print(average_income)

for value in all_incomes:
    total_income += value

for n in Simulation.Households:
    if n.income > 11499 and n.income < 11501 and n.dead == 0:
       kh_number += 1
    else:
        pass
#print(all_incomes)
#print(len(all_incomes))
print(kh_number)


#print(all_ages)
#print(len(all_ages))
# all_incomes = [i for i in all_incomes if i != 11500]


plt.hist(all_incomes, bins=5000, color="blue")
plt.axis(xmin=-10000, xmax=150000)
plt.show()

plt.hist(all_ages, bins=dict_bin_ages2, color="blue")
plt.axis(xmin=20, xmax=110)
plt.show()
