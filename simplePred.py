def predict(data):
    if len(data) == 0:
        return {}
    elif len(data) == 1:
        predicted_premiums = {}
        predicted_value = list(data.values())[0]
        for month in range(1, 13):
            if f"2023-{month:02d}" not in data:
                year_month = f"2023-{month:02d}"
                predicted_premiums[year_month] = round(predicted_value, 2)

        return predicted_premiums
    try:  
      x_values = [int(month.split('-')[1]) for month in data.keys()]
      y_values = list(data.values())

      n = len(x_values)
      sum_x = sum(x_values)
      sum_y = sum(y_values)
      sum_xy = sum(x * y for x, y in zip(x_values, y_values))
      sum_x_squared = sum(x**2 for x in x_values)

      slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x**2)
      intercept = (sum_y - slope * sum_x) / n

      predicted_premiums = {}
      for month in range(1, 13):
          if f"2023-{month:02d}" not in data:
              predicted_value = slope * month + intercept
              year_month = f"2023-{month:02d}"
              predicted_premiums[year_month] = round(predicted_value, 2)

      return predicted_premiums
    
    except:
        x_values = [int(year) for year in data.keys()]
        y_values = list(data.values())

        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x**2 for x in x_values)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n

        predicted_premiums = {}

        year = x_values[-1] + 1
        predicted_value = slope * year + intercept
        year = f"2023"
        predicted_premiums[year] = round(predicted_value, 2)
        
        return predicted_premiums