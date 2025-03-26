import React, {useEffect, useRef} from 'react';
import {observer} from 'mobx-react';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Alert from '@material-ui/lab/Alert';
import TextField from '@material-ui/core/TextField';
import FormLabel from '@material-ui/core/FormLabel';
import DateRangeIcon from '@material-ui/icons/DateRange';
import InputAdornment from '@material-ui/core/InputAdornment';

import {Utils} from 'common-ui/utils/utils';
import {STATUS} from 'common-ui/utils/globals';
import DateRangePicker from 'common-ui/lib/daterangepicker';
import {FormGroupInput} from 'common-ui/components/form_fields';
import {STATUS, DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CommandDisplay} from 'common-ui/components/action_buttons';
import {FormGroupInput, FormHorizontal, FormGroupCheckbox} from 'common-ui/components/form_fields';

const VAIApplicationApiKeysForm = observer(({form, _vState}) => {

  const {apiKeyName, description, neverExpire, tokenExpiry} = form.fields;
  const moment = Utils.dateUtil.momentInstance();
  const initialStartDate = moment().add(1, 'months').format(DATE_TIME_FORMATS.DATE_FORMAT);
  const apiKeySectionRef = useRef(null);

  useEffect(() => {
    if (_vState.apiKeyMasked && apiKeySectionRef.current) {
      apiKeySectionRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [_vState.apiKeyMasked]);

  return (
      <FormHorizontal>
          <FormGroupInput
              required={true}
              label="Name"
              fieldObj={apiKeyName}
              disabled={_vState.apiKeyMasked}
              data-testid="name"
          />
          <FormGroupInput
              label="Description"
              rows={2}
              as="textarea"
              maxLength={4000}
              fieldObj={description}
              disabled={_vState.apiKeyMasked}
              data-testid="description"
          />
          <FormGroupCheckbox
              label={'Never Expires'}
              fieldObj={neverExpire}
              disabled={_vState.apiKeyMasked}
              inputColAttr={{ xs: 12}}
              data-testid="never-expire"
          />
          {!neverExpire.value &&
              <Grid item xs={12}>
                  <FormLabel required={true}>Expiry</FormLabel>
                  <DateRangePicker
                      initialSettings={{
                          startDate: moment().add(1, 'months'),
                          minDate: moment(),
                          drops: "up",
                          timePicker: true,
                          timePicker24Hour: true,
                          singleDatePicker: true
                      }}
                      onApply={(event, picker) => {
                          tokenExpiry.value = picker.startDate;
                          neverExpire.value = false;
                      }}
                      >
                      <TextField
                          data-testid={'date-range-picker-api-key'}
                          label=""
                          readOnly
                          variant="outlined"
                          value={tokenExpiry.value ? moment(tokenExpiry.value).format(DATE_TIME_FORMATS.DATE_FORMAT) : initialStartDate}
                          InputProps={{
                              endAdornment:(
                                  <InputAdornment position="end" className='hint'>
                                      <DateRangeIcon />
                                  </InputAdornment>
                              )
                          }}
                          disabled={_vState.apiKeyMasked}
                          fullWidth
                      />
                  </DateRangePicker>
              </Grid>
          }
          {_vState.apiKeyMasked && (
              <Grid item xs={12} ref={apiKeySectionRef} data-testid="api-key-section">
                  <FormLabel>
                      API Key
                  </FormLabel>
                  <Alert severity="info" className="m-b-sm">
                      This API key is shown only once. Make sure to copy and save it securely, as it cannot be viewed again.
                  </Alert>
                  <Box style={{ backgroundColor: '#f0f0f0', padding: '10px', borderRadius: '4px' }}>
                      <CommandDisplay
                          key="command"
                          id="app-key"
                          command={_vState.apiKeyMasked}
                          copyButton
                      />
                  </Box>
              </Grid>
          )}
      </FormHorizontal>
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
  tokenExpiry: {},
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