/* eslint eqeqeq: [2, "allow-null"] */

import {default as React, Component, createRef} from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import classNames from 'classnames';
import moment from 'moment-timezone';
import fuzzy from 'fuzzy';
import Datetime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import listensToClickOutside from 'react-onclickoutside';

import TypeaheadSelector from './selector';
import KeyEvent from '../keyevent';


/**
 * A "typeahead", an auto-completing text input
 *
 * Renders an text input that shows options nearby that you can use the
 * keyboard or mouse to select.  Requires CSS for MASSIVE DAMAGE.
 */
class Typeahead extends Component {
  static propTypes = {
    customClasses: PropTypes.object,
    maxVisible: PropTypes.number,
    options: PropTypes.array,
    header: PropTypes.string,
    datatype: PropTypes.string,
    defaultValue: PropTypes.string,
    placeholder: PropTypes.string,
    onOptionSelected: PropTypes.func,
    onKeyDown: PropTypes.func,
    className: PropTypes.string,
  }

  static defaultProps = {
    options: [],
    header: 'Category',
    datatype: 'text',
    customClasses: {},
    defaultValue: '',
    placeholder: '',
    onKeyDown() { return; },
    onOptionSelected() { },
  }

  constructor( ...args ) {
    super( ...args );
    this._onTextEntryUpdated = this._onTextEntryUpdated.bind( this );
    this._onKeyDown = this._onKeyDown.bind( this );
    this._onFocus = this._onFocus.bind( this );
    this._onOptionSelected = this._onOptionSelected.bind( this );
    this._handleDateChange = this._handleDateChange.bind( this );
    this._onEnter = this._onEnter.bind( this );
    this._onEscape = this._onEscape.bind( this );
    this._onTab = this._onTab.bind( this );
    //this._addTokenForValue = this._addTokenForValue.bind( this );
    this.sel = createRef();
    this.input = createRef();
    this.datepicker= createRef();
    this.entry = createRef();
  }

  state = {
    // The set of all options... Does this need to be state?  I guess for lazy load...
    options: this.props.options,
    header: this.props.header,
    datatype: this.props.datatype,

    focused: false,

    // The currently visible set of options
    visible: this.getOptionsForValue( this.props.defaultValue, this.props.options ),

    // This should be called something else, "entryValue"
    entryValue: this.props.defaultValue,

    // A valid typeahead value
    selection: null,
  }

  componentDidUpdate(prevProps) {
    if (prevProps !== this.props) {
      const {options, header, datatype} = this.props;
      this.setState({
        options,
        header,
        datatype,
        visible: options,
      });
    }
    if (this.state.focused && this.entry.current && this.entry.current.focus) {
      this.entry.current.focus();
    }
  }

  getOptionsForValue( value, options ) {
    let result = fuzzy
      .filter( value, options )
      .map( res => res.string );

    if ( this.props.maxVisible ) {
      result = result.slice( 0, this.props.maxVisible );
    }
    return result;
  }

  setEntryText( value ) {
    if ( this.entry.current != null ) {
      ReactDOM.findDOMNode( this.entry.current ).value = value;
    }
    this._onTextEntryUpdated();
  }

  _renderIncrementalSearchResults() {
    if ( !this.state.focused ) {
      return '';
    }

    // Something was just selected
    if ( this.state.selection ) {
      return '';
    }

    // There are no typeahead / autocomplete suggestions
    if ( !this.state.visible.length ) {
      return '';
    }

    return (
      <TypeaheadSelector
        ref={this.sel}
        options={ this.state.visible }
        header={ this.state.header }
        onOptionSelected={ this._onOptionSelected }
        customClasses={ this.props.customClasses }
      />
    );
  }

  _onOptionSelected( option ) {
    const nEntry = ReactDOM.findDOMNode( this.entry.current );
    nEntry.focus();
    nEntry.value = option;
    this.setState({
      visible: this.getOptionsForValue( option, this.state.options ),
      selection: option,
      entryValue: option,
    });

    this.props.onOptionSelected( option );
  }

  _onTextEntryUpdated() {
    let value = '';
    if ( this.entry.current != null ) {
      value = ReactDOM.findDOMNode( this.entry.current ).value;
    }
    this.setState({
      visible: this.getOptionsForValue( value, this.state.options ),
      selection: null,
      entryValue: value,
    });
  }

  _onEnter( event ) {
    if ( this.sel.current.state.selectionIndex == undefined) {
      return this.props.onKeyDown( event );
    }

    this._onOptionSelected( this.sel.current.state.selection );
  }

  _onEscape() {
    this.sel.current.setSelectionIndex( null );
  }

  _onTab() {
    const option = this.sel.current.state.selection ?
      this.sel.current.state.selection : this.state.visible[ 0 ];
    this._onOptionSelected( option );
  }

  eventMap() {
    const events = {};

    events[ KeyEvent.DOM_VK_UP ] = this.sel.current.navUp;
    events[ KeyEvent.DOM_VK_DOWN ] = this.sel.current.navDown;
    events[ KeyEvent.DOM_VK_RETURN ] = events[ KeyEvent.DOM_VK_ENTER ] = this._onEnter;
    events[ KeyEvent.DOM_VK_ESCAPE ] = this._onEscape;
    events[ KeyEvent.DOM_VK_TAB ] = this._onTab;

    return events;
  }

  _onKeyDown( event ) {
    // If Enter pressed
    if ( event.keyCode === KeyEvent.DOM_VK_RETURN || event.keyCode === KeyEvent.DOM_VK_ENTER ) {
      // If no options were provided so we can match on anything
      if ( this.props.options.length === 0 ) {
        this._onOptionSelected( this.state.entryValue );
      }

      // If what has been typed in is an exact match of one of the options
      if ( this.props.options.indexOf( this.state.entryValue ) > -1 ) {
        this._onOptionSelected( this.state.entryValue );
      }
    }

    // If there are no visible elements, don't perform selector navigation.
    // Just pass this up to the upstream onKeydown handler
    if ( !this.sel.current ) {
      return this.props.onKeyDown( event );
    }

    const handler = this.eventMap()[ event.keyCode ];

    if ( handler ) {
      handler( event );
    } else {
      return this.props.onKeyDown( event );
    }
    // Don't propagate the keystroke back to the DOM/browser
    event.preventDefault();
  }

  _onFocus() {
    this.setState({ focused: true });
  }

  handleClickOutside() {
    this.setState({ focused: false });
  }

  isDescendant( parent, child ) {
    let node = child.parentNode;
    while ( node !== null ) {
      if ( node === parent ) {
        return true;
      }
      node = node.parentNode;
    }
    return false;
  }

  _handleDateChange( date ) {
    let newDate = moment( date, 'lll' );
    if ( !newDate.isValid()) newDate = moment();
    this.props.onOptionSelected( newDate.format( 'lll' ));
  }

  _showDatePicker() {
    if ( this.state.datatype === 'date' ) {
      return true;
    }
    return false;
  }

  inputRef() {
    if ( this._showDatePicker()) {
      return this.datepicker.current.refs.dateinput.refs.entry;
    }

    return this.entry.current;
  }

  render() {
    const inputClasses = {};
    let showTextArea = false;
    let inputType = 'input';
    if (this.props.datatype === this.props.customTypeOptions[1]) {
      showTextArea = true;
      inputType = 'textarea';
    }
    inputClasses[ this.props.customClasses[inputType] ] = !!this.props.customClasses[inputType];
    const inputClassList = classNames( inputClasses );

    const classes = {
      typeahead: true,
    };
    classes[ this.props.className ] = !!this.props.className;
    const classList = classNames( classes );

    if ( this._showDatePicker()) {
      let defaultDate = moment( this.state.entryValue, 'lll' );
      if ( !defaultDate.isValid()) defaultDate = moment();
      return (
        <span
          ref={this.input}
          className={ classList }
          onFocus={ this._onFocus }
        >
          <Datetime
            ref={this.datepicker}
            dateFormat={ "ll" }
            defaultValue={ defaultDate }
            onBlur={ this._handleDateChange }
            open={ this.state.focused }
          />
        </span>
      );
    }

    let htmlInput = null;
    if (showTextArea) {
      htmlInput = <textarea 
        ref={this.entry}
        rows="1"
        placeholder={ this.props.placeholder }
        className={ inputClassList }
        onChange={ this._onTextEntryUpdated }
        onKeyDown={ this._onKeyDown }
        {...this.props.inputProps}
      >
        { this.state.entryValue }
      </textarea>

    } else {
      htmlInput = <input
        data-testid="structured-filter-input"
        ref={this.entry}
        type="text"
        placeholder={ this.props.placeholder }
        className={ inputClassList }
        defaultValue={ this.state.entryValue }
        onChange={ this._onTextEntryUpdated }
        onKeyDown={ this._onKeyDown }
        {...this.props.inputProps}
      />
    }

    return (
      <span
        ref={this.input}
        className={ classList }
        onFocus={ this._onFocus }
      >
        {htmlInput}
        { this._renderIncrementalSearchResults() }
      </span>
    );
  }
}

export default listensToClickOutside( Typeahead );
