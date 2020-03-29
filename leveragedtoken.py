#!/usr/bin/python3

from sympy.solvers import solve
from sympy import Symbol
import math
import sys

# This is a simple script to compute the FTX Leveraged Token return for a given day
# Read the walkthrough from FTX carefully: 
#   https://help.ftx.com/hc/en-us/articles/360032509552-Leveraged-Token-Walkthrough-READ-THIS-
# Every day at 00:02:00 UTC the leveraged token rebalances its leverage to 3x based on any gain (or loss) throughout the day
# There is also an intra-day rebalance for when the token's underlying has a negative return that brings its 
#    effective leverage to 4x
# For BULL tokens this is a 11% drop in the underlying, for BEAR tokens this is a 6.5% rise in the underlying
# Note that there is no longer any rebalance when the underlying has large moves in its favour (up for BULL, down for BEAR)

# This script requires 5 arguments:
# 1) bull or bear to indicate it is a bull or bear token (3x long, 3x short)
# 2) start underlying price -- the price of underlying contract at 00:02:00 UTC for the day 0
# 3) peak / trough intraday price -- this is the lowest price (trough) for BULL tokens or the highest price (peak) for 
#    BEAR tokens
# 4) end underlying price -- the price of underlying contract at 00:02:00 UTC the next day 1
# 5) token start price -- this is the price of the token at 00:02:00 for day 0

# Example: BULL token for ETH/USD with start underlying price $130, trough price $81.564, end underlying price $84, 
#    and start token price $20
# python3 leveragedtoken.py bull 130 81.564 84 20
# Start price of underlying: $130
# Number of rebalances: 4
# Price of trough: $81.564
# End price of underlying: $84
# Return on underlying: -35.38%
# Token start price: $20
# Token end price: $4.150591349124615

# Get historical underlying data and token data:
# https://ftx.com/api/markets/ETH-PERP/candles?resolution=86400&start_time=1583971320
# https://ftx.com/api/markets/ETHBULL/USD/candles?resolution=86400&start_time=1583971320
#
# Get historical rebalance data for token:
# https://ftx.com/api/etfs/ETHBULL/major_rebalances

def solvebull(troughreturn):
	x = Symbol('x')
	solution=solve(1 - 0.8812**(x-1) - troughreturn, x)
	numrebalances=math.floor(solution[0])-1
	return numrebalances

def solvebear(peakreturn):
	x = Symbol('x')
	solution=solve(1.067**(x-1) - 1 - peakreturn, x)
	numrebalances=math.floor(solution[0])-1
	return numrebalances


if len(sys.argv) < 5:
	print("Must enter at least five arguments: bull/bear, start underlying price, peak price (bear) or trough price (bull), end of day underlying price, and token start price")
	exit()

type=sys.argv[1]
underlyingstart=sys.argv[2]
underlyingopp=sys.argv[3]
underlyingend=sys.argv[4]
tokenstartprice=sys.argv[5]
tokenendprice=float(tokenstartprice)
if sys.argv[1]=="bull":
	boom=(float(sys.argv[2])-float(sys.argv[3]))/float(sys.argv[2])
	if boom>=0.1112:
		numrebalances=solvebull(boom)
		droptotrough=round(100*((float(underlyingstart)-float(underlyingopp))/float(underlyingstart)),2)
		oppmsg="Price of trough: $" + str(underlyingopp) + "\nDrop to trough: " + str(droptotrough) + "%\nNumber of rebalances: " + str(numrebalances)
		loopnum=numrebalances+1
		x=0
		while x<loopnum:
			tokenendprice=tokenendprice*0.6664
			x+=1
		finalreturn=(float(underlyingend)-float(underlyingopp))/float(underlyingopp)
		tokenendprice=tokenendprice*(1+(finalreturn*3))
		totalreturn=(float(underlyingend)-float(underlyingstart))/float(underlyingstart)
	else:
		numrebalances=0
		oppmsg="No drop triggering rebalance for peak $" + str(underlyingopp)
		totalreturn=(float(underlyingend)-float(underlyingstart))/float(underlyingstart)
		tokenendprice=tokenendprice*(1+(totalreturn*3))
elif sys.argv[1]=="bear":
	boom=(float(sys.argv[3])-float(sys.argv[2]))/float(sys.argv[2])
	if boom>=0.067:
		numrebalances=solvebear(boom)
		jumptopeak=round(100*((float(underlyingopp)-float(underlyingstart))/float(underlyingstart)),2)
		oppmsg="Price of peak: $" + str(underlyingopp) + "\nJump to peak: " + str(jumptopeak) + "%\nNumber of rebalances: " + str(numrebalances)
		loopnum=numrebalances+1
		tokenendprice=float(tokenstartprice)
		x=0
		while x<loopnum:
			tokenendprice=tokenendprice*0.799
			x+=1
		finalreturn=(float(underlyingopp)-float(underlyingend))/float(underlyingopp)
		tokenendprice=tokenendprice*(1+(finalreturn*3))
		totalreturn=(float(underlyingstart)-float(underlyingend))/float(underlyingstart)
	else:
		numrebalances=0
		oppmsg="No rise triggering rebalance for peak $" + str(underlyingopp)
		totalreturn=(float(underlyingstart)-float(underlyingend))/float(underlyingstart)
		tokenendprice=tokenendprice*(1+(totalreturn*3))
else:
	print("Must specify bull or bear token")
	exit()


print("Start price of underlying: $" + str(underlyingstart))
print(oppmsg)
print("End price of underlying: $" + str(underlyingend))
print("Daily return on underlying: " + str(round(100*totalreturn,2)) + "%")
print("Token start price: $" + str(tokenstartprice))
print("Token end price: $" + str(tokenendprice))
