import React, {Component, createRef} from 'react';
import Highcharts from 'highcharts'

import HighchartsDrillDown from 'highcharts/modules/drilldown';
import HighchartsExporting from 'highcharts/modules/exporting';
import HighchartsExportingOffline from 'highcharts/modules/offline-exporting';
import HeatMap from 'highcharts/modules/heatmap';
import Accessibility from 'highcharts/modules/accessibility';
import AddNoDataModule from 'highcharts/modules/no-data-to-display';
import HighChartWordCloud from 'highcharts/modules/wordcloud';

HighchartsExporting(Highcharts);
HighchartsExportingOffline(Highcharts);
HeatMap(Highcharts);
Accessibility(Highcharts);
AddNoDataModule(Highcharts);
HighchartsDrillDown(Highcharts);
HighChartWordCloud(Highcharts);

class ReactHighcharts extends Component {
  constructor(props){
    super(props);
    this.container = createRef();
  }
  componentDidMount() {
    const p = this.props
    const highcharts = p.highcharts || Highcharts;
    const constructorType = p.constructorType || 'chart';
    // Create chart
    this.chart = highcharts[constructorType](this.container.current, Object.assign({}, p.options));
  }
  shouldComponentUpdate(nextProps, nextState) {
    const update = this.props.update
    // Update if not specified or set to true
    return (typeof update === 'undefined') || update
  }
  componentDidUpdate() {
    this.chart.update(Object.assign({}, this.props.options), true, !(this.props.oneToOne === false))
  }
  
  componentWillUnmount() {
    // Destroy chart
    this.chart && this.chart.destroy()
  }

  render() {
    const {containerProps} = this.props;
    return (
      <div {...containerProps} ref={this.container}></div>
    )
  }
}
ReactHighcharts.defaultProps = {
  containerProps: {}
}

export default ReactHighcharts;