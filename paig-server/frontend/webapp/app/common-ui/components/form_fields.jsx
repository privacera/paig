import React, {Component, Fragment, createRef} from 'react';
import {observer} from 'mobx-react';
import {isArray, isEmpty, compact} from 'lodash';
import AceEditor from "react-ace";
import ReactQuill from 'react-quill';
import "ace-builds/src-noconflict/mode-json";
import "ace-builds/src-noconflict/theme-github";

import Grid from '@material-ui/core/Grid';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormLabel from '@material-ui/core/FormLabel';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import TextField from '@material-ui/core/TextField';
import Switch from '@material-ui/core/Switch';
import Checkbox from '@material-ui/core/Checkbox';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import Tooltip from '@material-ui/core/Tooltip';
import Box from '@material-ui/core/Box';
import CancelIcon from '@material-ui/icons/Cancel';
import Chip from '@material-ui/core/Chip';
import AddCircleIcon from '@material-ui/icons/AddCircle';
import Typography from '@material-ui/core/Typography';
import Paper from "@material-ui/core/Paper/Paper";

import { STRING_OPERATORS } from 'common-ui/utils/globals';
import MProperty from 'common-ui/data/models/m_property';
import {Select2} from 'common-ui/components/generic_components';
import f from 'common-ui/utils/f';
import {matchText} from 'common-ui/components/view_helpers'
import {Utils} from 'common-ui/utils/utils';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';

const FormHorizontal = ({className="", children, ...props}) => {
    return (
        <Grid container spacing={3} className={className} data-test="form" style={{padding: '5px 10px'}} {...props}>
            {children}
        </Grid>
    )
}

const ValidationMsgField = ({msg, msgAttr}) => {
    return (
        <FormHelperText data-testid="error-msg" margin="dense" error required {...msgAttr}>{msg}</FormHelperText>
    )
}

const ValidationAsterisk = ({className=''}) => {
    return (
        <span className={`text-danger ${className}`}>*</span>
    )
}

const DisplayText = ({value, ...textAttr}) => {
    return (
        <Typography component="div" className="profile-text" {...textAttr}>{value || '--'}</Typography>
    )
}
@observer
class FormGroupBase extends Component {
   constructor(props) {
        super(props);
    }
    getTextValue = () => {
        let value = this.inputAttr.value || '';
        if (this.inputAttr.fieldObj && this.inputAttr.fieldObj.value != null) {
            value = this.inputAttr.fieldObj.value
        }
        if (typeof value == 'boolean' || typeof value == 'number') {
            value = '' + value
        }
        if (value == null && this.props.textAttr) {
            value = this.props.textAttr.emptyText || "";
        }
        return value;
    }
    getField() {
        if (this.props.textOnly) {
            return this.displayText();
        }
        return this.displayField();
    }
    displayText() {
        const textAttr = this.props.textAttr || {};
        return <DisplayText {...textAttr} value={this.getTextValue()} />
    }
    displayField() {
        return null;
    }
    render() {
        let {formGroupAttr, showLabel, label, labelAttr, errMsg, errAttr, inputColAttr, children, textOnly, textAttr, wrapFormGroup, 
            showHelperText, ...inputAttr
        } = this.props;
        this.inputAttr = inputAttr;
        if (!errMsg && inputAttr.fieldObj && inputAttr.fieldObj.errorMessage) {
            errMsg = inputAttr.fieldObj.errorMessage;
        }

        if (!textOnly && errMsg) {
            inputAttr.error = true;
            if (showHelperText && !inputAttr.helperText) {
                inputAttr.helperText = errMsg;    
            }
        }

        return (
            <Grid item {...inputColAttr} >
                {showLabel &&
                    <FormLabel required={this.props.required && !this.props.textOnly} {...labelAttr}>{label}</FormLabel>
                }
                {this.getField()}
                {children}
            </Grid>
        )
    }
}
FormGroupBase.defaultProps = {
    formGroupAttr: {},
    showLabel: true,
    label: '',
    labelAttr: {},
    errMsg: "",
    errAttr: {},
    inputColAttr: {
        xs: 12
        // md: 8
    },
    required: false,
    textOnly: false,
    textAttr: {},
    wrapFormGroup: true,
    showHelperText: true
}

@observer
class FormControlBase extends FormGroupBase {
    render() {
        let {formGroupAttr, showLabel, labelAttr, errMsg, errAttr, inputColAttr, children, textOnly, textAttr, wrapFormGroup, tooltip, 
            showHelperText, ...inputAttr
        } = this.props;
        this.inputAttr = inputAttr;
        if (!errMsg && inputAttr.fieldObj && inputAttr.fieldObj.errorMessage) {
            errMsg = inputAttr.fieldObj.errorMessage;
        }

        if (!textOnly && errMsg) {
            inputAttr.error = true;
            inputAttr.helperText = errMsg;
        }

        return (
            <Grid item {...inputColAttr}>
                {this.getField()}
                {children}
            </Grid>
        )
    }
}

class FormGroupInput extends FormGroupBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, required, as, InputProps={}, ...inputAttr} = this.inputAttr;
        let {endAdornment, ...restInputProps} = InputProps;

        let props = {
            required,
            rowsMax: 10
        };

        if (as == 'textarea') {
            props.rows = 4;
            props.multiline = true;
        }

        if (fieldObj) {
            inputAttr.value = inputAttr.value || fieldObj.value;
            inputAttr.onChange = inputAttr.onChange || ((e) => fieldObj.value = e.target.value);
        }

        if (endAdornment) {
            endAdornment = [endAdornment]
        } else {
            endAdornment = []
        }
        if (this.props.tooltip) {
            endAdornment.push(
                <Tooltip key={'tooltip'} placement="top" arrow
                    title={<Typography variant="body2">{this.props.tooltip}</Typography>}
                >
                    <InfoOutlinedIcon color="action" fontSize="small" />
                </Tooltip>
            )
        }

        return (
            <TextField
                variant="outlined"
                fullWidth
                size="small"
                inputProps={{"data-testid": "input-field"}}
                InputProps={{
                    endAdornment,
                    ...restInputProps
                }}
                {...props}
                {...inputAttr}
            />
        )
    }
}

class FormGroupAceEditor extends FormGroupBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, ...inputAttr} = this.inputAttr;
        if (fieldObj) {
            inputAttr.value = inputAttr.value || fieldObj.value;
            inputAttr.onChange = inputAttr.onChange || (value => fieldObj.value = value);
        }
        return <AceEditor key={1} {...inputAttr} />
    }
}

class FormGroupSelect2 extends FormGroupBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, ...inputAttr} = this.inputAttr;
        let errorClass;

        // if (inputAttr.error) {
            // inputAttr.error = '' + inputAttr.error;
        // }
        delete inputAttr.helperText;

        if (fieldObj) {
            inputAttr.value = inputAttr.value || fieldObj.value || [];
            inputAttr.onChange = inputAttr.onChange || ((value, changedValue) => {
                if (typeof value == 'string') {
                    value = Array.from(new Set(value.split(','))).join(',');
                }
                fieldObj.value = value;
            })
            if (!inputAttr.data && fieldObj.fieldOpts && fieldObj.fieldOpts.values) {
                inputAttr.data = fieldObj.fieldOpts.values;
            } else if (inputAttr.data && f.isPromise(inputAttr.data)) {
                inputAttr.data = f.models(inputAttr.data);
            }
        }

        //Adds error border on select elements on error.
        if(fieldObj && fieldObj.fieldOpts && 	
            fieldObj.fieldOpts.hasOwnProperty('errorClass') && fieldObj.fieldOpts.errorClass){	
                errorClass = fieldObj.fieldOpts.errorClass;	
        };
        return (
            <Select2 className={errorClass && errorClass} key={1} {...inputAttr} />
        )
    }
    displayText() {
        let value = this.inputAttr.value || (this.inputAttr.fieldObj && this.inputAttr.fieldObj.value) || "";
        if (this.inputAttr.data && this.inputAttr.valueKey) {
            if (typeof value == "string") {
                value = value.split(',');
            }
            this.inputAttr.data.forEach(data => {
                let index = value.indexOf(data[this.inputAttr.valueKey]);
                if (index > -1) {
                    value[index] = data[this.inputAttr.labelKey];
                }
            })
            value = value.join(',');
        }
        if (value && this.props.textAttr && this.props.textAttr.displayTextAsLabel) {
            if (typeof value == "string") {
                value = value.split(',')
            }
            value = value.map && value.map((val, i) =>
                <Tooltip arrow placement="top" key={i}
                    title={<Typography variant="body2">{val}</Typography>}
                >
                    <Chip
                        color="primary"
                        className="m-t-xs m-r-xs"
                        label={Utils.smartTrim(val, 30)}
                    />
                </Tooltip>
            )
        }
        if (this.props.textAttr && !value || (isArray(value) && !value.length)) {
            value = this.props.textAttr.emptyText || "";
        }
        return <DisplayText value={value} />

    }
}

class FormGroupOperatorSelect2 extends FormGroupBase {
    constructor(props) {
        super(props);
        this.valueSeparator = ';';
    }
    componentDidMount() {
        let {fieldObj} = this.inputAttr;
        //For existing okta user sync applications
        if(fieldObj.value && fieldObj.value.indexOf(this.valueSeparator) === -1) {
            fieldObj.value = this.getFieldObjValue(fieldObj.value, STRING_OPERATORS.EQUALS.value);
        }
    }

    getInputAttrValue = (value) => {
        const {valueSeparator = this.valueSeparator} = this.inputAttr.operatorInputAttr;
        return value.indexOf(valueSeparator) >= 0 ? value.split(valueSeparator)[1] :  value;
    }
    getOperatorInputAttrValue = (value) => {
        const {valueSeparator = this.valueSeparator} = this.inputAttr.operatorInputAttr;
        return value.indexOf(valueSeparator) >= 0 ? value.split(valueSeparator)[0] : STRING_OPERATORS.EQUALS.value;
    }
    getFieldObjValue = (value, operatorValue) => {
        const {valueSeparator = this.valueSeparator} = this.inputAttr.operatorInputAttr;
        return operatorValue + valueSeparator + value;
    }
    displayField() {
        let {fieldObj, operatorInputAttr, ...inputAttr} = this.inputAttr;

        let errorClass;

        delete inputAttr.helperText;

        if (fieldObj) {
            inputAttr.value = inputAttr.value || this.getInputAttrValue(fieldObj.value) || [];
            operatorInputAttr.value = this.getOperatorInputAttrValue(fieldObj.value) || operatorInputAttr.value
                || STRING_OPERATORS.EQUALS.value;

            inputAttr.onChange = inputAttr.onChange || ((value, changedValue) => {
                if (typeof value == 'string') {
                    value = Array.from(new Set(value.split(','))).join(',');
                }
                fieldObj.value = this.getFieldObjValue(value, operatorInputAttr.value);
            })
            if (!inputAttr.data && fieldObj.fieldOpts && fieldObj.fieldOpts.values) {
                inputAttr.data = fieldObj.fieldOpts.values;
            } else if (inputAttr.data && f.isPromise(inputAttr.data)) {
                inputAttr.data = f.models(inputAttr.data);
            }
            operatorInputAttr.onChange = ((value, changedValue) => {
                if (typeof value == 'string') {
                    operatorInputAttr.value = value;
                    fieldObj.value = this.getFieldObjValue(inputAttr.value, value);
                }
            })
        }

        //Adds error border on select elements on error.
        if(fieldObj && fieldObj.fieldOpts &&
            fieldObj.fieldOpts.hasOwnProperty('errorClass') && fieldObj.fieldOpts.errorClass){
            errorClass = fieldObj.fieldOpts.errorClass;
        };

        return (
            <Grid container spacing={0} className={"operator-select-tag"}>
                <Grid item xs={2}>
                    <Select2 className={errorClass && errorClass} key={1} {...operatorInputAttr}/>
                </Grid>
                <Grid item xs={10}>
                    <Select2 className={errorClass && errorClass} key={1} {...inputAttr} />
                </Grid>
            </Grid>
        )
    }
    componentWillUnmount() {
        let { fieldObj } = this.inputAttr;
        if(fieldObj.value && isEmpty(this.getInputAttrValue(fieldObj.value))) {
            fieldObj.value = '';
        }
    }
}

class FormGroupSwitch extends FormControlBase {
    constructor(props) {
        super(props);
    }
    values=[['false', 'true'], ['0', '1'], [false, true], [0, 1], ['enable', 'disable'], ['enabled', 'disabled']]
    getValue(e) {
        let {fieldObj} = this.inputAttr;

        let values = this.values.find(val => val.includes(fieldObj.value));
        let val = e.target.checked;
        if (values) {
            val = values[+e.target.checked];
        }
        return val;
    }
    displayField() {
        let {fieldObj, label, ...inputAttr} = this.inputAttr;
        let {labelAttr={}, tooltip} = this.props;
        if (fieldObj) {
            inputAttr.checked = ['true', '1', 'enable', 'enabled'].includes('' + fieldObj.value);
            inputAttr.onChange = inputAttr.onChange || (e => fieldObj.value = this.getValue(e));
        }
        return (
            <Fragment>
                <FormControlLabel
                    // labelPlacement="start"
                    control={<Switch inputProps={{'data-testid': 'toggle-switch'}} id='toggle-switch' name={label} color="primary" {...inputAttr} />}
                    label={label}
                    {...labelAttr}
                />
                {
                    tooltip &&
                    <Tooltip key={'tooltip'} placement="top" arrow
                        title={<Typography variant="body2">{tooltip}</Typography>}
                    >
                        <InfoOutlinedIcon color="action" fontSize="small" />
                    </Tooltip>
                }
            </Fragment>
        )
    }
    displayText() {}
}

class FormGroupCheckbox extends FormControlBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, label, ...inputAttr} = this.inputAttr;
        let {labelAttr={}} = this.props;
        if (fieldObj) {
            inputAttr.checked = ('' + fieldObj.value) == 'true';
            inputAttr.onChange = inputAttr.onChange || (e => fieldObj.value = e.target.checked);
        }
        return (
            <FormControlLabel
                // labelPlacement="start"
                control={<Checkbox name={label} color="primary" {...inputAttr} />}
                label={label}
                {...labelAttr}
            />
        )
    }
}

class FormGroupRadio extends FormControlBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, label, ...inputAttr} = this.inputAttr;
        let {labelAttr={}} = this.props;
        if (fieldObj) {
            inputAttr.checked = ('' + fieldObj.value) == '' + inputAttr.value;
            inputAttr.onChange = inputAttr.onChange || (e => fieldObj.value = e.target.value);
        }
        return (
            <FormControlLabel
                // labelPlacement="start"
                control={<Radio name={label} color="primary" {...inputAttr} />}
                label={label}
                {...labelAttr}
            />
        )
    }
}

class FormGroupRadioList extends FormControlBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, label, valueKey, labelKey, ...inputAttr} = this.inputAttr;
        let {labelAttr={}} = this.props;
        if (fieldObj) {
            inputAttr.onChange = inputAttr.onChange || (e => {
                fieldObj.value = e.target.value
            });
        }
        return (
          <FormControl component="fieldset">
              <FormLabel component="legend">{this.inputAttr.label}</FormLabel>
              <RadioGroup row aria-label="position" name="group-radio" defaultValue="top" value={fieldObj.value} onChange={inputAttr.onChange} {...inputAttr}>
                  {fieldObj.fieldOpts.values.map((option, i) => {
                      return (<FormControlLabel
                        className='m-r-md'
                        key={option[valueKey]}
                        label={option[labelKey]}
                        labelPlacement="end"
                        control={<Radio color="primary" required={true} {...inputAttr} value={option[valueKey]}/>}

                      />);
                    })}
              </RadioGroup>
          </FormControl>
        );
    }
}


class FormGroupRadioGroup extends FormControlBase {
    constructor(props) {
        super(props);
    }
    displayField() {
        let {fieldObj, label, valueKey, labelKey, ...inputAttr} = this.inputAttr;
        let {labelAttr={}} = this.props;
        if (fieldObj) {
            // inputAttr.checked = ('' + fieldObj.value) == '' + inputAttr.value;
            inputAttr.onChange = inputAttr.onChange || (e => {
                fieldObj.value = e.target.value
            });
        }
        return (
          <FormControl component="fieldset">
              <FormLabel component="legend">{this.inputAttr.label}</FormLabel>
              <RadioGroup row aria-label="position" name="group-radio" defaultValue="top" value={fieldObj.value} onChange={inputAttr.onChange} {...inputAttr}>
                  {fieldObj.fieldOpts.values.map((option, i) => {
                      return (<FormControlLabel
                        key={option[valueKey]}
                        label={option[labelKey]}
                        labelPlacement="bottom"
                        //TODO FIX
                        // control={this.inputAttr.control(option,  this.inputAttr, i)}
                        control={(
                          <span className="select-platform-radio-hide">
                              <Radio color="primary" required={true} {...inputAttr} value={option[valueKey]} className="visibility-hidden"/>
                              <Paper elevation={2} className={`m-b-sm application-widget select-platform-toggle white-bg ${fieldObj.value == option[valueKey] ? 'selected-service' : ''}`}>
                              <div className="halo app-icon pointer">
                                  <img className="services-logo" src={option.logo} alt="service-logo" />
                              </div>
                              </Paper>
                          </span>)}

                      />);
                    })}
              </RadioGroup>
          </FormControl>
        );
    }
}

const ChartCount = observer(({fieldObj, getTextLength, charLimit}) => {
    return <p className='text-right'>Character Limit:  { getTextLength(fieldObj.value) } /{charLimit}</p>
})

class RichTextEditorField extends FormControlBase {
    constructor(props) {
        super(props);
        this.quillRef = createRef();
        this.timeOut = null
    }

    componentDidMount() {
        this.quillRef.editingArea.addEventListener('paste', this.onPaste.bind(this), true);
    }

    componentWillUnmount() {
        clearTimeout(this.timeOut)
        this.quillRef.editingArea.removeEventListener('paste', this.onPaste, true)
    }

    getCalculatedText = (html) => {
        const calculate = (data) => {
        const { charLimit } = this.props;
        const len = this.getTextLength(data);
        if (len > charLimit) {
            data = data.substring(0, data.length - (len - charLimit));
            return calculate(data);
        } else {
            return data;
        }
        }
        return calculate(html);
    }

    onPaste = () => {
        clearTimeout(this.timeOut)
        this.timeOut = setTimeout(() => {
            const { fieldObj } = this.props;
            const quill = this.quillRef;
            let html = quill.unprivilegedEditor.getHTML();
            fieldObj.value = this.getCalculatedText(html)
            this.forceUpdate();
        }, 200);
    }

    getTextLength = (text) => {
        return text.replace( /(<([^>]+)>)/ig, '').length;
    }

    onKeyDown = (event) => {
        const { charLimit } = this.inputAttr;
        const unprivilegedEditor = this.quillRef?.unprivilegedEditor;
        if (unprivilegedEditor && unprivilegedEditor.getLength() > charLimit && event.key !== 'Backspace') {
          event.preventDefault();
        }
        this.inputAttr.onKeyDown?.(event);
    }

    displayField() {
        let {fieldObj, charLimit=3000, ...inputAttr} = this.inputAttr;
        if (fieldObj) {
            inputAttr.value = inputAttr.value || fieldObj.value;
            inputAttr.onChange = inputAttr.onChange || (value => { fieldObj.value = value });
        }
        return (
            <Fragment>
                <ReactQuill
                    ref={ ref => this.quillRef = ref }
                    key={1}
                    defaultValue={fieldObj.value}
                    {...inputAttr}
                    onKeyDown={this.onKeyDown}/>
                <ChartCount
                    getTextLength={this.getTextLength}
                    fieldObj={fieldObj}
                    charLimit={charLimit}
                />
            </Fragment>
        )
    }
}

RichTextEditorField.defaultProps = {
    charLimit: 3000
}


class PropertiesFields extends Component {
    state = {
        fields: [],
        deletePropIds: new Set()
    }
    componentDidMount() {
        if (this.props.properties && isArray(this.props.properties)) {
            let fields = this.props.properties.slice();
            if(fields.length){
                fields = fields.map(field => {
                    field.type = 'string';
                    return new MProperty(field);
                })
            }else if(this.props.showDefaultProperty) {
                fields = [ new MProperty({'name' : null, 'value': null, type: 'string'}) ];
            }
            this.setState({fields});
        }
    }
    getProperties = () => {
        return this.state.fields.map(m => m.toJSON());
    }
    getDeletePropIds = () => {
        return Array.from(this.state.deletePropIds).join(',');
    }
    handleValueChange = (attr, value, prop) => {
        if (!attr) {
            return;
        }
        prop[attr] = value || undefined;
        if(this.props.handleChange){
            this.props.handleChange(this.state.fields);
        }
        this.setState(this.state, () => {
            if(this.props.handleChange){
                this.props.handleChange(this.getProperties());
            }
        });
    }
    removeProperties = (index, prop) => {
        const {showDefaultProperty} = this.props;
        if (prop && prop.id) {
            this.state.deletePropIds.add(prop.id);
        }
        this.state.fields.splice(index, 1);
        //show default property
        if(this.state.fields.length === 0 && showDefaultProperty){
            this.state.fields.push(new MProperty({type: 'string'}));
        }

        this.setState(this.state,() => {
            if(this.props.handleChange){
                this.props.handleChange(this.getProperties());
            }
        });
    }
    render () {
        const {addBtnClassName = '', showDefaultProperty = false} = this.props;
        let fields = [];
        let disableRemovePropertyBtn = false;
        if(this.state.fields.length === 1 && showDefaultProperty){
            disableRemovePropertyBtn = isEmpty(this.state.fields[0].name) && isEmpty(this.state.fields[0].value) ? true : false;
        }
        this.state.fields && this.state.fields.forEach((prop, i) => {
            let type = "text";
            let passRegex = new RegExp("password|secretkey|secret");
            if (prop.name && prop.name && matchText(prop.name, passRegex)) {
                type = "password";
            }
            let disableRemoveProp = (prop.disabledKey && prop.disabledValue) ? true : false;
            fields.push(
                <Fragment key={i}>
                    <Grid item xs={12}>
                        <Grid container spacing={3} className="align-items-center">
                            <FormGroupInput
                                data-test="key"
                                placeholder="Key"
                                inputColAttr={{md: 5}}
                                value={prop.name || ""}
                                onChange={e => this.handleValueChange("name", e.target.value, prop)}
                                disabled={prop.disabledKey ? true : false}
                            />
                            <FormGroupInput
                                data-test="key"
                                placeholder="Value"
                                inputColAttr={{md: 5}}
                                type={type}
                                value={prop.value || ""}
                                onChange={e => this.handleValueChange("value", e.target.value, prop)}
                                disabled={prop.disabledValue ? true : false}
                            />
                            <Grid item md={2}>
                                <CustomAnchorBtn
                                    size="small"
                                    tooltipLabel="Remove"
                                    aria-label="delete"
                                    icon={<CancelIcon color={disableRemoveProp ? "disabled" : disableRemovePropertyBtn ? "disabled": "action"} />}
                                    onClick={e => this.removeProperties(i, prop)}
                                    disabled={disableRemoveProp || disableRemovePropertyBtn}
                                />
                            </Grid>
                        </Grid>
                    </Grid>
                </Fragment>
            );
        });

        fields.push(
            <Grid item xs={12} key={fields.length + 1}>
                <Box mt={1}>
                    <CustomAnchorBtn
                        aria-label="add"
                        tooltipLabel="Add"
                        color="primary"
                        size="small"
                        className={addBtnClassName}
                        onClick={(e) => {
                            this.state.fields.push(new MProperty({type: 'string'}));
                            this.setState(this.state);
                        }}
                        icon={<AddCircleIcon />}
                    />
                </Box>
            </Grid>
        )

        if (this.props.wrapForm) {
            return <FormHorizontal className="m-t-sm">{fields}</FormHorizontal>;
        }
        return <Fragment>{fields}</Fragment>;
    }
}
PropertiesFields.defaultProps = {
    properties: [],
    wrapForm: true,
    showDefaultProperty: false
}

class InputSelect2Field extends Component {
    state = {
        fields: [],
        deletePropIds: new Set()
    }
    componentDidMount() {
        this.setFields()
    }

    componentDidUpdate(prevProps) {
        const {extraInfo: {select2data} }=this.props;
        if((prevProps.extraInfo.select2data && select2data) && JSON.stringify(prevProps.extraInfo.select2data) != JSON.stringify(select2data)){
            const { fields } = this.state
            fields.forEach((field)=>{
              let findIfCurrentFieldExistorNot = prevProps.extraInfo.select2data.find((obj)=>{
                return obj.name == field.value;
              })
              if(!findIfCurrentFieldExistorNot){
                field.value = '';
              }
            })
            this.setState({ fields });
        }
        if(prevProps.properties !== this.props.properties){
            this.setFields()
        }
    }

    setFields = () => {
        let { fields } = this.state
        const { properties = [{}] } = this.props;
        fields = properties.map(field => {
            field.value = field.name
            return new MProperty(field);
        })
        this.setState({ fields })
    }

    getProperties = () => {
        return compact(this.state.fields.map(m => {
          if(m.name && m.value){
            return {nameKey:m.name,valueKey:m.value};
          }
        }));
    }

    validate=()=>{
      let isValid = true
        if(this.state.fields.length) {
            this.state.fields.some(field => {
                if((field.name && !field.value) || (!field.name && field.value) || (!field.name && !field.value)){
                isValid=false;
                f.notifyWarning(this.props.extraInfo.validationMessage);
                return true;
                }
            })
        } else {
            isValid=false;
            f.notifyWarning(this.props.extraInfo.validationMessage);
        }
      return isValid ;
    }
    getDeletePropIds = () => {
        return Array.from(this.state.deletePropIds).join(',');
    }
    handleValueChange = (attr, value, prop) => {
        if (!attr) {
            return;
        }
        prop[attr] = value || undefined;
        if(this.props.handleChange){
            this.props.handleChange(this.state.fields);
        }
        this.setState(this.state, () => {
            if(this.props.handleChange){
                this.props.handleChange(this.getProperties());
            }
        });
    }

    removeProperties = (index, prop) => {
        const { fields, deletePropIds } = this.state;
        if (prop && prop.id) {
            deletePropIds.add(prop.id)
        }
        fields.splice(index, 1);
        this.setState({fields, deletePropIds},() => {
            if(this.props.handleChange){
                this.props.handleChange(this.getProperties());
            }
        });
    }
    render () {
        const {properties, extraInfo={}} = this.props;
        const {select2PlaceHolder, sourceSelect2Data=[], select2DesPlaceHolder, select2data=[], select2value}= extraInfo;
        let fields = [];

        this.state.fields && this.state.fields.forEach((prop, i) => {
            fields.push(
                <Grid container spacing={3} alignItems="center">
                     <Grid item xs={12} sm={5}>
                        <Select2 
                            data={sourceSelect2Data.length ? sourceSelect2Data : [] } 
                            placeholder={select2PlaceHolder} 
                            valueKey={'name'} 
                            clearable={false} 
                            labelKey={'name'} 
                            onChange={ val => this.handleValueChange("name",val, prop)}
                            value={prop.name || ''}
                        />
                        <Box component="div" className="validation text-danger ">
                            <small></small>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={1}>
                        <Box textAlign="center" mt="5px">
                            <strong>To</strong>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={5}>
                        <Select2 
                            data={select2data.length ? select2data : [] }
                            placeholder={select2DesPlaceHolder}
                            valueKey={'name'}
                            clearable={false}
                            labelKey={'name'}
                            onChange={ val => this.handleValueChange("value",val, prop)}
                            value={prop.value || ''}
                        />
                        <Box component="div" className="validation text-danger">
                            <small></small>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={1}>
                        <Box>
                            <CustomAnchorBtn
                                aria-label="delete"
                                tooltipLabel="Remove"
                                onClick={e => this.removeProperties(i, prop)}
                                icon={<CancelIcon />}
                            />
                        </Box>
                    </Grid>
                </Grid>
            );
        });

        fields.push(
            <Grid container spacing={3}>
                <Grid item xs={12} md={1}>
                    <CustomAnchorBtn 
                        fontSize="medium"
                        color="primary" 
                        tooltipLabel="Add" 
                        onClick={(e) => {
                            this.state.fields.push(new MProperty({type: 'string'}));
                            this.setState(this.state);
                        }}
                        icon={<AddCircleIcon />} 
                    />
                {/* <IconButton color="primary" aria-label="add" size="large">
                    <AddCircleIcon onClick={(e) => {
                        this.state.fields.push(new MProperty({type: 'string'}));
                        this.setState(this.state);
                    }}/>
                </IconButton> */}
                </Grid>
            </Grid>
            
        )

        return <div className="m-t-xs">{fields}</div>;
    }
}
InputSelect2Field.defaultProps = {
    properties: [],
    wrapForm: true
}

export {
    FormHorizontal,
    ValidationMsgField,
    ValidationAsterisk,
    DisplayText,
    FormGroupInput,
    FormGroupAceEditor,
    FormGroupSelect2,
    FormGroupSwitch,
    FormGroupCheckbox,
    FormGroupRadio,
    PropertiesFields,
    InputSelect2Field,
    FormGroupRadioGroup,
    FormGroupOperatorSelect2,
    FormGroupRadioList,
    RichTextEditorField
}
