import {default as React, Component} from 'react';
import PropTypes from 'prop-types';
import TypeaheadOption from './option';
import classNames from 'classnames';
import Paper from '@material-ui/core/Paper'
import MenuList from '@material-ui/core/MenuList';
import ListSubheader from '@material-ui/core/ListSubheader';

/**
 * Container for the options rendered as part of the autocompletion process
 * of the typeahead
 */
export default class TypeaheadSelector extends Component {
  static propTypes = {
    options: PropTypes.array,
    header: PropTypes.string,
    customClasses: PropTypes.object,
    selectionIndex: PropTypes.number,
    onOptionSelected: PropTypes.func,
  }

  static defaultProps = {
    selectionIndex: null,
    customClasses: {},
    onOptionSelected() {},
  }

  constructor( ...args ) {
    super( ...args );
    this._onClick = this._onClick.bind( this );
    this.navDown = this.navDown.bind( this );
    this.navUp = this.navUp.bind( this );
  }

  state = {
    selectionIndex: this.props.selectionIndex,
    selection: this.getSelectionForIndex( this.props.selectionIndex ),
  }

  componentWillReceiveProps() {
    this.setState({ selectionIndex: null });
  }

  setSelectionIndex( index ) {
    this.setState({
      selectionIndex: index,
      selection: this.getSelectionForIndex( index ),
    });
  }

  getSelectionForIndex( index ) {
    if ( index === null ) {
      return null;
    }
    return this.props.options[ index ];
  }

  _onClick( result ) {
    this.props.onOptionSelected( result );
  }

  _nav( delta ) {
    if ( !this.props.options ) {
      return;
    }

    let newIndex;
    if ( this.state.selectionIndex === null ) {
      if ( delta === 1 ) {
        newIndex = 0;
      } else {
        newIndex = delta;
      }
    } else {
      newIndex = this.state.selectionIndex + delta;
    }

    if ( newIndex < 0 ) {
      newIndex += this.props.options.length;
    } else if ( newIndex >= this.props.options.length ) {
      newIndex -= this.props.options.length;
    }

    const newSelection = this.getSelectionForIndex( newIndex );
    this.setState({
      selectionIndex: newIndex,
      selection: newSelection,
    });
  }

  navDown() {
    this._nav( 1 );
  }

  navUp() {
    this._nav( -1 );
  }

  render() {
    const classes = {
      'typeahead-selector': true,
    };
    classes[ this.props.customClasses.results ] = this.props.customClasses.results;
    const classList = classNames( classes );

    const results = this.props.options.map(
      ( result, i ) => (
        <TypeaheadOption
          ref={ result }
          key={ result }
          result={ result }
          hover={ this.state.selectionIndex === i }
          customClasses={ this.props.customClasses }
          onClick={ this._onClick }
        >
          { result }
        </TypeaheadOption>
      )
    , this );

    return (
      <MenuList data-testid="filter-options-ul" className="typeahead-selector"> 
      <Paper elevation={3}>
        <ListSubheader className="header">{ this.props.header }</ListSubheader>
        { results }
      </Paper>
    </MenuList>
      
    );
  }
}
