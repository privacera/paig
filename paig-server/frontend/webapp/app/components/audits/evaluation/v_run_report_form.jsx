import React, { useEffect, useState} from 'react';
import { observer } from 'mobx-react';

import { FormHorizontal, FormGroupInput, FormGroupSelect2 } from 'common-ui/components/form_fields';

const VRunReportForm = observer(({form, mode, asUser = false}) => {
  const { name, report_name, auth_user } = form.fields;
  const [authType, setAuthType] = useState('basicauth');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [applicationID, setApplicationID] = useState('');
  useEffect(() => {
    const generateReportName = () => {
      if (name.value) {
        const now = new Date();
        const formattedDate = now.toLocaleDateString('en-GB').split('/').reverse().join(''); // Format: DDMMYYYY
        const formattedTime = now.toLocaleTimeString('en-GB', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }).replace(':', ''); // Format: HHmm
        const reportType = mode === "rerun_report" ? "rerun_report" : "report";
        return `${name.value}_${reportType}_${formattedDate}${formattedTime}`;
      }
      return '';
    };

    report_name.value = generateReportName();
  }, [name.value, report_name]);

  useEffect(() => {
    if (!asUser) {
     if (auth_user) auth_user.value = null;
    } else {
      setApplicationID(form.model.application_ids.split(',').map(val => val.trim()))
    }
  }, [asUser]);

  useEffect(() => {
    if (asUser) {
      if (authType === 'basicauth' && username && password) {
        auth_user.value = { applicationID: 
          { 'token': 'Basic ' + btoa(`${username}:${password}`), 'username': username}};
      } else if (authType === 'bearertoken' && token) {
        auth_user.value = { applicationID: 
          {'token': token, 'username': username}};
      } else {
        auth_user.value = null; // Reset if input is incomplete
      }
    }
  }, [authType, username, password, token, asUser]);

  return (
    <FormHorizontal>
      <FormGroupInput
        textOnly={true}
        label={"Security Evaluation Name"}
        fieldObj={name}
        inputProps={{ 'data-testid': 'name-input' }}
      />
      <FormGroupInput
        required={true}
        label={"Report Name"}
        fieldObj={report_name}
        inputProps={{ 'data-testid': 'report-input' }}
      />
      {asUser && (<> <FormGroupSelect2
        label="Authorization Type"
        data={[
          { label: 'Basic Auth', value: 'basicauth' },
          { label: 'Bearer Token', value: 'bearertoken' }
        ]}
        value={authType}
        onChange={(value) => setAuthType(value)}
        required={true}
        multiple={false}
      />
      <FormGroupInput
        label="Username- user as target user for AI Application"
        value={username}
        placeholder="username"
        inputProps={{ 'data-testid': 'username-input' }}
        onChange={(e) => setUsername(e.target.value)}
      />
      {authType === 'basicauth'?(<FormGroupInput
        label={'Password'}
        type={'password'}
        value={password}
        placeholder="password"
        inputProps={{ 'data-testid': 'userpassword-input' }}
        onChange={(e) => setPassword(e.target.value)}
      />):
        <FormGroupInput
        required={true}
        label={"Bearer Token"}
        value={token}
        placeholder="Bearer <token>"
        inputProps={{ 'data-testid': 'token-input' }}
        onChange={(e) => setToken(e.target.value)}
        />
      }
      </>
    )}
    </FormHorizontal> 
  );
});

export default VRunReportForm;

const evaluation_run_form_def = {
  id: {},
  name: {
    validators: {
      errorMessage: 'Evaluation Name is required!',
      fn: (field) => (field.value || '').trim().length > 0
    }
  },
  report_name: {
    validators: {
      errorMessage: 'Report Name is required!',
      fn: (field) => (field.value || '').trim().length > 0
    }
  },
  auth_user: {
    validators: {
      errorMessage: 'Please Select Valid Authorization',
      fn: (field) => (field.value) && Object.keys(field.value).length > 0
    }
  }
}

export {
  evaluation_run_form_def
}