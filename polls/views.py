from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Algo, Trend
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Sum
import urllib.request, json
import dateutil.parser
import re
import numpy

def algos(request):
  algos = []
  for algo in Algo.objects.all():
    algos.append({'id': algo.id, 'name': algo.name, 'pnl': algo.trend_set.aggregate(Avg('pnl'))})
  
  return render(request, 'polls/algos.html', {'algos': algos})

def algo_detail(request, algo_id):
  algo = get_object_or_404(Algo, pk=algo_id)
  trends = algo.trend_set.all()
  
  xs = list(range(1, trends.count()+1))
  ys = []
  for trend in trends:
    ys.append(trend.pnl)
  
  context = {'xs': xs, 'ys': ys}
  
  return render(request, 'polls/algo_detail.html', context)


def trend(request):
  return render(request, 'polls/trend.html')

def trend_submit(request):

  with urllib.request.urlopen("https://api.iextrading.com/1.0/stock/%s/chart/1y" % request.POST['ticker']) as url:
      data = json.loads(url.read().decode())

  now = datetime.now()
  prices = []

  for row in data:
    if dateutil.parser.parse(row['date']) > datetime.now()-timedelta(days=365):
      prices.append(row['close'])
  
  [ positions, PnL] = algo_result(request.POST['signal'], request.POST['trade'], prices)

  print(positions)
  print('\n')
  print(PnL)

  algo = Algo(name=request.POST['name'], signal=request.POST['signal'], trade=request.POST['trade'], ticker=request.POST['ticker'])
  algo.save()
  algo = Algo.objects.last()

  idx = 0
  for position in positions:    
    trend = Trend(position=position, pnl=PnL[idx])
    trend.algo = algo
    trend.save()
    idx = idx + 1

  return HttpResponse("You're looking at question.")

def algo_result(condition, action, prices):
    comparisons = ['larger than', 'smaller than']

    for comparison in comparisons:
        search_res = re.findall(comparison, condition)

        if len(search_res) == 1:
            condition_parts = condition.split(comparison)
            break
        else:
            print('This condition is not supported yet')
            exit()

    avg_price = []

    # Here we calculate the moving averages for those two windows
    MA = []
    for condition_part in condition_parts:

        # find the MA window
        period = re.findall('\d+ \w+', condition_part )[0]
        period = period.split()

        if period[1] == 'days':
            num_days = int(period[0])
        else:
            if period[1] == 'weeks':
                num_days = int(period[0]) * 5 # a world without holidays!
            else:
                print( 'please use the time period in days or weeks')
                exit()

        # calculate MA
        MA.append( [ numpy.mean(prices[i-num_days:i]) for i in range(1, len(prices)+1)])

    # Get buy/sell signal
    MA0 = numpy.array(MA[0])
    MA1 = numpy.array(MA[1])

    if comparison == 'larger than':
        buy_sell = MA0 > MA1
    else:
        buy_sell = MA0 < MA1

    # Create positions and PnL
    num_shares = re.findall('\d+', action)
    num_shares = int(num_shares[0])

    positions = [0]
    PnL = [0]
    for i in range(1,len(prices)-1):
        if buy_sell[i]:
            positions.append(positions[i-1] + num_shares)
        else:
            positions.append(0)

        PnL.append(positions[i-1] * (prices[i] - prices[i-1]))

    return positions, PnL
