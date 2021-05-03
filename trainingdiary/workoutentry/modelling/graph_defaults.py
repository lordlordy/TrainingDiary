class TimeSeriesDefaults:

    # This implementation returns a single case of defaults. This is ok as not graphing to compare say two ctl graphs
    # When that come the case will need to sperate out the default object from the data.
    # At the moment the data is being stuck inside this default

    def __init__(self):
        self.dd = {
            'atl': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'atl', '#ff0000', '#ff0000', False, 3, 15, True),'left',  1, 'linear', True),
            'ctl': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'ctl', '#00ff00', '#00ff00', False, 3, 15, True), 'left', 1, 'linear', True),
            'tsb': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'tsb', '#0000ff', '#11e7ff', True, 3, 15, True), 'left', 1, 'linear', True),
            'tss': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'tss', '#ff00dd', '#ff00dd', False, 5, 15, False), 'right', 1, 'linear', True),
            'seconds': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'seconds', '#ff00dd', '#ff00dd', False, 5, 15, False), 'right', 1, 'linear', True),
            'minutes': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'minutes', '#ff00dd', '#ff00dd', False, 5, 15, False), 'right', 1, 'linear', True),
            'hours': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('bar', 'hours', '#ff00dd', '#ff00dd', False, 5, 15, False), 'right', 1, 'linear', True),
            'km': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('bar', 'km', '#171743', '#171743', False, 5, 15, False), 'right', 1, 'linear', True),
            'ed_num': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'ed#', '#ff0000', '#fad2d7', False, 1, 10, True), 'left', 1, 'linear', True),
            'plus_one': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', '+1', '#008f00', '#008f00', False, 1, 2, True), 'left', 1, 'linear', True),
            'contributor': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'contributors', '#0000ff', '#0000ff', False, 3, 7, False), 'left', 1, 'linear', True),
            'annual_ed_num': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'annual ed#', '#6a0296', '#d27ff5', False, 10, 20, False), 'left', 1, 'linear', True),
            'annual_plus_one': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'annual ed#', '#0000ff', '#0000ff', False, 5, 10, False), 'left', 1, 'linear', True),
            'monthly_ed_num': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'annual ed#', '#6a0296', '#d27ff5', False, 10, 20, False), 'left', 1, 'linear', True),
            'monthly_plus_one': TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'annual ed#', '#0000ff', '#0000ff', False, 5, 10, False), 'left', 1, 'linear', True),
        }

    def defaults(self, series_definition):
        if series_definition is None:
            return TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', 'Unknown Measure', '#111111', '#777777', True, 3, 15, True), 'left', 1, 'linear', True)
        measure = series_definition.measure
        if measure in self.dd:
            defaults = self.dd[measure]
        else:
            defaults = TimeSeriesDefaults.Default(TimeSeriesDefaults.DataSet('line', measure, '#111111', '#777777', True, 3, 15, True), 'left', 1,  'linear', True)

        return self.__adjust_for_definition(defaults, series_definition)

    def __adjust_for_definition(self, defaults, series_definition):
        if series_definition.is_rolling():
            defaults.position = 'left'
            defaults.dataset.chart_type = 'line'
            defaults.dataset.showLine = True
            defaults.dataset.fill = False
            defaults.dataset.label += f" {series_definition.title_component()}"
            defaults.dataset.borderColour = self.__adjust_colour_by(defaults.dataset.borderColour, 0.85)
            defaults.dataset.backgroundColour = defaults.dataset.borderColour
            defaults.dataset.pointRadius = 1
            defaults.dataset.pointHoverRadius = 7
        elif series_definition.period.to_date:
            defaults.position = 'left'
            defaults.number = 2
            defaults.dataset.chart_type = 'line'
            defaults.dataset.showLine = True
            defaults.dataset.fill = False
            defaults.dataset.label += f" {series_definition.title_component()}"
            defaults.dataset.pointRadius = 1
            defaults.dataset.pointHoverRadius = 5

        return defaults

    def __adjust_colour_by(self, colour, percentage):
        as_int = int(int(colour.strip("#"), 16) * percentage)
        return f"#{hex(as_int).strip('0x')}"

    class Default:

        def __init__(self, dataset, position, number, scale_type, draw_grid_lines):
            self.dataset = dataset
            self.position = position
            self.number = number
            self.scale_type = scale_type
            self.draw_grid_lines = draw_grid_lines

        def axis_id(self):
            return Scales.axis_id(self.position, self.number, self.scale_type, self.draw_grid_lines)

    class DataSet:

        def __init__(self, chart_type, label, borderColour, backgroundColour, fill, pointRadius, pointHoverRadius, showline):
            self.chart_type = chart_type
            self.label = label
            self.borderColour = borderColour
            self.backgroundColour = backgroundColour
            self.fill = fill
            self.pointRadius = pointRadius
            self.pointHoverRadius = pointHoverRadius
            self.showLine = showline
            self.yAxisID = "not configured"
            self.data = list()

        def set_data(self, data):
            self.data = data

        def set_yaxis_id(self, yaxis_id):
            self.yAxisID = yaxis_id

        def data_dictionary(self):
            return {'type': self.chart_type,
                    'label': self.label,
                    'borderColor': self.borderColour,
                    'backgroundColor': self.backgroundColour,
                    'fill': self.fill,
                    'pointRadius': self.pointRadius,
                    'pointHoverRadius': self.pointHoverRadius,
                    'showLine': self.showLine,
                    'yAxisID': self.yAxisID,
                    'data': self.data}


class Scales:

    @staticmethod
    def axis_id(position, number, scale_type, draw_grid_lines) -> str:
        components = [position, str(number)]
        if scale_type != 'linear':
            components.append(scale_type)
        if not draw_grid_lines:
            components.append('nolines')
        return "-".join(components)

    class YAxis:

        def __init__(self, defaults):
            self.position = defaults.position
            self.number = defaults.number
            self.titles = [defaults.dataset.label]
            self.scale_type = defaults.scale_type
            self.draw_grid_lines = defaults.draw_grid_lines

        def axis_id(self) -> str:
            return Scales.axis_id(self.position, self.number, self.scale_type, self.draw_grid_lines)

        def add_to_axis(self, title):
            self.titles.append(title)

        def data_dictionary(self):
            return {'type': self.scale_type,
                    'display': True,
                    'position': self.position,
                    'gridLines': {'drawOnChartArea': self.draw_grid_lines},
                    'title': {'display': True,
                              'font': {'size': 18},
                              'text': " ".join(self.titles)}}

    def __init__(self):
        self.scales = dict()

    def add(self, defaults) -> str:
        axis_id = defaults.axis_id()
        if axis_id in self.scales:
            self.scales[axis_id].add_to_axis(defaults.dataset.label)
        else:
            axis = Scales.YAxis(defaults)
            self.scales[axis_id] = axis
        return axis_id

    def data_dictionary(self):
        return {key: value.data_dictionary() for key, value in self.scales.items()}
