/* library imports */
import React from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';
import Chip from '@material-ui/core/Chip';

/* other project imports */
import { FormHorizontal, FormGroupInput, FormGroupSelect2, FormGroupSwitch } from 'common-ui/components/form_fields';
import UiState from 'data/ui_state';

const VUserManagementForm = observer(function VUserManagementForm({ form, isProfile, readOnly }) {
  let {fields, model} = form;
  const {id, firstName, lastName, username, email, roles, status, password} = fields;
  return (
    <FormHorizontal>
      {
        UiState.user && UiState.user.id == id.value || readOnly
        ?
          <Grid item xs={12}>
            <FormLabel>Role</FormLabel>
            <div>
              {
                roles.value ? roles.value.map((role, i) => (
                  <Chip key={i} label={role} color="primary" size="small" className="m-r-xs m-t-xs" />
                )) : "--"
              }
            </div>
          </Grid>
        :
          (
            <FormGroupSelect2
              data-testid="roles-input"
              required={true}
              label="Role"
              fieldObj={roles}
              data={[
                { label: "OWNER", value: "OWNER" }, 
                { label: "USER", value: "USER" }
              ]}
              multiple={false}
              labelKey={'label'}
              valueKey={'value'}
              inputProps={{'data-test': 'roles'}}
              onChange={(value) => roles.value = value}
              onBlur={() => {
                if (roles.value.includes('USER') && !email.value) {
                  email.errorMessage = '';
                }
              }}
            />
          )
      }

      <FormGroupInput
        required={true}
        textOnly={!!id.value || readOnly}
        fieldObj={username}
        label={"User Name"}
        onChange={(e) => username.value = e.target.value.toLowerCase().trim()}
        // onBlur={(e) => checkUniqueUser('username', e.target.value)}
        data-test="user-name"
      />

      {!isProfile && 
        <FormGroupInput
          textOnly={!!id.value && model.password || readOnly}
          required={roles.value.includes('OWNER')}
          label={"Password"}
          type={"password"}
          fieldObj={password}
          onChange={(e) => password.value = e.target.value.trim()}
          onBlur={(e) => {
            let val = e.target.value;
          }}
          data-test="password"
        />
      }

      <FormGroupInput
        required={true}
        textOnly={(UiState.user && UiState.user.id == id.value) || isProfile || readOnly}
        label={"First Name"}
        fieldObj={firstName}
        data-test="first-name"
      />

      <FormGroupInput
        textOnly={(UiState.user && UiState.user.id == id.value) || isProfile || readOnly}
        label={"Last Name"}
        fieldObj={lastName}
        data-test="last-name"
      />

      <FormGroupInput
        textOnly={!!id.value && model.email || readOnly || isProfile}
        required={roles.value.includes('OWNER')}
        label={"Email Id"}
        fieldObj={email}
        onChange={(e) => email.value = e.target.value.toLowerCase().trim()}
        onBlur={(e) => {
          let val = e.target.value;
          // checkUniqueUser('email', val);
          setTimeout(() => {
            let index = val.indexOf('@');
            if (!username.value && val && !email.errorMessage && index > -1) {
              username.value = val.slice(0, index);
              // checkUniqueUser('username', username.value);
            }
          }, 200);
        }}
        data-test="email-id"
      />

      {!isProfile && 
        <FormGroupSwitch
          label="Enabled"
          fieldObj={status}
          disabled={UiState.user && UiState.user.id == id.value || readOnly}
          inputColAttr={{ xs: 12 }}
        />
      }

      </FormHorizontal>
    );
})

export default VUserManagementForm;
