import statistics
import numpy as np
import pandas as pd
import numpy_financial as npf
import matplotlib.pyplot as plt

MARR = (1.4**0.25) - 1

fig, ax = plt.subplots(1, 1)
ax.vlines(x=357204.30, ymin=0, ymax=1, linestyles='dashed', colors='b', label='Mean NPV (Deterministic)')

files = ["data/uncertainty_cs2_all.npy", "data/real_option_build.npy"]
# files = ["data/uncertainty_cs2_all.npy", "data/real_option_customer_all.npy"]

for file in files:
    data = np.load(file)
    stats = pd.DataFrame(columns=['NPV','IRR','CAPEX','System Hours','MRR'])

    for x in range(data.shape[2]):
        # df = pd.DataFrame(data[:,:,x], columns=['expenses_total','expenses_customer_acquisition',"expenses_build","expenses_maintenance","expenses_germination","expenses_op_cost","expenses_transactions","revenue_total","revenue_sale","revenue_subscription","revenue_transactions","client_count","active_units","average_lifetime","churned"])
        # capex = df['expenses_total'].iloc[0]
        df = pd.DataFrame(data[:,:,x], columns=['expenses_total','expenses_customer_acquisition',"expenses_build","expenses_maintenance","expenses_germination","expenses_op_cost","expenses_capex","expenses_transactions","revenue_total","revenue_sale","revenue_subscription","revenue_transactions","client_count","active_units","average_lifetime","churned"])
        capex = df['expenses_capex'].sum()

        df['run_hours'] = df['active_units']*168 #each week, each active unit runs for 168 hours

        cash_flows = df[["expenses_total", "revenue_total"]].groupby(df.index // 13).sum()
        cash_flows.loc[-1] = [capex, 0]
        cash_flows.index = cash_flows.index + 1
        cash_flows = cash_flows.sort_index()
        cash_flows["PW"] = (cash_flows["revenue_total"] - cash_flows["expenses_total"]) * (1 + MARR)**(-(cash_flows.index))
        # print(f"NET PROFIT: £{(cash_flows['revenue_total'] - cash_flows['expenses_total']).sum():,.2f}")
        irr = npf.irr(list(cash_flows['PW']))
        # if x==0: print(cash_flows)

        mrr = df['revenue_subscription'].groupby(df.index // 4).sum().iloc[-1]
        new_stats = pd.DataFrame([[cash_flows['PW'].sum(), irr, capex, df['run_hours'].sum(), mrr]], columns=['NPV','IRR','CAPEX','System Hours', 'MRR'])
        stats = pd.concat([stats, new_stats], ignore_index=True)

        # print("\nRUN STATISTICS")
        # print(f"\tCAPEX: £{capex:,.2f}")
        # print(f"\tNPV: £{(cash_flows['PW'].sum()):,.2f}")
        # print(f"\tIRR: {irr*100:.2f}% per quarter, {((1+irr)**4 - 1)*100:.2f}% annually")
        # print(f"\tTotal System Activity: {df['run_hours'].sum():,.0f} hours")
        # print(f"\tMonthly Recurring Revenue: £{mrr:,.2f}")


    print("\n-------\nSIM STATISTICS")
    print(f"\tMean NPV: £{(stats['NPV'].mean()):,.2f}")
    print(f"\tStd. Dev.: £{(stats['NPV'].std()):,.2f}")
    print(f"\tP5: £{(stats['NPV'].quantile(.05)):,.2f}")
    print(f"\tP95: £{(stats['NPV'].quantile(.95)):,.2f}")
    print(f"\tCAPEX: £{(stats['CAPEX'].mean()):,.2f}\n")

    # CDF CALCULATION
    stats_df = stats.groupby('NPV')['NPV'].agg('count').pipe(pd.DataFrame).rename(columns = {'NPV': 'frequency'})
    stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])
    stats_df['cdf'] = stats_df['pdf'].cumsum()
    stats_df = stats_df.reset_index()

    # CDF PLOT
    if 'uncertainty' in file:
        labels = ['NPV (Stochastic)', 'r']
    else:
        labels = ['NPV (Flexible)', 'g']

    stats_df.plot(x='NPV', y='cdf', ax=ax, color=labels[1], label=labels[0])
    ax.vlines(x=stats['NPV'].mean(), ymin=0, ymax=1, linestyles='dashed', colors=labels[1], label='Mean '+labels[0])

ax.legend()
ax.set_ylim(0, 1)
plt.show()
