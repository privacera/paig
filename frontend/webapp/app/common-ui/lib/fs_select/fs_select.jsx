/* library imports */
import React, { Component, Fragment } from 'react';
import { observable, action, reaction } from 'mobx';
import { observer } from 'mobx-react';
import PropTypes from 'prop-types';
import compact from 'lodash/compact';
import uniq from 'lodash/uniq';
import uniqBy from 'lodash/uniqBy';
import isObject from 'lodash/isObject';
import TagsInput from 'react-tagsinput'
import clsx from 'clsx';
import styled from 'styled-components';
import 'react-tagsinput/react-tagsinput.css'; // If using WebPack and style-loader.

// Material Imports
import { createFilterOptions } from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import { withStyles } from '@material-ui/core/styles';
import Chip from "@material-ui/core/Chip";
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import CloseIcon from '@material-ui/icons/Close';
import InputAdornment from '@material-ui/core/InputAdornment'
import FormHelperText from '@material-ui/core/FormHelperText';

// Other Imports
import {REGEX, TAG_MAX_CHARACTERS, TAG_ERROR_MESSAGE, TAG_MAX_CHARACTERS_ERROR} from 'utils/globals';
import {DEFAULTS} from 'common-ui/utils/globals';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import Autocomplete from "common-ui/lib/autocomplete";

const styles = {
  root: {
  },
  input: {
    border: 'none !important',
  },
  option: {
    wordBreak: 'break-all'
  },
  popper: {} // to remove warning from browser console.
}
const TagChip = styled(Chip)`
  min-height: 28px;
  // background-color: #666;
  // border-radius: 6px;
  // color: #fff;
  height: unset !important;

  /*& .MuiChip-deleteIcon{
    color: #fff
  }*/
  & .MuiChip-label{
    white-space: normal;
    word-break: break-all;
    text-overflow: unset;
    padding-bottom: 4px;
    padding-top: 4px;
  }
`
@observer
class FsSelect extends Component {

  constructor(props) {
    super(props)
    this.setValue(this.props);
    this.filter = createFilterOptions({trim: true});

    if (this.props.loadOptions && this.props.data && Array.isArray(this.props.data)) {
      this.disposeDataChangeReaction = reaction(
        () => this.props.data.length,
        () => {
          this.setOptions(this.props.data);
        }
      )
    }
  }

  @observable val = null;
  @observable _vState = {
    loading: this.props.loadOptions ? true : false,
    inputValue: '',
    options: []
  }
  searchValue = '';
  previousSearchValue = '';
  timeOut = null;

  componentDidMount() {
    const {triggerOnLoad, data=[]} = this.props;
    if(triggerOnLoad){
      this.fetchOptions();
    }else{
      this.setOptions(data);
    }
  }


  fetchOptions = (inputValue='') => {
    const {loadOptions} = this.props;
    if (loadOptions) {
      try {
        this._vState.loading = true;
        this.searchValue = inputValue;
        loadOptions(inputValue, this.setOptions);
      } catch (e) {
        this.searchValue = '';
        this._vState.loading = false;
      }
    };
  }
  @action
  setOptions = options => {
    this.searchValue = '';
    this._vState.options = options || [];
    this._vState.loading = false;
  }
  componentWillUnmount() {
    this.timeOut && clearTimeout(this.timeOut);
    if (this.disposeDataChangeReaction) {
      this.disposeDataChangeReaction();
    }
  }

  @action
  onChange = (event, value, changeAction, ...props) => {
    const {valueKey, labelKey, tagsInput, allowCreate, loadOptions, data, 
      multiple, uniqOptions, disableCloseOnSelect} = this.props;
    const hasSearchValue = this._vState.inputValue;
    const splitDelimiter = this.getSplitDelimiterStr();
    if (tagsInput) {
      value = event; // In tagsInput the first argument is the value and second is removed value;
    }
    if (isObject(value) && value.createdValue) {
      value[valueKey] = value.createdValue;
    }
    const val = value;
    const isArrayCheck = Array.isArray(value)
    if (value) {
      value = isArrayCheck ? value.reduce((acc, v, i) => {
        let _v = typeof v == 'string' ? v : v[valueKey].toString();
        if (v.createdValue) {
          _v = v.createdValue;
          val[i][valueKey] = _v;
        }
        if (v.createdValue && (typeof v[labelKey] != 'string')) {
          return acc;
        }
        if (!acc.split(splitDelimiter).includes(_v.toString().trim())) {
          acc += acc ? `${splitDelimiter}${_v.toString().trim()}` : _v.toString().trim();
        }
        return acc;
      }, '') : value[valueKey] ? value[valueKey].toString().trim(): value.value ? value.value.trim() : value.trim();
    }
    if ((Array.isArray(value) && value.length == 0) || !value) {
      value = this.props.tagsInput ? [] : '';
    }

    if (allowCreate) {
      if (value && typeof value == 'string') {
        value = value.split(splitDelimiter).map(val => val.trim()).filter(val => val);
        value = [...new Set(value)].join(splitDelimiter);
      } else if (value && Array.isArray(value)) {
        value.forEach((val, i) => {
          if (typeof val == 'string') {
            const temp = val.split(splitDelimiter).map(v => v.trim()).filter(val => val && !value.includes(val));
            value[i] = [...new Set(temp)].join(splitDelimiter);
          }
        });
      }
    }

    this.val = value;
    const opt = Array.isArray(val) ? val : [val];
    if (allowCreate && !multiple) {
      let op = opt.find(o => o && (o[valueKey] === value));
      this._vState.inputValue = op?.[labelKey] || value;
    } else {
      this._vState.inputValue = '';
    }
    if (allowCreate && loadOptions) {
      this._vState.options = this._vState.options.filter(o => !o.createdValue);
    }
    if (this.props.onChange) {
      if (uniqOptions) {
        this.props.onChange(value, opt, loadOptions ? this._vState.options : data);  
      } else {
        this.props.onChange(value, opt, changeAction, ...props);
      }
    }
    // If disableCloseOnSelect is enable in select3
    // When popup is open for multiple selection and user search for the specific option using async loadOptions
    // The left options are only with key used for search that's why we need to fetch new options manually.
    // So that it can have a fresh options.
    if (disableCloseOnSelect && loadOptions && hasSearchValue) {
      this.fetchOptions(hasSearchValue);
    }
  }

  onFocus = (e) => {
    if (!this.props.multiple && !this.props.customDropDown) {
      let timer = null;
      e.persist();
      clearTimeout(timer);
      timer = setTimeout(() => {
        const el = e.target;
        el.scrollLeft = el.scrollWidth;
        el.focus();
      }, 0);
    }
    if (this.props.onFocus) {
      this.props.onFocus(this.val, e);
    }
  }

  onInputChange = (event, value, reason) => {
    const val = value;
    //Don not fetch options when user selects option / click on option
    if (reason != 'reset' && (event.which !== 13 || event.type !== 'click') ) {
      this._vState.inputValue = val;
      if (this.props.loadOptions) {
        clearTimeout(this.timeOut);
        this.timeOut = setTimeout(() => {
          if (val.trim()) {
            this.previousSearchValue = val;
            this._vState.loading = true;
            this.fetchOptions(val.trim());
          }
        }, 500);
      }
    }
    if (this.props.onInputChange) {
      this.props.onInputChange(val)
    }
    if (val == '' && reason == 'input') {
      this.props.loadOptions && this.fetchOptions();
      this.forceUpdate()
    }
  }
  setValue = (newProps) => {
    if (newProps.data && newProps.data.length) {
      if (newProps.defaultValue && !newProps.value && this.val === null) {
        this.val = newProps.defaultValue;
      }
      if (newProps.firstSelected && (newProps.value ? !newProps.value : !this.val) && newProps.data) {
        let selectData = null;
        if (newProps.data.constructor.name === "ObservableArray") {
          selectData = newProps.data.slice()[0]
        } else if (Array.isArray(newProps.data)) {
          selectData = newProps.data[0];
        } else {
          selectData = newProps.data
        }
        this.val = selectData
        if (this.props.onChange) {
          this.props.onChange(selectData);
        }
      }
    }
  }

  getSplitDelimiterStr = () => {
    return this.props.splitValueDelimiter || ',';
  }

  getValues = (options=[], values) => {
    const {valueKey, labelKey} = this.props;
    const splitDelimiter = this.getSplitDelimiterStr();

    if (values && typeof values === 'string') {
      values = values.split(splitDelimiter);
    }
    let isValueArray = Array.isArray(values);

    if (options.length) {
      const val = isValueArray ? values : [values];
      if (options.length < val.length) {
        options = [];
      }
    }

    /*
      To remove duplicate options, some options can have same value but it can be of different resource
      eg: ssn can be value for db1/tabl1/ssn, db1/tabl2/ssn
      here ssn will be value and can be multiple but different on
      here using set trying to eliminate duplicate chip seen on ui
    */

    let valuesSet = new Set();
    let filteredOptions = options.filter(d => {
      const val = d[valueKey] || '';
      const label = d[labelKey] || '';
      if (isValueArray) {
        return values.some(_v => {
          let v = _v
          if (isObject(v)) {
            v = v[valueKey];
          }
          if (valuesSet.has(val) || valuesSet.has(label)) {
            return false;
          }
          if (v == val) {
            valuesSet.add(val);
            return true
          } else if (v == label) {
            valuesSet.add(label);
            return true;
          }
          return false;
        });
      } else {
        if (!val || valuesSet.has(val) || valuesSet.has(label)) {
          return false;
        }
        if (val == values) {
          valuesSet.add(val);
          return true;
        } else if (label == values) {
          valuesSet.add(label);
          return true;
        }
        return false;
      }
    });

    let len = filteredOptions.length;
    if (isValueArray && len > 1 && len === values.length) {
      //sort filteredOptions as per values
      filteredOptions.sort((a, b) => values.indexOf(a[valueKey]) - values.indexOf(b[valueKey]));
    }

    if ((values && len && (isValueArray && len < values.length)) || values && len == 0) {
      filteredOptions = this.createValueOptions(values);
    }

    return filteredOptions;
  }

  createValueOptions = (values) => {
    let options = [];
    const {valueKey, labelKey} = this.props;
    const splitDelimiter = this.getSplitDelimiterStr();
    if (typeof values == 'string' || (isObject(values) && !Array.isArray(values))) {
      if (values.includes && values.includes(splitDelimiter)) {
        values = values.split(splitDelimiter);
      } else {
        values = [values];
      }
    }
    if (Array.isArray(values) && values.length > 0) {
      options = compact(values).map(v => {
        let label = v;
        if (isObject(v)) {
          label = v[labelKey];
          v = v[valueKey];
        }
        const o = {};
        o[valueKey] = v;
        o[labelKey] = label;
        return o;
      })
    }
    return options;
  }

  renderInput = (params) => {
    const { _vState } = this;
    const { classes, placeholder = "Select...", error = false, tooltip, errorMessage = "Required", multiple, allowCreate,
      chromeAutoComplete, loaderDataTestId="loader", variant="outlined", customEndAdornment, renderInputParams, addKeyDown=true
    } = this.props;
    let { endAdornment, ...restParams} = params.InputProps

    if (renderInputParams) {
      renderInputParams(params);
    }

    if (tooltip) {
      endAdornment = <CustomEndAdornment endAdornment={endAdornment} tooltip={tooltip} />
    }
    const customProps = {variant};
    if (multiple && allowCreate && addKeyDown) {
      customProps.onKeyDown = (e) => {
        if (e.keyCode === 13 && e.target.value) {
          let value = e.target.value.trim();
          if (typeof this.props.value == 'string') {
            if (this.props.value) {
              const splitDelimiter = this.getSplitDelimiterStr();
              let values = new Set([...this.props.value.split(splitDelimiter)]);
              if (value) {
                values.add(value);
              }
              value = Array.from(values).join(splitDelimiter);
            }
            this.onChange(null, value);
          } else {
            this.onChange(null, (this.props.value || []).concat(value));
          }
        }
      }
    }
    const textField = (
      <TextField
        inputProps={{"data-testid": "fs-select-input"}}
        {...params}
        error={error}
        placeholder={placeholder}
        className="auto-complete-min-height"
        value={this._vState.inputValue}
        helperText={error ? errorMessage : ''}
        InputProps={{
          ...restParams,
          endAdornment: (
            <InputAdornment position="end" className="select-end-adornment">
              {_vState.loading ? <CircularProgress data-testid={loaderDataTestId} color="inherit" size={20} /> : null}
              {endAdornment}
              {customEndAdornment}
            </InputAdornment>
          )
        }}
        {...customProps}
      />
    );
    if( chromeAutoComplete === false ){
      // form element to ignore chrome auto suggestions
      return (
        <form autoComplete="new-password" onSubmit={e => e.preventDefault()}>
          {textField}
        </form>
      )
    }
    return textField;
  }

  filterOptions = (options, params) => {
    const {valueKey, labelKey, formatCreateLabel} = this.props;
    let filtered = this.filter(options, params);
    if(params.inputValue == "*"){
      filtered = options
    }
    const hasInput = filtered.some(f => f[labelKey].toLowerCase() == (params.inputValue || '').trim().toLowerCase())
    if (params.inputValue && !hasInput) {
      const customLabel = (formatCreateLabel && formatCreateLabel(params.inputValue)) || `Add "${params.inputValue}"`;
      filtered.unshift({
        createdValue: params.inputValue,
        [valueKey]: params.inputValue,
        [labelKey]: customLabel
      });
    }
    return uniqBy(filtered, labelKey);
  }

  renderTags = (value, getTagProps) => {
    const {labelKey} = this.props;
    return value.map((option, index) => (
      <TagChip
        label={option[labelKey]}
        {...getTagProps({ index })}
        key={option[labelKey] || index}
        deleteIcon={<CloseIcon />}
        data-testid="input-chip"
      />
    ))
  }

  setCustomProps = (customProps, final_data) => {
    const {isLoading, loading, filterOptions, renderInput, loadOptions, renderTags, disabled, multiple = false, noOptionsText, renderOption, data, allowCreate, value, labelKey, getOptionDisabled} = this.props;
    const {splitValueDelimiter, customEndAdornment, renderInputParams, ...restProps} = this.props;
    Object.assign(customProps, restProps);
    customProps.loading = isLoading || loading || this._vState.loading || false;
    customProps.disabled = disabled || false;
    customProps.blurOnSelect = multiple ? false : true;
    customProps.getOptionDisabled = getOptionDisabled || function (option) { return option.disabled };
    if (!final_data.length) {
      customProps.noOptionsText = noOptionsText || (loadOptions && !this._vState.inputValue ? <span>{DEFAULTS.SEARCH_TXT}</span> : <span>No Options</span>);
    }
    customProps.filterSelectedOptions = multiple ? true : false;
    customProps.renderInput = renderInput || this.renderInput;
    customProps.renderTags = renderTags || this.renderTags;
    customProps.renderOption = renderOption || this.renderOption;
    if (allowCreate) {
      customProps.filterOptions = filterOptions || this.filterOptions;
    }
    if (loadOptions) {
      let inputValue = this._vState.inputValue || '';
      if (inputValue == this.val && !value) {
        inputValue = '';
      } else if (!inputValue && !multiple && (this.val == value || !this.val && value)) {
       if (value) {
        if (Array.isArray(value)) {
          const [val] = value;
          if (val) {
            inputValue = isObject(val) ? val[labelKey] : (val || '');
          }
        } else {
          const [valOpt] = this.getValues(this._vState.options, value);
          inputValue = valOpt[labelKey];
        }
       }
      }
      customProps.inputValue = inputValue;
    }
    this.removeUnWantedProps(customProps);
  }

  removeUnWantedProps = customProps => { // Need to clean up from all the component...
    delete customProps.allowCreate;
    delete customProps.getNewOptionData;
    delete customProps.labelKey;
    delete customProps.valueKey;
    delete customProps.defaultValue;
    delete customProps.tagsInput;
    delete customProps.loadOptions;
    delete customProps.data;
    delete customProps.showTitle;
    delete customProps.allowClear;
    delete customProps.customDropDown;
    delete customProps.isLoading;
    delete customProps.fieldValue;
    delete customProps.fieldClassName;
    delete customProps.getValAsObjectArray;
    delete customProps.fData;
    delete customProps.regexRequired;
    delete customProps.regexPattern;
    delete customProps.valuePath;
    delete customProps.selectedList;
    delete customProps.keyProp;
    delete customProps.defaultOptions;
    delete customProps.inputProps;
    delete customProps._inputType;
    delete customProps.cutomLabelDropDown;
    delete customProps.refId;
    delete customProps.onChangeCallback;
    delete customProps.nestedParams;
    delete customProps.noFormGroup;
    delete customProps.labelClassName;
    delete customProps.triggerOnLoad;
    delete customProps.errorMessage;
    delete customProps.error;
    delete customProps.hideError;
    delete customProps.loaderDataTestId;
    delete customProps.loadOptionsOnOpen;
    delete customProps.cacheOptions;
    delete customProps.onlyUnique;
    delete customProps.splitValueDelimiter;
    delete customProps.multi;
  }

  renderOption = (option, state) => {
    if (this.props.renderOption) {
      return this.props.renderOption(option, this.props.labelKey, state);
    }

    let label = option[this.props.labelKey];
    if (typeof label != 'string') {
      return label;
    }
    return <span  data-testid="select-option-item">{label}</span>;
  }

  optionMenuClosed = (event, reason) => {
    if (reason == 'blur' && (!this.val || (this.val != this._vState.inputValue))) {
      this._vState.inputValue = '';
      this.searchValue = '';
    }
  }

  @action
  onOpen = (event) => {
    if(this.props.loadOptions && ((this.previousSearchValue !== this._vState.inputValue) || this.props.loadOptionsOnOpen) ){
      this._vState.loading = true;
      this._vState.options = [];
      this.previousSearchValue = "";
      this.onInputChange(event, this._vState.inputValue, 'input');
    }
  }

  render() {
    const { data=[], loadOptions, multiple = false, value, tagsInput, classes, className, getOptionDisabled, uniqOptions } = this.props;
    const { loadOptionsOnOpen, splitValueDelimiter, customEndAdornment, renderInputParams, addKeyDown, ...customProps } = this.props;
    let final_value;
    let final_data = [];
    if (value === "" || (value !== undefined && value !== null)) {
      if (value.constructor.name === "ObservableArray") {
        final_value = value.slice();
      } else {
        final_value = value;
      }
    }
    if (data) {
      final_data = data.slice ? data.slice() : data;
    } else {
      final_data = [];
    }
    if (tagsInput && typeof final_value == 'string') {
      final_value = final_value.split(',');
    }
    if (loadOptions) {
      final_data = this._vState.options;
      if (this.props.selectedList && this.props.selectedList.length) {
        final_data = final_data.filter(obj => {
          return this.props.selectedList.findIndex(o => {
            return obj[this.props.labelKey] == o[this.props.labelKey];
          }) == -1
        });
      }
    }
    if (uniqOptions) {
      final_data = uniqBy(final_data, this.props.labelKey)
    }
    if (!tagsInput) {
      this.setCustomProps(customProps, final_data);
      if (!final_value || (Array.isArray(final_value) && !final_value.length)) {
        customProps.disableClearable = true;
      }
    }
    const _className = clsx(classes.root, classes.option, className);
    return (
      <Fragment>
        {tagsInput
          ? (
              <Fragment>
                <TagsInput {...customProps}
                  className={`react-tagsinput ${this.props.error ? 'invalid-tag' : ''}`} 
                  value={final_value}
                  onChange={this.onChange}
                />
                {this.props.error && <FormHelperText margin="dense" error required>Required</FormHelperText>}
              </Fragment>
            )
          : (<Autocomplete
              clearOnBlur
              handleHomeEndKeys
              autoHighlight
              clearOnEscape
              autoComplete
              includeInputInList
              className={_className}
              getOptionSelected={(option, value) => {
                let match = false;
                if (Array.isArray(value)) {
                  match = value.some(val => {
                    if (typeof val === 'object') {
                      return option[this.props.labelKey] == val[this.props.labelKey];
                    } else {
                      return option[this.props.labelKey] == val;
                    }
                  });
                } else {
                  match = option[this.props.labelKey] == value[this.props.labelKey];
                }
                return match;
              }}
              getOptionLabel={(option) => {
                const opt = (!Array.isArray(option) || typeof option == 'string') ? [option] : option;
                return opt.map(o => {
                  if (isObject(o)) {
                    return o[this.props.labelKey]
                  } else {
                    return o
                  }
                }).join(',')
              }}
              {...customProps}
              multiple={ multiple }
              options={final_data}
              value={this.getValues(final_data, final_value)}
              getOptionDisabled={getOptionDisabled || ((option) => option.disabled)}
              onInputChange={this.onInputChange}
              onChange={this.onChange}
              onClose={this.optionMenuClosed}
              onOpen={this.onOpen}
            />
          )}
      </Fragment>
    )
  }

}

FsSelect.defaultProps = {
  showTitle: true,
  triggerOnLoad: true,
  loadOptionsOnOpen: false
}

FsSelect.propTypes = {
  isLoading: PropTypes.bool,
  onChange: PropTypes.func,
  labelKey: PropTypes.string,
  valueKey: PropTypes.string,
  placeholder: PropTypes.string,
  multiple: PropTypes.bool,
  firstSelected: PropTypes.bool,
  defaultValue: PropTypes.oneOfType([PropTypes.string, PropTypes.object, PropTypes.array, PropTypes.number]),
  data: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  value: function (props, propName, componentName) {
    if (!props['onChange'] && props[propName]) {
      return new Error('Value props require onChange function to update selected value');
    }
  },
  showTitle: PropTypes.bool,
};

const CustomEndAdornment = observer(({endAdornment, tooltip}) => {
  const {props} = endAdornment;
  const {children, className} = props;
  return (
    <div className={className}>
      {children}
      {
        tooltip &&
        <Tooltip key="tooltip" placement="top" arrow
          title={<Typography variant="body2">{tooltip}</Typography>}
        >
          <InfoOutlinedIcon color="action" fontSize="small" className="m-r-xs" />
        </Tooltip>
      }
    </div>
  )
})

export default withStyles(styles)(FsSelect)

class WrapAutoCompleteTag extends Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
      inputValue: ''
    }
    this.tempValues = new Set();
    this.disabledTags = new Set();
    this.isTagAutocomplete = null;
    this.errMsg = null;
    this.filter = createFilterOptions({trim: true});
  }

  componentDidMount() {
    this.isTagAutocomplete = new Date().getTime();
    window.addEventListener('keydown', this.handleKeyPress.bind(this));
  }

  componentWillUnmount() {
    window.removeEventListener('keydown', this.handleKeyPress.bind(this));
    this.isTagAutocomplete = null;
  }

  setTempValues = arr => {
    arr.forEach(a => {
      const value = a[this.props.valueKey] || a['value'];
      if (value) {
        this.tempValues.add(value.trim());
      }
    })
  }

  handleChange = (event, value) => {
    this.state.inputValue = '';
    const hasDisabled = value.some(v => this.disabledTags.has((v.value || '').toUpperCase().trim()))
    if (hasDisabled || this.validValue(value)) {
      return;
    }
    this.tempValues = new Set(this.getFieldValues().map(tag=> tag.trim()));
    this.setTempValues(value);
    this.props.field.value = Array.from(this.tempValues);
    this.errMsg = null;
  }

  validValue = value => {
    return value.some(v => {
      if (v.createdValue) {
        v.label = v.createdValue;
      }
      return !REGEX.TAG_DEF.test(v.value) || (v.value.length > TAG_MAX_CHARACTERS)
    })
  }

  getOptionsData = () => {
    let list = [];
    this.disabledTags.clear();
    let res = f.models(this.props.suggestionList) || [];
    res = [this.state.inputValue, ...res.map(r => {
      if (!r.status || r.disabled) {
        this.disabledTags.add(r.name);
      }
      return r.name;
    })];
    res = compact(uniq(res));
    if ((this.state.inputValue || '').trim() && (!REGEX.TAG_DEF.test(this.state.inputValue) || this.state.inputValue.length > TAG_MAX_CHARACTERS)) {
      return [{label: this.getErrorNode(), value: ''}];
    }
    list = Utils.filterByName(res, this.state.inputValue);
    list = list.filter(l => this.getFieldValues().findIndex(a => a.toUpperCase() === l.toUpperCase()) === -1);
    return this.getLabelValue(list);
  }

  getLabelValue = arr => {
    const list = arr.sort((a, b) => a < b ? -1 : a > b ? 1 : 0).reduce((cum, curr) => {
    const value = curr.toUpperCase();
      let label = value;
      if (this.state.inputValue == label) {
        return cum;
      }
      const o = {label, value, id: `${value}`};
      if (this.disabledTags.has(value)) {
        o.disabled = true;
      }
      cum.push(o);
      return cum;
    }, []);
    return list;
  }

  handleKeyPress = event => {
    const {field} = this.props;
    const name = event.target.name;
    if (!name || (name && name != this.isTagAutocomplete) || this.errMsg) {
      return;
    }
    if (event.keyCode === 8 && field.value && field.value.length > 0 && this.state.inputValue === '') {
      this.state.inputValue = '';
       const values = field.value.slice(0,-1);
       field.value = values;
       this.tempValues = new Set(...values);
    }
  }

  filterOptions = (options, params) => {
    const {valueKey, labelKey, formatCreateLabel} = this.props;
    const filtered = this.filter(options, params);
    if (params.inputValue !== "") {
      const val = params.inputValue.toUpperCase();
      this.errMsg = null;
      const customLabel = (formatCreateLabel && formatCreateLabel(val)) || `Add "${val}"`;
      if(!REGEX.TAG_DEF.test(val)){
        this.errMsg = TAG_ERROR_MESSAGE
      } else if (val.length > TAG_MAX_CHARACTERS){
        this.errMsg = TAG_MAX_CHARACTERS_ERROR
      }
      const obj = {
        createdValue: val,
        [valueKey]: val,
        [labelKey]: customLabel
      }
      obj.disabled = this.getFieldValues().includes(val);
      if (this.disabledTags.has(val)) {
        obj.disabled = true;
      }
      if (this.errMsg) {
        obj.label = this.getErrorNode();
      }
      filtered.push(obj);
    }
    return filtered;
  }

  renderInput = (params) => {
    const {classes, placeholder="Select..."} = this.props;
    return (
      <TextField
        {...params}
        label={''}
        className={classes.input}
        placeholder=""
        value={this.state.inputValue}
        // autoFocus
        InputProps={{
          ...params.InputProps,
          placeholder,
          className: "custom-select-tag",
          name: `${this.isTagAutocomplete}`
        }}
      />
    )
  }

  getFieldValues = () => {
    const {field} = this.props;
    let values = field.value;
    if (typeof values == 'string') {
      values = values.split(',');
    }
    return values;
  }

  onInputChange = (event, val, reason)=>{
    this.state.inputValue = val.trim().toUpperCase();
    if (val.trim() == '' && reason == 'input') {
      this.forceUpdate();
    }
  }

  getErrorNode = () => {
    return <span className='text-danger'>{this.errMsg}</span>;
  }

  renderOption = (option, state) => {
    let label = option[this.props.labelKey];
    if (typeof label != 'string') {
      return label;
    }
    return <span>{label}</span>;
  }

  render() {
    const {classes, className } = this.props;
    const _className = clsx(classes.root,classes.option, className);
    return (
      <Autocomplete
        clearOnBlur
        handleHomeEndKeys
        autoHighlight
        clearOnEscape
        autoComplete
        includeInputInList
        multiple
        filterSelectedOptions
        className={_className}
        value={[]}
        options={this.getOptionsData()}
        getOptionSelected={(option, value) => {
          let match = false;
          if (Array.isArray(value)) {
            match = value.some(val => {
              if (typeof val === 'object') {
                return option[this.props.labelKey] == val[this.props.labelKey];
              } else {
                return option[this.props.labelKey] == val;
              }
            });
          } else {
            match = option[this.props.labelKey] == value[this.props.labelKey];
          }
          return match;
        }}
        getOptionLabel={(option) => {
          const opt = (!Array.isArray(option) || typeof option == 'string') ? [option] : option;
          return opt.map(o => {
            if (isObject(o)) {
              return o[this.props.labelKey]
            } else {
              return o
            }
          }).join(',')
        }}
        renderInput={this.renderInput}
        renderOption={this.renderOption}
        filterOptions={this.filterOptions}
        getOptionDisabled={option => option.disabled}
        onInputChange={this.onInputChange}
        onChange={this.handleChange}
        onKeyPress={this.handleKeyPress}
      />
    );
  }
}

WrapAutoCompleteTag.defaultProps = {
  labelKey: 'label',
  valueKey: 'value',
  placeholder: 'Input Tags'
}

const AutoCompleteTag = withStyles(styles)(WrapAutoCompleteTag)

export const autoCompleteRenderInput = (form, tagsList, field) => {
  return ({ ...props }) => {
    let tags = field || form.fields.tags;
    const autosuggestProps = {
      field: tags,
      suggestionList: tagsList
    }
    return <AutoCompleteTag {...props} {...autosuggestProps} />
  }
}
export {TagChip}
