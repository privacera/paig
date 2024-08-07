import React, { Component } from 'react';
import { observer } from 'mobx-react';

import { Box, Paper } from '@material-ui/core';


import hashHistory from 'common-ui/routers/history';
import { DATE_UNITS_GAP } from 'utils/globals';
import { BarHighcharts } from 'common-ui/components/charts';

@observer
class UserByApplicationChart extends Component {
	formatBarGraphDataForField = (data = []) => {
		const obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			const o = { y: parseInt(d.count) };
			obj.data.push(o)
		});
		return obj;
	}
	render() {
		const { options, title } = this.props;
		const { cUserByApplication } = options;
		const chartOptions = {
			chart: {
				type: "bar",
				spacing: [10, 25, 10, 25],
				height: 852
			},
			colors: ["#6FF17C"],
			plotOptions: {
				bar: {
					dataLabels: {
						enabled: true,
						formatter: function () {
							if (typeof this.y === 'number' && this.y > 0) {
								return this.y;
							}
						}
					},
					groupPadding: 1,
					pointWidth: 20,
					events: {
						legendItemClick: function (e) {
							e.preventDefault();
						}
					}
				}
			},
			xAxis: {
				gridLineWidth: 1,
				lineWidth: 1
			},
			yAxis: {
				title: "",
				gridLineWidth: 1,
				lineWidth: 1
			},
			tooltip: {
				valueSuffix: ' counts'
			},
			legend: {
				layout: 'vertical',
				align: 'right',
				verticalAlign: 'top',
				x: 0,
				y: 0,
				floating: true
			},
			title: {
				text: title,
				align: 'left',
				style: {
					fontSize: '18px',
					fontWeight: '500',
					fontFamily: 'Roboto'
				}		
			},
			series: [{
				name: 'Counts',
				data: []
			}],
			exporting: {
				url: null,
				enabled: false,
				sourceWidth: 700,
				sourceHeight: 400,
				chartOptions: {
					chart: {
						marginTop: 50
					},
					legend: {
						itemStyle: {
							fontSize: '14px',
							textOverflow: null
						}
					},
					plotOptions: {
						series: {
							dataLabels: {
								enabled: true
							}
						},
						xAxis: {
							labels: {
								style: {
									fontSize: '14px'
								}
							}
						},
						yAxis: {
							labels: {
								style: {
									fontSize: '14px'
								}
							}
						}
					}
				},
				fallbackToExportServer: false
			}
		}
		return (
			<Paper data-track-id="users-by-applications">
				<Box p={2}>
					<BarHighcharts
						ref={ref => this.userByAppChart = ref}
						chartOptions={chartOptions}
						data={cUserByApplication}
						formatData={(data) => this.formatBarGraphDataForField(data)}
						xAxisText=""
						yAxisText=""
					/>
				</Box>
			</Paper>
		)
	}
}

@observer
class TopUsersChart extends Component {
	formatBarGraphDataForField = (data = []) => {
		const obj = {
			categories: [],
			data: []
		}
		data.forEach(d => {
			obj.categories.push(d.name);
			const o = { y: parseInt(d.count) };
			obj.data.push(o)
		});
		return obj;
	}

	handleNavigation = () => {
		hashHistory.push(`/audits_security`);
	}

	render() {
		const { options, title } = this.props;
		const { cTopUsers } = options;
		const chartOptions = {
			chart: {
				type: "column",
				spacing: [10, 25, 10, 25],
				height: 400
			},
			colors: ["#B2D4F4"],
			plotOptions: {
				column: {
					dataLabels: {
						enabled: true,
						formatter: function () {
							if (typeof this.y === 'number' && this.y > 0) {
								return this.y;
							}
						}
					}
				}
			},
			xAxis: {
				title: "",
				gridLineWidth: 1,
				lineWidth: 1,
				labels: {
					rotation: -45
				}
			},
			yAxis: {
				title: "",
				gridLineWidth: 1,
				lineWidth: 1
			},
			title: {
				text: title,
				align: 'left',
				style: {
					fontSize: '18px',
					fontWeight: '500',
					fontFamily: 'Roboto'				
				}
			},
			series: [{
				data: [],
				pointWidth: 20
			}],
			exporting: {
				url: null,
				enabled: false,
				sourceWidth: 700,
				sourceHeight: 400,
				chartOptions: {
					chart: {
						marginTop: 50
					},
					plotOptions: {
						series: {
							dataLabels: {
								enabled: true
							}
						}
					}
				},
				fallbackToExportServer: false
			}
		}
		return (
			<Paper data-track-id="top-users">
				<Box p={2} className='p-relative'>
					{/*
						!f.isLoading(cTopUsers) && (
							<Link style={{ position: "absolute", right: "8px", zIndex: 1 }} onClick={this.handleNavigation}>
								View all (audits) <LaunchIcon fontSize="small" />
							</Link>
						)
					*/}
					<BarHighcharts
						ref={ref => this.topUsersChartRef = ref}
						chartOptions={chartOptions}
						data={cTopUsers}
						formatData={(data) => this.formatBarGraphDataForField(data)}
						xAxisText=""
						yAxisText=""
					/>
				</Box>
			</Paper>
		)
	}
}

@observer
class ActivityTrends extends Component {
	formatBarGraphDataForField = (data = []) => {
		const { options } = this.props;
		const { _vState, moment } = options;
		const obj = {
			categories: [],
			data: []
		}
		const gapObj = DATE_UNITS_GAP[_vState.gap?.toUpperCase()];
		data = _.sortBy(data, 'name');
		data.forEach(d => {
			let name = d.name;
			if (gapObj) {
				const date = moment(d.name);
				name = date.format(gapObj.format);
			}
			obj.categories.push(name);
			const o = { y: parseInt(d.count) };
			obj.data.push(o)
		});
		return obj;
	}

	render() {
		const { options, title } = this.props;
		const { cActivityTrends } = options;
		const chartOptions = {
			chart: {
				type: "column",
				spacing: [10, 25, 10, 25],
				height: 400
			},
			colors: ["#2D9CDB"],
			plotOptions: {
				column: {
					dataLabels: {
						enabled: true,
						formatter: function () {
							if (typeof this.y === 'number' && this.y > 0) {
								return this.y;
							}
						}
					}
				}
			},
			xAxis: {
				title: "",
				gridLineWidth: 1,
				lineWidth: 1,
				labels: {
					rotation: -45
				}
			},
			yAxis: {
				title: "",
				gridLineWidth: 1,
				lineWidth: 1,
			},
			title: {
				text: title,
				align: 'left',
				style: {
					fontSize: '18px',
					fontWeight: '500',
					fontFamily: 'Roboto'				
				}
			},
			series: [{
				name: 'Usage',
				data: [],
				pointWidth: 20
			}],
			legend: {
				layout: 'vertical',
				align: 'right',
				verticalAlign: 'top',
				x: 0,
				y: 0,
				floating: true
			},
			exporting: {
				url: null,
				enabled: false,
				sourceWidth: 700,
				sourceHeight: 400,
				chartOptions: {
					chart: {
						marginTop: 50
					},
					legend: {
						itemStyle: {
							fontSize: '14px',
							textOverflow: null
						}
					},
					plotOptions: {
						series: {
							dataLabels: {
								enabled: true
							}
						}
					}
				},
				fallbackToExportServer: false
			}
		}
		return (
			<Paper className="m-t-md" data-track-id="activity-trend">
				<Box p={2}>
					<BarHighcharts
						ref={ref => this.activityTrendsChartRef = ref}
						chartOptions={chartOptions}
						data={cActivityTrends}
						formatData={(data) => this.formatBarGraphDataForField(data)}
						xAxisText=""
						yAxisText=""
					/>
				</Box>
			</Paper>
		)
	}
}

export {
	UserByApplicationChart,
	TopUsersChart,
	ActivityTrends
};