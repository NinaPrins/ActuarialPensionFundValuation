#import
import datetime
from dateutil.relativedelta import relativedelta
import csv
import pandas as pd
import math

# state all fixed variables
# effective date is on 30 June 2018
effectiveDate = datetime.date(2018, 6, 30)
# increase date is on 31 Desember each year with 5%
increasePercentage = 0.05
firstIncr = datetime.date(effectiveDate.year, 12, 31)
lastIncr = firstIncr + relativedelta(years=+120)
incrDate = {}
while firstIncr.year < lastIncr.year:
    incrDate[firstIncr] = increasePercentage
    firstIncr += relativedelta(years=+1)
# Fees is a fixed 0.02%
fee = 0.0002     

#import all the data
# Mortality Rates (qx) containing: Age, Males, Females using a PA92 Mortality Table
MortalityTable = pd.read_csv("PA92_mortality_rates.csv")
# Data containing: id, first_name, last_name, date_of_birth, gender, pension
Mock_Data = pd.read_csv("MOCK_DATA.csv", parse_dates=['date_of_birth'])
# Yield curve
yieldCurveGross = pd.read_csv("YieldCurve.csv", parse_dates=['Date'])

# find the interest at which you discount (NACC)
yieldCurveNet = {}
for yieldCurveIndex in yieldCurveGross.index:
    yieldCurveNet[yieldCurveGross["Date"][yieldCurveIndex].date()] = yieldCurveGross["NACCRate"][yieldCurveIndex] - fee

# Find the discounting factor (V)
def DiscountFactor(payment_date):
    timeElapsed = payment_date - effectiveDate
    n = timeElapsed.days / 365.25
    v = math.exp(- n * yieldCurveNet[payment_date])
    return v

# dictionary containing the CF at the date the payment is made
def CashFlow(pension):
    CF = {}
    #use the dates that the yield is available which is the same dates that payments are made
    for yieldCurveIndex in yieldCurveGross.index:
        if yieldCurveGross["Date"][yieldCurveIndex].date() in incrDate:
            numInc = 1
            pension = pension * (1 + incrDate[yieldCurveGross["Date"][yieldCurveIndex].date()])**(numInc)
            numInc += 1 
        CF[yieldCurveGross["Date"][yieldCurveIndex].date()] = pension
    return CF
    
# Find the whole number age of person at a specific date
def Age(date_given, date_of_birth):
    if date_of_birth.month <= date_given.month:
        age = date_given.year - date_of_birth.year
    else:
        age = date_given.year - date_of_birth.year - 1
    return age

# assume a CFM: Px = exp(-force_of_mortality_for_age_x)
# return the force of mortality
def Survival(current_age, gender):
    if current_age >= 120:
        surviving = 0
    else:
        #Px
        # current_age - 1 since python starts counting at 0 when reading off a CSV.file
        # Current_age - 20 since the PA92 table starts at age 20
        surviving = 1 - MortalityTable[gender + 's'][current_age - 20]
    if surviving > 0:
        # Px = exp(-force_of_mortality_for_age_x)
        # force_of_mortality_for_age_x = - ln(Px)
        force_of_mortality = math.log(surviving) * -1
    else:
        force_of_mortality = 0
    return force_of_mortality    

# find the probability of surviving from starting age to subsequent birthdays
# return the probability of surviving to the previous birthday at each payment date
def Birthday_survival(date_of_birth, gender):
    # to calculate the keys in the dictionary first find next birthday
    # take into account if person was born on leap day
    if date_of_birth.year % 4 == 0 and date_of_birth.month == 2 and date_of_birth.day == 29:
        if datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day-1) <= effectiveDate:
            next_birth = datetime.date(effectiveDate.year + 1, date_of_birth.month, date_of_birth.day-1)
        else:
             next_birth = datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day-1)
    else:
        if datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day) <= effectiveDate:
            next_birth = datetime.date(effectiveDate.year + 1, date_of_birth.month, date_of_birth.day)
        else:
             next_birth = datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day)  
    # birthday variable which starts at the next birthday
    birth = next_birth
    #find age at effective date (x)
    current_age = Age(effectiveDate, date_of_birth)
    # dictionary
    tPx = {}
    # starting probability
    P0 = 1
    # first entry at T0
    tPx[effectiveDate] = P0
    # use the dates that payments are made meaning the dates NACC are available
    for yieldCurveIndex in yieldCurveGross.index:
        # first few months before next birthday P0 = 1 since assume alive at effective date
        if yieldCurveGross["Date"][yieldCurveIndex].date() <= next_birth:
            tPx[yieldCurveGross["Date"][yieldCurveIndex].date()] = P0
        if yieldCurveGross["Date"][yieldCurveIndex].date() >= birth:
            # birthday occured and age increases
            current_age +=1
            if current_age == 120:
                break
            #Px
            # current_age - 1 since python starts counting at 0
            # Current_age - 20 since the PA92 table starts at age 20
            surviving = 1 - MortalityTable[gender + 's'][current_age - 21]
            P0 = P0 * surviving
            # birthday date for the following year
            birth += relativedelta(years=+1)    
        tPx[yieldCurveGross["Date"][yieldCurveIndex].date()] = P0
    return tPx

#probability of surviving from previous birthday up to date the payment is made
def Payment_survival(date_of_birth, gender):
    CFM ={}
    # entry age
    age = Age(effectiveDate, date_of_birth)
    #calculate next birthday date
    # take into account if person was born on leap day
    if date_of_birth.year % 4 == 0 and date_of_birth.month == 2 and date_of_birth.day == 29:
        if datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day-1) <= effectiveDate:
            next_birth = datetime.date(effectiveDate.year + 1, date_of_birth.month, date_of_birth.day-1)
        else:
            next_birth = datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day-1)
    else:
        if datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day) <= effectiveDate:
            next_birth = datetime.date(effectiveDate.year + 1, date_of_birth.month, date_of_birth.day)
        else:
            next_birth = datetime.date(effectiveDate.year, date_of_birth.month, date_of_birth.day)
    # birthday variable start define as next birthday
    birth = next_birth 
    #use the dates that the NACC is available
    for yieldCurveIndex in yieldCurveGross.index:
        if yieldCurveGross["Date"][yieldCurveIndex].date() >= birth:
            # next birthday
            birth += relativedelta(years=+1)
            #age increase by a year
            age += 1
        if age == 120:
            break
        else:
            # until next birthday you only take in to account survival from effective date to next birthday
            if yieldCurveGross["Date"][yieldCurveIndex].date() <= next_birth:
                # take in to account if it is a leap year
                if yieldCurveGross["Date"][yieldCurveIndex].year % 4 == 0 and date_of_birth.year % 4 == 0 and date_of_birth.month == 2 and date_of_birth.day == 29:
                    n = (yieldCurveGross["Date"][yieldCurveIndex].date() - effectiveDate - datetime.timedelta(days = 1)).days/ 365.25
                else:
                    n = (yieldCurveGross["Date"][yieldCurveIndex].date() - effectiveDate).days/ 365.25
            else:
                # exact age at payment date minus the whole number age is the time that the person needs
                # to survive from their birthday to that payment date
                # take into account if leap year
                if yieldCurveGross["Date"][yieldCurveIndex].year % 4 == 0 and date_of_birth.year % 4 == 0 and date_of_birth.month == 2 and date_of_birth.day == 29:
                    n = (yieldCurveGross["Date"][yieldCurveIndex].date() - date_of_birth - datetime.timedelta(days = 1)).days/365.25 - Age(yieldCurveGross["Date"][yieldCurveIndex].date(), date_of_birth)
                else:
                    n = (yieldCurveGross["Date"][yieldCurveIndex].date() - date_of_birth).days/365.25 - Age(yieldCurveGross["Date"][yieldCurveIndex].date(), date_of_birth)
            # force of mortality
            u = Survival(age, gender)
            CFM[yieldCurveGross["Date"][yieldCurveIndex].date()] = math.exp(- u * n)
    return CFM

# create a dictionary containing ID and NPV
NPVperMember = {}
# create a list containing ID, date of payment, cash flow and PV of the Cash Flow on that date
CashFlowProjection = []
# starting NPV of the pension fund is 0
NPV_PF = 0
# loop calculating the NPV of the pension per person
# loop calculating the NPV of the pension fund
for index in Mock_Data.index:
    print("Processing member id ", Mock_Data['id'][index])
    #starting age
    age = Age(effectiveDate, Mock_Data['date_of_birth'][index])
    #dictionary of CFs
    CFs = CashFlow(Mock_Data['pension'][index])
    # gender
    sex = str(Mock_Data['gender'][index])
    #dictionary containing probability of survival from previous birthday to payment date assuming a constant force of mortality
    CFM = Payment_survival(Mock_Data['date_of_birth'][index].date(), sex)
    # dictionary containing tPx on birthdays eg. probability of surviving to previous birthday at payment date
    tPx = Birthday_survival(Mock_Data['date_of_birth'][index].date(), sex)
    # starting NPV is 0
    NPV = 0
    #use the dates that the yield is available
    for yieldCurveIndex in yieldCurveGross.index:
        if yieldCurveGross["Date"][yieldCurveIndex].date() in tPx:
            # PV of a single cash flow @ payment date = CF * V * tPx *yPx+t 
            # t is an integer of time from x to previous birthday
            # and y is the time between payment date and previous birthday
            # exact age at payment date = x + t + y
            CF = CFs[yieldCurveGross["Date"][yieldCurveIndex].date()]
            PV_sCF = CF * DiscountFactor(yieldCurveGross["Date"][yieldCurveIndex].date()) * tPx[yieldCurveGross["Date"][yieldCurveIndex].date()]*CFM[yieldCurveGross["Date"][yieldCurveIndex].date()]
            #NPV = sum of all single PV of the single cash flows
            NPV = NPV + PV_sCF
            # expand list
            CashFlowProjection.append([Mock_Data['id'][index], yieldCurveGross["Date"][yieldCurveIndex].date(), CF, PV_sCF])
        else:
            break 
    NPV_PF = NPV_PF + NPV
    # expand the dictionary containing ID and NPV
    NPVperMember[Mock_Data['id'][index]] = NPV 

# create CSV file containing id and NPV
df = pd.DataFrame.from_dict(NPVperMember, orient='index', columns = ["NPV"])
df.to_csv("NPVperMember.csv", index_label  = "Member ID", columns = ["NPV"])
print("CSV file containing the ID and NPV of each member is written as NPVperMember.csv")

# create CSV file containing id, date of payment and PV of cash flow
# create CSV file containing id, date of payment and PV of cash flow
df = pd.DataFrame(CashFlowProjection, columns = ["Member ID", "Date of payment", "Cash Flow", "Present Value of Cash Flow"])
df.to_csv("CashflowProjection.csv", index = False)
print("CSV file containing the ID, date of payment and the Cash Flow on that date is written as CashflowProjection.csv")