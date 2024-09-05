import {default as React, Component} from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import Token from './token';
import KeyEvent from '../keyevent';
import Typeahead from '../typeahead';
import classNames from 'classnames';

/**
 * A typeahead that, when an option is selected, instead of simply filling
 * the text entry widget, prepends a renderable "token", that may be deleted
 * by pressing backspace on the beginning of the line with the keyboard.
 *
 * Example usage:
 *
 *      import StructuredFilter from 'react-structured-filter';
 *
 *      <StructuredFilter
 *        placeholder="Search..."
 *        options={[
 *          {category:"Name",type:"text"},
 *          {category:"Price",type:"number"},
 *        ]}
 *      />
 */
export default class Tokenizer extends Component {

  static propTypes = {
    /**
     * An array of structures with the components `category` and `type`
     *
     * * _category_: Name of the first thing the user types.
     * * _type_: This can be one of the following:
     *   * _text_: Arbitrary text for the value. No autocomplete options.
     *     Operator choices will be: `==`, `!=`, `contains`, `!contains`.
     *   * _textoptions_: You must additionally pass an options value which
     *     will be a function that returns the list of options choices as an
     *     array (for example `function getOptions() {return ["MSFT", "AAPL",
     *     "GOOG"]}`). Operator choices will be: `==`, `!=`.
     *   * _number_: Arbitrary text for the value. No autocomplete options.
     *     Operator choices will be: `==`, `!=`, `<`, `<=`, `>`, `>=`.
     *   * _date_: Shows a calendar and the input must be of the form
     *     `MMM D, YYYY H:mm A`. Operator choices will be: `==`, `!=`, `<`, `<=`, `>`,
     *     `>=`.
     *
     * Example:
     *
     *     [
     *       {
     *         "category": "Symbol",
     *         "type": "textoptions",
     *         "options": function() {return ["MSFT", "AAPL", "GOOG"]}
     *       },
     *       {
     *         "category": "Name",
     *         "type": "text"
     *       },
     *       {
     *         "category": "Price",
     *         "type": "number"
     *       },
     *       {
     *         "category": "MarketCap",
     *         "type": "number"
     *       },
     *       {
     *         "category": "IPO",
     *         "type": "date"
     *       }
     *     ]
     */
    options: PropTypes.array,

    /**
     * An object containing custom class names for child elements. Useful for
     * integrating with 3rd party UI kits. Allowed Keys: `input`, `results`,
     * `listItem`, `listAnchor`, `typeahead`, `hover`
     *
     * Example:
     *
     *     {
     *       input: 'filter-tokenizer-text-input',
     *       results: 'filter-tokenizer-list__container',
     *       listItem: 'filter-tokenizer-list__item'
     *     }
     */
    customClasses: PropTypes.object,

    /**
     * **Uncontrolled Component:** A default set of values of tokens to be
     * loaded on first render. Each token should be an object with a
     * `category`, `operator`, and `value` key.
     *
     * Example:
     *
     *     [
     *       {
     *         category: 'Industry',
     *         operator: '==',
     *         value: 'Books',
     *       },
     *       {
     *         category: 'IPO',
     *         operator: '>',
     *         value: 'Dec 8, 1980 10:50 PM',
     *       },
     *       {
     *         category: 'Name',
     *         operator: 'contains',
     *         value: 'Nabokov',
     *       },
     *     ]
     */
    defaultValue: PropTypes.array,

    /**
     * **Controlled Component:** A set of values of tokens to be loaded on
     * each render. Each token should be an object with a `category`,
     * `operator`, and `value` key.
     *
     * Example:
     *
     *     [
     *       {
     *         category: 'Industry',
     *         operator: '==',
     *         value: 'Books',
     *       },
     *       {
     *         category: 'IPO',
     *         operator: '>',
     *         value: 'Dec 8, 1980 10:50 PM',
     *       },
     *       {
     *         category: 'Name',
     *         operator: 'contains',
     *         value: 'Nabokov',
     *       },
     *     ]
     */
    value: PropTypes.array,

    /**
     * Placeholder text for the typeahead input.
     */
    placeholder: PropTypes.string,

     /**
     * Additional attributes for typeahed input
     */
    inputProps: PropTypes.object,

    /**
     * Event handler triggered whenever the filter is changed and a token
     * is added or removed. Params: `(filter)`
     */
    onChange: PropTypes.func,
  }

  static defaultProps = {
    // value: [],
    // defaultValue: [],
    options: [],
    customClasses: {},
    placeholder: '',
    inputProps: {'data-test': 'input-tokenizer'},
    onChange() {},
  }

  constructor( ...args ) {
    super( ...args );
    this._addTokenForValue = this._addTokenForValue.bind( this );
    this._onKeyDown = this._onKeyDown.bind( this );
    this._getOptionsForTypeahead = this._getOptionsForTypeahead.bind( this );
    this._removeTokenForValue = this._removeTokenForValue.bind( this );
  }

  state = {
    selected: this.getStateFromProps( this.props ),
    category: '',
    operator: '',
  }

  customTypeOptions = ['textoptions', 'textareaoptions'];

  componentDidMount() {
    this.props.onChange( this.state.selected, 'renderEnd');
  }

  componentDidUpdate(prevProps) {
    if ( prevProps.value !== this.props.value ) {
      this.setState({selected : this.getStateFromProps(this.props)});
    }
  }

  getStateFromProps( props ) {
    const value = props.value || props.defaultValue || [];
    return value.slice( 0 );
  }

  _renderTokens() {
    const tokenClasses = {};
    tokenClasses[ this.props.customClasses.token ] = !!this.props.customClasses.token;
    const classList = classNames( tokenClasses );
    const result = this.state.selected.map( selected => {
      const mykey = selected.category + selected.operator + selected.value;

      return (
        <Token
          key={ mykey }
          className={ classList }
          onRemove={ this._removeTokenForValue }
        >
          { selected }
        </Token>

      );
    }, this );
    return result;
  }

  _getOptionsForTypeahead() {
    let categoryType;

    if ( this.state.category === '' ) {
      const categories = [];
      for ( let i = 0; i < this.props.options.length; i++ ) {

        const opt = this.props.options[ i ];
        if( opt.multi == false ) {
          if( this.state.selected.find( s => s.category === opt.category ) ){
            continue;
          }
        }

        categories.push( opt.category );
      }
      return categories;
    } else if ( !this.props.noOperator && this.state.operator === '' ) {

      let categoryOperator = this._getCategoryOperator() || this.props.operator;

      if(categoryOperator && categoryOperator != 'default') {
        return categoryOperator;
      }

      categoryType = this._getCategoryType();

      if ( categoryType === 'text' ) {
        return [ '==', '!=', 'contains', '!contains' ];
      } else if (this.customTypeOptions.includes(categoryType)) {
        return [ '==', '!=' ];
      } else if ( categoryType === 'number' || categoryType === 'date' ) {
        return [ '==', '!=', '<', '<=', '>', '>=' ];
      }

      /* eslint-disable no-console */
      console.warn( `WARNING: Unknown category type in tokenizer: "${categoryType}"` );
      /* eslint-enable no-console */

      return [];
    }
    const options = this._getCategoryOptions();
    if ( options === null || options === undefined ) return [];
    return options();
  }

  _getHeader() {
    if ( this.state.category === '' ) {
      return 'Category';
    } else if(this.props.noOperator){
      return "Value"
    } else if ( this.state.operator === '' ) {
      return 'Operator';
    }

    return 'Value';
  }

  _getCategoryType( category ) {
    let categoryType;
    let cat = category;
    if ( !category || category === '' ) {
      cat = this.state.category;
    }
    for ( let i = 0; i < this.props.options.length; i++ ) {
      if ( this.props.options[ i ].category === cat ) {
        categoryType = this.props.options[ i ].type;
        return categoryType;
      }
    }
  }

  _getCategoryOptions() {
    for ( let i = 0; i < this.props.options.length; i++ ) {
      if ( this.props.options[ i ].category === this.state.category ) {
        return this.props.options[ i ].options;
      }
    }
  }

  _getCategoryOperator() {
    for ( let i = 0; i < this.props.options.length; i++ ) {
      if ( this.props.options[ i ].category === this.state.category ) {
        return this.props.options[ i ].operator;
      }
    }
  }


  _onKeyDown( event ) {
    // We only care about intercepting backspaces
    if ( event.keyCode !== KeyEvent.DOM_VK_BACK_SPACE ) {
      return;
    }

    // Remove token ONLY when bksp pressed at beginning of line
    // without a selection
    const entry = ReactDOM.findDOMNode( this.typeahead.instanceRef.inputRef());
    if ( entry.selectionStart === entry.selectionEnd &&
        entry.selectionStart === 0 ) {
      if ( this.state.operator !== '' ) {
        this.setState({ operator: '' });
      } else if ( this.state.category !== '' ) {
        this.setState({ category: '' });
      } else {
        // No tokens
        if ( !this.state.selected.length ) {
          return;
        }
        const lastSelected = JSON.parse(
          JSON.stringify( this.state.selected[ this.state.selected.length - 1 ])
        );
        this._removeTokenForValue(
          this.state.selected[ this.state.selected.length - 1 ]
        );
        this.setState({ category: lastSelected.category, operator: lastSelected.operator });
        if (!this.customTypeOptions.includes(this._getCategoryType( lastSelected.category ))) {
          this.typeahead.instanceRef.setEntryText( lastSelected.value );
        }
      }
      event.preventDefault();
    }
  }

  _removeTokenForValue( value ) {
    const index = this.state.selected.indexOf( value );
    if ( index === -1 ) {
      return;
    }

    this.state.selected.splice( index, 1 );
    this.setState({ selected: this.state.selected });
    this.props.onChange( this.state.selected, 'remove');

    return;
  }

  _addTokenForValue( value ) {
    if ( this.state.category === '' ) {
      this.setState({ category: value });
      this.typeahead.instanceRef.setEntryText( '' );
      return;
    }

    if ( !this.props.noOperator && this.state.operator === '' ) {
      this.setState({ operator: value });
      this.typeahead.instanceRef.setEntryText( '' );
      return;
    }

    if(value == '') {
      return;
    }

    if (this.state.selected.length) {
      let index = this.state.selected.findIndex((obj) => obj.category == this.state.category && obj.operator == this.state.operator && obj.value == value);
      if (index > -1) {
        this.typeahead.instanceRef.setEntryText( '' );
        this.setState({
          category: '',
          operator: '',
        });
        return;
      }
    }

    const newValue = {
      category: this.state.category,
      operator: this.state.operator,
      value,
    };

    this.state.selected.push( newValue );
    this.setState({ selected: this.state.selected });
    this.typeahead.instanceRef.setEntryText( '' );
    this.props.onChange( this.state.selected, 'add');

    this.setState({
      category: '',
      operator: '',
    });

    return;
  }

  /*
   * Returns the data type the input should use ("date" or "text")
   */
  _getInputType() {
    const categoryType = this._getCategoryType();
    if ( this.state.category !== '' && this.state.operator !== '' ) {
      return categoryType;
    }
    if (this.customTypeOptions[1] === categoryType) {
      return 'textarea';
    }

    return 'text';
  }

  render() {
    const classes = {};
    classes[ this.props.customClasses.typeahead ] = !!this.props.customClasses.typeahead;
    const classList = classNames( classes );
    return (
      <div className="filter-tokenizer">
        <div className="token-collection">
          { this._renderTokens() }

          <div className="filter-input-group">
            <div className="filter-category">{ this.state.category } </div>
            <div className="filter-operator">{ this.state.operator } </div>

            <Typeahead ref={ref => this.typeahead = ref}
              className={ classList }
              placeholder={ this.props.placeholder }
              customClasses={ this.props.customClasses }
              options={ this._getOptionsForTypeahead() }
              header={ this._getHeader() }
              datatype={ this._getInputType() }
              onOptionSelected={ this._addTokenForValue }
              onKeyDown={ this._onKeyDown }
              inputProps={this.props.inputProps}
              customTypeOptions={this.customTypeOptions}
            />
            </div>
          </div>
      </div>
    );
  }
}
