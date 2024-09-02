import {default as React, Component, Fragment} from 'react';
import PropTypes from 'prop-types';

// material Imports
import Chip from '@material-ui/core/Chip';
import CloseIcon from '@material-ui/icons/Close';
import Box from '@material-ui/core/Box';

/**
 * Encapsulates the rendering of an option that has been "selected" in a
 * TypeaheadTokenizer
 */
export default class Token extends Component {
  static propTypes = {
    children: PropTypes.object,
    onRemove: PropTypes.func,
  }

  constructor( ...args ) {
    super( ...args );
    this._handleClick = this._handleClick.bind( this );
  }

  _handleClick( event ) {
    this.props.onRemove( this.props.children );
    event.preventDefault();
  }

  _makeCloseButton() {
    if ( !this.props.onRemove ) {
      return '';
    }
    return (
      <a className="typeahead-token-close" href="#" onClick={ this._handleClick }><CloseIcon fontSize="small" /></a>
    );
  }

  render() {
    const { category, operator, value } = this.props.children;
    const {onRemove, ...props} = this.props;

    return (
      <Chip
        data-testid="chip-token"
        label={
          <Fragment>
            <span data-testid="token-category" className="token-category">{ category }</span>
            <span data-testid="token-operator" className="token-operator">{ operator || ':' }</span>
            <span data-testid="token-value" className="token-value">{ value }</span>
          </Fragment>
        }
        deleteIcon={<CloseIcon data-testid="token-clear" fontSize="small" />}
        onDelete={this._handleClick}
      />
    )

    return (
      <Box pt={0} pb={0} pl={1} pr={1} display="flex" alignItems="center" component="div" {...props} className="typeahead-token">
        <span className="token-category">{ category }</span>
        <span className="token-operator">{ operator || ':' }</span>
        <span className="token-value">{ value }</span>
        { this._makeCloseButton() }
      </Box>
    );
  }
}
