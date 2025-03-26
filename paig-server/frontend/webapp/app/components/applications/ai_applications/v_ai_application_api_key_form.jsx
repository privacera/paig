import React, {Fragment} from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import Alert from '@material-ui/lab/Alert';
import TextField from '@material-ui/core/TextField';
import FormLabel from '@material-ui/core/FormLabel';
import DateRangeIcon from '@material-ui/icons/DateRange';
import InputAdornment from '@material-ui/core/InputAdornment';

import {Utils} from 'common-ui/utils/utils';
import DateRangePicker from 'common-ui/lib/daterangepicker';
import {STATUS, DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {FormGroupInput, FormHorizontal, FormGroupCheckbox} from 'common-ui/components/form_fields';
import {CommandVisibilityToggle} from 'components/applications/ai_applications/v_ai_application_api_keys';

const moment = Utils.dateUtil.momentInstance();

const VAIApplicationApiKeysForm = observer(({form, _vState}) => {
  const {apiKeyName, description, neverExpire, tokenExpiry} = form.fields;
  const initialStartDate = moment().add(1, 'months').format(DATE_TIME_FORMATS.DATE_ONLY_FORMAT);
  return (
    <Fragment>
      {_vState.apiKeyMasked ? (
        <Grid item xs={12} data-testid="api-key-section">
          <Alert severity="info" className="m-b-sm">
            This API key is shown only once. Make sure to copy and save it securely, as it cannot be viewed again.
          </Alert>
          <CommandVisibilityToggle key="command" id="app-key" command={_vState.apiKeyMasked} />
        </Grid>
      ) : (
        <FormHorizontal>
          <FormGroupInput
            required={true}
            label="Name"
            fieldObj={apiKeyName}
            data-testid="name"
          />
          <FormGroupInput
            label="Description"
            rows={2}
            as="textarea"
            maxLength={4000}
            fieldObj={description}
            data-testid="description"
          />
          <FormGroupCheckbox
            label={'Max Validity (1 year)'}
            fieldObj={neverExpire}
            inputColAttr={{ xs: 12}}
            data-testid="never-expire"
          />
          {!neverExpire.value &&
            <Grid item xs={12}>
              <FormLabel required={true}>Expiry</FormLabel>
              <DateRangePicker
                initialSettings={{
                  startDate: moment().add(1, 'months'),
                  minDate: moment().add(1, 'day'),
                  maxDate: moment().add(1, 'year'),
                  drops: "up",
                  singleDatePicker: true
                }}
                onApply={(event, picker) => {
                  tokenExpiry.value = moment(picker.startDate).set({ hour: 0, minute: 0, second: 0 }).utc().toISOString();
                  neverExpire.value = false;
                }}
                >
                <TextField
                  data-testid={'date-range-picker-api-key'}
                  label=""
                  readOnly
                  variant="outlined"
                  value={tokenExpiry.value ? moment(tokenExpiry.value).format(DATE_TIME_FORMATS.DATE_ONLY_FORMAT) : initialStartDate}
                  InputProps={{
                    endAdornment:(
                      <InputAdornment position="end" className='hint'>
                        <DateRangeIcon />
                      </InputAdornment>
                    )
                  }}
                  fullWidth
                />
              </DateRangePicker>
            </Grid>
          }
        </FormHorizontal>
      )}
    </Fragment>
  )
});

const ai_application_api_keys_form_def = {
  id: {},
  userId:{},
  addedById:{},
  applicationId:{},
  apiKeyName: {
    validators: {
      errorMessage: 'Required!',
      fn: (field) => {
        return (field.value || '').length > 0;
      }
    }
  },
  description: {},
  tokenExpiry: {
    defaultValue: moment().add(1, 'months').set({ hour: 0, minute: 0, second: 0, millisecond: 0 }).utc().toISOString()
  },
  neverExpire: {
    defaultValue: STATUS.disabled.value
  },
  scopes: {
    defaultValue: [3]
  },
  status: {
    defaultValue: STATUS.enabled.value
  }
}

export {
  ai_application_api_keys_form_def
}
export default VAIApplicationApiKeysForm;