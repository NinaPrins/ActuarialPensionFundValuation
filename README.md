# Actuarial pension fund valuation
## Summary

The project's goal is to calculate the Net Present Value (NPV) of each member's pension in a pension fund and finding the NPV of the entire pension fund. To start with, a thousand test cases was generated containing, amongst other things, the date of birth and previous pension received of each of the thousand members. An Excel model was built to calculate the NPV of each member's pension and with that, calculate the NPV of the pension fund. Python code was written using the same data as the Excel model with the same goal. The results in the Excel model and the Python model was compared to ensure that the NPV is calculated on the same way.

## Assumptions

-         Pensions are received monthly in arrears
-         Constant force of mortality for each age year using the [PA92 Mortality Table](https://www.actuaries.org.uk/learn-and-develop/continuous-mortality-investigation/cmi-mortality-and-morbidity-tables/92-series)
- Fees is a fixed rate being charged on each payment made
- Increases on the pension is a fixed percentage made once a year
- Present Value of a Cash Flow principal:
  - `Present Value = CashFlow @ payment date * V * tPx`
  - `V` = discounting factor taking into account the yield @ payment date, fee and the time from effective date to the payment date
  - `tPx` = probability of surviving from effective date to the payment date
- Calculating the probability of survival: `t + yPx = tPx * yPx + t` 
  - for each payment date the probability of surviving from the effective date to their birthday calculated as `tPx` and a subsequent probability of surviving from their birthday to the to the payment date (time = `y`) is calculated as `yPx+t`.

## Excel model
### Inputs
- Effective Date (date on which the NPV is calculated)
- Fees percentage
- Increase percentage
- Increase date
- If a specific member is to be looked at:
  - Member id

### Output
- NPV per member can individually be calculated
- NPV per member for the whole pension fund can be calculated
- NPV for the pension fund

### How the Excel model works
The Excel Model has three sheets. On the `Inputs` sheet the user needs to indicate the necessary information as described above. The `Data` sheet contains the yield curve, the PA92 Mortality Table and the data for the 1000 members of the pension fund. On the `PV of CF` sheet the NPV of a member is calculated using the Present Value of a Cash Flow principal as described above. The Excel model can run for the entire pension fund and the NPV for each member is shown in the `Data` sheet.


## Python model
### Input
- Import:
  - `MOCK_DATA.csv` containing the information on each member
  - `PA92_mortality_rates.csv` containing the mortality table
  - `YieldCurve.csv` containing the interest rate (NACC) at which each payment must be discounted

- Specify:
  - `EffectiveDate` = date at which the NPV is to be calculated
  - `firstIncr` = Next increase date
  - `increasePercentage` = fixed increase percentage
  - `fee` = fixed fees percentage

### Outputs
- CSV file containing the id and NPV of each member
- CSV file containing for the pension fund and specifically for each member their id, the date of payment and the present value of the payment made

### How the Python code works
After entering the necessary inputs as described above, the code runs through each member to calculate the NPV of their pension. Three dictionaries are built up, using functions, with their keys at each date a payment is made. The attributes in the `CashFlow` dictionary is the cash flow including the necessary increase on the payment date. The attributes in the `Birthday_survival` dictionary is the probability of surviving to the previous birthday on the payment date. The attributes in the `Payment_survival` dictionary contains the probability of surviving from the previous birthday to the payment date. The discounting factor is found by calling the `DiscountFactor` function with using the payment date as a reference. To calculate the present value of the cash flow of each date the payment date is called in each dictionary and the attributes with the discounting factor is multiplied as shown in the Present Value of a CashFlow principal as described above. Summing all the present values of all the cash flows, the NPV is found.

## Credits
- Student: [Nina Prins](https://github.com/NinaPrins)
- Supervisor: [Francois Botha](https://github.com/igitur)