import React, {Component, Fragment} from 'react';
import {observable, action} from 'mobx';
import {observer} from 'mobx-react';
import clsx from 'clsx';
import { isEmpty } from 'lodash';

import { withStyles } from '@material-ui/core/styles';
import styled from 'styled-components';
import Grid from '@material-ui/core/Grid';
import { Box } from '@material-ui/core';
import TextField from '@material-ui/core/TextField';
import FormGroup from '@material-ui/core/FormGroup';
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';
import InputAdornment from '@material-ui/core/InputAdornment';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MUICheckbox from '@material-ui/core/Checkbox';
import Radio from '@material-ui/core/Radio';
import MUISwitch from '@material-ui/core/Switch';
import FormLabel from '@material-ui/core/FormLabel';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import SearchIcon from '@material-ui/icons/Search';
import ClearIcon from '@material-ui/icons/Clear';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CloseIcon from '@material-ui/icons/Close';

import { SEARCH_TYPE } from 'common-ui/utils/globals';
import stores from 'data/stores/all_stores';
import {Select2} from 'common-ui/components/generic_components';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import FsSelect, {TagChip } from 'common-ui/lib/fs_select/fs_select';
import DateRangePicker from 'common-ui/lib/daterangepicker';
import KeyEvent from 'common-ui/lib/react-structured-filter/keyevent';
import {ValidationMsgField} from 'common-ui/components/form_fields';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';


const searchStyles = theme => ({
    root: {
    },
    dropdown: {
        width: "180px",
        display: 'inline-block',
    },
    searchInput: {
        width: 'calc(100% - 180px)',
        display: 'inline-block'
    }
  })
@observer
class SearchFieldWrap extends Component {

    state = { value: '', searchType: this.props.searchType }
    handleKeyUp = (e) => {
        let value = e.target.value || undefined;
        if (value && this.props.trimValue) {
            value = value.trim();
        }
        this.props.onKeyUp && this.props.onKeyUp(value, e);
        switch ((e.keyCode || e.which)) {
            case KeyEvent.DOM_VK_RETURN:
            case KeyEvent.DOM_VK_ENTER:
                this.props.onEnter && this.props.onEnter(value, e);
                break;
            case KeyEvent.DOM_VK_PASTE:
                e.ctrlKey && this.props.onEnter && this.props.onEnter(value, e);
                break;
        }
    }
    handleOnChange = (e) => {
        let value = e.target.value;
        this.setValue(value);
        this.props.onChange && this.props.onChange(e, value);
    }

    handleSelectChange = (value) => {
        this.setSearchType(value);
        this.props.onSearchTypeSelect && this.props.onSearchTypeSelect(value);
    }

    componentDidMount() {
        this.setValue(this.props.initialValue);
        this.setSearchType(this.props.searchType)
    }

    componentDidUpdate(prevProps){
        if (prevProps.initialValue.trim() !== this.props.initialValue.trim()) {
            this.setValue(this.props.initialValue);
        }
        if (prevProps.searchType !== this.props.searchType && this.props.searchType !== this.state.searchType) {
            this.setSearchType(this.props.searchType);
        }

    }
    handleOnCross = () => {
        this.setValue('');
        this.props.handleClearSearchText && this.props.handleClearSearchText();
    }
    getValue() {
        return this.state.value;
    }
    setValue(value) {
        this.setState({
            value: value
        });
    }
    setSearchType(value) {
        this.setState({ searchType: value });
    }

    clearSearch = () => {
        this.setValue('');
        this.props.onClear && this.props.onClear('');
    }

    render() {
        const {sm, md, lg, colAttr, onKeyUp, onChange, onEnter, initialValue, trimValue, showClearButton , showSearchFilter, onClickSearchInfo, 
            showSearchInfo, clearable, showSearchIcon, searchType, searchFilterOptionList, classes, showOnlyIcon, className,
            searchbarWrapperClass, handleClearSearchText, onClear, customAnchorProps, ...restProps} = this.props;
            const formControlProps = Utils.excludeProps({...restProps}, ['onSearchTypeSelect']);
            const _className = clsx(classes.root, className);
            let showIcon = showSearchIcon || showOnlyIcon;
        return (
            <Grid item sm={sm} md={md} lg={lg} className={_className} {...colAttr}>
                <Fragment>
                    {showSearchFilter && <div className={`${classes.dropdown} height-adjust-filters`}>
                        <FsSelect
                            value={this.state.searchType}
                            data={this.props.searchFilterOptionList}
                            onChange={this.handleSelectChange}
                            multiple={false}
                            disableClearable={true}
                            labelKey="label"
                            valueKey="value"
                            customDropDown={true}
                        />
                    </div>}
                    {
                        <div className={`${showSearchFilter ? classes.searchInput : ''} ${searchbarWrapperClass}`}>
                            <TextField
                                // id="outlined-basic"
                                inputProps={{"data-testid": "input-search-box"}}
                                variant="outlined"
                                value={this.state.value}
                                onKeyUp={this.handleKeyUp} 
                                onChange={this.handleOnChange}
                                fullWidth
                                InputProps={{
                                    startAdornment: (
                                        showIcon && <InputAdornment position="start">
                                            <SearchIcon color="action" fontSize="small" />
                                        </InputAdornment>
                                    ),
                                    endAdornment: <InputAdornment position="end">
                                        {
                                            (showClearButton && this.state.value.trim()) &&
                                            <CustomAnchorBtn
                                                size="small"
                                                tooltipLabel="Clear"
                                                className="clear-searchbar"
                                                onClick={() => this.handleOnCross()}
                                                icon={<ClearIcon />}
                                            />
                                        }
                                        {this.state.value && clearable &&
                                            <CustomAnchorBtn
                                                tooltipLabel="Clear"
                                                color="default"
                                                icon={<CloseIcon fontSize="small" />}
                                                onClick={this.clearSearch}
                                                {...customAnchorProps}
                                            />
                                        }
                                        {
                                            showSearchInfo &&
                                            <CustomAnchorBtn
                                                tooltipLabel="Search Info"
                                                color="primary"
                                                icon={<InfoOutlinedIcon fontSize="inherit" />}
                                                onClick={() => onClickSearchInfo()}
                                                {...customAnchorProps}
                                            />
                                        }
                                    </InputAdornment>
                                  }}
                                {...formControlProps}
                            />
                        </div>
                    }
                </Fragment>
            </Grid>
        )
    }
}
SearchFieldWrap.defaultProps = {
    sm: 10,
    md: null,
    lg: null,
    type: "text",
    "data-test": "searchBox",
    placeholder: "Search",
    colAttr: {},
    trimValue: true,
    initialValue: '',
    searchType: SEARCH_TYPE.PARTIAL_MATCH.value,
    searchFilterOptionList: [{ label: SEARCH_TYPE.PARTIAL_MATCH.label, value: SEARCH_TYPE.PARTIAL_MATCH.value }, { label: SEARCH_TYPE.EXACT_MATCH.label, value: SEARCH_TYPE.EXACT_MATCH.value }],
    showSearchInfo: false,
    clearable: false,
    showSearchIcon: true,
    showOnlyIcon: false,
    searchbarWrapperClass: "",
    customAnchorProps: {}
}

const SearchField = withStyles(searchStyles)(SearchFieldWrap);

@observer
class DateRangePickerComponent extends Component {
    constructor(props) {
        super(props);
        this.datepicker = React.createRef();
        this.setStartingState(props)
    }

    @action
    setStartingState = (props) => {
        const {from, to} = this._vState;
        const {ranges, chosenLabel, disabledWithSwitch} = props;
        this._vState.checkboxChecked = from && to && props.isDateFilterOn ? true : false ;
        this._vState.disabledWithSwitch = disabledWithSwitch ? disabledWithSwitch : ((!from && !to) ? true : false);
        if (!from && !to && ranges && ranges[chosenLabel]) {
            this._vState.from = ranges[chosenLabel][0];
            this._vState.to = ranges[chosenLabel][1];
        }
    }
    @observable _vState = {
        from: this.props.isDateFilterOn && this.props.daterange[0],
        to: this.props.isDateFilterOn && this.props.daterange[1],
        chosenLabel: this.props.chosenLabel,
        checkboxChecked: true,
        disabledWithSwitch: false,
        selectedTimeValue : this.props.selectedTimeValue ? this.props.selectedTimeValue: this.props.timeWiseFilterOptionList[1].timeFilterType
    }
    @action
    _changeDate = (picker) => {
        this._vState.chosenLabel = picker.chosenLabel;
        this._vState.from = picker.startDate;
        this._vState.to = picker.endDate;
    }
    _handleDateChange = (event, picker) => {
        try {
            let range = this.props.ranges[picker.chosenLabel];
            if (range) {
                picker.startDate = range[0];
                picker.endDate = range[1];
                let p = this.datepicker.$picker.data('daterangepicker')
                p.ranges[picker.chosenLabel][0] = range[0];
                p.ranges[picker.chosenLabel][1] = range[1];
            }
        } catch(e) {}
        if(this.props.showTimeFilter){
          picker.timeFilterType = this._vState.selectedTimeValue;
        }
        this._changeDate(picker);
        this.props.handleEvent(event, picker,this._vState);
    }
    setDate = (picker, silent=false) => {
        if (!picker) {
            return;
        }

        if (this.datepicker) {
            this.datepicker.setStartDate(picker.startDate);
            this.datepicker.setEndDate(picker.endDate);
        }

        if (silent) {
            return this._changeDate(picker)
        }
        return this._handleDateChange(null, picker);
    }
    _formatedValue = () => {
        const {formatValue, dateFormat} = this.props;
        const {_vState} = this;
        if (_vState.disabledWithSwitch && !_vState.checkboxChecked) {
          return 'Date Filter Not Applied'
        }
        if (formatValue && typeof formatValue == "function") {
            return formatValue(_vState);
        }
        if (!_vState.from || !_vState.to || !_vState.checkboxChecked) {
          return 'Date Filter Not Applied'
        }
        return `${_vState.from.format(dateFormat)} - ${_vState.to.format(dateFormat)}`;
    }
    handleCheckboxChange = (e)=> {
      const {ranges, chosenLabel} = this.props;
      const {from, to} = this._vState;
      if(e.currentTarget.checked) {
        this._vState.disabledWithSwitch = false;
        this._vState.checkboxChecked = true;
        if(chosenLabel == "Custom Range" && (!from && !to)){
          this._vState.from = ranges[Object.keys(ranges)[0]][0];
          this._vState.to = ranges[Object.keys(ranges)[0]][1];
          this._vState.chosenLabel = Object.keys(ranges)[0]
        }
        this.props.handleEvent(null, {
            startDate: this._vState.from,
            endDate: this._vState.to,
            chosenLabel: this._vState.chosenLabel,
            timeFilterType: undefined
        }, this._vState);
      } else {
        this._vState.disabledWithSwitch = true;
        this._vState.checkboxChecked = false;
        this.props.handleEvent(null, {
            startDate: undefined,
            endDate: undefined,
            chosenLabel: this._vState.chosenLabel,
            timeFilterType: this._vState.selectedTimeValue
        }, this._vState);
      }
    }
    handleFilterChange = (value)=>{
      const {ranges, chosenLabel} = this.props;
      const {from, to} = this._vState;
      this._vState.selectedTimeValue = value;
      switch(value) {
          case 'none':
          this._vState.disabledWithSwitch = true;
          this._vState.checkboxChecked = false;
          this.props.handleEvent(null, {startDate:undefined,endDate:undefined,chosenLabel:this._vState.chosenLabel,timeFilterType:undefined},this._vState);
        break;
        default:
          this._vState.disabledWithSwitch = false;
          this._vState.checkboxChecked = true;
          if(chosenLabel == "Custom Range" && (!from && !to)){
            this._vState.from = ranges[Object.keys(ranges)[0]][0];
            this._vState.to = ranges[Object.keys(ranges)[0]][1];
            this._vState.chosenLabel = Object.keys(ranges)[0]
          }
          this.props.handleEvent(null, {startDate:this._vState.from,endDate:this._vState.to,chosenLabel:this._vState.chosenLabel,timeFilterType:this._vState.selectedTimeValue} , this._vState);
        }
    }

    setSwitchCheckbox(value) {
        this._vState.checkboxChecked = value
    }

    renderOption = (option, state) => {
        let label = option["label"];
        if (typeof label != 'string') {
          return label;
        }
        return <span className="word-break-dropdown">{label}</span>;
    }
    
    render() {
        const {_vState, _handleDateChange} = this;
        const {disabledWithSwitch, selectedTimeValue} = _vState;
        const {ranges, colAttr, dateRangePickerAttr, formControlAttr,disabled,showSwitchBox,showTimeFilter} = this.props;
                
        let formControl = (
            <Box flexGrow={2}>
                <TextField
                    inputProps={{"data-testid": "date-range-picker"}}
                    className={`pointer ${(disabled || !showSwitchBox || showTimeFilter) ? 'date-picker' : ''}`}
                    name="daterange"
                    fullWidth
                    readOnly
                    data-test="date-range-picker"
                    data-track-id="date-range-picker"
                    value={this._formatedValue()}
                    onChange={(e) => {}}
                    disabled={disabled || disabledWithSwitch}
                    variant="outlined"
                    size="small"
                    {...formControlAttr}
                />
            </Box>
        )
        return (
            <Grid item  {...colAttr} className="date-picker-custom">
                <Box display="flex">
                    {(disabled || !showSwitchBox || showTimeFilter) ? null :
                        <MUISwitch
                            inputProps={{"data-testid": "input-date-picker-switch"}}
                            data-testid="date-picker-switch"
                            data-track-id="date-range-picker-switch"
                            className="date-picker-switch"
                            checked={_vState.checkboxChecked}
                            onChange={this.handleCheckboxChange}
                            color="primary"
                        />
                    }
                    {
                        showTimeFilter ?
                            <div className="input-group table-group-dropdown height-adjust-filters date-picker">
                                <FsSelect
                                    renderOption={this.renderOption}
                                    value={selectedTimeValue}
                                    data={this.props.timeWiseFilterOptionList}
                                    onChange={(value) => this.handleFilterChange(value)}
                                    multiple={false}
                                    disableClearable={true}
                                    labelKey="label"
                                    valueKey="timeFilterType"
                                    customDropDown={true}
                                    data-track-id="date-range-picker-time-filter"
                                />
                            </div>
                        : null
                    }
                    {
                        (disabled || disabledWithSwitch) ? formControl :
                        <DateRangePicker 
                            ref={ref => this.datepicker = ref}
                            onApply={(event, picker) => _handleDateChange(event, picker)}
                            initialSettings={{
                                startDate: _vState.from,
                                endDate: _vState.to,
                                opens: "left",
                                ranges,
                                ...dateRangePickerAttr
                            }}
                        >
                            {formControl}
                        </DateRangePicker>
                    }
                    <div className="input-group-btn">
                        <div className="date-info-button" data-testid="date-picker-label" data-track-id="date-range-picker-chosen-label">
                            {_vState.chosenLabel}
                        </div>
                    </div>
                </Box>
            </Grid>
        )
    }
}
DateRangePickerComponent.defaultProps = {
    colAttr: {
        sm: 12,
        md: 4
    },
    formatValue: null,
    daterange: Utils.dateUtil.getLast7DaysRange(),
    ranges: Utils.dateRangePickerRange(),
    chosenLabel: 'Last 7 Days',
    dateRangePickerAttr: {},
    formControlAttr: {},
    dateFormat: "L",
    disabled: false,
    checkboxChecked: true,
    disabledWithSwitch: false,
    showSwitchBox:true,
    showTimeFilter:false,
    isDateFilterOn : true,
    timeWiseFilterOptionList: [{
        label: 'Resource Create Time',
        timeFilterType: 'createTime'
    }, {
        label: 'Classified Time',
        timeFilterType: 'updateTime'
    }, {
        label: 'Turn Off',
        timeFilterType: 'none'
    }],
    handleEvent: () => {}
}

const Switch = observer(function Switch({label='', ...props}) {
    let {pullRight, switchClass, labelClass, formControlAttr={}, ...rest} = props;

    return (
        <FormControlLabel
            control={<MUISwitch name={label} color="primary" {...rest} />}
            label={label}
            {...formControlAttr}
        />
    )
})
Switch.defaultProps = {
    labelClass:'',
    switchClass: '',
    checked: '',
    onChange: () => {},
    pullRight: false
}

const CustomClassNameSwitch = observer(function Switch({pullRight, contentClassName, checked, onChange, label, ...rest}) {
    let randomKey = Math.random()

    return (
        <div className={`switch ${contentClassName ? contentClassName : ''} ${pullRight ? 'pull-right' : ''}`}>
            <FormControlLabel   
                control={   
                    <MUISwitch  
                        checked={checked} 
                        onChange={onChange}   
                        color={'primary'}   
                    />  
                }   
                label={label}
            />
        </div>
    )
})
CustomClassNameSwitch.defaultProps = {
    checked: '',
    onChange: () => {},
    pullRight: false
}

const ICheckRadio = ({label, ...props}) => {
    return (
        <FormControlLabel
            control={<Radio name={label} {...props} />}
            label={label}
        />
    )
}
ICheckRadio.defaultProps = {
    label: '',
    checked: '',
    color: 'primary'
}

@observer
class InputGroupSelect2 extends Component {
    render () {
        const {data, colAttr, label, children, fieldObj, fieldKey, ...rest} = this.props;
        if (fieldObj && fieldKey) {
            rest.value = fieldObj[fieldKey];
        }
        return (
            <Grid item {...colAttr}>
                {label && <h5>{label}</h5>}
                <FormGroup>
                    <Select2 data={data && f.isPromise(data) ? f.models(data) : data} {...rest} />
                </FormGroup>
                {children}
            </Grid>
        )
    }
}
InputGroupSelect2.defaultProps = {
    colAttr: {
        sm: 6,
        md: 4,
        xs: 12
    },
    value: '',
    placeholder: 'Search...',
    label: '',
    labelKey: 'name',
    valueKey: 'name',
    multiple: true,
    //inputProps: {'data-test': 'application'}
}

const Checkbox = observer(function Checkbox(
    {labelText, children, checked, fields, attr, onChange, containerProps={}, containerClassName, type, ...props}
) {
    let isChecked = checked || false;
    if (checked == null && fields && attr) {
        isChecked = fields[attr] === true;
        if (!onChange) {
            onChange = (e) => {
                fields[attr] = e.target.checked;
            }
        }
    }
    return (
        <FormControlLabel
            control={
                <MUICheckbox
                    {...props}
                    checked={isChecked}
                    onChange={onChange}
                />
            }
            label={labelText}
            className={containerClassName}
            {...containerProps}
        />
    )
})
Checkbox.defaultProps = {
    type: "checkbox",
    "data-test": "checkbox-box",
    className: "",
    labelText: '',
    checked: null,
    onClick: null,
    color: 'primary'
}

@observer
class DropDownFilter extends Component {
    constructor(props) {
        super(props);
        Object.assign(this.properties, props);
    }
    properties = {
        data: f.initCollection(),
        nameUpperCase: false,
        storeName: '',
        storeFunction: '',
        params: {size: 99999999, sort: 'name'},
        modelAttrName: 'name',
        fieldObj: '',
        fieldAtr: '',
        labelKey: 'name',
        valueKey: 'name',
        multiple: true
    };
    componentDidMount() {
        this.reload();
    }
    getStoreFetch() {
        const {storeName, storeFunction, params} = this.properties;
        if (!storeName || !storeFunction) {
            return;
        }
        return stores[storeName][storeFunction]({params});
    }
    reload = () => {
        let store = this.getStoreFetch();
        if (!store) {
            return;
        }
        const {data, modelAttrName} = this.properties;
        store.then((resp) => {
            let {models} = resp;
            if (this.props.nameUpperCase) {
                models = models.map(m => ({
                    name: this.props.nameUpperCase ? (m[modelAttrName] || "").toUpperCase() : (m[modelAttrName] || "")
                })).filter(m => m.name);
            }
            f.resetCollection(data, models);
        });
    }
    render() {
        const {nameUpperCase, storeName, storeFunction, params, modelAttrName, fieldObj, fieldAtr, ...props} = this.properties;
        if (!props.hasOwnProperty('value') && fieldObj && fieldAtr) {
            props.value = fieldObj[fieldAtr];
        }
        return (
            <InputGroupSelect2 {...props} />
        )
    }
}

class TagsFilter extends DropDownFilter {
}
TagsFilter.defaultProps = {
    storeName: 'tagStore',
    storeFunction: 'searchTagDefs',
    placeholder: 'Search by Tags',
    className:'height-adjust-filters'

}

class SecurityZones extends DropDownFilter {
}
SecurityZones.defaultProps = {
    storeName: 'securityZoneStore',
    storeFunction: 'searchSecurityZone',
    placeholder: 'Search by Security Zones'
}

class ServiceFilter extends DropDownFilter {
}
ServiceFilter.defaultProps = {
    storeName: 'serviceStore',
    storeFunction: 'searchServices',
    placeholder: 'Search by Service'
}


class DatazoneFilter extends DropDownFilter {
}
DatazoneFilter.defaultProps = {
    storeName: 'datazoneStore',
    storeFunction: 'searchDataZones',
    placeholder: 'Search by Datazone'
}

class TagAttrFilter extends DropDownFilter {
}
TagAttrFilter.defaultProps = {
    storeName: 'tagAttrStore',
    storeFunction: 'searchTagAttrDef',
    placeholder: 'Search by Tag attributes'
}

const ToggleButtonStyle = observer(function ToggleButtonStyle({
    className='', label, checked, fields, attr, onChange, color="primary", inputAttr={},
    labelPlacement="end"
}) {
  let isChecked = checked || false;
  if (checked == undefined && fields && attr) {
    isChecked = ('' + fields[attr]) == 'true';
  }
  inputAttr.className = inputAttr.disabled ? `${inputAttr.className} inactive` : inputAttr.className;
  return (
    <div className={`${className}`}>
        <FormControlLabel
            control={
                <MUISwitch
                    checked={isChecked}
                    onChange={onChange}
                    color={color}
                    {...inputAttr}
                />
            }
            label={label}
            labelPlacement={labelPlacement}
        />
    </div>
  )
});

const Toggle = styled(ToggleButtonStyle)`
    label {
        pointer-events: ${props => (props.inputAttr && props.inputAttr.disabled) ? 'none !important' : 'auto'};
    }
`
class CustomButtonGroup extends Component {
    constructor(props) {
        super(props);
        this.state = {
            activeBtn: (props.value || props.defaultValue) ? [props.value || props.defaultValue] : []
        };
    }

    static getDerivedStateFromProps(nextProps, prevState){
        const [value] = prevState.activeBtn;
        if(nextProps.value !== value){
          return { value: nextProps.value};
        }
        return null;
    }
	
    componentDidUpdate = prevProps => {
        if (prevProps.value != this.props.value) {
            this.setState({activeBtn:  [this.props.value]});	
        }
    }

    handleClick = (event, value) => {
        const val = Array.isArray(value) ? value.pop() : value;
        value = [val];
        if (this.props.onClick) {
            this.props.onClick(val);
        }
        this.setState({activeBtn: value});
    }

    render() {
        const {activeBtn} = this.state;
        const {buttonList, className = '', disabled=false, btnGroupClass = '', suffix, size="medium", orientation="horizontal"} = this.props;
        const randomKey = Math.random();
        return (
            <ToggleButtonGroup {...this.props.onChange} orientation={orientation} value={activeBtn} className={btnGroupClass} size={size} onChange={this.handleClick} >
                {buttonList.map((txt, i) => {
                    return <CustomToggleButtonStyle id={randomKey}
                                variant="contained"
                                color="default"
                                key={i}
                                disabled={disabled}
                                selected={activeBtn.includes(txt)}
                                value={txt}
                            >
                            {txt}
                            {suffix}
                            </CustomToggleButtonStyle>;
                })}
            </ToggleButtonGroup>
        )
    }

}
CustomButtonGroup.defaultProps = {
    buttonList: [],
    onClick: () => {}
}

const CustomToggleButton = observer((props) => {
    const {children} = props;
    return(
        <ToggleButton {...props}>
            {children}
        </ToggleButton>
    );
})

const CustomToggleButtonStyle = styled(CustomToggleButton)`
    background-color: ${props =>  props.selected ? `#498ee6 !important` : 'transparent !important'};
    color: ${props => props.selected ? 'white !important' : 'inherit !important'}
`

class CustomButtonGroupWithValue extends Component {
    constructor(props) {
        super(props);
        this.state = {
            activeBtn: props.value || props.defaultValue
        };
    }

    handleClick = (e, val) => {
        if (this.props.onClick) {
            this.props.onClick(e, val);
        }
        this.setState({activeBtn: val});
    }

    render() {
        const {activeBtn} = this.state;
        const {buttonList, className = '', disabled=false, btnGroupClass = '', size="medium", orientation="horizontal", buttonGroupProps = {}} = this.props;
        const randomKey = Math.random();
        return (
            <ToggleButtonGroup onChange={this.props.onClick} className={btnGroupClass} orientation={orientation} size={size} {...buttonGroupProps} >
                {buttonList.map((button, i) => {
                    return <ToggleButton id={randomKey}
                                key={i}
                                disabled={disabled}
                                title={button.title ? button.title : ''}
                                value={button.value}
                                className={`${className} ${activeBtn === button.value ? 'active' : ''}`}
                                data-button-text={button.value}
                                onClick={(e)=>{
                                    this.handleClick(e, button.value)
                                }}
                            >
                            {button.component}
                            </ToggleButton>;
                })}
            </ToggleButtonGroup>
        )
    }

}
CustomButtonGroupWithValue.defaultProps = {
    buttonList: [],
    onClick: () => {}
}


@observer
class CreatableSelect2  extends Component{
    render(){
        let {data, label, colAttr,fieldObj, fieldKey, errMsg, ...restProps} = this.props;
        if (fieldObj && fieldKey) {
            restProps.value = fieldObj[fieldKey];
        }
        return (
            <Grid item {...colAttr}>
                {/*label && <h5>{label}</h5>*/}
                {label && <FormLabel required={restProps.required || false}>{label}</FormLabel>}
                <FormGroup>
                <Select2 data={data && f.isPromise(data) ? f.models(data) : data} allowCreate={true} {...restProps} />
                {/*errMsg && <Grid item className="validation text-danger">&nbsp;<small>{errMsg}</small></Grid>*/}
                {errMsg && <ValidationMsgField msg={errMsg} />}
                </FormGroup>
            </Grid>
        )
    }
  }

  CreatableSelect2.defaultProps = {
    colAttr: {
        sm: 6,
        md: 4
    },
    value: '',
    placeholder: 'Select...',
    label: '',
    labelKey: 'label',
    valueKey: 'value',
    multiple: true,
    disabled: false
}

const SelectWithCheckBoxOptions = observer(({ value=[], options=[], onChange, labelKey="name", valueKey="value", placeholder="Select", error=false, errorMessage="Required", ...props }) => {
    let allSelected = value?.length === options?.length;
    const selectAllOption = {[labelKey]: "Select All", [valueKey]: "all"};

    const optionsList = !isEmpty(options) ? [selectAllOption, ...options].map(o => ({...o, label: o[labelKey], value: o[valueKey]})) : [];
    if (value?.length) {
        if (value.includes('all')) {
            allSelected = true;
            value = optionsList.filter(o => o[valueKey] !== 'all');
        } else {
            value = optionsList.filter(o => value.includes(o[valueKey]))
        }
    }

    const handleChange = (event, opts, reason) => {
        const values = opts.map(o => o[valueKey]);
        let filteredValues = [];
        if (reason === "select-option" || reason === "remove-option") {
            if (opts.find(o => o[valueKey] === "all")) {
                if (allSelected) {
                    allSelected = false;
                    filteredValues = [];
                } else {
                    filteredValues = options;
                }
            } else {
                if (values.length === options.length) {
                    allSelected = true;
                }
                filteredValues = options.filter(o => values.includes(o[valueKey]));
            }
          } else if (reason === "clear") {
            filteredValues = [];
          }
        if (onChange) {
            onChange(filteredValues);
        }
    }

    const renderTags = (value, getTagProps) => {
    return value.map((option, index) => (
          <TagChip
            // variant="outlined"
            label={option[labelKey]}
            {...getTagProps({ index })}
            deleteIcon={<CloseIcon fontSize="small" />}
            data-testid="input-chip"
          />
        ))
    }

    const getOptionLabel = option => `${option[labelKey]}`;

    const optionRenderer = (option, { selected }) => {
        const selectAllProps = option[valueKey] === "all" ? { checked: allSelected } : {};
        return (
          <div className={`custom-check-box ${(option[valueKey] === "all" && allSelected) ? ' check-all' : ''}`}>
            <MUICheckbox
              color="primary"
              icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
              checkedIcon={<CheckBoxIcon fontSize="small" />}
              style={{ marginRight: 3 }}
              checked={selected}
              {...selectAllProps}
            />
            {getOptionLabel(option)}
          </div>
        );
      };

    return (
        <Autocomplete
            value={value}
            multiple
            limitTags={3}
            id="checkboxes-select"
            options={optionsList}
            disableCloseOnSelect
            getOptionLabel={(option) => option[labelKey]}
            onChange={handleChange}    
            renderOption={optionRenderer}
            renderInput={(params) => (
                <TextField {...params} error={error} helperText={error ? errorMessage : ''} variant="standard" placeholder={allSelected ? '' : placeholder} />
            )}
            renderTags = {renderTags}
            ListboxProps={{className: "policy-authoring-options"}}
        />
    );
})



export {
    SearchField,
    DateRangePickerComponent,
    Switch,
    ICheckRadio,
    InputGroupSelect2,
    Checkbox,
    DropDownFilter,
    TagsFilter,
    DatazoneFilter,
    TagAttrFilter,
    Toggle,
    CustomButtonGroup,
    CustomButtonGroupWithValue,
    CustomClassNameSwitch,
    SecurityZones,
    ServiceFilter,
    CreatableSelect2,
    SelectWithCheckBoxOptions
}
