import {default as React, Component} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import MenuItem from '@material-ui/core/MenuItem';

// material Imports
import withStyles from '@material-ui/core/styles/withStyles'
/**
 * A single option within the TypeaheadSelector
 */ 

 const styles = {
   root: {
      textDecoration: 'none',
      backgroundColor: 'rgba(0, 0, 0, 0.04)'
   }
 }
class TypeaheadOption extends Component {
  static propTypes = {
    customClasses: PropTypes.object,
    result: PropTypes.string,
    onClick: PropTypes.func,
    children: PropTypes.string,
    hover: PropTypes.bool,
  }

  static defaultProps = {
    customClasses: {},
    onClick( event ) {
      event.preventDefault();
    },
  }

  constructor( ...args ) {
    super( ...args );
    this._onClick = this._onClick.bind( this );
  }

  _getClasses() {
    const classes = {
      'typeahead-option': true,
    };
    classes[ this.props.customClasses.listAnchor ] = !!this.props.customClasses.listAnchor;
    return classNames( classes );
  }

  _onClick( event ) {
    event.preventDefault();
    return this.props.onClick( this.props.result );
  }

  render() {
    const classes = {
      hover: this.props.hover,
    };
    classes[ this.props.customClasses.listItem ] = !!this.props.customClasses.listItem;
    const classList = classNames( classes );
    const {classes : styleClass} = this.props;

    return (
      <MenuItem data-testid="filter-options" classes={{root: this.props.hover && styleClass.root}} className={ `${classList} ${this._getClasses()}` } onClick={ this._onClick } >
        { this.props.children }
      </MenuItem>
    );
  }
}   

export default withStyles(styles)(TypeaheadOption)