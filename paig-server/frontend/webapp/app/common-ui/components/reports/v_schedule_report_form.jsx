/* library imports */
import React, {Component} from 'react';
import {observer} from 'mobx-react';
import {transaction} from 'mobx';

// Material Imports
import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import { withStyles } from '@material-ui/styles';
import TextField from '@material-ui/core/TextField';
import DateRangeIcon from '@material-ui/icons/DateRange';
import InputAdornment from '@material-ui/core/InputAdornment';

/* other project imports */
import {ENUMS} from 'utils/globals';
import {SCHEDULE_TYPE, STATUS, DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {Checkbox, Toggle as ToggleButton} from 'common-ui/components/filters';
import {FormHorizontal, FormGroupInput, FormGroupSelect2, ValidationAsterisk} from 'common-ui/components/form_fields';
import DateRangePicker from 'common-ui/lib/daterangepicker';
import {Utils} from 'common-ui/utils/utils';

const moment = Utils.dateUtil.momentInstance();

const styles = theme => ({
  label: {
    marginRight: '10px'
  },
  labelPlacementStart: {
	marginLeft: '0'
  }
});

@observer
class VScheduleReportForm extends Component {
    state={
    	scheduleSupport: true
	}
	setScheduleSupport(){
		if (this.props.scheduleSupport == undefined) {
			return;
		}
		let scheduleSupport = this.props.scheduleSupport;
		if (typeof scheduleSupport == 'function') {
			scheduleSupport = this.props.scheduleSupport();
		}
		// this.state.scheduleSupport = scheduleSupport;
		this.setState({
			scheduleSupport
		});
	}

  componentDidMount() {
		this.setScheduleSupport();
	}
    getScheduleType() {
    	const {scheduleType} = this.props.form.fields;
    	return scheduleType && scheduleType.value;
    }
    isDaily() {
    	return this.getScheduleType() == SCHEDULE_TYPE.DAILY.value;
    }
    isWeekDay() {
    	return this.getScheduleType() == SCHEDULE_TYPE.WEEKLY.value;
    }
    isMonthly() {
    	return this.getScheduleType() == SCHEDULE_TYPE.MONTHLY.value;
    }
    getDaysForMonths() {
    	const {month} = this.props.form.fields;
    	let days = 31
    	if (month.value) {
    		let allMonthDays = month.value.split(',').map(month => moment((parseInt(month)+1), "M").daysInMonth());
    		days = Math.min(...allMonthDays) || days;
    	}
    	return [...Array(days)].map((a, i) => ({name: i+1, value: i+1}));
    }
    render() {
			const {schedulerName, reportName, description, scheduleType, startTime, day, month, isAll, emailTo, emailMessage, status, scheduleId, scheduleReport} = this.props.form.fields;
			
			const { classes } = this.props;

	    let scheduleFormFields = null;

	    if (scheduleReport.value) {
	    	scheduleFormFields = [];

	    	scheduleFormFields.push(...[
	    		<FormGroupInput
	    			key={1}
	    			required={true}
	    			label={"Scheduler Name"}
	    			placeholder="Scheduler Name"
	    			value={schedulerName.value}
	    			onChange={(e) => schedulerName.value = e.target.value}
	    			data-test="scheduler-name"
	    			errMsg={schedulerName.errorMessage}
	    		/>,
	    		<FormGroupSelect2
			        key={2}
			        required={true}
			        label={"Recurring"}
			        fieldObj={scheduleType}
			        data={[SCHEDULE_TYPE.ONCE, SCHEDULE_TYPE.DAILY, SCHEDULE_TYPE.WEEKLY, SCHEDULE_TYPE.MONTHLY]}
			        // placeholder={'Select Schedule Type'}
			        disableClearable={true}
			        labelKey={'name'}
			        valueKey={'value'}
			        onChange={(value) => {
			          transaction(() => {
			            scheduleType.value = value;
			            day.value = '';
			            month.value = '';
			            isAll.value = false;
			          })
			        }}
			        inputProps={{'data-test': "scheduleType"}}
			    />,
				<Grid item md={12} sm={12} xs={12}>
					<FormLabel>
						Start Time <ValidationAsterisk />
					</FormLabel>
					<DateRangePicker 
						label=""
						startDate={startTime.value ? moment(startTime.value) : ""} 
						// minDate={moment()} 
						ref={ref => this.datepicker = ref} 
						className="date-icon" 
						initialSettings={{
							timePicker: true, 
							timePicker24Hour:true, 
							singleDatePicker: true,
							minDate:moment() 
						}}
						onApply={(event, picker) => {
							startTime.value = picker.startDate;
						}}
					>
						<TextField
							data-test={'date-range-picker'}
							label=""
							readOnly
							variant="outlined"
							value={startTime.value ? moment(startTime.value).format(DATE_TIME_FORMATS.DATE_FORMAT) : ''}
							InputProps={{
								endAdornment:(
									<InputAdornment position="end">
										<DateRangeIcon />
									</InputAdornment>
								)
							}}
							fullWidth
						/>
						{/* <div className="date-icon">
							<TodayIcon fontSize="small" />
							<input type="text" className="dashboard-datepicker" name="daterange" readOnly data-test={'date-range-picker'}
									value={startTime.value ? moment(startTime.value).format(DATE_TIME_FORMATS.DATE_FORMAT) : ''} onChange={(e) => {}}
							/>
						</div> */}
					</DateRangePicker>
					</Grid>
	    	])

	    	if (this.isWeekDay()) {
				scheduleFormFields.push(
					<FormGroupSelect2
						key={4}
						required={true}
						label={"Week Days"}
						fieldObj={day}
						data={moment.weekdays().map((d, i) => ({name: d, value: i+1}))}
						placeholder={'Select Weekdays'}
						labelKey={'name'}
						multiple={true}
						valueKey={'value'}
						value={isAll.value ? moment.weekdays().map((d, i) => (i+1)).join(',') : day.value}
						//disabled={isAll.value.toString() == "true"}
						onChange={(value) => {
						  transaction(() => {
							day.value = value;
							if (value.split(',').length < 7) {
								isAll.value = false;
							}
						  })
						}}
						inputProps={{'data-test': "day"}}
						inputColAttr={{ sm: 9, md: 10 }}
					>
					</FormGroupSelect2>
				)
				scheduleFormFields.push(
				<Checkbox checked={isAll.value} containerClassName="schedule-checkbox" labelText="All" containerProps={{sm: 3, md: 2}} onClick={e => {
					let isChecked = e.target.checked;
					day.value = isChecked ? moment.weekdays().map((d, i) => (i+1)).join(',') : '';
					isAll.value = isChecked;
					if (!isChecked) {
						day.value = "";
					}
				}} />)
	    	}

	    	if (this.isMonthly()) {
	    		scheduleFormFields.push(...[
	    			<FormGroupSelect2
	    				key={5}
				        required={true}
				        label={"Months"}
				        fieldObj={month}
				        data={moment.months().map((d, i) => ({name: d, value: i}))}
				        placeholder={'Select Months'}
				        labelKey={'name'}
				        multiple={true}
				        valueKey={'value'}
				        value={isAll.value ? moment.months().map((d, i) => i).join(',') : month.value}
				        //disabled={isAll.value.toString() == "true"}
				        onChange={(value) => {
				          transaction(() => {
				            month.value = value;
				            if (value.split(',').length < 12) {
				            	isAll.value = false;
				            }
				            if(day.value > 28) {
				            	day.value = '';
				            }
				          })
				        }}
				        inputProps={{'data-test': "month"}}
						inputColAttr={{ sm: 9, md: 10 }}
				    >
				    </FormGroupSelect2>,
					<Checkbox key={10} checked={isAll.value} containerClassName="schedule-checkbox" labelText="All" containerProps={{sm: 3, md: 2}} onClick={e => {
						let isChecked = e.target.checked;
						transaction(() => {
							month.value = isChecked ? moment.months().map((d, i) => i).join(',') : '';
							isAll.value = isChecked;
							if (isChecked) {
								if(day.value > 28) {
									day.value = '';
								}
							} else {
								month.value = '';
							}
						})
					}} />,
				    <FormGroupSelect2
				    	key={6}
				        required={true}
				        label={"Date"}
				        fieldObj={day}
				        data={this.getDaysForMonths()}
				        placeholder={'Select Date'}
				        labelKey={'name'}
				        multiple={false}
				        valueKey={'value'}
				        onChange={(value) => {
				          transaction(() => {
				            day.value = value;
				          })
				        }}
				        inputProps={{'data-test': "month"}}
				    />
	    		])
	    	}

	    	scheduleFormFields.push(...[
	    		<FormGroupInput
	    			key={7}
						required={true}
						//textOnly={!!id.value}
						label={"Email To"}
						value={emailTo.value}
						onChange={(e) => emailTo.value = e.target.value.trim()}
						//onBlur={(e) => checkUniqueUser('email', e.target.value)}
						data-test="email-id"
						errMsg={emailTo.errorMessage}
					/>,
					<FormGroupInput
							key={8}
							fieldObj={emailMessage}
							label={"Email Message"}
							as="textarea"
							placeholder=""
							maxLength={4000}
							data-test="emailMessage"
					/>,
					<Grid container spacing={3} className="enable-switchbox" key={9}>
						{/* <Grid item sm={12} md={3} component={FormLabel}>Schedule Status</Grid>
						<Grid item sm={12} md={8}>
							<div className="pull-left m-r-sm m-t-xs">
								<Switch
									checked={status.value == STATUS.enabled.value ? 'checked' : ''}
									onChange={e => status.value = e.target.checked ? STATUS.enabled.value : STATUS.disabled.value}
								/>
							</div>
						</Grid> */}
						<Grid item xs={12}>
							<ToggleButton 
								containerClassName="noClass"  
								label="Schedule Status" 
								checked={status.value == STATUS.enabled.value ? 'checked' : ''}
								onChange={e => status.value = e.target.checked ? STATUS.enabled.value : STATUS.disabled.value} 
								labelPlacement="start"
							/>
						</Grid>
					</Grid>
	    	])
	    }

	    return (
	    	<FormHorizontal>
		        <FormGroupInput
	        		required={true}
	        		label={"Report Name"}
	        		placeholder="Report Name"
	        		value={reportName.value}
	        		onChange={(e) => reportName.value = e.target.value}
	        		maxLength={50}
	        		data-test="report-name"
	        		errMsg={reportName.errorMessage}
	        	/>
	        	<FormGroupInput
	        		fieldObj={description}
	        		label={"Description"}
	        		as="textarea"
	        		placeholder="Report Description"
	        		maxLength={4000}
	        		data-test="desc"
	        	/>
	        	{
	        		this.state.scheduleSupport && !scheduleId.value &&
						<Grid item xs={12}>
							<FormControlLabel
								// value="start"
								control={<Checkbox containerClassName='checkbox-container inline-block' checked={scheduleReport.value} onClick={e => scheduleReport.value = e.target.checked} />}
								label="Schedule Report"
								labelPlacement="start"
								classes={{label: classes.label, labelPlacementStart: classes.labelPlacementStart}}
							/>
						</Grid>
	        	}
	        	{scheduleFormFields}
	        </FormHorizontal>
	    );
    }
}

const schedule_report_form_def = {
	id: {},
	reportName: {
		defaultValue: "",
	    validators: {
	      errorMessage: "Required!",
	      fn: (field, fields) => {
	      	if (!field.value || !field.value.trim()) {
	      		return false;
	      	}
	      	return true;
			// return Utils.characterValidation(field);
	      }
	    }
	},
	description: {},
	schedulerName: {
		defaultValue: "",
	    validators: {
	      errorMessage: "Required!",
	      fn: (field, fields) => {
	        if (fields.scheduleReport.value) {
	        	return Utils.characterValidation(field);
	        }
	        return true;
	      }
	    }
	},
	scheduleType: {
		defaultValue: SCHEDULE_TYPE.WEEKLY.value
	},
	startTime: {
		defaultValue: moment().add(1, 'hours'),
    	validators: {
	        errorMessage: 'Required!',
	        fn: (field, fields) => {
	        	return true;
	        }
	    }
	},
	day: {
		validators: {
	        errorMessage: 'Required!',
	        fn: (field, fields) => {
	        	if (fields.scheduleReport.value && fields.scheduleType.value == SCHEDULE_TYPE.MONTHLY.value && !fields.isAll.value && !field.value) {
		            return false;
	        	}
	        	if (fields.scheduleReport.value && fields.scheduleType.value == SCHEDULE_TYPE.WEEKLY.value && !fields.isAll.value && !field.value) {
		            return false;
	        	}
	        	return true;
	        }
	    }
	},
	month: {
		validators: {
	        errorMessage: 'Required!',
	        fn: (field, fields) => {
	        	if (fields.scheduleReport.value && fields.scheduleType.value == SCHEDULE_TYPE.MONTHLY.value && !fields.isAll.value && !field.value) {
		            return false;
	        	}
	        	return true;
	        }
	    }
	},
	isAll: {
		defaultValue: false
	},
	objectId: {},
	objectClassType: {
		defaultValue: ENUMS.CLASS_TYPE_REPORT_CONFIG
	},
	emailTo: {
		validators: {
	        errorMessage: 'Required!',
	        fn: (field, fields) => {
	        	if (fields.scheduleReport.value && (!field.value || !field.value.trim())) {
		            return false;
	        	}
	        	return true;
	        }
	    }
	},
	emailMessage: {},
	paramJson: {},
	status: {
		defaultValue: STATUS.enabled.value
	},
	scheduleId: {},
	scheduleReport: {
		defaultValue: STATUS.disabled.booleanValue
	}
}

export default withStyles(styles)(VScheduleReportForm);
export {
	schedule_report_form_def
}