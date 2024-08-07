/* library imports */
import React, { Component, createRef } from 'react';
import {reaction } from 'mobx';
import Highcharts from 'highcharts';
import {isArray} from 'lodash';

/* other project imports */
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import f from 'common-ui/utils/f';
import { Utils } from 'common-ui/utils/utils';
import ReactHighcharts from 'common-ui/lib/highcharts/ReactHighcharts';



class Charts extends Component {
	constructor(props) {
		super(props);
		if (this.props.data && f.isPromise(this.props.data)) {
			reaction(
				() => !f.isLoading(this.props.data),
				() => {
					this.setData && this.setData(f.models(this.props.data));
				}
			);
		}
		this.chart = createRef();
	}

	componentDidMount(){
		if (!this.props.addLoader && this.props.data && f.isPromise(this.props.data) && !f.isLoading(this.props.data)){
			this.setData && this.setData(f.models(this.props.data))
		}
	}

	commonOptions = {
		exporting: {
			enabled: false,
			url: null,
			// sourceWidth: 1000,
			// sourceHeight: 600,
			sourceWidth: 900,
			sourceHeight: 550,
			chartOptions: { // specific options for the exported image
				plotOptions: {
					series: {
						dataLabels: {
							enabled: this.props.exportDataLabel,
							inside: false,
							crop: false,
							overflow: 'justify',
							rotation: -60,
							padding: 0,
							y: -15,
							allowOverlap: true,
							formatter: function () {
								if (typeof this.y == 'number' && this.y > 0) {
									return this.y;
								}
							},
							style: {
								textOutline: false,
							},
						}
					},
					bar: {
						dataLabels: {
							enabled: true,
							formatter: function () {
								if (typeof this.y == 'number' && this.y > 0) {
									return this.y;
								}
							}
						}
					}
				}
			},
			fallbackToExportServer: false
		},
		title: {
			text: this.props.title
		},
		credits: {
			enabled: false
		}
	}
	options = {}
	getMergeOptions() {
		const { chartOptions } = this.props;
		this.mergeOptions = { ...this.commonOptions, ...this.options, ...(chartOptions || {}) };
		return this.mergeOptions;
	}
	setData(data) { }
}

Charts.defaultProps = {
	title: "",
	chartOptions: {},
	exportDataLabel: true,
	addLoader : true
}

class PieHighcharts extends Charts {
	//colors=['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4'];
	options = {
		chart: {
			plotBackgroundColor: null,
			plotBorderWidth: null,
			plotShadow: false,
			type: 'pie'
		},
		tooltip: {
			pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
		},
		plotOptions: {
			pie: {
				allowPointSelect: true,
				cursor: 'pointer',
				dataLabels: {
					enabled: false,
					format: '<b>{point.name}</b>: {point.percentage:.1f} %',
					style: {
						color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
					},
					showInLegend: true
				}
			}
		},
		series: []
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		let obj = {
			name: '',
			colorByPoint: true,
			data: []
		}
		data.forEach(d => {
			obj.data.push({
				//color: this.colors[Math.floor(Math.random() * this.colors.length)],
				name: d.name,
				y: parseInt(d.value)
			})
		})
		return obj;
	}
	setData(data = []) {
		const { state } = this;
		const { formatData, chartOptions } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options = { ...state.options, ...(chartOptions || {}) };
		state.options.series = isArray(data) ? data : [data];
		this.setState(state);
	}
	render() {
		const { state } = this;
		const {data, containerProps={}, addLoader} = this.props;
		const component = (
			<ReactHighcharts containerProps={{/*style: {maxWidth: '600px'}, */className: 'center', ...containerProps}} ref={this.chart} options={state.options} />
		)

		if (addLoader) {
			return (
				<Loader promiseData={data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
					{component}
				</Loader>
			)
		}
		
		return component;
	}
}
PieHighcharts.defaultProps = {
	exportDataLabel: false,
	addLoader: true
}

class BarHighcharts extends Charts {
	//colors=['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
	options = {
		chart: {
			type: 'column'
		},
		xAxis: {
			categories: [],
			title: {
				text: this.props.xAxisText || ''
			}
		},
		yAxis: {
			min: 0,
			allowDecimals: false,
			title: {
				text: this.props.yAxisText || ''
			}
		},
		series: [{
			name: '',
			data: [],
			maxPointWidth: 50
		}],
		legend: {
			enabled: false
		},
		tooltip: {
			formatter: function () {
				return `${this.x}: <b>${this.y}</b>`;
			}
		}
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		let obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			obj.data.push({
				//color: this.colors[Math.floor(Math.random() * this.colors.length)],
				y: parseInt(d.value)
			})
		})
		return obj;
	}
	setData(data = []) {
		const { state } = this;
		const {combo=false} = this.props;
		const { formatData } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options.xAxis.categories = data.categories;
		if (combo) {
			state.options.series = data.data;
		} else {
			state.options.series[0].data = data.data;
		}
		this.setState(state);
	}
	render() {
		const { state } = this;
		const {data, containerProps={}} = this.props;
		return (
			<Loader promiseData={data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
				<ReactHighcharts ref={this.chart} options={state.options} containerProps={containerProps} />
			</Loader>
		)
	}
}

class MultibarHighcharts extends Charts {
	options = {
		chart: {
			type: this.props.type || 'column'
		},
		xAxis: {
			categories: [],
			title: {
				text: this.props.xAxisText || ''
			},
			crosshair: false
		},
		yAxis: {
			//min: 0,
			allowDecimals: false,
			title: {
				text: this.props.yAxisText || ''
			}
		},
		series: [{
			name: '',
			data: []
		}],
		legend: {
			enabled: false
		},
		tooltip: {
			headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
			pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
				'<td style="padding:0"> <b>{point.y:.1f}</b></td></tr>',
			footerFormat: '</table>',
			shared: false,
			useHTML: true
		},
		plotOptions: {
			column: {
				pointPadding: 0.2,
				borderWidth: 0,
				groupPadding: 0
			}
		}
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		let obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			obj.data.push({
				//color: this.colors[Math.floor(Math.random() * this.colors.length)],
				y: parseInt(d.value)
			})
		})
		return obj;
	}
	setData(data = []) {
		const { state } = this;
		const { formatData } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options = { ...state.options, ...{ chartOptions: this.props.chartOptions } };
		state.options.xAxis.categories = data.categories;
		state.options.series = data.data;
		if (data.drilldown) {
			state.options.drilldown = {series:data.drilldown};
		}
		this.setState(state);
	}
	render() {
		const {state} = this;
		const {containerProps={}, addLoader} = this.props;
		const component = (
			<ReactHighcharts ref={this.chart} options={state.options} containerProps={containerProps} />
		)
		if (addLoader) {
			return (
				<Loader promiseData={this.props.data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
					{component}
				</Loader>
			)
		}
		return component;
	}
}

class SparklinesChart extends Charts {
	options = {
		chart: {
			backgroundColor: null,
			borderWidth: 0,
			type: 'area',
			margin: [2, 0, 2, 0],
			width: 120,
			height: 100,
			style: {
				overflow: 'visible'
			},

			// small optimalization, saves 1-2 ms each sparkline
			skipClone: true
		},
		title: {
			text: ''
		},
		credits: {
			enabled: false
		},
		xAxis: {
			labels: {
				enabled: false
			},
			title: {
				text: null
			},
			startOnTick: false,
			endOnTick: false,
			tickPositions: []
		},
		yAxis: {
			endOnTick: false,
			startOnTick: false,
			labels: {
				enabled: false
			},
			title: {
				text: null
			},
			tickPositions: [0]
		},
		legend: {
			enabled: false
		},
		tooltip: {
			backgroundColor: 'white',
			borderWidth: 1,
			hideDelay: 0,
			shared: true,
			padding: 8,
			borderColor: 'silver',
			borderRadius: 3,
			positioner: function (w, h, point) {
				return { x: point.plotX - w / 2, y: point.plotY - h };
			}
		},
		plotOptions: {
			series: {
				animation: false,
				lineWidth: 1,
				shadow: false,
				states: {
					hover: {
						lineWidth: 1
					}
				},
				marker: {
					radius: 1,
					states: {
						hover: {
							radius: 2
						}
					}
				},
				fillOpacity: 0.25
			},
			column: {
				negativeColor: '#910000',
				borderColor: 'silver'
			}
		},

		series: [{
			data: []
		}]
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		let obj = {
			name: '',
			data: []
		}
		data.forEach(d => {
			obj.name = d.name
			obj.data.push(parseInt(d.value))
		})
		return obj;
	}
	componentDidMount() {
		this.setData(this.props.data);
	}
	setData(data = []) {
		const { state } = this;
		const { formatData } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options.series = data;
		this.setState(state);
	}
	render() {
		const { state } = this;
		return (
			<ReactHighcharts ref={this.chart} options={state.options} />
		)
	}
}

class HeatMapHighChart extends Charts {
	getPointCategoryName = (point, dimension) => {
		const series = point.series;
		const isY = dimension === 'y';
		const axis = series[isY ? 'yAxis' : 'xAxis'];
		return axis.categories[point[isY ? 'y' : 'x']];
	}
	options = {
		chart: {
			type: this.props.type || 'heatmap',
			marginTop: 40,
			marginBottom: 80,
			plotBorderWidth: 1
		},
		xAxis: {
			categories: [],
			title: {
				text: this.props.xAxisText || ''
			},
			crosshair: false
		},
		yAxis: {
			categories: [],
			allowDecimals: false,
			title: {
				text: this.props.yAxisText || ''
			}
		},
		series: [{
			name: '',
			data: [],
			dataLabels: {
				enabled: true,
				color: '#000000'
			}
		}],
		accessibility: {
			point: {
				descriptionFormatter: (point) => {
					let ix = point.index + 1;
					let xName = this.getPointCategoryName(point, 'x');
					let yName = this.getPointCategoryName(point, 'y');
					let val = point.value;
					return ix + '. ' + xName + ' sales ' + yName + ', ' + val + '.';
				}
			}
		},
		colorAxis: {
			min: 0,
			minColor: '#FFFFFF',
			maxColor: Highcharts.getOptions().colors[0]
		},
		legend: {
			align: 'right',
			layout: 'vertical',
			margin: 0,
			verticalAlign: 'top',
			y: 25,
			symbolHeight: 280
		},
		tooltip: {
			headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
			pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
				'<td style="padding:0"> <b>{point.y:.1f}</b></td></tr>',
			footerFormat: '</table>',
			shared: false,
			useHTML: true
		},
		plotOptions: {
			column: {
				pointPadding: 0.2,
				borderWidth: 0,
				groupPadding: 0
			}
		},
		exporting: {
			url: null,
			enabled: false,
			sourceWidth: 800,
			sourceHeight: 450,
			chartOptions: {
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true
						}
					}
				}
			},
			fallbackToExportServer: false
		},
		responsive: {
			rules: [{
				condition: {
					maxWidth: 500
				},
				chartOptions: {
					yAxis: {
						labels: {
							formatter: function () {
								return this.value.charAt(0);
							}
						}
					}
				}
			}]
		}
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		let obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			obj.data.push({
				//color: this.colors[Math.floor(Math.random() * this.colors.length)],
				y: parseInt(d.value)
			})
		})
		return obj;
	}
	setData(data = []) {
		const { state } = this;
		const { formatData } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		let xAxisPointCategoryData = data.xAxisCategories;
		data.xAxisCategories = data.xAxisCategories.map((x)=>{
			return Utils.smartTrim(x, 10);
		});
		state.options.xAxis.categories = data.xAxisCategories;
		state.options.yAxis.categories = data.yAxisCategories;
		state.options.xAxis.pointCategoryData = xAxisPointCategoryData;
		state.options.series[0].data = data.data;
		this.setState(state);
	}
	render() {
		const { state } = this;
		return (
			<Loader promiseData={this.props.data} loaderContent={getSkeleton('SINGLE_FAT_LOADER2')}>
				<ReactHighcharts ref={this.chart} options={state.options} />
			</Loader>
		)
	}
}

class StackedHighBarChart extends Charts{
	options = {
		chart: {
	        type: this.props.type || 'column'
	    },
	    xAxis: {
	        categories: [],
	        title: {
	            text: this.props.xAxisText || ''
	        },
	        crosshair: false
	    },
	    yAxis: {
	        //min: 0,
	        allowDecimals: false,
	        title: {
	            text: this.props.yAxisText || ''
	        }
	    },
	    series: [{
	        name: '',
	        data: []
	    }],
	    legend: {
	    	enabled: false
	    },
	    plotOptions: {
	        column: {
	            pointPadding: 0.2,
	            borderWidth: 0,
	            groupPadding: 0
	        }
	    }
	}
	state={
		options: this.getMergeOptions()
	}
	getData(data=[]) {
		let obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			obj.data.push({
				//color: this.colors[Math.floor(Math.random() * this.colors.length)],
				y: parseInt(d.value)
			})
		})
		return obj;
	}
	setData(data = []) {
		const {state} = this;
		const {formatData} = this.props;
		data = formatData ? formatData(data) : this.getData(data);
    state.options = {...state.options, ...{chartOptions: this.props.chartOptions}};
		state.options.xAxis.categories = data.categories;
		state.options.series = data.data;
		this.setState(state);
	}
	render() {
		const {state} = this;
		const {containerProps={}} = this.props;
		return (
			<Loader promiseData={this.props.data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
				<ReactHighcharts ref={ref => this.chart = ref} options={state.options} containerProps={containerProps} />
			</Loader>
		)
	}
}


class AreaSplineHighcharts extends Charts {
	options = {
		chart: {
				type: this.props.type || 'areaspline',
				height : this.props.height || "500px",
	    },
	    xAxis: {
	        title: {
	            text: this.props.xAxisText || ''
			},
		},
	    yAxis: {
	        //min: 0,
	        allowDecimals: false,
	        title: {
	            text: this.props.yAxisText || ''
			},
			labels: {
				formatter: function () {
					return this.value;
				}
			}
	    },
		legend: {
			layout: 'vertical',
			align: 'left',
			verticalAlign: 'top',
			x: 150,
			y: 100,
			floating: true,
			borderWidth: 1,
			backgroundColor:
				Highcharts.defaultOptions.legend.backgroundColor || '#FFFFFF'
		},
		series: [{
			name : this.props.seriesName || '',
			data : [],
		}],
		plotOptions: this.props.plotOptions || {},
	    tooltip:     {
			headerFormat: '{point.x}<br />',
			pointFormat: '{point.x}: {point.y:.0f}',
			shared: true,
		  },  
	}
	state={
		options: this.getMergeOptions()
	}
	getData(data=[]) {
		let obj = {
			categories: data.categories && data.categories,
			data: data.data
		}
		return obj;
	}
	setData(data = []) {
		const {state} = this;
		const {formatData, formatDataForSpline} = this.props;
		if(formatDataForSpline) {
			state.options.series = formatDataForSpline(data);
			this.setState(state);
			return;
		}
		data = formatData ? formatData(data) : this.getData(data);
		state.options = {...state.options, ...{chartOptions: this.props.chartOptions}};
		state.options.xAxis.categories = data.categories;
		state.options.series[0].data = data.data
		this.setState(state);
	}
	render() {
		const {state} = this;
		const {data, containerProps={}} = this.props;
		return (
			<Loader promiseData={data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
				<ReactHighcharts ref={ref => this.chart = ref} options={state.options} containerProps={containerProps} />
			</Loader>
		)
	}
}

class LineHighcharts extends Charts {
	options = {
		chart: {
	        type: this.props.type || 'line',
			height : this.props.height || "500px",
	    },
	    xAxis: {
	        title: {
	            text: this.props.xAxisText || ''
			},
		},
	    yAxis: {
	        //min: 0,
	        allowDecimals: false,
	        title: {
	            text: this.props.yAxisText || ''
			},
			labels: {
				formatter: function () {
					return this.value;
				}
			}
	    },
		legend: {
			layout: 'vertical',
			align: 'right',
			verticalAlign: 'middle'
		},
		series: [{
			name : this.props.seriesName || '',
			data : []
		}],
		plotOptions: this.props.plotOptions || {},
	    tooltip:     {
			headerFormat: '{series.name}<br />',
			pointFormat: 'Total Count on Day {point.x:.0f}: {point.y:.0f}',
			crosshairs: [true],
		  },  
	}
	state={
		options: this.getMergeOptions()
	}
	getData(data=[]) {
		let obj = {
			categories: [data.categories && data.categories],
			data: data
		}
		return obj;
	}
	setData(data = []) {
		const {state} = this;
		const {formatData} = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options = {...state.options, ...{chartOptions: this.props.chartOptions}};
		state.options.xAxis.categories = data.categories;
		state.options.series[0].data = data.data
		this.setState(state);
	}
	render() {
		const {state} = this;
		const {data, containerProps={}} = this.props;
		return (
			<Loader promiseData={data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
				<ReactHighcharts ref={ref => this.chart = ref} options={state.options} containerProps={containerProps} />
			</Loader>
		)
	}
}

class WordCloudChart extends Charts {
	options = {
		chart: {
			type: 'wordcloud'
		},
		accessibility: {
			screenReaderSection: {
				beforeChartFormat: '<h5>{chartTitle}</h5>' +
					'<div>{chartSubtitle}</div>' +
					'<div>{chartLongdesc}</div>' +
					'<div>{viewTableButton}</div>'
			}
		},
		series: [{
			type: 'wordcloud',
			data: [],
			name: 'Occurrences'
		}],
		title: {
			text: this.props.title || '',
			align: 'left'
		},
		tooltip: {
			headerFormat: '<span style="font-size: 16px"><b>{point.key}</b></span><br>'
		}
	}
	state = {
		options: this.getMergeOptions()
	}
	getData(data = []) {
		return data.map(d => {
			return ({
				name: d.name,
				weight: parseInt(d.value)
			})
		});
	}

	setData(data = []) {
		const { state } = this;
		const { formatData } = this.props;
		data = formatData ? formatData(data) : this.getData(data);
		state.options.series[0].data = data;
		this.setState(state);
	}

	render() {
		const { state } = this;
		const { data, containerProps = {} } = this.props;
		return (
			<Loader promiseData={data} loaderContent={getSkeleton('SINGLE_FAT_LOADER')}>
				<ReactHighcharts ref={this.chart} options={state.options} containerProps={containerProps} />
			</Loader>
		)
	}
}


export {
    PieHighcharts, 
    BarHighcharts, 
    MultibarHighcharts, 
    HeatMapHighChart,
    SparklinesChart,
	StackedHighBarChart,
	AreaSplineHighcharts,
	LineHighcharts,
	WordCloudChart
}

export default Charts;