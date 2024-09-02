import {REGEX} from 'utils/globals';
import {STATUS} from 'common-ui/utils/globals';

const user_form_def = {
  id: {},
  firstName: {
    defaultValue: "",
    validators: {
      errorMessage: 'Required!',
      fn: (field) => {
        if (field.value.trim().length > 0) {
          let isValid = REGEX.FIRSTNAME.test(field.value);
          field._originalErrorMessage = 'Invalid Firstname!';
          return isValid;
        }
        field._originalErrorMessage = 'Required!';
        return false;
      }
    }
  },
  lastName: {},
  email: {
    defaultValue: '',
    validators: {
      errorMessage: 'Required!',
      fn: (field, fields) => {
        if (field.value.trim().length) {
          let isValid = REGEX.EMAIL.test(field.value);
          field._originalErrorMessage = 'Invalid Email Address!';
          return isValid;
        } else if (fields.roles.value?.includes('OWNER')) {
          field._originalErrorMessage = 'Required!';
          return false;
        }
        field._originalErrorMessage = '';
        return true;
      }
    }
  },
  username: {
    defaultValue: "",
    validators: {
      errorMessage: '',
      fn: (field, fields) => {
        let isValid = (field.value || '').length > 0;
        field._originalErrorMessage = "Required!";
        return isValid;
      }
    }
  },
  password: {
    defaultValue: '',
    validators: {
      errorMessage: 'Required!',
      fn: (field, fields) => {
        if (field.value.trim().length) {
          let isValid = REGEX.PASSWORD.test(field.value);
          field._originalErrorMessage = "Valid Password Required!";
          return isValid;
        } else if (fields.roles.value?.includes('OWNER')) {
          field._originalErrorMessage = 'Required!';
          return false;
        }
        field._originalErrorMessage = '';
        return true;
      }
    }
  },
  roles: {
    defaultValue:[],
    validators: {
      errorMessage: 'Required!',
      fn: (field, fields) => {
          return (''+field.value || '').length > 0;
      }
    },
  },
  status: {
    defaultValue: STATUS.enabled.value
  },
  userInvited: {
    defaultValue: true
  }
}

export {
  user_form_def
}
