import {observable, computed, action, transaction, extendObservable, autorun, isObservableArray} from 'mobx';
import Promise from 'bluebird';
import debounce from 'debouncy';
import clsc from 'coalescy';
import ReactDOM from "react-dom"

class Field {
  @observable _name;
  @observable _value;
  _skipValidation = false;
  @observable _interacted = false;
  @observable _fieldOpts;
  @observable _valid = true;
  @observable errorMessage='';
  @observable interactive = true;

  _originalErrorMessage;
  defaultValue;


  markAsTouch() {
    if (!this._touched) {
      this._touched = true;
    }
  }

  @computed get valid() {
    return this._valid;
  }

  @computed get interacted() {
    return this._interacted;
  }

  get name() {
    return this._name;
  }

  set name(_name) {
    this._name = _name;
  }

  get value() {
    if (isObservableArray(this._value)) {
      return [].slice.call(this._value);
    }
    return this._value;
  }

  set value(val) {
    if (!this._interacted && this._value != undefined) {
      this._interacted = true;
    }

    if (this._value === val) {
      return;
    }

    this._value = val;

    if (this._skipValidation) {
      return;
    }

    if (this.interactive) {
      this._debouncedValidation();
    } else {
      this._debounceClearValidation();
    }
  }

  clearValidation() {
    this._valid = true;
    this.errorMessage = '';
  }

  clearInteractive() {
    this._interacted = false;
  }

  set fieldOpts(fieldOpts = {}){
    this._fieldOpts = fieldOpts;
  }

  get fieldOpts(){
    return this._fieldOpts;
  }
  @action
  validate(force = false) {
    if (!this._validateFn) {
      return;
    }

    if (!force && !this._interacted) {
      // if we're not forcing the validation
      // and we haven't interacted with the field
      // we asume this field pass the validation status
      this._valid = true;
      this.errorMessage = '';
      return;
    }
    const res = this._validateFn(this, this.model.fields, this.model);

    // if the function returned a boolean we assume it is
    // the flag for the valid state
    if (typeof res === 'boolean') {
      this._valid = res;
      this.errorMessage = res ? '' : this._originalErrorMessage;
      return;
    }

    // otherwise we asumme we have received a promise
    const p = Promise.resolve(res);
    return new Promise((resolve) => { // eslint-disable-line consistent-return
      p.then(
        () => {
          this._valid = true;
          this.errorMessage = '';
          resolve(); // we use this to chain validators
        },
        ({ error } = {}) => {
          this.errorMessage = (error || '').trim() || this._originalErrorMessage;
          this._valid = false;
          resolve(); // we use this to chain validators
        });
    });
  }

  addValidator(validatorDescriptor = {}) {
    this._originalErrorMessage = validatorDescriptor.errorMessage;
    this._validateFn = validatorDescriptor.fn || validationNOOP;
    this.interactive = clsc(validatorDescriptor.interactive, true);
  }

  constructor(model, name='', value={}, fieldOpts = {}, validatorDescriptor = {}, defaultValue="") {
    this.model = model;
    this._debouncedValidation = debounce(this.validate, 300, this);
    this._debounceClearValidation = debounce(this.clearValidation, 300, this);
    this.name = name;
    this.value = value;
    this.fieldOpts = fieldOpts;
    this.defaultValue = defaultValue;
    this._originalErrorMessage = validatorDescriptor.errorMessage;
    let validationNOOP = () => Promise.resolve();
    this._validateFn = validatorDescriptor.fn || validationNOOP;
    this.interactive = clsc(validatorDescriptor.interactive, true);

    /*autorun(() => {
      console.log('name changed', this.name);
    });
    autorun(() => {
      console.log('value changed', this.value);
    });*/
  }
}

class FSForm {
  @observable fields = {};
  // @observable validating = false;
  validating = false;
  @computed get valid() {
    if (this.validating) {
      return false; // consider the form invalid until the validation process finish
    }
    const keys = Object.keys(this.fields);
    return keys.every((key) => {
      const field = this.fields[key];
      return !!field.valid;
    }, true);
  }

  @computed get interacted() {
    const keys = this.fieldKeys();
    return keys.some((key) => {
      const field = this.fields[key];
      return !!field.interacted;
    });
  }

  clearValues(obj) {
    transaction(() => {
      Object.keys(obj).forEach((key) => this.updateField(key, obj[key], true));
    });
  }

  clearForm = () => {
    transaction(() => {
      this.fieldKeys().map(key => this.updateField(key, this.fields[key].defaultValue, true));
    });
  }

  fieldKeys() {
    return Object.keys(this.fields);
  }

  getField(field, throwError = true) {
    const theField = this.fields[field];
    if (throwError && !theField) {
      throw new Error(`Field ${theField} not found`);
    }
    return theField;
  }

  // valueOf(field) {
  //   return this.getField(field).value;
  // }

  @computed get summary() {
    return this.fieldKeys().reduce((seq, key) => {
      const field = this.fields[key];
      if (field.errorMessage) {
        seq.push(field.errorMessage);
      }
      return seq;
    }, []);
  }

  triggerFormChange = (action) => {
    if (this.onChange) {
      this.onChange(action);
    }
  };

  // Smartly update the value of our fields with those from newValues
  @action
  refresh(newValues){
    const keys = Object.keys(this.fields);
    keys.forEach((field) => {
      if(newValues[field] || newValues[field] == 0){
          // TODO. Use updateField() here!
          this.fields[field].value = newValues[field];
      }
    });
    this.triggerFormChange('refresh')
  }

  @action
  clearFormInteractive(){
    const keys = Object.keys(this.fields);
    keys.forEach((field) => {
          this.fields[field]._interacted = false;
      });
  }

  validate(_this) {
    this.validating = true;
    const p = this.fieldKeys().reduce((seq, key) => {
      const field = this.fields[key];
      return seq.then(() => field.validate(true));
    }, Promise.resolve());
    p.then(() => (this.validating = false));
    _this && this.scrollToField(_this);
    return p
  }

  toJSON() {
    const keys = Object.keys(this.fields);
    return keys.reduce((seq, key) => {
      const field = this.fields[key];
      seq[field.name || key] = field.value && field.value.trim ? field.value.trim() : field.value;
      return seq;
    }, {});
  }

  //scroll to the error input field
  scrollToField = (nodeList) => {
    if (!nodeList) return;
    if (!this.valid) {
      const node = ReactDOM.findDOMNode(nodeList);
      if (node instanceof HTMLElement) {
        let nodes = node.querySelectorAll("[value='']");
        for (let el of nodes) {
          let node = null;
          if(el.required){
            if (el.type == 'hidden' || el.parentElement.classList.contains('Select-input')) {
              let parentElement = el.parentElement.parentElement.parentElement;
              let input = parentElement.querySelector('input');
              if (input && input.type == 'hidden' && !input.value) {
                node = parentElement;
              }
            } else {
              node = el;
            }
          }
          if (node) {
            node.scrollIntoView({
              behavior: 'smooth',
              block: 'nearest',
              inline: 'nearest'
            })
            break;
          }
        }
      }
    }
  }

  updateField(field, value, reset) {
    transaction(() => {
      const theField = this.getField(field);

      if (reset) {
        theField._skipValidation = true;
      }

      theField.value = value;

      if (reset) {
        theField.clearValidation();
        theField.clearInteractive();
        theField._skipValidation = false;
      }
    });
    this.triggerFormChange('updateField');
  }

  constructor(fields = {}, model = null) {
    const keys = Object.keys(fields);
    this.model = model;

    keys.forEach((key) => {
      /*const fieldOpts = fields[key]['fieldOpts'];

      extendObservable(this.fields, {
        [key]: new Field(this, fields[key]['defaultValue'] || '', fieldOpts, fields[key]['validators'], fields[key]['defaultValue'])
        //[key]: new Field(this, initialValue, fieldOpts, fields[key]['validators'])
      });*/
      this.addField(key, fields[key]);
    });

    //autorunAsync: is deprecated, we can also use async/await
    autorun(() => {
      this.onChange && this.onChange(this.valid, this.toJSON());
    }, 100);
  }
  addField(key, field={}) {
    let {fieldOpts, validators, name, defaultValue} = field;
    name = (name == null ? '' : name);
    defaultValue = (defaultValue == null ? '' : defaultValue);
    extendObservable(this.fields, {
      [key]: new Field(this, name, defaultValue, fieldOpts, validators, defaultValue)
    });
    this.triggerFormChange('addField');
  }
  updateFieldKey(oldKey, newKey) {
    const field = this.getField(oldKey);
    this.removeField(oldKey);
    extendObservable(this.fields, {
      [newKey]: field
    });
    this.triggerFormChange('updateFieldKey');
  }
  removeField(key) {
    this.fields[key] = undefined;
    delete this.fields[key];
    if(this.fields.$mobx && this.fields.$mobx.values && key){
      delete this.fields.$mobx.values[key]
    };
  }
  @action
  removeAllFields() {
    this.fieldKeys().forEach(key => {
      this.removeField(key);
    })
    this.triggerFormChange('removeAllFields');
  }
}

function createFSForm(fields, model = null) {
  const form = new FSForm(fields, model);
  form.modelToForm = fields.modelToForm;
  form.formToModel = fields.formToModel;
  return form;
}

const requiredValidation = {
  errorMessage: 'Required!',
  fn: (field, fields) => {
    if (field.value) {
      if (typeof field.value == 'string' && field.value.trim().length) {
        return true;
      }
      if (Array.isArray(field.value) && field.value.length) {
        return true;
      }
    }
    return false;
  }
}
const validators = {
  required: requiredValidation
};

export {
  createFSForm,
  validators
}